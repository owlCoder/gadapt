# I55 original 620 NPZ C1 corner forensics — first versus exact repeat

**2026-11-04 | Original A-process evidence only | DRAFT / NO-FREEZE / NOT_ESTABLISHED**

This is an independent *derived summary of already archived original
source calls*, plus a new original-full-clone tool that will distinguish
the two signed corners when its GitHub Actions run is available.
No new optimizer, PF, OPF or held-out COCO trial has been executed.

## Independently derived from the ORIGINAL published phase-level CI output

Original pinned full-clone Actions
[41804478669](https://github.com/owlCoder/gadapt/actions/runs/41804478669)
passed 620/620 raw NPZ source Git/blob/trace/flag/objective replay.
Its `i55_620_npz_phase_duplicate_context.json` has independently
reconfirmed SHA-256
`14ee6ea5839b59f3b15403921b7ed76a45c72a0ec39321f5aefde16dbe21d82f`,
from original artifact ID `13309441677`.

A C1 event requires **every coordinate to equal either −5 or +5**
(the two all-same-sign boundary corners). C2 means that the exact
float64 binary coordinate vector already appeared in that same cell's
ordered original trace. Thus `C1∩C2` identifies an **exact previous
corner replay**, not a new distinct first-corner appearance.

| Original function | C1 events | C1 first occurrence | C1 exact repeat |
|---|---:|---:|---:|
| Plateau | 1,820 | 74 | 1,746 |
| Sphere | 241 | 40 | 201 |
| Rastrigin | 44 | 35 | 9 |
| **Total** | **2,105** | **149** | **1,956** |

| Original dimension | C1 events | C1 first occurrence | C1 exact repeat |
|---|---:|---:|---:|
| 2D | 919 | 124 | 795 |
| 10D | 1,186 | 25 | 1,161 |
| **Total** | **2,105** | **149** | **1,956** |

C1 event-level exact repeat fraction is **1,956/2,105 ≈ 92.92%**.
Plateau's fraction is **1,746/1,820 ≈ 95.93%**; Sphere
**201/241 ≈ 83.40%**; Rastrigin **9/44 ≈ 20.45%**.
The original 10D recorded C1 events repeat at **1,161/1,186
≈ 97.89%**, compared with **795/919 ≈ 86.51%** in 2D.
These are **post-hoc descriptive ratios** of recorded calls, not
independent trials or p-values. Library composition and recorded
optimizer trajectories differ across strata.

A full machine-readable cross-stratum reconciliation, including the
eight original libraries with any C1 event, is in
[I65_I55_620_ORIGINAL_C1_FIRST_VS_REPEAT_EVIDENCE_2026-11-04.json](
I65_I55_620_ORIGINAL_C1_FIRST_VS_REPEAT_EVIDENCE_2026-11-04.json).

## New read-only two-corner directional audit: unexecuted on original source

The new [SHA-authenticated original 620 signed-corner classifier](
i55_620_corner_direction_source_audit.py) separately classifies:
- negative (all −5) and positive (all +5) corners;
- first versus exact-byte duplicate occurrence **within the same NPZ cell**;
- current phase search versus post.

For every valid original file, it confirms the Git-tree manifest,
the NPZ blob ID and size, original C1/C2 cell counts, and the previous
2,105 / 1,956 / 149 original totals. It then outputs signed breakdowns
overall and by original library, function and dimension. It refuses
nonfinite coordinates, non-float64 data, malformed phase arrays and
unrecognized dimensions. [Nine synthetic adversarial tests](
test_i55_620_corner_direction_source_audit.py) cover these rules.

**As of this version, there is NO observed GitHub Actions result of
the new signed-corner source program.** The original phase report
does **not** contain the negative-versus-positive split, so it would
be fabrication to report those two unknown numerical totals now.

For a fully cloned Git history with the 620 source files, a reviewer
can independently execute only archived-source reading and
synthetic tests:

```bash
python -m unittest discover -s research/i65/archive_review \
  -p 'test_i55_620_corner_direction_source_audit.py' -v
python research/i65/archive_review/i55_full_npz_attestation.py \
  --repo-root . --output /tmp/i55_620_full_source_check.json
python research/i65/archive_review/i55_620_corner_direction_source_audit.py \
  --repo-root . \
  --full-attestation /tmp/i55_620_full_source_check.json \
  --output /tmp/i55_620_signed_corner_report.json
```

The CI proposal runs the same read-only checks after the existing
620 raw original attestation and saves the signed-corner report.
It also runs the 38 earlier local I64-R/E synthetic tests; total
expected **133** cases, but **only an older source version's 86/86
is independently recorded as Actions SUCCESS**. No new latest-head
133-test CI verdict is yet available.

## Scientific limits

These C1 corners are *recorded geometry*, not proof of optimizer
software bugs. Their repeated visit count is not statistically
independent of the number of calls and should not be generalized
beyond this fixed 21-library, three-function, two-dimension design.
The original A′/B raw sequences remain unarchived with the original
620 A files; the off-Git R 4,200-record source remains unavailable.
No prior-art originality, defect specificity, M3 physical validation
or M5/M6 human signoff is implied.

**DRAFT / NO-FREEZE / NOT_ESTABLISHED; COCO NOT_RUN.**
