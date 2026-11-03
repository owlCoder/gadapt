"""Tests for the independent I49/I50 frozen objective-value oracle, no optimization."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np

from i55_npz_cross_archive_verifier import (
    check_frozen_objective_values, classify_arrays, evaluate_frozen_objective,
    replay_npz, sequence_hash,
)


class FrozenObjectiveOracleTests(unittest.TestCase):
    def test_sphere_2d_exact(self):
        x = np.array([[-1.3,-1.3],[-5.0,5.0],[0.,0.]], dtype=np.float64)
        out = evaluate_frozen_objective(x,"sphere")
        np.testing.assert_allclose(out, np.sum((x - (-5.+.37*10.))**2,axis=1))
        self.assertAlmostEqual(out[0],0.0,places=26)

    def test_rastrigin_origin_and_native_bounds(self):
        x = np.array([[0.,0.],[1.,-1.],[5.,5.]],dtype=np.float64)
        np.testing.assert_allclose(evaluate_frozen_objective(x,"rastrigin"),[0.,2.,50.],rtol=0,atol=1e-13)

    def test_plateau_negative_floor_and_beyond_bounds(self):
        x=np.array([[-.001,-1.000001],[2.99999,-5.3],[5.,5.]],dtype=np.float64)
        np.testing.assert_array_equal(evaluate_frozen_objective(x,"plateau"),[-3.,-4.,10.])

    def test_dimension_10(self):
        x=np.full((3,10),-1.3,dtype=np.float64)
        self.assertEqual(evaluate_frozen_objective(x,"sphere").shape,(3,))
        self.assertLess(float(np.max(evaluate_frozen_objective(x,"sphere"))),1e-25)

    def test_unknown_function_and_invalid_dimensions_fail(self):
        x=np.zeros((2,2),dtype=np.float64)
        with self.assertRaisesRegex(ValueError,"Unknown"):
            evaluate_frozen_objective(x,"rotm")
        with self.assertRaisesRegex(ValueError,"dimension"):
            evaluate_frozen_objective(np.zeros((2,5),dtype=np.float64),"sphere")
        with self.assertRaisesRegex(ValueError,"float64"):
            evaluate_frozen_objective(x.astype(np.float32),"sphere")

    def test_objective_mismatch_is_rejected(self):
        x=np.array([[0.,0.],[1.,-1.]],dtype=np.float64)
        f=evaluate_frozen_objective(x,"rastrigin")
        check_frozen_objective_values(x,f,"rastrigin")
        f[1]+=0.1
        with self.assertRaisesRegex(ValueError,"at call 1"):
            check_frozen_objective_values(x,f,"rastrigin")

    def test_numerical_tolerance_is_explicit(self):
        x=np.array([[0.,0.],[1.,1.]],dtype=np.float64)
        f=evaluate_frozen_objective(x,"sphere")
        f[0]+=1e-11
        self.assertTrue(check_frozen_objective_values(x,f,"sphere")["all_frozen_objective_values_match"])

    def test_nan_coordinates_and_nan_values_must_not_match_each_other(self):
        # The previous equal_nan=True oracle returned PASS here.
        x = np.array([[np.nan, 0.]], dtype=np.float64)
        f = np.array([np.nan], dtype=np.float64)
        with self.assertRaisesRegex(ValueError, "Non-finite archived objective coordinates"):
            check_frozen_objective_values(x, f, "sphere")

    def test_infinite_archived_value_not_equivalent_to_infinite_oracle(self):
        # A finite but overflowing coordinate creates +inf for sphere.
        x = np.array([[1e308, 0.]], dtype=np.float64)
        f = np.array([np.inf], dtype=np.float64)
        with self.assertRaisesRegex(ValueError, "Non-finite archived objective values"):
            check_frozen_objective_values(x, f, "sphere")

    def test_finite_archive_but_overflowing_independent_evaluation_rejected(self):
        x = np.array([[1e308, 0.]], dtype=np.float64)
        f = np.array([1e308], dtype=np.float64)
        with self.assertRaisesRegex(ValueError, "Non-finite independent objective result"):
            check_frozen_objective_values(x, f, "sphere")

    def test_valid_finite_oracle_reports_explicit_gate(self):
        x = np.array([[0., 0.]], dtype=np.float64)
        f = evaluate_frozen_objective(x, "rastrigin")
        report = check_frozen_objective_values(x, f, "rastrigin")
        self.assertTrue(report["all_coordinates_and_values_finite"])

    def test_full_npz_replay_rejects_self_consistent_nan_trace(self):
        # Both saved SHA256 and detector flags are consistent, but the
        # experimental x,f pair is not a valid finite objective evaluation.
        x = np.array([[np.nan, 0.]], dtype=np.float64)
        f = np.array([np.nan], dtype=np.float64)
        phase = np.array([0], dtype=np.int8)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sphere_2_6000.npz"
            np.savez_compressed(path, x=x, f=f, phase=phase,
                x_star=np.zeros(0), f_star=np.array([np.nan]),
                reported_evals=np.array([-1]), documented_max=np.array([-1]))
            flags = classify_arrays(x, f, phase, np.zeros(0), None, None, None)
            cell = {"function": "sphere", "d": 2, "calls": 1,
                    "hash": sequence_hash(x, f, phase), "flags": flags}
            with self.assertRaisesRegex(ValueError, "Non-finite archived objective coordinates"):
                replay_npz(path, cell)

    def test_full_npz_replay_rejects_self_consistent_infinite_trace(self):
        x = np.array([[1e308, 0.]], dtype=np.float64)
        f = np.array([np.inf], dtype=np.float64)
        phase = np.array([0], dtype=np.int8)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sphere_2_6000.npz"
            np.savez_compressed(path, x=x, f=f, phase=phase,
                x_star=np.zeros(0), f_star=np.array([np.nan]),
                reported_evals=np.array([-1]), documented_max=np.array([-1]))
            flags = classify_arrays(x, f, phase, np.zeros(0), None, None, None)
            cell = {"function": "sphere", "d": 2, "calls": 1,
                    "hash": sequence_hash(x, f, phase), "flags": flags}
            with self.assertRaisesRegex(ValueError, "Non-finite archived objective values"):
                replay_npz(path, cell)

    def test_replay_npz_enforces_oracle_not_just_sha(self):
        x=np.array([[0.,0.],[2.,1.]],dtype=np.float64)
        f=evaluate_frozen_objective(x,"sphere")
        phase=np.array([0,0],dtype=np.int8)
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/"sphere_2_6000.npz"
            np.savez_compressed(file,x=x,f=f,phase=phase,x_star=x[0],
                f_star=np.array([f[0]]),reported_evals=np.array([2]),documented_max=np.array([2]))
            cell={"function":"sphere","d":2,"calls":2,"hash":sequence_hash(x,f,phase),
                  "flags":classify_arrays(x,f,phase,x[0],float(f[0]),2,2)}
            result=replay_npz(file,cell)
            self.assertEqual(result["objective_oracle"]["verified_calls"],2)
            f_bad=f.copy();f_bad[1]+=1.0
            np.savez_compressed(file,x=x,f=f_bad,phase=phase,x_star=x[0],
                f_star=np.array([f[0]]),reported_evals=np.array([2]),documented_max=np.array([2]))
            cell["hash"]=sequence_hash(x,f_bad,phase)
            with self.assertRaisesRegex(ValueError,"Frozen objective value mismatch"):
                replay_npz(file,cell)


    def test_torch_original_sphere_uses_float32_score_not_float64_oracle(self):
        # Frozen I50 Recorder32: f = float(np.float32(problem(x))). Coordinates
        # are still float64, so changing coordinate precision would be wrong.
        x = np.array([[0., 0.], [2.25, -1.5]], dtype=np.float64)
        exact = evaluate_frozen_objective(x, "sphere")
        recorded = exact.astype(np.float32).astype(np.float64)
        self.assertTrue(np.any(np.abs(recorded - exact) > 1e-10))
        for lib in ("evox", "evotorch"):
            with self.subTest(lib=lib):
                witness = check_frozen_objective_values(x, recorded, "sphere", lib)
                self.assertEqual(witness["historical_recorded_precision"], "float32")
                self.assertEqual(witness["verified_calls"], 2)
        with self.assertRaisesRegex(ValueError, "Frozen objective value mismatch"):
            check_frozen_objective_values(x, recorded, "sphere", "baybe")

    def test_torch_rastrigin_float32_and_non_torch_distinguished(self):
        x = np.array([[0.37, -1.217], [0.731, 0.123]], dtype=np.float64)
        exact = evaluate_frozen_objective(x, "rastrigin")
        recorded = exact.astype(np.float32).astype(np.float64)
        self.assertTrue(np.any(np.abs(recorded - exact) > 1e-10))
        for lib in ("evox", "evotorch"):
            self.assertTrue(check_frozen_objective_values(x, recorded, "rastrigin", lib)
                            ["all_frozen_objective_values_match"])
            with self.assertRaisesRegex(ValueError, "Frozen objective value mismatch"):
                check_frozen_objective_values(x, exact, "rastrigin", lib)
        self.assertEqual(check_frozen_objective_values(x, exact, "rastrigin", "smac")
                         ["historical_recorded_precision"], "float64")

    def test_torch_plateau_is_integer_exact_under_both_recorders(self):
        x = np.array([[0.125, -1.1], [-3.2, 4.9]], dtype=np.float64)
        f = evaluate_frozen_objective(x, "plateau")
        for lib in ("evox", "evotorch", "baybe"):
            self.assertEqual(check_frozen_objective_values(x, f, "plateau", lib)
                             ["verified_calls"], 2)

    def test_nonfinite_float32_cast_is_rejected(self):
        x = np.array([[1e35, 0.]], dtype=np.float64)
        # The true float64 sphere objective is finite (~1e70), but float32
        # quantization would overflow: must not silently accept inf/inf.
        true_float64 = evaluate_frozen_objective(x, "sphere")
        self.assertTrue(np.all(np.isfinite(true_float64)))
        with self.assertRaisesRegex(ValueError, "Non-finite independent objective result"):
            check_frozen_objective_values(x, true_float64, "sphere", "evox")

    def test_unknown_archived_library_fails_closed(self):
        x = np.array([[0., 0.]], dtype=np.float64)
        f = evaluate_frozen_objective(x, "sphere")
        with self.assertRaisesRegex(ValueError, "Unknown archived I55 library"):
            check_frozen_objective_values(x, f, "sphere", "unregistered_package")

    def test_original_torch_scoring_path_full_npz_replay(self):
        x = np.array([[0., 0.], [1.25, -0.75], [2., 3.]], dtype=np.float64)
        f64 = evaluate_frozen_objective(x, "sphere")
        f32 = f64.astype(np.float32).astype(np.float64)
        phase = np.zeros(len(x), dtype=np.int8)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sphere_2_6000.npz"
            np.savez_compressed(path, x=x, f=f32, phase=phase, x_star=x[0],
                                f_star=np.array([f32[0]]),
                                reported_evals=np.array([len(x)]),
                                documented_max=np.array([len(x)]))
            flags = classify_arrays(x, f32, phase, x[0], float(f32[0]), len(x), len(x))
            cell = {"library": "evox", "function": "sphere", "d": 2,
                    "calls": len(x), "hash": sequence_hash(x, f32, phase), "flags": flags}
            report = replay_npz(path, cell)
            self.assertEqual(report["objective_oracle"]["historical_recorded_precision"], "float32")
            self.assertEqual(report["flag_mismatches"], {})
            self.assertEqual(report["objective_oracle"]["verified_calls"], 3)
            cell["library"] = "baybe"
            with self.assertRaisesRegex(ValueError, "Frozen objective value mismatch"):
                replay_npz(path, cell)


if __name__ == "__main__":
    unittest.main()
