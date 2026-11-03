# I65 — Fifty independent original I55 NPZ archive replays

**Date:** 2026-11-03. **Evidence status:** 50/50 additional original binary NPZ traces verified; 55/620 cumulative raw traces independently reproduced. **Not** a complete 620-trace attestation, an optimizer re-run, an experiment, an algorithmic novelty claim, or a supervisor-approved FREEZE.

## Question and scope

Can the frozen original A-process I55 traces be read from their original GitHub Git blob objects and independently recomputed without trusting the stored JSON summaries? The review ran **50 distinct, deliberately selected source-archive replay iterations**, rather than new optimizer experiments. It extends the previously independently checked 5 original traces to a nonoverlapping 55.

Original source commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`; pinned 620-entry source-index Git blob `50ca2e96762447070a74309850cb1aa6586d3eb3`. All original successful archives remain frozen. Each of the 50 original NPZ files was fetched with an explicit original commit ref via the connected GitHub API, decoded from Base64, verified byte-for-byte with the manifest and recomputed Git SHA-1 identity, decompressed as ZIP/NumPy NPY with schema guards, and evaluated against the original I49 objective function. For EvoX and EvoTorch, `Recorder32`'s original `float(np.float32(f(x)))` rule was used rather than an unjustified relaxed tolerance. Each saved `x/f/phase` stream was independently SHA-256 hashed using the original Python-float representation convention; all original C1–C5, R1–R3 and D2 classification counts were independently recomputed and compared with the pinned I55 `cells_<lib>.json` source blob.

The pure JavaScript connector replayer is `research/i65/archive_review/i55_original_npz_connector_replay.js` and its offline Python/Node regression suite is `test_i55_original_npz_connector_replay.py`. Neither imports or executes an optimizer. Nine separately stored JSON batch witnesses record exact per-file source Git blobs, saved versus computed SHA-256, cell key, counts, original flag map and oracle check. The independent nine-batch aggregator checked **50 different source paths, 50 successes, zero failures, 21 distinct libraries, no overlap** with the previous five successful replays.

## Verified results

| Check | Fifty new iterations | Cumulative including previous five |
|---|---:|---:|
| Original NPZ binaries numerically replayed | **50/50** | **55/620** |
| Entire call-sequence SHA-256 matches | **50/50** | 55/55 |
| C/R/D2 detector flag-map matches | **50/50** | 55/55 |
| Original objective `f(x)` values rechecked | **23,302** | **24,298** |
| Objective value disagreements | **0** | 0 |
| Original `float32` Recorder32 calls in new sample | **1,196** | 1,992 |
| Calls that the wrong float64-only oracle would reject | **756** | 1,500 |
| Original binary bytes covered in new sample | **857,443** | — |
| Valid NPZ files not yet numerically replayed | — | **565** |

All 21 eligible libraries were represented: one *sphere* d=2 and one *plateau* d=10 trace per library, plus eight additional *Rastrigin* d=2 traces. The resulting 50 comprise 21 sphere, 21 plateau and eight Rastrigin archives; 29 are d=2 and 21 are d=10. Seeds follow a fixed readable path roster in the [machine-readable index](I65_I55_FIFTY_ORIGINAL_NPZ_REPLAY_INDEX_2026-11-03.json). This purposive audit roster **is not a random sample** of 620 original cells. No sampling confidence interval is claimed, nor is the complete I55 reproduction implied.

### Detector outputs are *measurements*, not proven defects

Raw archived detector counts summed over these 50 traces are C1=233, C2=1,365, C3=762, C4=0, C5=80, R1=0, R2=2, R3=1, D2=0. These sum **flag counts**, including repeated evaluation calls, not 50 independent defects or a prevalence estimator. In particular, `C1` retains the historical I50 nonspecificity caveat, and `R2/R3` have not been independently assigned a software root cause. One DEAP plateau 10D trace has hundreds of originally flagged out-of-bounds evaluations; this fact is reproduced but does **not** independently establish error source, intentionality or end-user severity. The I55 H55a-c supported, H55d not supported decisions are **unchanged**.

### Historical precision matters

The original source `research/legacy/flat/iteration50_integrity_audit.py` (`class Recorder32`, `TORCH=('evox','evotorch')`) specifies single-precision objective-value recording for those two adapters. All 1,196 newly audited float32 calls agreed when compared with this exact rule, while **756 would have been false rejections** under the incorrect always-float64 oracle. This is a post hoc reproducibility-tool repair, not evidence of a bug in the original algorithms.

## Evidence files, local tests and reproducibility

Nine independently persisted batch witnesses, named `I65_I55_50_NPZ_REPLAY_BATCH_01_2026-11-03.json` through `..._09_...json`, are pinned by their respective Git blob identities in the [machine-readable index](I65_I55_FIFTY_ORIGINAL_NPZ_REPLAY_INDEX_2026-11-03.json). Each per-source witness records the original compressed Git blob, raw `f(x)` count, original vs independent SHA-256 and flags. They were staged as a linear chain of immutable Git tree objects before a final repository commit; the final base tree `e9aefbc7ce32033fd72d21809203075333005e86` was re-read and checked as a distinct aggregate step.

The standalone offline synthetic suite for the new connector verifier passed **9/9** unittest test methods, checking deflate/NumPy decoding, historical Python `repr(float)`, all three objective functions, dimensions 2/10, float32 adapters, malformed/nonfinite values, and altered blobs/hash/flags. A subsequent combined local selection passed **58 pytest tests plus nine subtests** (`0 failed`) after including the pinned original helper module on `PYTHONPATH`. Neither test count stands in for original-archive replay; the **50 separate archival replays above are direct source reads**.

The existing full original 620-NPZ read-only source-to-detector attestation workflow remains available for manual dispatch: `.github/workflows/research-i65-i55-full-npz-attestation-manual.yml`. It has not been run in this session. Its complete 620/620 source-tree, raw bytes, complete A-trace replay and all archived JSON controls remain a separate stricter **NOT_RUN** gate.

## Limits and doctoral decision

**565 original NPZ traces remain unverified numerically**. The archived A-prime and B process series are preserved as digest-level evidence, not as these 620 A-process NPZ files; this work did not recreate those processes. No new optimizer evaluations, PF/OPF, COCO heldout queries, independent defect-ground-truth experiment or real infrastructure validation was executed. The original off-Git I64-R `run.json.gz` has not been recovered, M6/C1 supervisor originality and dissertation-scope approval is unsigned, and the two manuscripts are still DRAFT. Scientific status remains **NO-FREEZE / COCO NOT_RUN / originality NOT_ESTABLISHED**.

**Bottom line:** 50 requested archival replay iterations are genuinely completed and individually verifiable. A complete 620/620 archival attestation and all nontechnical authorization gates remain open. No experimental or research novelty claims are strengthened beyond precise audit coverage.
