# I65 research direction — decision record and independent prior-art checkpoint

**Date:** 2026-11-01. **Outcome:** **GO for evidence-based consolidation, targeted independent review and instrumentation feasibility; NO-GO for a novel-algorithm claim, NO-FREEZE and no confirmatory run.**

This is a research **decision memo**, not a new optimizer, frozen preregistration, runtime integration or statistical reanalysis. [Repository rules](../AGENTS.md) and the [handoff](PHD_PROGRESS.md) govern further steps. No held-out COCO f21/f24 data have been used.

## 1. What question remains scientifically valuable?

> At a strict physical-evaluation budget, how do GAdapt's target-reaching efficiency, final quality, variance/tail risk, and feasibility change with orthogonal coupling and discrete simulator constraints, **and how much of an apparent result depends on the reliability of evaluation logging and witness validation**?

The question is *empirical and methodological*. The prior program already provides partial evidence on classical functions (I64) and ORPD (I56–I64). The only supported continuation now is an **independent provenance/measurement and thesis-scope review**, not another heuristic tweak.

### Strong existing evidence

- [S0](ITERATION64_S0_REPORT_SR.md): limited early efficiency under original mentor settings; DE wins final cell median in 14/21 cases.
- [E](ITERATION64_E_REPORT_SR.md), [R](ITERATION64_R_REPORT_SR.md): strong CMA-family baselines and sensitivity to Q; matched shift controls an important confound, but does not identify the causal mutation mechanism.
- [E3](ITERATION64_E3_REPORT_SR.md), [A](ITERATION64_A_REPORT_SR.md), [I2](ITERATION64_I2_REPORT_SR.md): the first GAdapt stage can matter in one fixed hybrid while hybrid superiority on ORPD remains unsupported.
- [I49–I55](EVIDENCE_SYNTHESIS.md): evaluation-accounting instrumentation offers practical reproducibility evidence, but known individual findings and I50's nonspecific detector limit novelty claims.

## 2. Closest external prior art and precise differences

| Work | Established result | Consequence for GAdapt proposal |
|---|---|---|
| Hansen et al., *COCO: Performance Assessment* (2016), arXiv:1605.03560, https://numbbo.github.io/coco-doc/perf-assessment/ | Budget measured in actual objective calls, target-based runtimes, ECDFs, simulated restarts and target attainment | Physical-call-based ECDF/AUC is **established practice**, not a new method; disclose whether GAdapt's hand-tuned normalization departs from COCO |
| *Using the Empirical Attainment Function for Analyzing Single-Objective Black-Box Optimization Algorithms*, DOI `10.1109/TEVC.2024.3462758`, https://doi.org/10.1109/TEVC.2024.3462758 | EAF compared with target-based ECDF; target choice and alternative anytime metrics studied | Do not claim novelty from ECDF area or an EAF summary; EAF may be an **independent secondary diagnostic** only, prespecified before viewing new results |
| *Benchmarking footprints of continuous black-box optimization algorithms* (2025), DOI `10.1016/j.swevo.2025.101895`, https://doi.org/10.1016/j.swevo.2025.101895 | Links algorithm success/failure to landscape features and algorithm footprints | Landscape-based selection or explanations of algorithm complementarity are existing ideas; no original GAdapt selector is established |
| *A methodology for comparing optimization algorithms for auto-tuning* (2024), DOI `10.1016/j.future.2024.05.021`, https://doi.org/10.1016/j.future.2024.05.021 | Explicit methodological framework for algorithm comparisons, stopping, baselines and runtime accounting | A benchmark-reporting protocol alone is **not** an unclaimed scientific method |
| [I65 prior-art audit](ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md) | IPOP, BIPOP, restart on stagnation, portfolios, memetic switching are preexisting | Candidate C (GAdapt on stagnation → CMA) is an engineering variant, **not** established novel theory |

Publisher/project documentation supports the four externally listed papers; direct Crossref-API verification was **not** performed in this memo. External sources are used to challenge claims, not to silently reinterpret historical study results. Full novelty vetting must use the repository's [literature-auditor rules](../.agents/skills/literature-auditor/SKILL.md).

## 3. Mathematical feasibility check: what is demonstrably true, and not novel?

