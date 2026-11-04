# I55 original C1 — call-weighted versus distinct signed-corner visits

**2026-11-04 | Archived original A-process evidence, post-hoc descriptive analysis**  
**DRAFT / NO-FREEZE / NOT_ESTABLISHED**

## Source and independent reconciliation

The original [full-clone I55 archive-only CI 41804478669](
https://github.com/owlCoder/gadapt/actions/runs/41804478669) authenticated
all **620 valid original NPZ traces** and 295,445 objective calls,
including 2,105 full-corner (C1) events. In a later independent
direct-Git source audit, every one of the **109 C1-positive NPZ binaries**
was retrieved from immutable original commit
`6b56fbc53ffc4d275ecef5e911ea4663474c9a08`,
compared against its original Git blob SHA-1 and byte size, and its
`x.npy` float64 rows counted exactly. The signed results matched
each of the frozen C1 per-cell totals.

[Complete original signed NPZ ledger](
I65_I55_ORIGINAL_109_C1_POSITIVE_NPZ_SIGNED_CORNER_DIRECT_BINARY_REPLAY_2026-11-04.json)
(Git blob `7f1716b061d703d5ab8c367d73386371dcb9d7a9`)
and [original C1-positive file roster](
I65_I55_109_C1_POSITIVE_NPZ_ORIGINAL_SOURCE_ROSTER_2026-11-04.json)
(Git blob `f1dd7d1b283eba1ee12562acaf22a144d9c525d5`)
were *again* checked against the SHA-256-pinned, independently
successful original-620 source census and NPZ phase/duplicate output.
The source-only [reconciliation program](
i55_109_signed_corner_source_weighting_gate.js) rejected **all 10**
tested deliberate modifications to source counts, source tree,
row identity, original NPZ Git blobs and prior census/phase counts.
A separate [13-case Node test suite](
test_i55_109_signed_corner_source_weighting_gate.cjs) has been
committed for future independent full-clone CI.

## The same original data, two different denominators

| Event/visitation measure | Full −5 corner | Full +5 corner | Total |
|---|---:|---:|---:|
| Original recorded C1 evaluation calls | 2,050 | 55 | 2,105 |
| Distinct first appearance of each signed corner **within a cell** | 97 | 52 | 149 |
| Subsequent identical-byte repeats in that cell | 1,953 | 3 | 1,956 |

**Call-weighted negative fraction:** `2050/2105 = 97.39%`.  
**Deduplicated first-corner negative fraction:** `97/149 = 65.10%`.

The difference is **32.29 percentage points**. The repeated-corner
population is almost entirely negative (`1953/1956 = 99.85%`).
These numbers are not contradictory: an originally observed cell
may keep proposing an identical negative corner and therefore
contribute dozens or hundreds of events but only **one** distinct
negative-corner visit.

Across **109** C1-positive original cells:
**57** visited only the negative corner, **12** only the positive
corner, and **40** both. Since a both-sign cell contributes *two*
first-corner visits, the denominator **149** describes
**(cell, signed corner) pairs**, *not 149 independent experiments*.
No significance test or causal inference is warranted.

## Repeat concentration and composition (exploratory only)

- Just **five** original cells account for **851 of 2,105 C1
  events (40.43%)**. The original per-cell ledger makes these five
  cases independently inspectable.
- Four original libraries, ranked **after observation** by repeated
  C1 counts, contribute **1,918 of 1,956 repeats (98.06%)**:
  Bofire 877, BayBE 534, EvoloPy 304 and Emukit 203.
- A post-hoc *leave-these-four-libraries-out descriptive check* retains
  **51 C1-positive cells** with 118 C1 events:
  **81 negative / 37 positive** (negative **68.64%** of event calls).
  Their first corners are **46 negative / 34 positive** (negative
  **57.5%** among 80 deduplicated cell-corner visits). These exclusions
  were not preregistered and must not be presented as a new
  confirmatory analysis.
- The original library mix and function/dimension allocations
  differ. C1 event shares cannot be interpreted as an IID
  population estimate or an optimizer ground-truth defect rate.

[Machine-readable full weighting/concentration report](
I65_I55_ORIGINAL_SIGNED_C1_DEDUP_WEIGHTING_AND_LIBRARY_CONCENTRATION_2026-11-04.json)
pins original source inputs and the retrospective sensitivity rule.

## Explicit scientific limits

The descriptive finding is **large repeated-event inflation** of the
negative corner in this fixed 21-library/three-function/two-dimension
archive. It does **not** establish biased software implementations,
algorithm novelty, a causal mechanism, physical validity, detector
specificity or broader external validity.

The separate new full-clone signed-corner GitHub Actions workflow,
including the 13 Node regression cases above, **does not yet have an
observed successful run at the latest PR head**. The prior 86/86 I55
CI remains PASS for its own historic source-code head. Original
I55 A′/B raw arrays and original off-Git I64-R 4,200-run source
remain missing; M3/M5/M6 independent reviews remain unsigned, and
held-out COCO is NOT_RUN/NOT_AUTHORIZED.

**No new optimizer, physical PF/OPF or COCO run was executed.**  
**DRAFT / NO-FREEZE / NOT_ESTABLISHED.**
