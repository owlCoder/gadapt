# I65 — M6/C1 supervisor decision package (evidence and explicit choices)

**Date:** 2026-11-03. **Status:** DRAFT FOR HUMAN REVIEW; UNSIGNED. **Research control state:** `NO-FREEZE`; held-out COCO `NOT_RUN`; originality `NOT_ESTABLISHED`; two manuscripts DRAFT and not submitted. No new optimizer, power-flow or physical experiments are authorized by this memo. This document deliberately distinguishes original registered decisions from post-hoc analyses.

## The decision to be made

**M6/C1 research scope:** Is a dissertation centered on *reproducible measurement integrity and context-bounded empirical characterization* (rather than a novel genetic-optimizer operator or restart policy) a sufficiently original, defensible contribution if backed by independent review, detector-specificity validation and explicit negative results? The answer is **not established** by the present evidence and must be recorded by a human reviewer.

**Requested outcomes (select one, date and sign):**

- **A — Conditional permission for external technical review of drafts.** Accept the *type* of proposed contribution for further originality scrutiny, subject to independent literature/detector-validity review and source-replay disclosure. This is **not** publication permission, novelty confirmation, experimental pre-registration or a freeze.
- **B — Current scope insufficient; distinct algorithmic/theoretical novelty required.** Existing fixed GAdapt→CMA switching, CMA restarts, physical-call accounting, ECDF/CVaR and provenance tracking are not new merely because implemented together. Maintain `NO-GO` on candidate-C implementation or a held-out benchmark until a *separate*, prior-art-distinct, falsifiable method and protocol are approved.
- **C — A prospective external-validity study is required before manuscript review.** Specify new function-family/Q draws or independent infrastructure systems and a statistical plan *before* seeing new outcomes. Require independent feasibility and budget review. This memo contains **no authorization to execute** such a study.

**Reviewer response:** Decision [A / B / C / Other: ______]; conditions ______; reviewer ______; date ______; signature ______. An unfilled response is **PENDING**, not implicit approval.

## Evidentiary ledger and what each result does NOT show

| Study / evidence | Verified quantitative claim | Scope restriction / missing evidence |
|---|---|---|
| I49–I50 evaluation integrity | I50 original non-specific C1-inclusive `11/12` result; excluding C1 post hoc `4/12`, and distinct documentation contradictions `2/12` | C1 is non-specific on corner/plateau search points; neither overall prevalence nor diagnostic sensitivity/specificity against independently adjudicated bugs is known |
| I52 transfer to AC dispatch | Frozen H52 **SUPPORTED**, library-status match `19/21`; descriptive Cohen κ `83/104 = 0.7981`; only `7/10` exact synthetic library/class findings recur (`7/11` Jaccard across both domains) | A binary match is not identity of defect mechanism; the archival complete-case match is `17/18`, and permissible missing-cell status bounds are `17..20/21`; library selection is not random |
| I55 controlled hash-seed study | H55a–c **SUPPORTED** and H55d **NOT SUPPORTED**; of 620 valid cells, `585` unchanged in A/A′ and A/B, `30` SMAC cells differ only with changed hash seed, `5` Nevergrad plateau-10D cells differ even at the same hash seed | All 620 saved A trace hashes are distinct *within their respective library* across 5 archived seeds per function/dimension, but uniqueness is **not** independence, mechanism, statistical significance or optimizer quality; only original A-process NPZ traces are archived. The original raw 620-NPZ decoder/flag replay remains **NOT_RUN** |
| I50↔I55 comparison | `318/358` full sequence digests agree; `357/358` binary C/R flag presence agrees. A single emukit plateau-2D seed-6001 C2 flag changes, while the C1 count differs without changing presence | Bitwise identity, exact flag-count identity, Boolean flag identity and attribution to thread settings are different evidence levels; earlier emukit VECLIB test was post hoc |
| I64 original / strong baselines | S0 GAdapt ECDF `0.698` vs DE `0.651` under mentor setup, but DE wins final median `14/21`; in E, GAdapt ECDF `0.6732` vs IPOP `0.7699` | S0 and E differ in configurations and conditions; aggregate early efficiency is not universal final accuracy or a novel GAdapt algorithm |
| I64-R matched orthogonal Q | Original fixed-21 contrast c4 `+0.07079178`, simultaneous 95% seed-only CI `[+0.05981187,+0.08177169]`; original H64r3 **SUPPORTED** | Post hoc delete-Rastrigin c4 `+0.04086609` has no inferential replacement interval; nine fixed function families and one Q each do not license population-level generalization. Original 4,200-run R archive was kept **off Git**, so the original R bootstrap is not independently repeated |
| I64-I2 paired ORPD tail | Original H64h2 **OPPOSITE**, IPOP-minus-hybrid CVaR `−0.12530676`, simultaneous 95% CI `[−0.25022391,−0.00038962]`; original 20,000-bootstrap replay matched 13/13 historical quantities | About 99.755% of the signed eight-cell contrast comes from selected `case39/j=3` (three hybrid non-feasible runs). Post hoc removing that cell gives `[−0.00130619,+0.00060502]`, not a replacement decision; post hoc single-cell McNemar two-sided p=`0.25` tests **binary feasibility**, not the registered CVaR effect |

