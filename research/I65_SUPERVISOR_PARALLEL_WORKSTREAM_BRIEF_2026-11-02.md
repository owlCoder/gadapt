# I65 — ready-to-review supervisor decision brief (UNSIGNED)

**Prepared:** 2026-11-02. **Repository:** owlCoder/gadapt. **Audience:** doctoral supervisor and separate methods/power-systems/statistics reviewers.  
**Status:** DECISION REQUEST, **NOT APPROVAL**. No mentor was contacted or signatures obtained by generating this document. No new optimization experiment or COCO evaluation was performed.

## Executive decision — request a reply on one page

The research now has a documented body of **bounded and reproducible engineering/empirical evidence**, including negative findings. It does **not** have a demonstrated original optimization algorithm or established independent field-data validation. The supervisor must decide which route is doctorate-sufficient **before** a new algorithm or confirmation protocol proceeds.

**A. Restricted empirical dissertation.** Scope: actual objective-call efficiency versus strong baselines, changed rankings under transformations, ORPD feasibility/tail risk and negative/STOP outcomes. Claim: a context-specific empirical characterization, **not** a new algorithm, universal superiority or industrial deployment certificate. Existing research [I64-S0](ITERATION64_S0_REPORT_SR.md), [I64-E](ITERATION64_E_REPORT_SR.md), [I64-R](ITERATION64_R_REPORT_SR.md), [I64-I/I2](ITERATION64_I_REPORT_SR.md), [I64-I2](ITERATION64_I2_REPORT_SR.md), [EVIDENCE_SYNTHESIS](EVIDENCE_SYNTHESIS.md) should be audited at manuscript level rather than selectively quoted.

**B. Applied evaluation-integrity paper.** Scope: actual-vs-wrapper objective call budgets, terminal witnesses, audit detector false positives, source lineage and separate numerical AC solver reconstruction. Publish only carefully differentiated reproducibility results; error classes themselves and classical Newton/ECDF/portfolio methods are known prior art. Sources include [I49–I55](EVIDENCE_SYNTHESIS.md), [I65 scope crosswalk](I65_M1_M6_EVIDENCE_AND_PRIOR_ART_CROSSWALK_2026-11-02.md) and [new prior-art challenge](I65_PARALLEL_PRIOR_ART_REVIEW_2026-11-02.md). The original I50 non-specific detector and other negatives **must** be disclosed.

**C. New original optimizer method.** **NO-GO** until a mathematically distinct proposal, targeted prior-art review, falsifiable mechanism and independently approved protocol exist. The current stagnation-triggered GAdapt→CMA switching candidate has no proven novelty.

**D. Defer / request independent review.** This is an acceptable disposition if the contribution standard, external-model requirements or statistics cannot be defended.

## Four parallel review packages (completed as documentary work)

| Workstream | Deliverable / question | Result that is supportable now | Blocker before scientific GO |
|---|---|---|---|
| **A — originality and literature** | [Prior-art review](I65_PARALLEL_PRIOR_ART_REVIEW_2026-11-02.md) | IPOP/BIPOP, COCO ECDF, EAF and standard reproducibility precedents confirmed from publisher/official sites; existing switch not novel on present evidence | M6/C1 reviewer must identify the exact defensible contribution and venue. Crossref API still inaccessible/unverified. |
| **B — data and independent model** | [External-case screening](I65_INDEPENDENT_MODEL_DATA_SCREEN_2026-11-02.md) | Separate PGLib-OPF and UW archival sources identified, their different model/format roles delineated; independent numerical solver on one case already verified | M3/C4 chooses data-independence level and actual permissible external case. No field data supplied, no new case admitted/run. |
| **C — physical/numerical budget** | [Cost-ledger review](I65_RESOURCE_ACCOUNTING_REVIEW_DRAFT_2026-11-02.md) | Objective, PF API, OPF API, internal Newton residuals, setup, interstage and terminal witness counted as distinct objects | M2/M3/C2/C3 selects primary resource, concurrency and failure rules, independent nested-call completeness review |
| **D — COCO and statistics** | [Six-contrast review](I65_COCO_ORACLE_SIX_CONTRAST_REVIEW_DRAFT_2026-11-02.md) | Official f21/f24 suite syntax checked via documentation, all K1–K6 contrasts and additive-offset normalizer risk explicitly specified | M4 runtime/f_opt oracle NOT_RUN; M5 six-contrast inference and M6/C6 full protocol NOT_FROZEN; requires signatures before any holdout |

## Requested formal reviewer decision form — blank until answered

| Choice | Options | Decision / reviewer / date |
|---|---|---|
| Doctorate-sufficient scope | A / B / A+B / C after new theory / D | **UNDECIDED** |
| Exact contribution claim (one sentence) and target venue | Write claim, strongest predecessor and required differentiator | **UNDECIDED** |
| Required grid evidence | L1 numerical software / L2 separate case / L3 independent physical model / L4 observed field data | **UNDECIDED** |
| Admissible dataset and copyright permissions | Source/version/license/owner/reviewer, or not applicable | **UNDECIDED** |
| Primary comparable resource | Objective attempts / vector OPF-PF ceilings / calibrated compute / other | **UNDECIDED** |
| Setup/interstage/final verification budget | Explicit inclusion, failures, parallel entries | **UNDECIDED** |
| COCO oracle | Official `bbob` instance versions, reliable independently witnessed f_opt, M4 approval | **NOT_RUN / UNDECIDED** |
| Six simultaneous contrasts/statistics | K1–K6, instance/seed nesting, margins, failure policy, M5 reviewer | **NOT_FROZEN** |
| Permission to build candidate C | Yes only with independently established novelty / No | **NO CURRENT APPROVAL** |
| Permission to run held-out COCO | Require dated signed freeze manifest / No | **NO CURRENT APPROVAL** |

