# I65 — I55 original A-trace C1/C2 event-phase and duplicate-provenance audit

**2026-11-04 | Read-only source evidence | DRAFT / NO-FREEZE / NOT_ESTABLISHED.**

This audit directly re-reads and numerically replays **all 620 original valid
I55 A-process NPZ files**, rather than inferring row-level behavior from
frozen per-cell C1/C2 totals. It executes no optimizer, numerical
optimization simulation, PF/OPF, or held-out COCO experiment.

## Origin and independent executable witness

- Original experiment source commit:
  `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`.
- Immutable 620-NPZ Git blob manifest:
  `50ca2e96762447070a74309850cb1aa6586d3eb3`.
- [Read-only full-clone GitHub Actions run](https://github.com/owlCoder/gadapt/actions/runs/41804478669):
  **SUCCESS** after replaying all 620 original NPZ source Git blobs, saved
  sequence SHA-256 digests, detector flags, and 295,445 original objective
  measurements against the frozen independent oracle.
- Artifact ID **13309441677**:
  `i55-pinned-original-source-only-audit`, ZIP SHA-256
  `b80fb1d666fdc05c219ad5c354a8fc495100aacb9b6822533b002731f378fd41`.
- New direct-binary report:
  `i55_620_npz_phase_duplicate_context.json`, SHA-256
  `14ee6ea5839b59f3b15403921b7ed76a45c72a0ec39321f5aefde16dbe21d82f`.
- All prior 620 attestation, 21-library flag census, and 205-stratum
  paired-function JSON files have matching previous SHA-256 values.
- **86 synthetic/unit tests passed** across seven suites
  (19+9+20+14+8+7+9). The new tests include exact repeated
  IEEE-754 bytes (including signed zero), missing/wrong phase,
  all-coordinate corners, C1/C2 overlap, and first-vs-current phase.

## Semantics grounded in the frozen C1/C2 source

C1 is incremented when an evaluated vector equals **all -5 coordinates**
or **all +5 coordinates**. Merely touching one box boundary is not C1.
C2 is incremented when a candidate's `float64` coordinate byte string
has appeared previously **in the same archived cell sequence**. A
repeat is not by itself a defect, and near-equal vectors need not be C2.

The `phase` label is saved in the original NPZ and included in its
original SHA-256 trace. Here `search` means phase byte 0, `post`
phase byte 1. The first phase of a duplicate is assigned using the first
exactly identical row seen earlier, not the most recent row.

| Original source observation | Search | Post | Total |
|---|---:|---:|---:|
| Objective calls stored in NPZ | 294,245 | 1,200 | 295,445 |
| C1 occurrences | 2,105 | 0 | 2,105 |
| C2 exact-coordinate repeats | 17,579 | 1,200 | 18,779 |
| Simultaneous C1 and C2 | 1,956 | 0 | 1,956 |

**1,956 / 2,105 = 92.92% of C1 *occurrences* also have C2 in that
same original trace.** Only **149** C1 occurrences have not previously
appeared as an exact row earlier in their own trace. This is a strong
event-level overlap under the archived observation rules, **not**
1,956 independently adjudicated software bugs.

## Where the 1,200 post events occur

**Exactly 1,200 post records are present in the 620 original NPZs.**
All belong to **PyGAD** (30 valid cells × 40 post evaluations); every
one is a C2 exact-coordinate duplicate whose first identical record was
in search. No post records occur in the other 20 libraries. No post
record is C1. Thus the original C2 total is separable into:

- **17,579 search→search repeats** (93.61% of original C2 events).
- **1,200 search→post repeats** (6.39%).
- **0 post→search or post→post repeats** when classified against the
  first observed coordinate instance.

Source-side chronological context: frozen
`research/legacy/flat/iteration49_integrity_audit.py`, original Git
blob `dc14a1c95a1f3bb1ba083f705a75503321bbeafd`,
has `run_pygad(...)` calling `ga.run()`, then
`rec.phase = "post"`, then `ga.best_solution()`. This is
**consistent** with the post-phase recorded calls; the archival audit
does not instrument PyGAD internals or prove that this one library call
alone causes every post-phase evaluation.

## Confounding by function and library remains important

| Function | Original calls | C1 search | C2 search | C2 post | C1∩C2 search |
|---|---:|---:|---:|---:|---:|
| Plateau | 95,275 | 1,820 | 6,914 | 400 | 1,746 |
| Sphere | 99,434 | 241 | 5,350 | 400 | 201 |
| Rastrigin | 100,736 | 44 | 5,315 | 400 | 9 |

These counts can be further compared with the prior
[205 matched function strata](I65_I55_205_PAIRED_C1_C2_CONTEXT_REVIEW_2026-11-04.md).
The exposure denominators are original *archived call counts*, not
independent samples of real-world bugs.

The new read-only program
[`i55_620_npz_phase_duplicate_context.py`](i55_620_npz_phase_duplicate_context.py)
first verifies the exact historical Git tree and every NPZ Git blob,
then replays every original SHA-256 trace, objective value and flag
before classifying phase events. It fails closed if C1/C2/C5 totals
disagree with frozen source cell JSON. Its source-only adversarial tests
[`test_i55_620_npz_phase_duplicate_context.py`](test_i55_620_npz_phase_duplicate_context.py)
were executed successfully in CI.

The source-anchored summary is
[`I65_I55_620_ORIGINAL_NPZ_PHASE_CONTEXT_SUMMARY_2026-11-04.json`](I65_I55_620_ORIGINAL_NPZ_PHASE_CONTEXT_SUMMARY_2026-11-04.json).

## What this does *not* establish

The audit **does not** assign ground-truth bug labels to any library,
quantify detector sensitivity/specificity, infer population causal
effects, establish algorithm originality, or approve any M6/C1
decision. The original I55 A′/B raw traces are not represented in
these A-process NPZ files. The original I64-R off-Git 4,200-run raw
archive remains unavailable. No held-out COCO was authorized or run.
The known I64 negative and sensitivity outcomes remain unchanged.

**Scientific state: DRAFT / NO-FREEZE / NOT_ESTABLISHED.**
