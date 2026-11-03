# I65 — I64-R off-Git raw evidence gate and function-family sensitivity audit

**Date:** 2026-11-03. **Status:** DOCUMENTATION + INDEPENDENT READ-ONLY ANALYTICS; NOT a new experiment, preregistration, confirmatory inference, or physical-grid validation. The original R hypothesis decisions and frozen files remain unchanged. PhD novelty `NOT_ESTABLISHED`; manuscript `DRAFT`; `NO-FREEZE`; held-out COCO `NOT_RUN`.

## 1. A newly explicit, material reproducibility limitation

The original I64-R procedure in [`research/i64/r_study.py`](../../i64/r_study.py) computes per-seed ECDF A from frozen E `shift`/`rot` events **plus original R `rotm` events**, then runs a 20,000-replicate shared-index, four-contrast max-studentized bootstrap, seed 70. Its per-cell means and standard errors **cannot** determine its exact sampling distribution without individual run data.

The exact current `owlCoder/gadapt/main` Git tree was independently listed (4,575 entries; not truncated): `research/results/iteration64_r/` has only `analysis.json.gz` (Git blob `59025d6cc052baef76b14e5496962704bdb7604a`) and `check_repro.json.gz` (Git blob `11ca5fdfabfe6ce20cb54752a2a41fe8e2deee3d`). The [original results commit `93a3ff7d36187532b68bb9eb7de72e7905bfedb3`](https://github.com/owlCoder/gadapt/commit/93a3ff7d36187532b68bb9eb7de72e7905bfedb3) added those two files, not `run.json.gz` or any `run_part_*.json.gz`. Git commit-history queries for the two expected raw paths returned no commits in current history. This is an observed **absence from Git**, not evidence of fabricated or lost experimental measurements.

**The historical progress record explicitly documents the reason**: an I64-R `run.json.gz` of approximately 8 MB, containing **4,200** original R runs, was kept **outside Git**, with a shortened SHA-256 `f23046f6…3618`. Its original copy may remain on the experimental machine at `research/results/iteration64_r/run.json.gz` in the local project; this session did not have access to that machine. The record also references frozen commit `b38c6fd...` and independent Codex-100 reproduction brief [`research/codex/100_r_reproduction_brief.md`](../../codex/100_r_reproduction_brief.md). A partial hash marker is **not full, independent provenance authentication**.

**Distinguish the evidence levels:** I64-R signed estimates and the published 95% simultaneous seed-only intervals were read and checked algebraically, and exact 21-pair means were reweighted independently. However, the **original 20,000-draw seed-level R bootstrap has not been independently replayed**, unlike I64-I2, where all 13 original numerical inferential quantities were exactly reproduced from 720 archived outcomes. Do not claim otherwise.

## 2. New exploratory family-level stress test using the 21 archived R pairs

The original analysis used nine fixed benchmark-function families with weight **1/9 per family**. Three functions are only two-dimensional; six have three dimensions, giving 21 pairs. The original registered contrast `c4 = [A_G(shift) - A_G(rotm)] - [A_IPOP(shift) - A_IPOP(rotm)]` estimates **0.070791779835**, with original seed-only simultaneous interval **[0.059811869726, 0.081771689945]**; H64r3 is **SUPPORTED for that fixed experimental design**.

New calculations in [`i64_r_family_resampling_audit.py`](i64_r_family_resampling_audit.py) use the already archived 21 individual `per_pair` means. The local execution used the derivative `I65_I64_R_I2_INFLUENCE_LEDGER_2026-11-03.json` snapshot with **c1/c2/c3 rounded to nine decimals** (source-anchored to the original R gzip blob); the tool also supports exact full-precision raw `analysis.json.gz` in a full clone, and refuses a blob mismatch. Difference between the nine-decimal snapshot's recomputed `c4 = 0.070791780074` and the exact archived point is less than `2.4e-10`.

| Function family | Family mean `c4` (post hoc descriptive) |
|---|---:|
| sphere | -0.0000733 |
| rosenbrock | -0.0205305 |
| rastrigin | +0.3101973 |
| ackley | +0.0548239 |
| griewank | +0.0244158 |
| styblinski_tang | +0.1911028 |
| beale | +0.0749194 |
| himmelblau | +0.0070008 |
| booth | -0.0047303 |

- **Leave Rastrigin out:** reweighted point `c4 ≈ 0.0408661`, below the original positive decision threshold 0.05 **as a point estimate**. The earlier source-anchored review documented this; we now extend the stress test.
- **Leave Rastrigin and Styblinski–Tang out:** point `c4 ≈ 0.0194037`.
- **Leave any two entire families out:** **8/36** combinations produce a point estimate below 0.05; the selection was based on observed effects and **is not** a family-wise statistical test.
- **Illustrative family resampling:** 100,000 draws of 9 families with replacement using `default_rng(7001)` over the nine archived family means. The **2.5th and 97.5th percentiles** of the point-estimate resampling distribution are approximately **[0.0114990, 0.1455463]**. **70.003%** of these artificial draws yield `c4>0.05`.

**Crucial limitation:** These nine families were **purposively selected and are not an IID random sample from a defined population of objective functions**. The percentile envelope is strictly an **illustrative heterogeneity diagnostic**, **NOT** a confidence interval, a bootstrap replacement for the original registered seed-only procedure, or the probability that H64r3 is true. Fixed Haar-orthogonal matrices may include reflections; the exercise does not identify a GAdapt internal mechanism.

## 3. Non-mutating original-run recovery gate

A new [`i64_r_off_git_raw_recovery_gate.py`](i64_r_off_git_raw_recovery_gate.py) accepts an **existing** original `run.json.gz` from a local experimental checkout; it never generates or repairs one. It verifies the abbreviated historical SHA marker (weak triage only), optionally requires a **separately trusted complete 64-character SHA-256**, checks all **4,200** R task/seed/configuration records and ordered best-so-far events under the 12,000-call budget, compares the `e_inputs` hash mapping and build manifest with the two original pinned Git blobs, and checks the presence of the 42 required archived E `run_part` files and normalizers. It exits nonzero if the file is missing; even with a valid structure it does **not** claim to have rerun the R inferential bootstrap. The exact original archive must be recovered first.

From a complete clone, only after locating the original off-Git file:

```sh
python research/i65/archive_review/i64_r_off_git_raw_recovery_gate.py \
  --repo-root . \
  --raw-run research/results/iteration64_r/run.json.gz \
  --output /tmp/i64_r_recovery_gate.json
```

A complete historical SHA-256 obtained from a **trusted independent original record**, if available, should be supplied with `--expected-full-sha256`; merely hashing the recovered copy afresh does not independently authenticate the original. The script does not modify the copy or write anything inside `research/results/`. If the file is missing, the report's correct status is **R RAW RUN NOT PRESENT IN GIT; ORIGINAL MAY EXIST OFF-GIT; EXACT R BOOTSTRAP NOT_REPLAYED**.

## 4. Doctoral interpretation and GO/NO-GO

**Surviving claim:** On 21 fixed pairs and two fixed optimizers, the registered R source reported stronger orthogonal sensitivity for GAdapt-M, with a positive seed-only simultaneous c4 interval. The independently recomputed means support the original point arithmetic. **Limit:** the result is notably concentrated in Rastrigin and Styblinski–Tang; the available Git archive alone does not support independent individual-R-run bootstrap reproduction. The additional sensitivity does not retroactively invalidate the registered test or imply any universal generalization.

**Research implication:** This is a concrete trace-archive completeness, estimand, and external-validity issue for the evaluation-integrity paper and empirical GAdapt chapter. The proposed original scientific contribution still requires independent novelty review, detector-specificity falsification and a dated supervisor decision M6/C1. **No novel optimizer or published theorem is claimed.** Do not launch a new R run merely to fill an archive hole; recover the exact original off-Git source or report the absence honestly.

**Software checks:** 21 new read-only tests passed for the family audit and recovery gate. Combined with the preceding offline archive tests, **108/108** passed in the local test snapshot. This validates the tools on synthetic and derived data, **not** a full R raw replay or a scientific freeze.
