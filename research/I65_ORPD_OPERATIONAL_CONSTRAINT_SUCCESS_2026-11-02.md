# I65 — real four-component ORPD constraint comparison PASS, infeasible midpoint preserved

**Date:** 2026-11-02. **Scope:** one fixed, previously used non-held-out I58 `case30,j=1,R=17` operating point. **Result:** **PASS for exact historical I56 four-component arithmetic equivalence and falsification detection**, NOT a feasible solution, independent PF solver, optimizer success or scientific novelty.
**Source commit:** `a30000d825f8d8bd12ddee6a56057e5adbd10f1e` on `owlCoder/gadapt/main`.
**GitHub CI:** [run #41407293845](https://github.com/owlCoder/gadapt/actions/runs/41407293845), `completed / success`.  
**Artifact:** [i65-orpd-operational-constraints-41407293845](https://github.com/owlCoder/gadapt/actions/runs/41407293845/artifacts/13122959673), exact ZIP SHA-256 `f621a405730a40d5b85d6124c85e860febf77853424e99ec2bb359c511f981da`.  
**Byte-preserved raw run:** [`I65_ORPD_OPERATIONAL_SUCCESS_2026-11-02.json`](I65_ORPD_OPERATIONAL_SUCCESS_2026-11-02.json), Git blob `c28da486647f22b7c42d3d4d8c5bce0419034c94`, SHA-256 `ccd3b2c69314c8353c47d874d04c68fd136f98ba1927796375a07ba910ba6af0`.

## Prespecified comparison: all four match the immutable original

Executed `research/legacy/flat/iteration56_orpd.py` I56 `ORPD.evaluate` once, plus exactly one separate PYPOWER PF for the independent NumPy AC residual and I56-compatible constraint aggregations, on the same fixed midpoint control vector; the source SHA was unchanged. The original source code and our separate implementation agree **exactly** at the recorded double-precision output for every component:

| I56 constraint component | Historical `ORPD.evaluate` | NumPy-only checker | Absolute difference |
|---|---:|---:|---:|
| Voltage (p.u. excursion sum) | 0 | 0 | **0.0** |
| Generator reactive (MVAr/baseMVA) | **0.5991137833375748** | **0.5991137833375748** | **0.0** |
| Reference-generator active (MW/baseMVA) | 0 | 0 | **0.0** |
| Thermal branch (MVA/baseMVA) | 0 | 0 | **0.0** |

The fixed **1e-8** component-absolute-difference threshold was satisfied in every cell. **Both implementations report `feasible=false`.** I56's threshold is `each component <= 1e-6`, and this *one chosen development midpoint* has a large reactive violation; this is an original negative finding to preserve. This is not a best-of-run or optimized candidate, so do not generalize its infeasibility to GAdapt's possible performance.

The separately programmed NumPy AC-equation residual preflight also passed, without relaxation: maximum nodal mismatch `1.5326914409472708e-08 MVA` (preset max `1e-3`), maximum complex branch-flow difference `7.272657421689707e-13 MVA` (preset max `1e-5`). The original and separate PF converged, returning active loss `3.114081587469094 MW` and independent AC-equation loss `3.114081587469144 MW`. This is not an independent *numerical AC power flow* calculation; PYPOWER supplies the solved state in both runs.

The bounded solver-API ledger recorded exactly the precommitted sequence: **1 `runopf` during scenario setup, 1 `runpf` in original I56 evaluation, and 1 `runpf` in independent witness**. Its separately recalculated event SHA-256 was `c3a0d74dc1798b4b913ed958e1fe2307b00daa39a1e635a4d99bcadbf58e3248`.

## Falsification and counterexample

Four in-memory changes to **limit metadata only**, with no additional solver calls, each caused its own penalty component to increase and the test to report `detected=true`:

- Voltage: `0 → 0.050000000000000044`
- Reactive: `0.5991137833375748 → 0.8483733709301324`
- Reference/slack active: `0 → 0.01`
- Thermal: `0 → 0.01`

The original [first real CI attempt #41406369109](https://github.com/owlCoder/gadapt/actions/runs/41406369109) failed only the **reactive limit-only tamper increase** assertion because the naive tamper reduced `QMIN` and accidentally masked pre-existing lower-bound violations. It preserved the **exact** original metric equality but changed `0.59911378 → 0.24925959` under the fake limits. See the [byte-preserved negative JSON](I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_2026-11-02.json) and [complete failure report](I65_ORPD_OPERATIONAL_FIRST_NEGATIVE_REPORT_2026-11-02.md). **Do not rewrite the previous FAIL as PASS.**

The repaired smoke **did not change any scientific data, comparison tolerance, metric formula or historic I56 source**. It chose a fake upper reactive limit that guarantees a new upper violation strictly exceeding the *entire previous aggregate* by 1 MVAr even if the previous lower violation is erased; the same whole-aggregate bound was applied to voltage and reference active tamper. Two new analytic tests reproduce and falsify the original masking issue. The final **17/17** unittest cases pass on Python `3.12.15` with `numpy==1.26.4` and `PYPOWER==5.1.19`.

## Verified raw archive and source provenance

Downloaded the actual GitHub Actions artifact; ZIP digest matched the GitHub-recorded SHA-256 exactly. Recomputed all four `hashes.sha256` entries from the **actual ZIP bytes** (4/4 matched):

| Archived file | SHA-256 |
|---|---|
| `commit.txt` | `1e574e015a601fbc13982377a2fbd513e46806bc4a38860fa71bf908991431ba` |
| `unit.log` | `4eede6b60164dd90bb96fae8e20efff8b25cf9e43c73d8b032de1333bab4746d` |
| `restore.log` | `b30a798b89b330808732f7473c8db60eeba02c2665c0ed53de7ebcf6f7f7278a` |
| `smoke.json` | `ccd3b2c69314c8353c47d874d04c68fd136f98ba1927796375a07ba910ba6af0` |

Independent compact sorted-key JSON serialization matched the internally recorded API ledger SHA-256 `c3a0d74dc1798b4b913ed958e1fe2307b00daa39a1e635a4d99bcadbf58e3248`.

Source Git blobs in the raw JSON matched the exact known hashes: frozen `iteration56_orpd.py` `43f2f279f7e6362250dc9277e58e0d939a98c12f`, frozen `iteration58_validation.py` `9747faea9c31526a163bd8439c74708214c07a3c`, previously verified AC equations checker `8e6bb1b4cf78578c15315be3b4cff127bc2c8036`, and new constraint checker `120244c35c610ac48b515df4ef86791eb6466e3f`. All **341** historical aliases were hash verified and restored before the test.

## Strict decision and next gate

**PASS:** equivalence of *four original I56 aggregate constraints* and deterministic limit-only falsifications on one development PF state, plus separately verified AC equation residual and solver API entry count. This closes a **narrow software and physical-equation-consistency gate only**.

**NO-GO / NOT_ESTABLISHED:** an independently implemented nonlinear numerical AC solver, external model/data validation, broader OPF feasibility constraints beyond the original four, complete accounting of nested PYPOWER internal subsolves, robust/scenario-wide fidelity, stochastic optimization improvements, an approved candidate-C mathematical novelty, full experimental protocol freeze, or held-out COCO confirmation.

**NEXT STEP:** present the exact negative reactive case and budget accounting to the supervisor, settle the scientific meaning of an independent AC oracle (e.g. independently implemented numerical PF/model), obtain M1–M6 novelty/scope decisions, and only then consider protocol freeze or approved new runs. Preserve `novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN`.
