"""Research-only, fail-closed data-lineage check for historical I56/I58 ORPD.

Records deterministic fingerprints of raw public benchmark case, load
scaling, continuous-OPF PG-only handoff and fixed grid control changes.
No PYPOWER imports here, and no license-restricted case data are copied
into the repository. This checks *software lineage*, not independent
physical measurement or mathematical model accuracy.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np


class LineageViolation(ValueError):
    pass


ARRAYS = ("bus", "gen", "branch", "gencost")
STAGES = ("raw", "scaled", "post_opf", "controlled")


def numeric_fingerprint(case):
    """SHA-256 exact numeric bytes, shape, key names, and model baseMVA.

    Canonical IEEE 754 little-endian binary64, C order, sorted keys.
    Non-finite data and missing arrays fail closed.
    """
    if not isinstance(case, dict) or not all(k in case for k in ("baseMVA", "bus", "gen", "branch")):
        raise LineageViolation("missing case arrays")
    h = hashlib.sha256()
    for key in sorted(("baseMVA",) + tuple(k for k in ARRAYS if k in case)):
        a = np.asarray(case[key], dtype=np.float64)
        if not np.isfinite(a).all() or (key != "baseMVA" and a.ndim != 2):
            raise LineageViolation("invalid or nonfinite numeric source")
        if key == "baseMVA" and (a.ndim != 0 or float(a) <= 0):
            raise LineageViolation("invalid base MVA")
        b = np.ascontiguousarray(a.astype("<f8", copy=False))
        h.update(json.dumps({"key": key, "shape": list(b.shape)},
                            sort_keys=True, separators=(",", ":")).encode("utf-8"))
        h.update(b.tobytes(order="C"))
    return h.hexdigest()


def _arr(case, name):
    try:
        a = np.asarray(case[name], dtype=float)
    except (KeyError, TypeError, ValueError) as e:
        raise LineageViolation("invalid case component: " + name) from e
    if a.ndim != 2 or not np.isfinite(a).all():
        raise LineageViolation("invalid matrix: " + name)
    return a


def _assert_same(a, b, field):
    if a.shape != b.shape or not np.array_equal(a, b):
        raise LineageViolation("unapproved change: " + field)


def audit_data_lineage(raw, scaled, post_opf, controlled, *,
                       load_factor, spread, seed, gen_rows, tap_rows,
                       shunt_rows, control_values):
    """Check exact allowed cell-level changes without executing solvers.

    raw: direct api.case30() original; scaled: before OPF; post_opf:
    preserved I56 base after OPF PG handoff; controlled: unsolved candidate.
    """
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise LineageViolation("invalid deterministic scenario seed")
    if not np.isfinite(load_factor) or load_factor <= 0 or not np.isfinite(spread) or not 0 <= spread <= 1:
        raise LineageViolation("invalid load scaling")
    for i, case in enumerate((raw, scaled, post_opf, controlled)):
        numeric_fingerprint(case)
        if set(case) != set(raw):
            raise LineageViolation("case fields changed at stage " + STAGES[i])
        if case.get("version") != raw.get("version"):
            raise LineageViolation("case format version altered")
    names = [k for k in ARRAYS if k in raw]
    for name in names:
        a = _arr(raw, name)
        if any(_arr(c, name).shape != a.shape for c in (scaled, post_opf, controlled)):
            raise LineageViolation("array shape changed: " + name)
    if any(_arr(raw, x).shape[1] < n for x,n in (("bus", 13), ("gen", 10), ("branch", 13))):
        raise LineageViolation("unsupported MATPOWER case column dimensions")
    for stage in (scaled, post_opf, controlled):
        if float(stage["baseMVA"]) != float(raw["baseMVA"]):
            raise LineageViolation("base MVA changed")
        if "gencost" in raw:
            _assert_same(_arr(raw, "gencost"), _arr(stage, "gencost"), "generator cost model")
    rows = len(_arr(raw, "bus"))
    factors = load_factor * (1 + spread * (2 * np.random.RandomState(int(seed)).random_sample(rows) - 1))
    expected = _arr(raw, "bus").copy()
    expected[:, 2] *= factors
    expected[:, 3] *= factors
    _assert_same(expected, _arr(scaled, "bus"), "scaled PD/QD and network fields")
    for name in ("gen", "branch"):
        _assert_same(_arr(raw, name), _arr(scaled, name), "load-stage " + name)
    _assert_same(_arr(scaled, "bus"), _arr(post_opf, "bus"), "OPF-stage bus fields")
    _assert_same(_arr(scaled, "branch"), _arr(post_opf, "branch"), "OPF-stage branch fields")
    original_gen = _arr(scaled, "gen").copy()
    opf_gen = _arr(post_opf, "gen").copy()
    original_gen[:, 1] = opf_gen[:, 1]
    _assert_same(original_gen, opf_gen, "OPF handoff (only PG allowed)")
    gen_rows = [int(x) for x in gen_rows]
    tap_rows = [int(x) for x in tap_rows]
    shunt_rows = [int(x) for x in shunt_rows]
    for name, ids, limit in (("gen",gen_rows,len(opf_gen)),
                             ("tap",tap_rows,len(_arr(scaled,"branch"))),
                             ("shunt",shunt_rows,rows)):
        if len(set(ids)) != len(ids) or any(x < 0 or x >= limit for x in ids):
            raise LineageViolation("invalid/duplicate " + name + " controls")
    x = np.asarray(control_values, dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all() or len(x) != len(gen_rows)+len(tap_rows)+len(shunt_rows):
        raise LineageViolation("invalid control vector length or values")
    b = _arr(post_opf, "bus").copy()
    g = _arr(post_opf, "gen").copy()
    line = _arr(post_opf, "branch").copy()
    ng, nt = len(gen_rows), len(tap_rows)
    g[gen_rows, 5] = x[:ng]
    line[tap_rows, 8] = x[ng:ng+nt]
    b[shunt_rows, 5] = x[ng+nt:]
    _assert_same(b, _arr(controlled,"bus"), "control-stage bus cells")
    _assert_same(g, _arr(controlled,"gen"), "control-stage gen cells")
    _assert_same(line, _arr(controlled,"branch"), "control-stage branch cells")
    return {
        "schema": "GADAPT_I65_ORPD_INPUT_LINEAGE_V1",
        "classification": "PUBLIC_MODIFIED_BENCHMARK_NOT_INDEPENDENT_GRID_MEASUREMENT",
        "stages": {n:numeric_fingerprint(c) for n,c in
                   zip(STAGES,(raw,scaled,post_opf,controlled))},
        "factors": {"min":float(min(factors)), "max":float(max(factors)),
                    "sum":float(sum(factors))},
        "number_of_load_buses":rows,
        "control_counts": {"vg":ng,"tap":nt,"shunt":len(shunt_rows)},
        "allowed_mutations": ["PD/QD random scenario scale","OPF PG handoff",
                              "snapped VG/TAP/BS candidate"],
        "not_a_physical_provenance_certificate":True,
    }
