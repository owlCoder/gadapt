# I65 — real I56 operational-constraint audit: first negative and repaired falsifier

**Date:** 2026-11-02. **Status:** **FIRST REAL CI RUN FAILED**, with exact four-component I56 numerical agreement; **infeasible candidate preserved**. The next tightened-falsifier rerun is NOT_RUN at this document's creation. This is a software measurement audit, **not** an optimizer benchmark.

## First full-clone observed run and immutable evidence

- [GitHub Actions run #41406369109](https://github.com/owlCoder/gadapt/actions/runs/41406369109), exact main commit `89411601f813235838356ba0902db9b588690c76`, `completed / failure`, with original full-history checkout and CPython `3.12.15`, NumPy `1.26.4` and PYPOWER `5.1.19`.
- [Raw original artifact](https://github.com/owlCoder/gadapt/actions/runs/41406369109/artifacts/13122989395), ZIP SHA-256 independently verified: `a0f1381c2c38d982ff03a590e388677e392eb3baa5f8522d74ab9c2ed8866291`. Archived a **byte-identical raw failure output** separately: [original `smoke.json`](I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_2026-11-02.json), Git blob `4e48eebf16a8cea681bac45f8a81973916c0bd28`, SHA-256 `cb67dfbb475f64ce98a46cb441dfdf900aa6b2c3c3beccc14a1ab636fe086aff`. The original ZIP contains four files (`commit.txt, restore.log, unit.log, smoke.json`) and does **not** contain `hashes.sha256` because `set -euo pipefail` stopped before the hash step. Do not invent a missing embedded digest ledger.
- SHA-256 of original archived `unit.log` = `757e247a660310913694f0870b40e1ae294f01c4aea9a3f5a789c076dda738c3`. The original 15/15 tests **PASS** in actual CI. All 341 root aliases hash-verified and restored.
- PYPOWER solver API: **1 setup OPF, 1 historical I56 candidate PF, 1 separate diagnostic PF**, exactly predeclared. Historical and diagnostic PF both converged; AC nodal residual `1.5326914409472708e-08 MVA`, branch difference `7.272657421689707e-13 MVA`, passing the *unchanged* fixed `1e-3 / 1e-5 MVA` tolerances. Audited API trace SHA-256 `c3a0d74dc1798b4b913ed958e1fe2307b00daa39a1e635a4d99bcadbf58e3248`.
- **Exact original I56 metric agreement:** `voltage=0`, `reactive=0.5991137833375748`, `slack=0`, `thermal=0` on both implementations; each of the four absolute differences was **0.0**, passing the preregistered **1e-8** component comparison. The candidate `feasible=false` **in BOTH** implementations because the reactive component is far above the I56 `1e-6` threshold. This is an important negative physical-operating-point finding, *not* a GAdapt optimizer outcome; the candidate is a fixed midpoint, not a selected best solution.

## Why the extra tamper assertion failed

The first smoke attempted to add a reactive upper-limit `QG-QMAX` violation to the first online generator while also *lowering* its `QMIN` so the bound interval remained valid. In a case with **pre-existing reactive violations**, reducing `QMIN` can remove the previous lower-limit penalty, giving a **smaller total**. Actual recorded reactive aggregate changed **0.5991137833375748 → 0.24925958759255765**, so the strict `changed > original + 1e-5` falsification rule correctly marked `detected=false` and failed. There is **no evidence of a wrong I56 metric formula**, and no excuse to silently erase or mark this run PASS.

## Narrow bounded correction (no goalposts moved)

Strengthened **only the construction of the fake limit-only example**; precommitted real-case scenario, two PF entries, nodal/flow tolerances, all four metric formulas and `changed > original + 1e-5` rule remain unchanged:

- Choose new upper reactive limit `QMAX' = QG - (old_total_reactive * baseMVA) - 1 MVAr`, and `QMIN' = min(old_QMIN, QMAX' - 1 MVAr)`. Even if the old lower-limit penalty disappears, the *new upper penalty alone* exceeds the **entire previous total** by 1 MVAr. This is guaranteed without assuming the original candidate was feasible.
- Apply the same whole-aggregate dominance idea to voltage `VMAX'` and slack `PMAX'` falsifications, ensuring they increase their totals even when original violations already exist.
- Add two exact analytic regressions: one **reproduces** naive tamper masking, another validates whole-aggregate strengthening. Local suite **17/17 PASS** under Python 3.13.5/NumPy 2.3.5. Code SHA snapshots: original I56 and I58 remain unchanged; strengthened smoke Git blob `658ab39b6ff17f3c13778e86eab822938bed7d6d`; tests blob `57bfc1a38ae7f022477ba44eb728783086fff2d7`; local 17-case test-log SHA-256 `4eede6b60164dd90bb96fae8e20efff8b25cf9e43c73d8b032de1333bab4746d`.

The next one-shot bounded GitHub workflow is scoped to root run `41357664531` attempt **6**, with 8-minute maximum and no push/PR/schedule trigger. A subsequent green test would close the **four-component accounting comparison** only, **not** certify a feasible candidate, a second AC numerical solver, full model independence, I65 method novelty or COCO. The original first-failure run and its raw JSON remain permanently traceable.
