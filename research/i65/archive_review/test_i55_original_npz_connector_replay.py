"""Synthetic adversarial checks for the pure-JS connected-GitHub NPZ replayer.

No optimizer, PF, COCO or network. Requires numpy and node only for this test.
"""
import base64
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

JS = Path(__file__).with_name("i55_original_npz_connector_replay.js")


def run_js(expr: str, **kw):
    script = (
        "const m=require(" + json.dumps(str(JS)) + ");"
        "const args=JSON.parse(process.env.I55_FIXTURE);"
        + expr
    )
    env = dict(os.environ, I55_FIXTURE=json.dumps(kw))
    proc = subprocess.run(["node", "-e", script], env=env, text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr)
    return json.loads(proc.stdout)


def fixture(lib, function, dims=2, seed=6000, faulty=None):
    xx = np.array([[-5, 5], [3.234, -1.21], [0, 0], [3.234, -1.21]], dtype=np.float64)
    if dims == 10:
        xx = np.tile(xx[:, :1], (1, 10))
    if function == "sphere":
        ff = np.sum((xx + 1.3) ** 2, axis=1)
    elif function == "rastrigin":
        ff = 10 * dims + np.sum(xx ** 2 - 10 * np.cos(2 * np.pi * xx), axis=1)
    else:
        ff = np.sum(np.floor(xx), axis=1)
    if lib in ("evox", "evotorch"):
        ff = ff.astype(np.float32).astype(np.float64)
    if faulty == "nan":
        ff[0] = np.nan
    if faulty == "inf":
        ff[0] = np.inf
    if faulty == "shift":
        ff[0] += 1.0
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "trace.npz"
        np.savez_compressed(path, x=xx, f=ff,
                            phase=np.zeros(len(ff), dtype=np.int8),
                            x_star=xx[int(np.nanargmin(ff))], f_star=np.array([np.nanmin(ff)]),
                            reported_evals=np.array([len(ff)]), documented_max=np.array([len(ff)]))
        b = path.read_bytes()
    rawhash = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\x00" + b).hexdigest()
    transcript = hashlib.sha256()
    for row, f in zip(xx, ff):
        transcript.update(row.tobytes())
        transcript.update(repr(float(f)).encode())
        transcript.update(b"search")
    flags = {k: 0 for k in ("C1", "C2", "C3", "C4", "C5", "R1", "R2", "R3", "D2")}
    seen = set()
    for row in xx:
        if np.array_equal(row, -5 * np.ones(dims)) or np.array_equal(row, 5 * np.ones(dims)):
            flags["C1"] += 1
        if row.tobytes() in seen:
            flags["C2"] += 1
        seen.add(row.tobytes())
    metadata = dict(library=lib, function=function, d=dims, seed=seed,
                    flags=flags, calls=len(ff), hash=transcript.hexdigest(), error=None)
    sourcepath = f"research/results/iteration55/traces/{lib}/{function}_{dims}_{seed}.npz"
    return dict(path=sourcepath, b64=base64.b64encode(b).decode(), blob=rawhash,
                entry={"path": sourcepath, "git_blob_sha1": rawhash, "size": len(b)}, cell=metadata)


class ConnectorNPZReplayTest(unittest.TestCase):
    def test_crypto_known_vectors(self):
        self.assertTrue(run_js("console.log(JSON.stringify([m.i55Sha1(m.i55Decode64(args.raw)),m.i55Sha256(m.i55Decode64(args.raw))]))",
                               raw="YWJj") == ["a9993e364706816aba3e25717850c26c9cd0d89d",
                                                       "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"])

    def test_python_float_repr_sample(self):
        vals = [0., -0., 1., 4., 1e-4, 1e-5, 1e-7, 1e12, 1e15, 1e16,
                -12.001, 1e-12, 1234.51233, float(np.float32(1e-4)), 0.00010000000000002]
        got = run_js("console.log(JSON.stringify(args.values.map(m.i55PyRepr)))", values=vals)
        self.assertEqual(got, [repr(float(x)) for x in vals])

    def test_all_frozen_functions_original_recorder(self):
        for fn in ("sphere", "rastrigin", "plateau"):
            with self.subTest(function=fn):
                a = fixture("baybe", fn)
                got = run_js("console.log(JSON.stringify(m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)))", **a)
                self.assertEqual(got["objective_mismatches"], 0)
                self.assertEqual(got["objective_calls_rechecked"], 4)
                self.assertTrue(got["trace_sha256_match"])

    def test_float32_recorders(self):
        for lib in ("evox", "evotorch"):
            for fn in ("sphere", "rastrigin"):
                with self.subTest(library=lib, function=fn):
                    a = fixture(lib, fn)
                    got = run_js("console.log(JSON.stringify(m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)))", **a)
                    self.assertTrue(got["float32_recorder"])
                    self.assertEqual(got["objective_calls_rechecked"], 4)

    def test_dim_10(self):
        a = fixture("smac", "plateau", dims=10)
        got = run_js("console.log(JSON.stringify(m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)))", **a)
        self.assertEqual(got["objective_calls_rechecked"], 4)

    def test_invalid_f_saved(self):
        for kind in ("nan", "inf", "shift"):
            a = fixture("baybe", "sphere", faulty=kind)
            expr = "let ok=false; try {m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)} catch(e){ok=true;} console.log(JSON.stringify(ok))"
            self.assertTrue(run_js(expr, **a), kind)

    def test_mismatched_raw_blob(self):
        a = fixture("baybe", "sphere")
        a["entry"]["git_blob_sha1"] = "0" * 40
        expr = "let ok=false; try {m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)} catch(e){ok=true;} console.log(JSON.stringify(ok))"
        self.assertTrue(run_js(expr, **a))

    def test_mismatched_trace_hash(self):
        a = fixture("baybe", "sphere")
        a["cell"]["hash"] = "f" * 64
        expr = "let ok=false; try {m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)} catch(e){ok=true;} console.log(JSON.stringify(ok))"
        self.assertTrue(run_js(expr, **a))

    def test_mismatched_flags(self):
        a = fixture("baybe", "sphere")
        a["cell"]["flags"]["C1"] += 1
        expr = "let ok=false; try {m.i55ArchiveAudit(args.path,args.b64,args.blob,args.entry,args.cell)} catch(e){ok=true;} console.log(JSON.stringify(ok))"
        self.assertTrue(run_js(expr, **a))


if __name__ == "__main__":
    unittest.main()
