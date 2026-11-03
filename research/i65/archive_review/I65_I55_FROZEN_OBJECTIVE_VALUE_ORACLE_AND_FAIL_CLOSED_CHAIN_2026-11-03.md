# I65: independent frozen I55 objective-value oracle (source-level audit)

**Date:** 2026-11-03. **Status:** code/unit-test verification only; original 620 NPZ raw-array replay **NOT RUN**. No new optimizer, AC power-flow, or held-out COCO run. All frozen data and original I49/I50/I55 classifications remain unmodified.

## The distinct evidence gap

A digest check confirms that the stored `x/f/phase` sequence is the same sequence recorded in the I55 JSON. Reclassifying the sequence confirms that the detector flags are internally consistent with that sequence. Neither verification establishes that recorded `f` values are numerically consistent with the **known frozen objective** evaluated on the recorded `x`.

To avoid conflating those three levels, this post hoc audit adds a **pure, independent objective evaluator** to the existing `research/i65/archive_review/i55_npz_cross_archive_verifier.py`. It is independently written from the original immutable `research/legacy/flat/iteration49_integrity_audit.py` `Problem.base` definition. It does not import historical optimizers or run experiments.

## Exact frozen problem definitions

Let `x` denote the untransformed original 2D or 10D vector (the I55 test suite did not use transformed GAdapt test objectives). The oracle computes:

- **Sphere:** `sum((x_i - c)**2)` with `c = -5 + 0.37*(5 - (-5)) = -1.3`.
- **Rastrigin:** `10*d + sum(x_i**2 - 10*cos(2*pi*x_i))`.
- **Plateau:** `sum(floor(x_i))`.

It evaluates *all* archived calls, not just the reported final point; including calls outside the bounds is intentional, because C3 is a detector, not an excuse to drop objective calls. It compares archived scalar values with the independently re-evaluated output using declared `rtol=1e-10`, `atol=1e-10` (small tolerance for cross-platform floating point), with NumPy nonfinite-equivalence semantics. An absent/unknown function, non-float64 data, incorrect dimension, or any inconsistent objective value fails the replay. This is an archived-data consistency check and **not** a second independent physical model or proof of external library defects.

## Integration and fail-closed behavior

1. The original end-to-end attestation first pins the manifest, original Git tree, and exact bytes of all 620 successful original NPZ blobs.
2. The existing `replay_npz()` still rehashes the exact `x/f/phase` call sequence and compares archived C/R detector flags.
3. **New:** before the flags are accepted, it computes every `f(x)` independently and rejects any mismatch. A trace with a self-consistent but fabricated digest and altered objective value now **fails**; this is tested explicitly.
4. The `audit()` output has `frozen_objective_value_calls_checked` and `frozen_objective_values_pass` fields. The top-level `i55_full_npz_attestation.py` independently requires those fields before returning `full_attestation_pass=true`.
5. The previously manual-only workflow is retained as manual-only; its inexpensive tests are expanded to include this new oracle and the existing byte, trace and attestation tests. **Do not dispatch the workflow automatically.**

Synthetic tests: **44/44 PASS** across the four relevant test files (`8` new oracle cases; `10` adapted prior trace tests; `14` chain tests including a missing-oracle failure; `12` Git source manifest tests). The existing trace unit fixture was adjusted to contain mathematically valid sphere objective values rather than arbitrary numbers. No historical science data changed.

## Evidence levels, not interchangeable

| Claim | Checked here | Required for future completion |
|---|---|---|
| Original Git NPZ roster is stable | Previously verified, 620 Git blob IDs, 12,319,037 bytes | Keep pinned historical commit/tree |
| Local oracle implementation and blocking logic | **YES**, 44 synthetic tests | Re-run tests on the GitHub full clone |
| Original 620 NPZ byte-level attestation | **NO** | Check original 620 working-tree files |
| Original 620 A-process SHA-256 and detector flag replay | **NO** | Read original `x/f/phase` arrays |
| Original 620 per-call frozen objective evaluations | **NO** | Run newly integrated independent objective oracle after source gates |
| A'/B trace-level external seed causality | **NO** | Those raw traces were not archived; original digest comparisons remain original evidence |

**Effect on the thesis:** this adds a stronger validity gate for the measurement-integrity manuscript and supplies a falsifiable audit criterion. It does not introduce a novel optimization algorithm or estimator, alter the predeclared I55 H55a–d outcomes, measure detector specificity, or establish transfer beyond the frozen objective families. H55a–c supported; H55d not supported; originality **NOT_ESTABLISHED**, M6/C1 pending, `NO-FREEZE`, held-out COCO `NOT_RUN`.
