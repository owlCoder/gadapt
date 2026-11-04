"""Eleven archive-only adversarial tests; never invoke an AC solver."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).resolve().with_name("i32_original_archive_readonly_verify.py")
spec = importlib.util.spec_from_file_location("i32_original_archive_readonly_verify", SCRIPT)
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class OriginalI32SourceOnlyRegression(unittest.TestCase):
    def setUp(self):
        directory = os.environ.get("I32_ORIGINAL_ARTIFACT_DIR")
        if not directory:
            self.skipTest("Original Actions artifact is not available in this environment")
        p = Path(directory)
        self.j = (p / replay.JSON_NAME).read_bytes()
        self.c = (p / replay.CSV_NAME).read_bytes()

    def test_sha256_pins_and_complete_original_72(self):
        out = replay.verify_contents(self.j, self.c)
        self.assertEqual(out["original_method_seed_records"], 72)
        self.assertEqual(out["original_native_ac_calls_not_new"], 12913)
        self.assertEqual(out["archived_9d_witness_schema_cost_checks"], 51)
        self.assertEqual(out["original_paired_contrasts_rechecked"], 5)
        self.assertFalse(out["original_zip_bytes_sha256_checked_in_this_invocation"])

    def test_clean_directory_with_exact_original_two_files(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name)
            (p / replay.JSON_NAME).write_bytes(self.j)
            (p / replay.CSV_NAME).write_bytes(self.c)
            a, b, transport = replay.read_archive(source_dir=p)
            self.assertEqual((a, b, transport), (self.j, self.c, False))
            (p / "extra.txt").write_text("disallowed")
            with self.assertRaisesRegex(ValueError, "roster"):
                replay.read_archive(source_dir=p)

    def test_modified_json_sha256_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "JSON SHA-256"):
            replay.verify_contents(self.j + b" ", self.c)

    def test_modified_csv_sha256_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "CSV SHA-256"):
            replay.verify_contents(self.j, self.c + b" ")

    def forged(self, mutate):
        document = json.loads(self.j)
        mutate(document)
        forged = json.dumps(document).encode()
        # Override only JSON pin to exercise deeper fail-closed validation.
        with patch.object(replay, "JSON_SHA256", hashlib.sha256(forged).hexdigest()):
            return replay.verify_contents(forged, self.c)

    def test_duplicate_seed_in_same_method_fails_closed(self):
        def bad(d):
            first = d["runs"][0]
            first["seed"] = next(r["seed"] for r in d["runs"]
                                 if r["method"] == first["method"]
                                 and r["seed"] != first["seed"])
        with self.assertRaisesRegex(ValueError, "72 method/seed|CSV / JSON"):
            self.forged(bad)

    def test_forged_observed_physical_partition_fails_closed(self):
        def bad(d):
            d["runs"][0]["actually_observed_source_feasible_per_scenario"][0] += 1
        with self.assertRaisesRegex(ValueError, "partition"):
            self.forged(bad)

    def test_forged_method_aggregate_fails_closed(self):
        def bad(d):
            d["summary"]["gadapt_stop_fixed"]["actual_true_native_AC"] += 1
        with self.assertRaisesRegex(ValueError, "Original method summary"):
            self.forged(bad)

    def test_forged_paired_exact_pvalue_fails_closed(self):
        def bad(d):
            d["paired_seed_contrasts"][3]["exact_two_sided_discordant_binomial_p_UNADJUSTED"] = 0.01
        with self.assertRaisesRegex(ValueError, "Paired"):
            self.forged(bad)

    def test_corrupt_zip_not_accepted_as_original_artifact(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "mock.zip"
            with zipfile.ZipFile(p, "w") as archive:
                archive.writestr(replay.JSON_NAME, self.j)
                archive.writestr(replay.CSV_NAME, self.c)
            with self.assertRaisesRegex(ValueError, "ZIP SHA-256"):
                replay.read_archive(zip_path=p)


class PureStatisticalAndSafetyTests(unittest.TestCase):
    def test_original_exact_binomial_undisputed(self):
        self.assertEqual(replay.original_two_sided_exact(0, 0), 1.0)
        self.assertEqual(replay.original_two_sided_exact(0, 5), 0.0625)
        self.assertEqual(replay.original_two_sided_exact(1, 3), 1.0)

    def test_import_tree_has_no_solvers_or_optimizers(self):
        tree = ast.parse(SCRIPT.read_text())
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules += [spec.name for spec in node.names]
            if isinstance(node, ast.ImportFrom):
                modules.append(node.module or "")
        self.assertTrue({"argparse", "hashlib", "csv", "zipfile", "json"} <= set(modules))
        self.assertFalse(any(m.split(".")[0] in
                             {"pypower", "pandapower", "gadapt", "scipy", "numpy", "research"}
                             for m in modules))


if __name__ == "__main__":
    unittest.main()
