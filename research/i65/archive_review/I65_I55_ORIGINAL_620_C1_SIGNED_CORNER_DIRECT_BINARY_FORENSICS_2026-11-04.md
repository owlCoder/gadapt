# I55 original A-source signed C1 corner audit — exact binary closure

**2026-11-04. Original source only; no optimizer or physical PF/OPF/COCO runs.
DRAFT / NO-FREEZE / NOT_ESTABLISHED.**

## What was independently observed

The earlier full-clone GitHub Actions [41804478669](
https://github.com/owlCoder/gadapt/actions/runs/41804478669)
had already authenticated all **620 valid original A-process NPZ traces**,
**295,445** objective observations and the frozen C1/C2 detector flags.
It established **109 C1-positive cells** and **511 C1-zero cells**.

In this follow-up I fetched the **original binary NPZ content of each
of those 109 C1-positive cells directly from the immutable historical
Git commit** `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`.
The list was built from the eight original frozen per-library
`cells_*.json` files whose Git blob SHA-1 IDs match the original
`i55_npz_cross_archive_verifier.py` SHA-pinned roster, then joined
to the authenticated original 620-file NPZ Git manifest, blob
`50ca2e96762447070a74309850cb1aa6586d3eb3`.

**Every one of 109 original NPZ payloads matched its original Git blob
SHA-1 and compressed byte size; every decoded `x.npy` float64
shape/call roster matched its original frozen cell; and its independently
counted negative-plus-positive full corners matched the original C1
event count exactly. No mismatches.** The original source was not
regenerated; all NPZs were read from the original historical Git ref.

## New result: extreme asymmetry of recorded signed corners

| Original function | All −5 events | All +5 events | C1 total |
|---|---:|---:|---:|
| Plateau | 1,803 | 17 | 1,820 |
| Sphere | 225 | 16 | 241 |
| Rastrigin | 22 | 22 | 44 |
| **All** | **2,050** | **55** | **2,105** |

| Original dimension | All −5 events | All +5 events | C1-positive cells | Cells visiting both signs |
|---|---:|---:|---:|---:|
| 2D | 864 | 55 | 84 | 40 |
| 10D | 1,186 | 0 | 25 | 0 |
| **All** | **2,050** | **55** | **109** | **40** |

**2,050/2,105 = 97.39%** of recorded original C1 events were
at the all−5 corner, **55/2,105 = 2.61%** at the all+5 corner.
All 55 positive-corner events were in 2D.
This is a **fixed-design descriptive proportion**, not a frequentist
estimate of general optimizer boundary bias.

| Library with original C1 | All −5 | All +5 | Total C1 |
|---|---:|---:|---:|
| BayBE | 546 | 13 | 559 |
| Bayes_opt | 15 | 12 | 27 |
| Bofire | 888 | 0 | 888 |
| Emukit | 222 | 5 | 227 |
| EvoloPy | 313 | 0 | 313 |
| EvoX | 48 | 10 | 58 |
| GFO | 15 | 15 | 30 |
| Niapy | 3 | 0 | 3 |
| **All** | **2,050** | **55** | **2,105** |

Every other original library had zero frozen C1 events. The original
repeated-candidate C1∩C2 total **1,956** now separates as
**1,953 all−5 repeats** and **three all+5 repeats**.
The **149 first occurrences** separate as **97 all−5 first**
and **52 all+5 first**. Thus repeated visits are heavily
concentrated on the negative corner, whereas +5 appears
principally as a first corner visitation in original cells.

The independently re-derived occupied-cell total remains **40 cells
with both signs, all of them 2D**; **69** have exactly one sign,
as established by the earlier original-source C1/C2 aggregate proof.

## Provenance, reproducibility and limits

- [Machine-readable full 109-file direct Git-binary result, with each
  original NPZ path, original SHA-1, original call count and exact
  signed event count](
  I65_I55_ORIGINAL_109_C1_POSITIVE_NPZ_SIGNED_CORNER_DIRECT_BINARY_REPLAY_2026-11-04.json).
- [SHA-pinned original 109-source C1-positive roster](
  I65_I55_109_C1_POSITIVE_NPZ_ORIGINAL_SOURCE_ROSTER_2026-11-04.json).
- [Independent small JavaScript binary NPZ/DEFLATE and NumPy x.npy
  reader used for this direct Git connector read](
  i55_original_npz_x_binary_readonly_decoder.js).
- [Independent full-original-clone Python NPZ signed-corner checker
  (latest-head CI pending)](
  i55_620_corner_direction_source_audit.py).

The 109 scanned NPZs cover **every original C1-positive cell** because
all other 511 valid source cells had C1=0 according to the already
verified frozen original full-source CI. The historical 10 failed
Nevergrad cells have no valid NPZ trace and were not fabricated.

**This new direct Git-binary validation is complete for the 109
C1-positive original sources, but the separate new full-clone
Python signed-corner GitHub Actions job has no observed result yet.**
Do not claim the latest 133-test Actions run passed.

A full signed corner is **every coordinate exactly −5** or **every
coordinate exactly +5**. C2 is a previous **exact coordinate-byte**
duplicate within the same original cell. No claims are made here
about a library's internal behavior, whether a repeated point
constitutes a software defect, causal explanations, originality,
or extrapolation to other benchmark populations.

Original I55 A′/B coordinate/value streams and the off-Git I64-R
4,200-run source remain unavailable. Independent M3/M5/M6 human
reviews remain unsigned; held-out COCO is NOT_RUN and NOT_AUTHORIZED.

**DRAFT / NO-FREEZE / NOT_ESTABLISHED.**
