# I65 / GAdapt research audit — technical closeout and unclosed scientific gates

> **2026-11-04 later integration addendum, superseding only old
> branch/CI-state statements below:** PRs #14/#15/#16/#17 have
> **all been merged**; `main` reached `c429f88f29c44b449d19db5e5c80c720af86aa6c`.
> Exact-main I55 audit [41885799766](https://github.com/owlCoder/gadapt/actions/runs/41885799766)
> **177/177 PASS**; regression [41885799812](https://github.com/owlCoder/gadapt/actions/runs/41885799812)
> **Python 3.10/3.11/3.12 PASS**, exploratory optimizer skipped.
> The technical historical notes below are retained for provenance.
> [Current authoritative source-only status](I65_CURRENT_MAIN_ARCHIVAL_EVIDENCE_STATUS_2026-11-04.md).
> This updates **no** missing raw data, scientific interpretation,
> human review, or `DRAFT / NO-FREEZE / NOT_ESTABLISHED` decision.


**Date 2026-11-04. Status DRAFT / NO-FREEZE / NOT_ESTABLISHED.**
This is an explicitly limited archival engineering closure note, NOT a
dissertation signoff, new optimizer experiment, new grid simulation, new
statistical preregistration or authorization to merge either draft PR.

## Technical questions that HAVE been answered with original source

| Gate | Technical finding | Exact reproducible source |
|---|---|---|
| I55 original Git trace population | **CLOSED: 620/620 original valid A-process NPZ blobs** authenticated and replayed, 295,445 archived objective calls, zero original trace/oracle/flag discrepancies; 10 historical Nevergrad failures remain excluded | [read-only Actions 41804478669](https://github.com/owlCoder/gadapt/actions/runs/41804478669), Git manifest blob `50ca2e96762447070a74309850cb1aa6586d3eb3`, original Git source commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08` |
| I55 detector occurrence accounting | **CLOSED as descriptive archive arithmetic only:** C1 2,105/109 flagged cells, C2 18,779/245, and 350/620 with any overlapping flag; no accepted true-bug labels | [complete census](I65_I55_620_FLAG_CENSUS_AND_POST_ATTESTATION_OPEN_GATES_2026-11-04.md) |
| I55 function context | **CLOSED as post-hoc descriptive matching only:** 205/210 library×dimension×seed strata with three valid original functions, missing five paired Nevergrad 10D strata; original C1 plateau/sphere left-only 31, right-only 3, both 26, neither 145 | [paired context](I65_I55_205_PAIRED_C1_C2_CONTEXT_REVIEW_2026-11-04.md) |
| I55 exact per-event phase | **CLOSED:** 294,245 original search + 1,200 original post calls; C1 2,105 search/0 post; C2 17,579 search/1,200 post; all post calls occur in original PyGAD and duplicate prior search bytes | [raw NPZ direct audit](I65_I55_620_RAW_PHASE_AND_C1_C2_DUPLICATE_FORENSICS_2026-11-04.md) |
| I64-I2 original archived seed-bootstrap | **CLOSED (archival statistical arithmetic):** original 20,000-draw replay and 13/13 archived quantities matched; H64h2 remains **OPPOSITE** | [previous exact bootstrap review](I65_I64_I2_EXACT_BOOTSTRAP_AND_POSTHOC_AUDIT_2026-11-03.md) |
| Original I32 source and synthetic CI | **CLOSED on draft recovery branch, NOT merged to main:** exact seven original I9/I11/I14/I17/I32 source/protocol Git blob identities recovered and authenticated at the original I32 workflow head; new guarded source-only CI **19/19 PASS**, physical job **SKIPPED** | [separate draft PR #15](https://github.com/owlCoder/gadapt/pull/15), [Actions 41812770932](https://github.com/owlCoder/gadapt/actions/runs/41812770932) |
| Original I32 archived 72-run output | **CLOSED as read-only archival outcome accounting:** authenticated Oct 21 original 72-run Actions JSON/CSV, reproduced 72 paired-seed records, 216 per-scenario partitions, 6 method summaries, 5 original exact paired test numbers, 51 archived 9D witness schema/recorded mean cost checks. **12,913 historical native AC calls; ZERO NEW solver calls.** | [historic Actions 39686171613](https://github.com/owlCoder/gadapt/actions/runs/39686171613), ZIP SHA-256 `c2a84c57571841737c7a9f006091a4a97097fe6843d42265ef3ccbd84937f782`; [machine ledger PR #15](https://github.com/owlCoder/gadapt/blob/audit/i32-original-source-recovery-readonly-20261104/research/I32_ORIGINAL_SOURCE_AND_72RUN_ARCHIVE_RECONCILIATION_2026-11-04.json) |

A **historical original source** is not a claim of scientific priority.
An archived solver's `witness_checked` value or stored AC mismatch
is not an independently repeated physical-model verification.

## Technical CI safety status

- Original I55 full-clone run 41804478669: **SUCCESS**, source-only;
  tests **86** (seven suites); no new I55 optimization or physics.
- New I32 restoration run 41812770932: **SUCCESS**; 19 original
  zero-native-AC tests, all original source hashes matched;
  physically solving I32 job **SKIPPED**.
- An unrelated **older robustness** workflow inadvertently ran a
  **12-run × 120-generation optimizer benchmark** when I32 draft
  PR #15 initially opened (run 41812770943). It is NOT part of any
  original I55/I32 registered experiment; it MUST NOT be counted
  or described as archival replay. The corresponding
  `exploratory-benchmark` workflow has been made **manual-opt-in-only**
  in both draft PRs, source blob
  `32774ed66c7e16a7851195463f67b023234ee5b9`.
  The already-executed accidental CI cannot be undone.
- Both proposed PRs are **DRAFT and OPEN**. Main remains at
  `8d376a720afe2704af5efdb39777dac7a2c5e742`.
  The historical I32 files remain absent from main **until the
  recovery PR is independently reviewed and merged**. The temporary
  I32 workflow edit has been reverted to the exact `main` Git blob
  on I55 PR #14, so the I55 PR now does **not** change the I32 workflow.
  Original older I32 failures on I55 PR #14 do not invalidate I55 source audit.

## What is still scientifically OPEN and why

| Outstanding decision or source | Current state | Evidence genuinely needed to close |
|---|---|---|
| I55 original A′/B full coordinates and values | **SOURCE_NOT_ARCHIVED_WITH_ORIGINAL_A_NPZ** | Recover and authenticate ORIGINAL source trajectories, if available; cannot extrapolate from SHA digests or synthesize replacement optimizers |
| I64-R 4,200 original raw runs | **BLOCKED_OFF_GIT_SOURCE** | Recover the ~8 MB ORIGINAL `research/results/iteration64_r/run.json.gz` and independently trusted full SHA-256 (only historic shortened marker `f23046f6…3618` known); run read-only structural/seed bootstrap. 15 visible active branch tips, GitHub releases, targeted connected Drive and Library filename searches did not produce this original |
| Independent detector precision/specificity and software-root-cause attribution | **NOT_ESTABLISHED** | Blind/independent ground-truth defect labels and source adjudication; source-level 620/620 numerical replay is not a ground-truth set |
| Independent M3 ORPD/IEEE14 witness and model validation | **NOT_ESTABLISHED** | Independent power-system expert checks and physical model replay if a real engineering generalization is proposed; not authorized here |
| M5 independent statistical methods/selection-bias review | **HUMAN_REVIEW_PENDING** | Reassess fixed 21-cell vs function-family inference and rare I2 ORPD tail-cell dependence; no new post hoc selection-based confirmatory claim |
| M6/C1 doctoral originality/scope | **HUMAN_SIGNATURE_MISSING** | Reviewer explicitly selects, dates, signs A/B/C/Other in [supervisor package](I65_M6_C1_SUPERVISOR_DECISION_PACKAGE_2026-11-03.md); no AI inference is a signature |
| Held-out COCO and any new prospective optimizer/PF experiments | **NOT_RUN / NOT_AUTHORIZED** | A prospective protocol, predeclared new method/baselines/seeds, credible independent budget/physics review and human approval **before any run** |

## Retrieval handoff for actual missing originals

The missing original off-Git I64-R 4,200-run file and I55 A-prime/B
byte sequences **cannot** be manufactured from existing aggregate
reports. [Owner-machine provenance and exact read-only commands](
I65_EXTERNAL_ORIGINAL_SOURCE_RECOVERY_HANDOFF_2026-11-04.md) define
where to look, how to capture an independently witnessed full SHA-256,
and what the existing strict R structural verifier can establish.
GitHub Actions listings on the historical I55 source-results date
**2026-10-23** and I64-R source-results date **2026-10-29** returned
no workflow runs. Those two negative date scopes do not prove loss
from the original experimental machine.

## Final handoff principle

The original mechanical archive can be **technically closed** without
inventing missing raw data, new algorithmic novelty or independent
physics. Conversely, **technical closure cannot substitute** for
signed human M6/C1 decisions, a defensible novelty comparison or a
prospectively designed external-validity study. Manuscripts remain
**DRAFT**, held-out COCO remains **NOT_RUN**, and the research remains
**NO-FREEZE / NOT_ESTABLISHED**.
