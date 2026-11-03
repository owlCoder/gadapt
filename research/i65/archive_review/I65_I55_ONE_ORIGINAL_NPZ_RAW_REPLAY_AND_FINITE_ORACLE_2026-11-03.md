# I65: one original I55 raw NPZ replay and finite-oracle repair — 2026-11-03

**Evidence level: one original A-process NPZ numerically replayed (1/620); FULL 620-NPZ ATTESTATION NOT RUN.** No optimizer, simulator, PF or COCO executed.

## Real original binary, not only a metadata summary

Frozen commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`, original binary [BayBE plateau d=2 seed=6003](https://github.com/owlCoder/gadapt/blob/6b56fbc53ffc4d275ecef5e911ea4663474c9a08/research/results/iteration55/traces/baybe/plateau_2_6003.npz).
The connected GitHub source returned actual Base64 NPZ bytes; these were decoded with Python and independently checked against the original binary Git blob SHA-1 `c663f533a29983f5e9397c8cbc341c3166d3f5d7`. The 1,539-byte compressed file has independent raw SHA-256 `93978724717bdcb5d6b51bd00a7b514d2d94077834674f45df2a796bdfbfcb10`.

The full saved A-process call-sequence SHA-256 was independently rehashed from `x/f/phase` NumPy arrays and **exactly matched** `fa89b7dc7299a0e4f744c286f4cdfa2d26826cb3834192640cd747d9f015a4e1`. All **200/200** recorded objective values exactly equal `sum(floor(x))` on finite input coordinates. All original C1–C5/R1–R3/D2 detector flags were independently recomputed with **0 mismatches**. C1=188 (187 calls at the all-lower corner, 1 at the all-upper corner), C2=186 repeated points, exactly 14 unique coordinate vectors. All 200 phases are `search`. The ask/tell source has no reported final `x_star/f_star`, hence R flags are not applicable (zero). The plateau corner result illustrates *C1 nonspecificity*, not a new documented algorithm bug.

## Falsified test-harness assumption and repair

The prior I55 objective oracle used `np.isclose(..., equal_nan=True)` and did not enforce finite inputs or outputs. On a synthetic adversarial sphere cell it **incorrectly accepted** `x=(NaN,0), f=NaN`; it also accepted `x=(1e308,0), f=+Inf` when the independent evaluation overflowed. These are **counterexamples to the checker**, not observations of original BayBE behavior.

The repaired oracle rejects non-finite archived coordinates, non-finite stored objective values, and non-finite independent objective results; `equal_nan=False`. Six new tests include full NPZ fixtures with internally matching SHA-256 and detector flags that must nonetheless fail the numerical oracle. **50/50 local tests pass**, up from 44; the one original BayBE NPZ still passes all checks.

## Scientific limits

This is a **single-cell original raw replay**, not 620/620. The other 619 original NPZ arrays were not decoded in this continuation; a full Git clone is unavailable over the current network. Original A′/B raw traces are not in the 620 A-process NPZ files. Metadata identity, partial rehashing, and synthetic tests must never be described as full independent reproduction or detector specificity. Original H55a–c SUPPORTED and H55d NOT SUPPORTED are unchanged, as are manuscript DRAFT, NO-FREEZE, COCO NOT_RUN, originality NOT_ESTABLISHED, and unsigned M6/C1.

Read-only source: [updated verifier](i55_npz_cross_archive_verifier.py), [regression tests](test_i55_frozen_objective_oracle.py), [machine-readable single-cell witness](I65_I55_ONE_ORIGINAL_NPZ_RAW_REPLAY_AND_FINITE_ORACLE_2026-11-03.json). Full original replay remains a [manual-only workflow](https://github.com/owlCoder/gadapt/blob/main/.github/workflows/research-i65-i55-full-npz-attestation-manual.yml).