**Human sign-off:** reviewer name _______   role _______   date _______   signature/reference _______.  
**Disposition:** [ ] APPROVE_SCOPED_EMPIRICAL  [ ] REQUEST_CHANGES  [ ] REQUIRE_NEW_METHOD  [ ] NO_GO.  
**Restrictions/comments:** ________________________________________.

## Source-grounded meeting agenda (25 minutes, proposed)

1. **5 minutes — what is reliable:** full-clone Python 3.12 regression M1 technical PASS, separate Newton/dispatch software replication M3 narrow PASS, source/model hash chain and preserved negative reactive result. No production certification.
2. **8 minutes — scientific contribution:** examine existing I64 empirical evidence (including DE better final medians in 14/21 original cells, strong IPOP/BIPOP transformed comparison, ORPD negative outcomes) and detector specificity limitations. Decide A/B/C.
3. **5 minutes — data/model and resource fairness:** choose L1–L4 and primary counted resources. Existing fixed case30/j1 has VG=6, TAP=0, BS=2; do not infer tapped-transformer optimization from it.
4. **5 minutes — protocol:** official COCO f_opt question, corrected shift-invariant scale, six familywise contrasts and only three held-out instances per f/d. Decide whether any new confirmatory protocol can eventually be frozen.
5. **2 minutes — sign/date:** record named responsible reviewers, outstanding proof/data requests and explicit STOP/GO outcome.

## Ready-to-send supervisor message (NOT SENT)

**Subject:** GAdapt doctorate: decision required on empirical contribution and I65 protocol

Dear Professor,

I have consolidated the verified GAdapt replication and independent numerical AC-check evidence together with the documented negative and STOP results. The current work supports a bounded empirical characterization and evaluation-integrity study; it does not establish a novel optimizer or independent measured network model.

Could we decide whether an empirical/evaluation-integrity dissertation is acceptable, or whether an original mathematical optimization method is essential? The attached decision brief lists the exact M1–M6 gates, remaining data/model independence questions, the OPF/PF/witness cost-accounting choices, and the still-unfrozen six-contrast COCO/statistical protocol. No held-out COCO runs or new optimizer experiments have been performed.

I would appreciate a written scope decision and the reviewer assignments/conditions for any remaining technical work. Until then, the research protocol remains NO-FREEZE and candidate-C novelty remains unestablished.

Kind regards,

[Student]

---

**Important:** This text is prepared for forwarding. It has **not** been sent and does not stand in for mentor approval. The historical GAdapt sources and all frozen outcomes remain unchanged.

## Focused contribution choice and two manuscript-ready archival outlines (2026-11-02; UNSIGNED)

The [research route decision and prior-art challenge](I65_RESEARCH_RESOLUTION_RECOMMENDATION_2026-11-02.md) places [evaluation-integrity paper v0](I65_EVALUATION_INTEGRITY_MANUSCRIPT_DRAFT_2026-11-02.md) **first** and [context-dependent GAdapt results paper v0](I65_CONTEXT_DEPENDENT_GADAPT_MANUSCRIPT_DRAFT_2026-11-02.md) second. Their novelty is **NOT ESTABLISHED**: Ravber et al. (2025) compared implementations in 13 frameworks, SIMPROV (2025) addressed heterogeneous simulation provenance, and Variable Cost Runtime Analysis (2025) already established a theory of variable evaluation cost. The potentially defensible specific contribution is independently falsified **evaluation-call and returned-best integrity** transferred from synthetic functions to AC simulation while preserving false-positive and failed-replay findings.

**Decision demanded:** explicitly accept or reject a doctorate based on a rigorous, negative-aware empirical/integrity contribution without a new optimizer. If institutionally insufficient, state the missing mathematical theorem/method and originality bar before any candidate C implementation. The drafts were prepared but **not submitted, emailed, signed, peer reviewed or based on new experiments**.

## Artifact-backed independent publication check — 2026-11-02 (still UNSIGNED)

The two papers now include source-verification addenda from a six-file original I49/I50/I52/I55 audit. Its [machine-readable source-blob ledger](I65_ARCHIVED_CLAIM_RECHECK_2026-11-02.json) confirms the reported `4/9, 11/12, 4/12 POST_HOC, 2/12, 19/21` counts and I55 emukit mismatch. An [independent 95% Clopper–Pearson arithmetic check](I65_CP_INTERVAL_INDEPENDENT_RECHECK_2026-11-02.json) matched **all five original intervals**, max error `1.55e-15`. Read the [detailed manuscript-falsification audit](I65_ARCHIVAL_MANUSCRIPT_FALSIFICATION_REVIEW_2026-11-02.md).

The critical corrections are: I52's post hoc complete-only `17/18`, missingness bounds `17..20/21` **do not overturn the original preregistered >=17/21 success**, but prevent generalizing the exact 19/21 ratio; I49's original JSON has **33 nonstandard Infinity tokens**, disclosed without changing it; and S0's original final medians are measured at **original algorithm stopping** while ECDF A is measured through 12,000 physical calls. **No scientific novelty was inferred, no new optimizer experiment was executed, and no supervisor signature was received.**

**Reviewer request unchanged:** decide if the bounded evaluation-integrity and context-dependent GAdapt manuscripts satisfy the actual doctoral originality requirement, whether a further raw NPZ/bootstrap reanalysis is needed, and who will independently adjudicate detector specificity. Until this decision, `M6/C1 PENDING`, `NO-FREEZE`, `COCO NOT_RUN`.
