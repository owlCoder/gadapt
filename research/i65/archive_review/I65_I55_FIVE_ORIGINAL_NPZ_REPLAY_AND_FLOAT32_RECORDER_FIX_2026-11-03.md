# I65: original I55 NPZ replay and frozen float32 recorder correction — 2026-11-03

**Status:** PARTIAL ORIGINAL-BYTE REPLAY **5/620**; **615 not replayed**. This corrects the *post hoc verifier*, not any frozen experimental source, result, hypothesis or optimizer implementation. No fresh optimization, PF/OPF or held-out COCO run. Originality NOT_ESTABLISHED, NO-FREEZE, human M6/C1 decision pending.

## Source-level defect in the post hoc oracle

The prior `i55_npz_cross_archive_verifier.py` objective oracle recomputed `f(x)` in float64 and compared against the archived recorded value with `rtol=atol=1e-10`. That is **not** the scoring rule for all frozen I55 libraries. In the unmodified historical [I50 adapter](../../legacy/flat/iteration50_integrity_audit.py) (Git blob `17ed62641f2066cdbc8b19b817b9114f144e784c`), `TORCH=("evox", "evotorch")` and `Recorder32.__call__` writes `float(np.float32(self.problem(x)))` to the record. The original I49 `Problem.base` definitions (Git blob `dc14a1c95a1f3bb1ba083f705a75503321bbeafd`) operate on float64 coordinates. The original I55 runner calls I50 `execute`, thereby retaining the special recorded-score precision.

Consequently a float64-only oracle **falsely rejects authentic original Torch-adapter traces**. Merely increasing tolerances would be less discriminating and would conceal the mechanism. The repaired oracle preserves the original math and exact legacy output path: evaluate `f(x)` in float64; *only* for EvoX/EvoTorch, cast the score to float32 and back to float64; then apply the existing tight tolerance and strict finite-value requirements. Other 19 libraries retain float64 expectations. In particular **do not cast coordinate vectors to float32 here**: the original Recorder32 converted them to float64 before evaluating and archiving them.

## Independently read original compressed NPZ files

Five **distinct** original `.npz` byte streams were fetched through the connected GitHub repository, independently DEFLATE-decoded and parsed as `.npy` arrays, with a separately implemented SHA256 sequence function (validated on the standard `abc` vector). For each, the recomputed complete ordered call SHA256, archived call count and all applicable C/R/D2 flags match the original source; recomputation of all captured `f(x)` succeeds using the historical recorded precision.

| Source library / function / d / seed | Calls re-evaluated | Recorded score | Prior 64-bit-only oracle false rejects | After exact historical cast | Call SHA256 / flags |
|---|---:|---|---:|---:|---|
| baybe / plateau / 2 / 6003 | 200 | float64 | 0 | 0 | MATCH / MATCH |
| evox / sphere / 2 / 6000 | 200 | float32 | 200 | 0 | MATCH / MATCH |
| evox / rastrigin / 2 / 6000 | 200 | float32 | 192 | 0 | MATCH / MATCH |
| evotorch / sphere / 2 / 6001 | 198 | float32 | 154 | 0 | MATCH / MATCH |
| evotorch / rastrigin / 2 / 6002 | 198 | float32 | 198 | 0 | MATCH / MATCH |

**Totals: 5/620 original traces, 996 original objective calls, 796 torch-recorded values exactly aligned to original scoring precision; 744 false rejections would have been raised by the old post hoc oracle.** The original I55 C3 flags in the two sampled EvoTorch cells (4 and 7) remain **unchanged** and are not newly attributed to a package bug.

The frozen source SHA256 bytes for each cell and the Git blob identifiers are retained in [structured original-byte witness](I65_I55_FIVE_ORIGINAL_NPZ_REPLAY_AND_FLOAT32_RECORDER_FIX_2026-11-03.json). This independent per-cell replay does NOT substitute for verifying all 620 NPZ blobs in the full-clone chain and cannot reconstruct A′/B raw traces, which were archived only as digest comparisons.

## Implementation and regression proof

- [Corrected I55 cross-archive verifier](i55_npz_cross_archive_verifier.py): `FROZEN_FLOAT32_LIBRARIES={'evox','evotorch'}`, original `Recorder32` score cast and explicit oracle precision in each result. Unrecognized explicit library IDs fail closed; NaN/Infinity still fail closed before and after quantization.
- [Extended objective-oracle tests](test_i55_frozen_objective_oracle.py): 6 new focused cases covering Torch vs non-Torch sphere and Rastrigin, integer plateau, overflow after float32 quantization, unknown library and full NPZ digest/classifier replay. 
- **56/56** locally executed I55 verifier, source-manifest and attestation tests pass (`python -m unittest discover -p 'test_i55_*.py'` with all original fixtures in one test directory). These are regression tests; the separate **five** original raw NPZ replays above are empirical source checks, not part of the synthetic test count.

## Decisions and limitations

The registered H55a–c SUPPORTED / H55d NOT SUPPORTED verdicts remain unchanged. The I55 whole-archive `full_attestation_pass=true` is **not yet established**, since 615 original raw NPZ traces remain unexamined in this audit. Historical C1 nonspecificity, I52 class-transfer limits and all I64-R off-Git/COCO/mentor gates remain open. **No re-freeze, original data modification, new preregistration, scientific novelty proof or human approval** is implied.
