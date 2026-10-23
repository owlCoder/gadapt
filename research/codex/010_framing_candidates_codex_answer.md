**I recommend one bounded GO: a validated protocol for causal diagnosis.** The testing and measurement candidates fit the thesis, but their straightforward formulations do not clear the originality gate. None currently warrants an unconditional novelty claim.

Probabilities below are subjective estimates of obtaining a defensible **original methodological contribution**, conditional on the proposed work succeeding. They are separate from statistical power. This assessment used repository evidence and web searches; nothing was changed or executed experimentally. Where not established, DOI is marked **UNVERIFIED**.

**1. Validated oracle interventions with explicit limits on causal attribution**

**Research question.** Can interventions reliably distinguish mechanisms responsible for an optimizer’s performance deficit—and identify when the evidence is insufficient?

**Closest prior art.** Fawcett–Hoos already explain gains between configurations through ablation, DOI **10.1007/s10732-014-9275-9**. [Their paper](https://www.cs.ubc.ca/~hoos/Publ/FawHoo13.pdf) directly blocks novelty based on “explaining a performance gap.” [fANOVA](https://proceedings.mlr.press/v32/hutter14.html) partitions performance variation among parameters and interactions; DOI **UNVERIFIED**. Bezerra–López-Ibáñez–Stützle provide modular algorithm construction and comparison, DOI **10.1109/TEVC.2015.2474158**. [Accepted manuscript](https://pure.manchester.ac.uk/ws/portalfiles/portal/40316480/BezLopStu2015tec.pdf). [IOHxplainer](https://arxiv.org/html/2401.17842v2) already combines modular experiments and explainable performance analysis; DOI **UNVERIFIED**. Counterfactual component interventions also exist in [causal mediation analysis for neural models](https://papers.neurips.cc/paper_files/paper/2020/hash/92650b2e92217715fe312e6fa7b90d82-Abstract.html); DOI **UNVERIFIED**.

**Exact remaining difference.** A protocol whose *diagnostic accuracy is validated against deliberately planted mechanisms*, incorporating:

- factorial interventions and interaction estimates;
- independently generated, frozen references and reference-sensitivity checks;
- manipulation checks establishing what each oracle actually changes;
- an explicit “inconclusive” result for ineffective interventions, unstable reference gaps or incompatible mechanisms.

Neither factorial design nor closure \(C\) is independently novel. Use factorial contrasts of expected outcomes for primary inference; retain I53’s median-based \(C\) as a descriptive normalization. Do not force component contributions to sum to the cross-optimizer gap.

**Falsifiable hypothesis.** On blinded, held-out planted-mechanism cases, the protocol identifies the manipulated mechanism set in at least 90% of identifiable cases, falsely attributes mechanisms in at most 5% of sham cases, and returns inconclusive when the reference gap is negligible. Compare against ordinary ablation under equal experimental budgets.

**Head start.** [I53](research/ITERATION53_REPORT_SR.md) supplies working interventions, synthetic controls, frozen references and strict evaluation accounting. Its negative result is especially useful: failure of this scalar oracle does **not** exonerate step-size control generally. I47–I48 provide contrasting problem regimes.

**Minimal experiment/budget.** Two optimizer implementations × four planted regimes—scale, reset, joint, sham—× five arms, including a clean comparator × 30 seeds × 3,000 evaluations: **3.6 million cheap evaluations**. Allow **five person-days** for specification and implementation. Advance to infrastructure validation only if diagnosis outperforms ordinary ablation without increasing false attribution.

**Gate: GO for this bounded validation screen; probability ~40%.** A general decomposition of the “true causes” of an arbitrary optimizer gap remains NO-GO. The plausible contribution is validated, explicitly limited diagnosis.

**2. Contract-conditioned optimizer testing with finite detection guarantees**

**Research question.** Can a library audit provide a meaningful detection guarantee while distinguishing contract violations from legitimate algorithm behavior?

**Closest prior art.** [Yoo (2010)](https://coinse.github.io/publications/pdfs/Yoo2010vn.pdf) already applies statistical metamorphic testing to stochastic optimization, evaluates mutants and discusses false positives and instance difficulty; DOI **UNVERIFIED**. [Rounds–Kanewala (2018)](https://arxiv.org/abs/1808.01033) identify 17 GA relations and modify relations with excessive failure rates; DOI **UNVERIFIED**. Most decisively, [Duque-Torres et al. (2025)](https://www.sciencedirect.com/science/article/pii/S0950584925001466), DOI **10.1016/j.infsof.2025.107807**, already combine relation applicability, mutation testing and sensitivity to the amount of test data.

**Exact remaining difference.** Formal, phase-aware predicates tied to explicitly declared contracts, with three outcomes: violation, no violation detected, or inapplicable/unknown. Validation must include legitimate counterexamples—corner initialization, documented population budget overshoot, non-best-returning APIs—not merely faulty mutants.

Sampling guarantees alone add little novelty. Under independent trials and per-trial detection probability \(p\ge p_{\min}\),

\[
P(\text{miss})\le(1-p_{\min})^n.
\]

For eight classes, \(p_{\min}=0.1\), **49 trials per class** bound the probability of missing any class by 0.05 using a union bound. This assumes the detection probabilities; it does not establish them. Holm correction controls statistical false alarms only when the underlying tests and relations are valid.

**Falsifiable hypothesis.** On held-out faults and legal implementations, contract conditioning reduces false accusations relative to the existing classifier without reducing detection of genuine violations.

**Head start.** I49–I52 provide real failure mechanisms, adapters and planted faults. I50’s C1 failure supplies an unusually valuable negative control. However, [review #009](research/codex/009_manuscript_review_codex_answer.md) identifies prerequisites: missing reconstructable traces and the hash-seed intervention error. The drivers still use `-I`, which [ignores `PYTHON*` variables](https://docs.python.org/3/using/cmdline.html#cmdoption-I).

**Minimal experiment/budget.** Eight classes × two faults and two legal controls × 49 trials × 200 evaluations × up to four executions: **≤1.26 million cheap calls**, approximately **five person-days**, including launch correction and trace retention.

**Gate: NO-GO as currently specified; probability ~20%.** Valuable audit development, but contracts plus standard sampling and multiplicity control do not yet establish a new method.

**3. A certificate limiting what penalized-score rankings imply**

**Research question.** Over which penalty weights and feasibility tolerances does a score-based comparison support an operational conclusion?

**Closest prior art.** Deb already separates feasibility from objective quality and explains penalty-selection difficulties, DOI **10.1016/S0045-7825(99)00389-8**. [Paper](https://repository.ias.ac.in/9407/1/310.pdf). [COCO’s constrained suite](https://numbbo.github.io/coco-doc/bbob-constrained/functions.pdf) explicitly addresses joint objective/constraint assessment and feasible-point runtime measures; DOI for that suite document **UNVERIFIED**. Thus, “penalties can mislead; report feasibility” is established.

**Exact remaining difference.** A reproducible certificate reporting regions of penalty weights and tolerances where a ranking persists, alongside disagreement with feasible-solution attainment. For fixed candidate points, \(S=f+w^\top v\) gives ranking boundaries through linear inequalities—standard mathematics. Originality would require something beyond plotting these regions, such as validated uncertainty-aware certification of operational decisions.

**Falsifiable hypothesis.** On fresh infrastructure cases, score rankings remain unchanged across a prespecified weight range while feasible-attainment probabilities differ by at least 0.5 in at least two of three cases.

**Head start.** I53 case118 gives G0 **2/12** versus ORN **12/12** runs that *found* a feasible point, while CMA retains the better penalized score. That is disagreement in conclusions, not a demonstrated rank reversal. The archive distinguishes best score and best feasible cost, but lacks complete trajectories; finding feasibility also differs from returning a feasible solution.

**Minimal experiment/budget.** Three methods × three cases × 30 fresh seeds × 3,000 evaluations: **810,000 `runpf` calls**, approximately **three person-days**. Archive costs, violations and returned points; rescore frozen traces offline. Such rescoring does not predict search under changed penalties.

**Gate: NO-GO as a standalone original method; probability ~10%.** Strong measurement-validity material for the thesis, with insufficient methodological separation from established constrained benchmarking.
---
**Lead verification (Claude, 2026-10-23 20:55):** DOIs checked on Crossref: 10.1007/s10732-014-9275-9 (Fawcett, Hoos),
10.1109/TEVC.2015.2474158 (Bezerra, López-Ibáñez, Stützle), 10.1016/S0045-7825(99)00389-8 (Deb); IOHxplainer
arXiv:2401.17842 confirmed on arxiv.org; 10.1016/j.infsof.2025.107807 verified earlier. Candidate 1 (validated
oracle-intervention diagnosis) sent to an independent adversarial prior-art audit (literature-auditor) before any
GO; candidates 2 and 3 NO-GO as standalone methods (kept as thesis material).