Let `n` be sequential actual objective attempts, `B` the budget, and `limit≤B`. If the evaluator checks `n<limit`, reserves the next attempt by `n←n+1` **before** calling the objective, and never allows other unaccounted calls, induction proves `0≤n≤B` and no invocation past the Bth reservation. This is a basic **instrumentation safety invariant**, *not* a novel optimization theorem. It does not apply automatically to parallel/vectorized evaluations or a Python objective that invokes multiple physical solvers.

An important invariance issue in the [I65 DRAFT](ITERATION65_DRAFT_PROTOCOL_SR.md): its significant-improvement test is

`f_old−f_new > eps_abs + eps_rel·max(1,|f_old|)`.

Under an arbitrary objective offset `f→f+c`, the improvement `f_old−f_new` is unchanged, but the relative threshold can change for `eps_rel>0`. Thus this detector is **not shift-invariant** in raw f units when its relative tolerance is enabled. Its development candidate `eps_rel=0` avoids this specific additive-offset problem but still uses an *absolute cost-unit-dependent* `eps_abs`. This is a straightforward check of assumptions, **not** a proposed original algorithm.

## 4. Falsifiable next gates without confirmation runs

1. **Provenance/compatibility:** independently check the original Git blobs and 341 migrated paths, restore old aliases in a real clone, and execute only inexpensive I41/I63/I64 research unit tests. A complete-clone regression result must be recorded `PASS` or `NOT_TESTED`; existing sandbox tests cannot stand in for it.
2. **Instrument integration:** require verified GAdapt complete-generation boundary, SciPy callback accounting, pycma ask/tell accounting, independent final witness within B, B−1/B/B+1 and exception/mutable input handling. *Any* uncounted physical attempt or hidden B+1 blocks FREEZE. No need to invent a new optimizer to review these interfaces.
3. **Oracle feasibility:** independently verify COCO suite IDs f21/f24, native bounds, optimum access for normalized-gap analysis, held-out separation, and all physical setup costs. If a trusted oracle cannot be established, do not improvise an optimum or claim validated target gap.
4. **Statistics and sample limits:** disclose that three held-out instances and 30 seeds per cell provide weak rare-failure/generalization evidence. Keep instance-level and seed-level uncertainty distinct. Expand the four-contrast family to include both reach-rate noninferiority contrasts **before any freeze** if candidate C were ever authorized.
5. **Research-scope gate:** supervisor/independent reviewer must say whether a **rigorous empirical characterization and evaluation-integrity toolkit** meet the dissertation's originality requirement. If a new algorithm is required, the current candidate fails the novelty gate; do **not** implement or run it merely to try to obtain a positive outcome.

## 5. Strong baselines, resources and decision rule

- **Baselines for any future independently approved f21/f24 protocol:** GAdapt-M, SciPy DE, CMA-ES, IPOP, BIPOP and the archived E3 fixed hybrid. The I65 draft further proposes A/B/C, but implementation remains blocked under AGENTS until an explicit novelty/scope decision.
- **Unchanged prospective ceiling in the DRAFT:** 18 primary cells × nine methods × 30 seeds = 4,860 runs, up to 58.32 million physical attempts; 12 controls × nine methods × 15 seeds = 1,620 runs, up to 19.44 million attempts. Proposed 120 CPU-hour hard cap, **not a tested feasibility estimate**. Such a run is **not authorized by this memo**.
- **GO:** documentary consolidation, provenance audit, targeted methods review and low-cost adapter validity tests on *development-only* instances after explicit permission.
- **NO-GO:** claim of an original stagnation-switch optimizer or broad industrial algorithm recommendation.
- **NO-FREEZE / NOT_RUN:** all held-out f21/f24 confirmation remains at zero runs. If model feasibility, statistics or novelty requirements fail, report `NOT_SOLVED` / `UNDECIDED` as appropriate rather than retune.

## 6. Preferred dissertation/publication route

**Priority 1:** independently review and improve the **evaluation-integrity tool** and publish a carefully scoped, reproducible account of discovered documented/known failure modes, with specificity validation (I50) and AC-transfer evidence (I52). Do not assert a new detector theorem unless proved.

**Priority 2:** prepare a manuscript on **context-dependent GAdapt comparison** using S0/E/R/A/I/I2 with a transparent hierarchy of original versus transformed functions and synthetic versus ORPD evidence. Report negative operator experiments (E2/E4/C), calibration STOPs (I59/I61/I63) and limitations rather than omit them.

**Decision needed before new optimizer work:** independent scope and novelty review. The immediate next deliverable should be an **English supervisor decision package**, not an unapproved candidate-C benchmark.
