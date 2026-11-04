# I55 original A-process: exact occupancy of both ±5 corners in 620 archived cells

**2026-11-04. Read-only proof from original 620-source successful CI.**
Scientific disposition: **DRAFT / NO-FREEZE / NOT_ESTABLISHED.**

## What is now CLOSED from existing SHA-256-pinned historical evidence

Two original, successfully checked full-clone GitHub Actions [run
41804478669](https://github.com/owlCoder/gadapt/actions/runs/41804478669)
reports were independently SHA-256 rehashed from the downloaded
original source artifact:

| Original archive source | Exact SHA-256 |
|---|---|
| CI ZIP artifact 13309441677 | `b80fb1d666fdc05c219ad5c354a8fc495100aacb9b6822533b002731f378fd41` |
| `i55_620_original_flag_census.json` | `a0bfb1bfeaa2979ae8f195ffbcde8c9ff2c45b0562f96ecdf7915e229963c4ea` |
| `i55_620_npz_phase_duplicate_context.json` | `14ee6ea5839b59f3b15403921b7ed76a45c72a0ec39321f5aefde16dbe21d82f` |

The source population is the **620** original valid A-process NPZ
traces of the immutable original commit
`6b56fbc53ffc4d275ecef5e911ea4663474c9a08`,
Git root tree `f88d221152fcb4157a8e1151a11b53cdfe8180b7`.
Ten historically failed Nevergrad cells are not part of the NPZ
population. The original 295,445 calls, objective oracle and frozen
C1/C2 flags passed independent full-clone source attestation.

A C1 event is **only** a full vector at one of *two* distinct signed
corners, `(-5,...,-5)` or `(+5,...,+5)`. The original C2 flag
compares exact float64 coordinate bytes with an earlier vector in
the same ordered cell. Therefore **the first appearance of a signed
corner in a cell is necessarily C1 and not C2**. No third distinct
C1 vector exists.

Let `F = C1 calls - simultaneous C1∩C2 repeats` and `K =
number of original cells with at least one C1`. Every such cell
contributes either **one** or **two** distinct first-corner events,
so:

```text
cells with both signed corners = F - K
cells with exactly one corner = 2K - F

F = 2105 - 1956 = 149
K = 109
both = 149 - 109 = 40
one  = 218 - 149 = 69
```

This arithmetic is exact for the source-defined original C1/C2
rules, and does **not** require fresh optimizer or NPZ generation.

## Original verified breakdown

| Dimension | Original C1 cells | First distinct signed corners | One corner only | Both signed corners |
|---|---:|---:|---:|---:|
| 2D | 84 | 124 | 44 | **40** |
| 10D | 25 | 25 | 25 | **0** |
| **All** | **109** | **149** | **69** | **40** |

| Function | C1-positive cells | First distinct corners | One sign | Both signs |
|---|---:|---:|---:|---:|
| Plateau | 57 | 74 | 40 | 17 |
| Sphere | 29 | 40 | 18 | 11 |
| Rastrigin | 23 | 35 | 11 | 12 |
| **All** | **109** | **149** | **69** | **40** |

| Original library with any C1 | C1-positive cells | Both signs |
|---|---:|---:|
| GFO | 15 | 15 |
| Bayes_opt | 18 | 9 |
| BayBE | 18 | 7 |
| EvoX | 15 | 5 |
| Emukit | 20 | 4 |
| Bofire | 11 | 0 |
| EvoloPy | 9 | 0 |
| Niapy | 3 | 0 |
| **All** | **109** | **40** |

All three independent source report partitions (original library,
function and dimension) independently reconcile the same totals.
Specifically, **all 40 cells that visited BOTH corners occurred in
2D**; no original 10D C1-positive cell visited both signed corners.
This is a descriptive feature of the original fixed benchmark, not a
general law for high-dimensional optimization.

## Reproducibility and limits

[Machine-readable original-source closeout](
I65_I55_620_ORIGINAL_TWO_SIGN_C1_CELL_OCCUPANCY_2026-11-04.json)
records all original strata, source hashes and the proof.
An independent **Python standard-library** read-only verifier was
executed against the authenticated original ZIP, producing a
9,936-byte output JSON with SHA-256
`0142ed011c95276a78b71efd872d88b642c4ec194637651ec9d732250e785ed7`;
**11/11 tamper/invalid-roster/algebra tests PASSED locally**.
The standalone verifier source SHA-256 is
`57273d65ddfe9986ff266dcd700aa5ae44f35dc6311085b5f62367d0970ce6b8`.

A proposed CI step now verifies the same two original SHA256 values
and recomputes the cell-occupancy identity after the original
620-source and phase audit. But **no newest-head GitHub Actions result
is yet observed**. This proof is supported by the **earlier already
successful original source CI reports**, not by a claim of a new CI
execution.

**Still unknown:** the separate *event-level* counts of negative
versus positive corner calls. Both-sign cell occupancy does not
identify how many times each side was revisited. The additional
direct original 620 NPZ signed-corner reader remains available
but unexecuted on the complete original clone in this session.

C1/C2 are **observed instrument flags, not adjudicated software
defects or causal evidence**. All interpretations are descriptive
of the fixed original benchmark. No new optimizer, physical PF/OPF
or COCO was run; A′/B original raw and original off-Git I64-R
raw remain missing; M5/M6 human review remains unsigned.

**DRAFT / NO-FREEZE / NOT_ESTABLISHED.**
