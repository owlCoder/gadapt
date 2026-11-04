# I65 — Full I55 A-process census and outstanding scientific gates

**2026-11-04 | DRAFT / NO-FREEZE / NOT_ESTABLISHED.** This is a read-only
source audit and descriptive census, not a new optimization or power-flow
experiment, a clinical-style diagnostic validity study, or COCO validation.

## Full original A-process attestation

The [isolated read-only GitHub Actions run](https://github.com/owlCoder/gadapt/actions/runs/41797397598)
succeeded with original I55 commit
6b56fbc53ffc4d275ecef5e911ea4663474c9a08, source tree
f88d221152fcb4157a8e1151a11b53cdfe8180b7 and frozen
620-NPZ manifest blob 50ca2e96762447070a74309850cb1aa6586d3eb3.

**PASS: all 620 original NPZ source bytes, A-process coordinate/value/phase
SHA-256 transcripts, objective-value oracle over 295,445 archived
evaluations, and all C/R/D2 flags. No observed discrepancies.**

The old 181-source checks and four additional direct connector checks are
subsets of 620, not independent additive datasets. The original 10 failed
Nevergrad source cells are excluded from the 620 valid NPZ archive.

GitHub Actions artifact **13305773463** includes the 181-source
reconciliation, full 620 attestation and the 620-detector-flag census.
SHA-256 content checksums:

- ZIP archive: 8fde49274a3ba909cef5cfc8985476c17262473ef9ae224276f8b2bfb05a3681
- Full 620 attestation JSON: 9a6a5a3d32120394798ccf47675aaff403b82062fac240267a47e327283fa111
- Prior 181-witness reconciliation JSON: dfbe7cc7f1dc55ca5eeb96aa85e9c44b2636a525ac083d4300745e9d740c4dea
- New 620 flag census JSON: a0bfb1bfeaa2979ae8f195ffbcde8c9ff2c45b0562f96ecdf7915e229963c4ea

The new workflow completed 70 synthetic/unit tests across five suites
(19+9+20+14+8). The I55 census is gated on full 620-source PASS.

## Complete descriptive A-process flag population

The new [read-only Python census](i55_620_flag_census.py)
authenticates the original 21 frozen cell-archive Git blobs and counts
both (i) flag occurrences and (ii) distinct cells with any occurrence
of that flag.

| Flag | Original occurrences | Distinct valid cells flagged |
|---|---:|---:|
| C1 | 2,105 | 109 |
| C2 | 18,779 | 245 |
| C3 | 8,474 | 60 |
| C4 | 110 | 10 |
| C5 | 1,200 | 30 |
| R1 | 0 | 0 |
| R2 | 25 | 25 |
| R3 | 11 | 11 |
| D2 | 0 | 0 |

**350 / 620 original valid cells have one or more overlapping flags.**
This is NOT 350 independently adjudicated defects. Never add individual
flag frequencies as though they were mutually exclusive or infer detector
sensitivity, specificity, true-positive rate or bug prevalence from them.

**C1 function mix:** plateau 1,820 / 2,105 occurrences (86.46%),
sphere 241, Rastrigin 44. Those correspond respectively to 210 / 205 /
205 valid cells and 95,275 / 99,434 / 100,736 original objective
calls. C1 has a strong plateau/context association, not demonstrated
causal specificity for software defects.

The census is a descriptive aggregation of frozen original JSON with
a prerequisite PASS of the complete binary NPZ replay, not a second
independent reading of all 620 binary files.

## Material open gates

1. **A-prime/B raw source** — Original A-process NPZ archives do not
   preserve A-prime/B coordinates and objective values. Existing
   A/A-prime/B digest comparisons are a different evidence level.
2. **Original I64-R 4,200-run off-Git archive** — The tracked R directory
   contains only analysis.json.gz and check_repro.json.gz. The original
   run.json.gz was retained outside Git; known SHA-256 is abbreviated
   f23046f6…3618. Targeted searches in accessible connected Drive and
   GitHub release listings found no candidate. This cannot prove
   absence from the original research machine. Require the original
   file plus a separately trusted complete SHA-256 before applying the
   [read-only recovery gate](i64_r_off_git_raw_recovery_gate.py).
   Do not regenerate experiments as a substitute.
3. **Detector specificity/root cause** — Independent ground-truth
   adjudication and validity studies remain NOT_ESTABLISHED.
4. **Human M6/C1 originality sign-off** — The
   [supervisor decision package](I65_M6_C1_SUPERVISOR_DECISION_PACKAGE_2026-11-03.md)
   remains unsigned; choose/date/sign A, B, C or another decision.
5. **Independent physical ORPD validation / held-out COCO** —
   independent M3 witness/model review is unresolved and no COCO
   confirmation is authorized or executed.

The historical 2026-11-03 literature, I55 and I64 assessments must remain
frozen. This dated addendum supersedes only old statements that full
620-source mechanical replay is NOT_RUN. It does not alter the
supported/unsupported I55 hypotheses or original negative I64 results.

[Machine-readable post-620 register](I65_POST_620_ORIGINAL_A_PROCESS_EVIDENCE_GATE_REGISTER_2026-11-04.json)

**Scientific disposition: DRAFT / NO-FREEZE / NOT_ESTABLISHED / COCO NOT_RUN.**

CI safety: An unrelated exploratory benchmark ran automatically during
earlier PR-wide CI before its PR guard was added. The dedicated source
audit and new census do not call optimizers; the benchmark was skipped
in the latest guarded PR workflow.
