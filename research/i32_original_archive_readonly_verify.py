#!/usr/bin/env python3
"""I32 original GitHub Actions 72-run archive: read-only, no native AC/optimizer.

Verify original run 39686171613 artifact ZIP, or its two untouched payloads
unpacked by actions/download-artifact@v4. A directory verifies both payload
SHA256 values; only ZIP mode additionally authenticates the transport ZIP.
No PYPOWER, pandapower, scipy, GA, or project research modules are imported.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import zipfile
from pathlib import Path

ORIGINAL_RUN = 39686171613
ORIGINAL_ARTIFACT = 12386702402
ZIP_SHA256 = "c2a84c57571841737c7a9f006091a4a97097fe6843d42265ef3ccbd84937f782"
JSON_SHA256 = "a8e707cc6044390213f8c9112ab59ab47f8a30321b28a669e2624d5c0df4d534"
CSV_SHA256 = "60a58eba49759f116e0f69e8c98887853cb99b112a022663cd051bd5eb1e7533"
JSON_NAME = "ieee14_i32_12seed_6arm_raw_real_AC.json"
CSV_NAME = "ieee14_i32_12seed_6arm_raw_real_AC.csv"
METHODS = ("gadapt_full_true", "gadapt_full_censored", "gadapt_stop_fixed",
           "gadapt_stop_adaptive", "de_full_true", "de_stop_fixed")
SCENARIOS = ("nominal", "odd_bus_plus1pct", "even_bus_plus1pct")
SEEDS = tuple(range(2104, 2116))
PAIRS = (("gadapt_full_true", "gadapt_full_censored"),
         ("gadapt_full_censored", "gadapt_stop_fixed"),
         ("gadapt_stop_fixed", "gadapt_stop_adaptive"),
         ("gadapt_stop_fixed", "de_stop_fixed"),
         ("gadapt_full_true", "de_full_true"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def equal_number(a, b, label):
    require(a is not None and b is not None and
            math.isclose(float(a), float(b), abs_tol=1e-9, rel_tol=1e-12),
            f"{label}: {a} != {b}")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_archive(*, zip_path=None, source_dir=None):
    require((zip_path is None) != (source_dir is None), "Exactly one source required")
    if zip_path is not None:
        raw = Path(zip_path).read_bytes()
        require(_sha(raw) == ZIP_SHA256, "Original artifact ZIP SHA-256 mismatch")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            require(set(archive.namelist()) == {JSON_NAME, CSV_NAME}, "ZIP roster differs")
            return archive.read(JSON_NAME), archive.read(CSV_NAME), True
    root = Path(source_dir)
    require(root.is_dir() and {p.name for p in root.iterdir()} == {JSON_NAME, CSV_NAME},
            "Unpacked original artifact roster differs")
    return (root / JSON_NAME).read_bytes(), (root / CSV_NAME).read_bytes(), False


def original_two_sided_exact(discordant_min, discordant_total):
    if discordant_total == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(discordant_total, j)
                          for j in range(discordant_min + 1)) / (2 ** discordant_total))


def verify_contents(json_raw: bytes, csv_raw: bytes, *, original_zip_verified=False):
    """Trust no count until both original file digests are exact."""
    require(_sha(json_raw) == JSON_SHA256, "Original I32 JSON SHA-256 mismatch")
    require(_sha(csv_raw) == CSV_SHA256, "Original I32 CSV SHA-256 mismatch")
    data = json.loads(json_raw)
    metadata, rows, summaries = data["metadata"], data["runs"], data["summary"]
    require(tuple(metadata["methods"]) == METHODS and
            tuple(metadata["scenarios"]) == SCENARIOS and
            tuple(metadata["seeds"]) == SEEDS, "Frozen I32 roster differs")
    require(metadata["max_native_AC_per_method_seed"] == 180 and
            metadata["max_true_native_AC"] == 12960 and
            metadata["num_native_AC_OPF_calls"] == 0 and
            metadata["nine_decision_variables_not_full_acopf"] is True,
            "Original preregistered budget/scope differs")
    expected = {(method, seed) for method in METHODS for seed in SEEDS}
    require(len(rows) == 72 and {(r["method"], r["seed"]) for r in rows} == expected,
            "Original 72 method/seed records incomplete/duplicated")
    require(set(summaries) == set(METHODS), "Method summary set mismatch")
    require(sum(r["actual_native_AC_calls"] for r in rows) ==
            metadata["actual_native_AC"] == 12913, "Original 12,913 calls mismatch")
    verified_witnesses = 0
    for row in rows:
        method, seed = row["method"], row["seed"]
        label = f"{method}/{seed}"
        require(row["source_scenarios"] == list(SCENARIOS) and
                row["max_native_AC_budget"] == 180, "Scenario/budget: " + label)
        counts = row["actual_AC_per_scenario"]
        keys = ("actually_observed_source_feasible_per_scenario",
                "actually_observed_physical_source_failures_per_scenario",
                "actually_observed_numerical_unknown_per_scenario")
        require(len(counts) == 3 and all(type(n) is int and n >= 0 for n in counts),
                "Malformed AC counts: " + label)
        for key in keys:
            require(len(row[key]) == 3 and all(type(n) is int and n >= 0 for n in row[key]),
                    "Malformed observed scenario: " + label + "/" + key)
        for i in range(3):
            require(counts[i] == sum(row[key][i] for key in keys),
                    "Observed AC partition mismatch: " + label)
        paid = sum(counts)
        require(paid == row["actual_native_AC_calls"] and paid <= 180,
                "Historical physical budget mismatch: " + label)
        complete = row["completely_evaluated_candidates"]
        feasible = row["verified_all_scenario_feasible_candidates"]
        stop1, stop2 = (row["candidates_stopped_after_1_real_AC"],
                        row["candidates_stopped_after_2_real_AC"])
        require(all(type(n) is int and n >= 0 for n in
                    (complete, feasible, stop1, stop2)) and feasible <= complete,
                "Complete/feasible/early-stop mismatch: " + label)
        failed_third = row["early_screened_physically_infeasible_candidates"] - stop1 - stop2
        require(failed_third >= 0 and
                3 * (complete + failed_third) + stop1 + 2 * stop2 == paid,
                "Third-scenario failure / paid AC mismatch: " + label)
        require(2 * stop1 + stop2 == row["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] and
                row["unobserved_missing_results_are_never_source_feasible"] is True,
                "Unobserved scenario counted as feasible: " + label)
        if method.endswith("full_true") or method.endswith("full_censored"):
            require(stop1 == stop2 == 0 and complete * 3 == paid and len(set(counts)) == 1,
                    "Original fully paid AC method skipped a scenario: " + label)
        value = row["best_verified_robust_mean_economic_cost_or_null"]
        require((value is not None) == (feasible > 0),
                "Best archived feasible cost mismatch: " + label)
        if feasible:
            witness = row["best_verified_robust_source_physics_or_null"]
            x = row["best_verified_robust_vector_or_null"]
            require(isinstance(witness, dict) and len(x) == 9,
                    "Stored 9D witness schema mismatch: " + label)
            for key in ("per_scenario_max_KCL_mva", "per_scenario_original_cost",
                        "per_scenario_real_source_normalized_violation"):
                require(len(witness[key]) == 3 and all(isinstance(v, (int, float)) and
                        math.isfinite(v) for v in witness[key]),
                        "Stored witness values malformed: " + label)
            require(all(v == 0 for v in witness["per_scenario_real_source_normalized_violation"]),
                    "Archived witness declares nonzero violation: " + label)
            equal_number(statistics.mean(witness["per_scenario_original_cost"]), value,
                         "Archived witness recorded mean: " + label)
            verified_witnesses += 1
    table = list(csv.DictReader(io.StringIO(csv_raw.decode("utf-8"))))
    require(len(table) == 72, "CSV row count mismatch")
    for i, (row, flat) in enumerate(zip(rows, table)):
        for key, value in row.items():
            want = (json.dumps(value, sort_keys=True) if isinstance(value, (dict, list))
                    else "" if value is None else str(value))
            require(flat[key] == want, f"CSV / JSON disagreement: {i}/{key}")
        require(all(not value for key, value in flat.items() if key not in row),
                f"Unexpected CSV field in row {i}")
    summary_keys = {
        "runs": lambda z, f: len(z),
        "successful_seeds": lambda z, f: len(f),
        "actual_true_native_AC": lambda z, f: sum(r["actual_native_AC_calls"] for r in z),
        "complete_all_three_candidates": lambda z, f: sum(r["completely_evaluated_candidates"] for r in z),
        "verified_robust_source_feasible_candidates": lambda z, f: sum(r["verified_all_scenario_feasible_candidates"] for r in z),
        "proven_physical_early_screens": lambda z, f: sum(r["early_screened_physically_infeasible_candidates"] for r in z),
        "numerically_unknown_candidates": lambda z, f: sum(r["numerically_unknown_candidates"] for r in z),
        "objective_requests": lambda z, f: sum(r["objective_requests"] for r in z),
        "skipped_unobserved_scenarios": lambda z, f: sum(r["unobserved_scenarios_NOT_counted_as_feasible_or_infeasible"] for r in z),
        "best_truly_robust_source_mean_economic_cost_or_null": lambda z, f: min(f) if f else None,
        "median_truly_verified_cost_conditional_on_seed_success_or_null": lambda z, f: statistics.median(f) if f else None,
    }
    for method in METHODS:
        subset = [r for r in rows if r["method"] == method]
        values = [r["best_verified_robust_mean_economic_cost_or_null"] for r in subset
                  if r["best_verified_robust_mean_economic_cost_or_null"] is not None]
        for key, calculate in summary_keys.items():
            got, archived = calculate(subset, values), summaries[method][key]
            if got is None or archived is None:
                require(got is archived, f"Null summary mismatch: {method}/{key}")
            else:
                equal_number(got, archived, f"Original method summary {method}/{key}")
    require(len(data["paired_seed_contrasts"]) == len(PAIRS), "Paired contrast roster mismatch")
    paired = []
    for archived, (left, right) in zip(data["paired_seed_contrasts"], PAIRS):
        lhs = {r["seed"]: r["verified_all_scenario_feasible_candidates"] > 0
               for r in rows if r["method"] == left}
        rhs = {r["seed"]: r["verified_all_scenario_feasible_candidates"] > 0
               for r in rows if r["method"] == right}
        aa = sum(lhs[s] and rhs[s] for s in SEEDS)
        ab = sum(lhs[s] and not rhs[s] for s in SEEDS)
        ba = sum(not lhs[s] and rhs[s] for s in SEEDS)
        bb = sum(not lhs[s] and not rhs[s] for s in SEEDS)
        expected_pair = dict(first=left, second=right, both=aa, first_only=ab,
                             second_only=ba, neither=bb,
                             exact_two_sided_discordant_binomial_p_UNADJUSTED=
                             original_two_sided_exact(min(ab, ba), ab + ba))
        for key, value in expected_pair.items():
            if isinstance(value, (float, int)):
                equal_number(value, archived[key], f"Paired {left}/{right}/{key}")
            else:
                require(value == archived[key], f"Paired {left}/{right}/{key} differs")
        paired.append(expected_pair)
    require(verified_witnesses == 51, "Archived witness roster differs")
    return {
        "schema": "I65_I32_SOURCE_ONLY_ORIGINAL_ARTIFACT_REPLAY_V2",
        "status": "PASS_ORIGINAL_ARCHIVED_ACCOUNTING",
        "original_workflow_run": ORIGINAL_RUN,
        "original_artifact_id": ORIGINAL_ARTIFACT,
        "expected_original_artifact_zip_sha256": ZIP_SHA256,
        "original_zip_bytes_sha256_checked_in_this_invocation": bool(original_zip_verified),
        "original_json_sha256_verified": JSON_SHA256,
        "original_csv_sha256_verified": CSV_SHA256,
        "original_method_seed_records": 72,
        "original_source_scenarios_observed": 216,
        "archived_9d_witness_schema_cost_checks": verified_witnesses,
        "original_method_summaries_rechecked": len(METHODS),
        "original_paired_contrasts_rechecked": len(PAIRS),
        "original_native_ac_calls_not_new": 12913,
        "registered_original_native_ac_max": 12960,
        "paired_contrasts": paired,
        "new_native_ac_calls": 0,
        "new_optimizer_runs": 0,
        "caution": "Original archived JSON/CSV accounting only; not independent physical PF/OPF re-evaluation",
        "research_status": "DRAFT / NO-FREEZE / NOT_ESTABLISHED",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--zip", type=Path)
    g.add_argument("--source-dir", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    j, c, full_zip_verified = read_archive(zip_path=a.zip, source_dir=a.source_dir)
    result = verify_contents(j, c, original_zip_verified=full_zip_verified)
    report = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if a.output:
        a.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