**Cross-cutting limit:** none of these findings proves priority over prior art, a novel optimizer theorem, general industrial safety, independent physical-model replication, or performance on held-out COCO functions. `witness_checked` in a historical record is not a newly verified electrical witness.

## Proposed publication scope for independent review

**Draft paper 1 — Evaluation-integrity instrumentation and reproducibility across Python optimizers.** The defensible contribution is a *reproducible, qualified audit* documenting specific source-verified behaviors, cross-domain class persistence and the limits of naive detectors. Compare against known cross-framework auditing / provenance literature cited in [Research Decision](../../RESEARCH_DECISION_2026-11-01.md), not a claim to have invented trace logging, D3x, source hashing or an error detector. Require a blinded/independent ground-truth set or clearly label specificity `NOT_ESTABLISHED`.

**Draft paper 2 — Conditional GAdapt performance under transformations and discrete AC constraints.** Present S0/E/R/E3/A/I/I2 as distinct frozen designs; include the *negative* stronger-CMA, hybrid-transfer and feasibility results; report post-hoc family/cell sensitivity adjacent to original intervals. Do not claim a novel switch policy or deployment-ready ORPD reliability.

## Specific missing items and evidence-dependent next steps

1. **I55 raw A-trace evidence:** The original Git commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08` contains all 620 expected valid NPZ files (12,319,037 compressed bytes) with unchanged Git identities. The four-stage source→bytes→SHA-256/flags verifier and manual-only workflow exist; as of this memo, **full numerical 620-trace replay is still NOT_RUN**. It requires the full Git clone or a *manual* GitHub Actions dispatch; never describe a unit-test PASS as a 620-NPZ PASS. A′/B arrays were not archived in those NPZ files.
2. **I64-R source recovery:** Locate the original approximately 8 MB `research/results/iteration64_r/run.json.gz` on the original experimental machine; historical notes give only shortened SHA-256 `f23046f6…3618`. Require a separate trusted complete digest and pass the read-only gate before any R seed-level replay; do not synthesize missing runs.
3. **Methods/novelty review:** Independent M5 statistics assessment of seed-only/fixed-cell intervals, post-hoc selection bias and rare-event evidence; M6/C1 originality decision against the concrete prior-art literature; M3 independent ORPD witness/model review if external validity is claimed.
4. **No opportunistic experiments:** A new optimizer or prospective COCO evaluation requires a different mathematical contribution or protocol, explicitly frozen seeds/metrics, controls, baselines (DE/CMA/IPOP/BIPOP), budget and human sign-off. Until then `NO-GO`.

## Source register

- Original frozen conclusions and current status: [Evidence Synthesis](../../EVIDENCE_SYNTHESIS.md), [Research Decision](../../RESEARCH_DECISION_2026-11-01.md), [PHD Progress](../../PHD_PROGRESS.md).
- Verified I55 data/source gate: [full NPZ attestation note](I65_I55_ORIGINAL_620_NPZ_END_TO_END_ATTESTATION_GATE_2026-11-03.md); [control-conditioned I55 review](I65_I55_CONTROL_CONDITIONED_HASH_SEED_REVIEW_2026-11-03.md).
- I52 [class-transfer review](I65_I52_CHANCE_CORRECTED_AND_CLASS_TRANSFER_REVIEW_2026-11-03.md); I64-I2 [exact bootstrap and selected-dropout audit](I65_I64_I2_EXACT_BOOTSTRAP_AND_POSTHOC_AUDIT_2026-11-03.md); I64-R [off-Git source and family-stress audit](I65_I64_R_OFFGIT_SOURCE_AND_FUNCTION_FAMILY_STRESS_2026-11-03.md).
- Drafts to be reviewed: [evaluation integrity](../../I65_EVALUATION_INTEGRITY_MANUSCRIPT_DRAFT_2026-11-02.md) and [contextual GAdapt](../../I65_CONTEXT_DEPENDENT_GADAPT_MANUSCRIPT_DRAFT_2026-11-02.md).

**Do not construe this memo as approval, source replay or completion of any pending gate.**
