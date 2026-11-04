"""Adversarial tests for SHA-pinned I55 181-witness evidence chain.

These are synthetic fixtures, NOT additional NPZ source replays.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import i55_181_npz_evidence_reconcile as r
from test_i55_181_npz_evidence_reconcile import fixture


def make_chain(root: Path) -> tuple[dict, dict, str]:
    _, earlier, batches, _, libs = fixture()
    witnesses = []
    source_paths = []
    total_calls = total_bytes = 0
    for ordinal, batch in enumerate(batches, 1):
        data = (json.dumps(batch, indent=2, sort_keys=True) + "\n").encode("utf-8")
        (root / r.BATCH_PATTERN.format(ordinal)).write_bytes(data)
        records = batch["results"]
        calls = sum(x["objective_calls_rechecked"] for x in records)
        size = sum(x["source_binary_size"] for x in records)
        witnesses.append({
            "batch_id": ordinal,
            "library": batch["batch_library"],
            "source_npz": len(records),
            "objective_calls": calls,
            "compressed_source_bytes": size,
            "path": str(r.ROOT / r.BATCH_PATTERN.format(ordinal)),
            "git_blob_sha1": r.git_blob(data),
        })
        source_paths.extend(x["path"] for x in records)
        total_calls += calls
        total_bytes += size
    before = earlier["prior_five_source_paths"] + earlier["new_fifty_source_paths"]
    index = {
        "schema": "I65_I55_NEXT_126_SOURCE_REPLAY_INDEX_V1",
        "original_source_commit": r.SOURCE_SHA,
        "frozen_620_manifest_blob": r.MANIFEST_SHA,
        "prior_55_index_blob": r.INDEX_SHA,
        "replay_engine_blob": r.ENGINE_SHA,
        "per_library_witnesses": witnesses,
        "new_replay_witnesses": len(source_paths),
        "new_original_eligible_libraries": len(libs),
        "old_55_source_paths": before,
        "prior_original_raw_replay_witnesses": len(before),
        "prior_objective_evaluations": earlier["cumulative_original_evaluations_recomputed"],
        "new_npz_source_paths": source_paths,
        "new_original_evaluations": total_calls,
        "new_compressed_binary_bytes": total_bytes,
        "total_raw_replay_witnesses": len(before) + len(source_paths),
        "total_original_evaluations_recomputed": earlier["cumulative_original_evaluations_recomputed"] + total_calls,
        "original_total_valid_npz": len(before) + len(source_paths),
        "remaining_raw_npz_unreplayed": 0,
        "number_new_failed_raw_replays": 0,
    }
    index_sha = save_index(root, index)
    return earlier, index, index_sha


def save_index(root: Path, index: dict) -> str:
    raw = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (root / r.NEXT_INDEX).write_bytes(raw)
    return r.git_blob(raw)


def verify(root: Path, earlier: dict, sha: str):
    return r.load_pinned_batches(
        root, earlier, index_sha=sha,
        expected_libraries=frozenset(("baybe", "evox")), per_library=3,
    )


class PinnedBatchChainTests(unittest.TestCase):
    def test_intact_pinned_index_and_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior, index, sha = make_chain(root)
            got, batches = verify(root, prior, sha)
            self.assertEqual(got["new_replay_witnesses"], 6)
            self.assertEqual(len(batches), 2)

    def test_modified_unchecked_report_field_fails_blob_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior, _, sha = make_chain(root)
            path = root / r.BATCH_PATTERN.format(1)
            batch = json.loads(path.read_text())
            batch["results"][0]["objective_max_absolute_error"] = 1e100
            path.write_text(json.dumps(batch), encoding="utf-8")
            with self.assertRaisesRegex(r.ReconciliationError, "Frozen Git JSON identity changed"):
                verify(root, prior, sha)

    def test_mutated_index_without_repinning_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior, index, sha = make_chain(root)
            index["new_original_evaluations"] += 1
            save_index(root, index)
            with self.assertRaisesRegex(r.ReconciliationError, "Frozen Git JSON identity changed"):
                verify(root, prior, sha)

    def test_reauthenticated_index_with_wrong_roster_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior, index, _ = make_chain(root)
            index["new_npz_source_paths"].pop()
            sha = save_index(root, index)
            with self.assertRaisesRegex(r.ReconciliationError, "Indexed NPZ path roster mismatch"):
                verify(root, prior, sha)

    def test_reauthenticated_index_with_inflated_total_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior, index, _ = make_chain(root)
            index["new_original_evaluations"] += 100
            sha = save_index(root, index)
            with self.assertRaisesRegex(r.ReconciliationError, "126-source index aggregate"):
                verify(root, prior, sha)


if __name__ == "__main__":
    unittest.main()
