# I65 — Control-conditioned hash-seed divergence in the frozen I55 archive

**Date:** 2026-11-03. **Scientific status:** independent *read-only reclassification* of the original I55 A/A′/B source metadata, **not** a new experimental study, detector, causal mechanism, or newly discovered upstream defect. Original preregistered H55a–H55d decisions remain unchanged: H55a–c SUPPORTED, H55d strict NOT SUPPORTED. Both doctoral manuscripts remain DRAFT; `NOVELTY NOT_ESTABLISHED`, `NO-FREEZE`, `COCO NOT_RUN`, mentor M6/C1 pending.

## Source and verification boundary

Read the 21 original `research/results/iteration55/cells_<library>.json` archives directly from `owlCoder/gadapt`, previously pinned to Git commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`. Each original file was identified by its immutable Git blob SHA-1. The 21 archives contain 630 cell records: 620 technically valid with verified hash-seed sentinels and 10 Nevergrad failures. All 21 library groups were directly evaluated via the connected GitHub source, and each reported original 30-cell distribution was decomposed into a four-pattern control table. The local read-only checker additionally verifies every original blob identity, sentinel and C/R digest-consistency invariant when executed in a complete local clone. Its full-clone archival mode has **not** been run in the container; the observed full-cell results below come from independent direct GitHub reads. Complete original raw binary NPZ replay remains **NOT RUN** (prior small-sample NPZ checks are separate evidence).

The I55 preregistered protocol intentionally compares three fresh processes per cell with `PYTHONHASHSEED=1` (A), `PYTHONHASHSEED=1` (A′), and `PYTHONHASHSEED=2` (B), plus an in-process repeated optimizer run in A. The sentinel checks test whether hash-seed manipulation actually reached the Python interpreter. The `hash`, `hash_same`, `hash_diff`, `hash_rerun` fields are original SHA-256 *call-sequence* digests; no digest is regenerated from an uninspected binary trace in this review.

## 620-cell control-conditioned contingency

| A versus A′ (same `PYTHONHASHSEED`) | A versus B (different `PYTHONHASHSEED`) | Number of valid cells | Library composition | What can be said |
|---|---|---:|---|---|
| Equal | Equal | **585** | 19 other libraries, plus 15 Nevergrad cells | No observed trace difference in either one-shot cross-process comparison |
| Equal | Different | **30** | **SMAC: 30/30** | Change associated with hash-seed intervention **after passing the same-seed control** |
| Different | Different | **5** | **Nevergrad: 5/20 valid** | Cross-process trace instability under **both** conditions: the different-seed difference alone does **not** isolate a hash-seed effect |
| Different | Equal | **0** | None | No observed same-seed-only divergence with a matching B trace |
| **Total** | | **620** | 21 libraries; 10 Nevergrad invalid cells excluded | 620/620 valid sentinel manipulations; *not* 620/620 identical call traces |

In the direct cell data, the five Nevergrad exceptions are precisely `plateau`, dimension 10, seeds 6000–6004; all five also differ on the within-process rerun (`D3=1`). The 10 invalid Nevergrad cells comprise the 10-dimensional sphere and Rastrigin cases and have original execution errors, not negative stability observations. The 30 SMAC cells have `D3=0` and `D3x_same=0`, while `D3x_diff=1` in all 30. Every non-exception valid cell matches across the in-process rerun, A′ and B. Sentinel controls passed for every one of 620 valid cells.

**Headline distinction:** the original `D3x_diff` flag occurs in **35/620** valid cells across two libraries, but only **30/620** have an observed *same-seed-stable / different-seed-divergent* pattern; the other **5/620** also diverge at the same seed and therefore are ambiguous as to the intervention-specific cause. This is a *control-qualified interpretation* of the original detector, **not a correction of H55a's raw D3x-positive library set**. Across the 35 raw cross-seed divergences, 30/35 (85.7%) pass this one same-seed control. This ratio is *not* a population sensitivity/specificity estimate, and does not generalize to new software, hash seeds, or environments.

## Scientific integrity and potential doctoral contribution

The original [I55 report](../../legacy/flat/ITERATION55_REPORT_SR.md) already identifies SMAC's hash-seed dependence and Nevergrad's independent nondeterminism. The independent audit **does not claim to have newly discovered these mechanisms**. Its incremental value is a complete source-anchored contingency table and a fail-closed rule for wording a causal claim. A single successful A/A′ control per cell cannot eliminate every uncontrolled factor or establish a mechanistic theorem. The measurement itself is a call-sequence difference, not proof of a bug, a wasted objective call, or a physical feasibility defect.

For the evaluation-integrity manuscript, describe the measurement hierarchy explicitly:

1. **Exposure manipulation success:** the Python sentinel changed across A and B (620/620 valid cells).
2. **Unqualified D3x flag:** the A–B sequence digest differed (35/620).
3. **Control-qualified hash-seed-associated divergence:** A matched A′ but differed from B (30/620; SMAC only).
4. **Unresolved cause of cross-process nondeterminism:** A differed from A′ and from B (5/620; Nevergrad only).

Do not change the preregistered interpretation of H55a, H55b, H55c, or the original H55d negative verdict; do not retroactively replace outcomes with this post hoc interpretation. The second manuscript's I64-R/I2 conditional and negative results are unrelated to the I55 per-call trace comparator and cannot supply an unmeasured detector-specificity ground truth.

## Read-only reproduction

```sh
# Full clone, original frozen source blobs required; prints structured JSON.
python research/i65/archive_review/i55_control_conditioned_hash_audit.py --repo-root . \
  --output /tmp/i55_control_conditioned.json

# Fast synthetic tests for the four possible control states and fail-closed invariants.
python -m pytest -q research/i65/archive_review/test_i55_control_conditioned_hash_audit.py
```

**Remaining hard evidence gap:** full independent 620 primary-A original `.npz` trace decoding, SHA-256 reconstruction and classifier replay. Original I55 JSON contains valid archived digests, but that metadata-only verification cannot substitute for rehashing the underlying raw trace. Likewise independent blinded controls and prior-art differentiation are required before asserting doctoral originality or new specificity theory.
