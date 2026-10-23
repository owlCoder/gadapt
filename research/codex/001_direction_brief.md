# Brief for Codex (independent co-researcher, read-only) — 2026-10-23

You are an independent co-researcher on a PhD project about the GAdapt library (this repository, Python, `gadapt/`).
You are READ-ONLY: do not edit files, do not commit. Your answer is archived verbatim by the lead (Claude).
Write in English. Be blunt; negative conclusions are welcome.

## Objective (from CLAUDE.md, binding)
A defensible ORIGINAL methodological contribution to GAdapt for infrastructure optimization (continuous domain:
economic dispatch / OPF on IEEE/MATPOWER systems). Novelty must be established against prior art BEFORE implementation.
Never claim originality from implementation alone. Never invent citations: give a DOI only if you are sure; mark
anything uncertain as UNVERIFIED (the lead verifies every DOI on Crossref).

## What is already established (read the reports if you need detail)
- research/ITERATION43..48_REPORT_SR.md (Serbian), research/DIAGNOSTIC_STUDY_DRAFT_SR.md:
  * GAdapt's deficit is GAdapt-specific (textbook GA better 5/6, (1+1)-EA better 6/6 on binary route choice, I45);
    no single component is causal (I46 ablation); exploratory: GAdapt does not intensify near the best solution.
  * Continuous AC economic dispatch (5 MATPOWER cases, I47): CMA-ES is 3–5 orders of magnitude better than GAdapt at
    equal budget. Multimodal valve-point dispatch (I48): IPOP-CMA-ES better 2/3 but only 1.3–1.5x; GAdapt beats DE 2/3.
  * Columnar diversity on log((v-min)+1) is not unit/position invariant; opt-in `linear` metric is exactly invariant
    but gave no dispatch gain (I47, B1 0/5).
  * Opt-in `normal_distribution_mutation_min_std_dev_decay_generations`: ~1.8 orders lower median gap for ~20% more evals.
- Directions already rejected (do NOT re-propose without a genuinely new mathematical difference):
  * Adaptive operator selection / bandit credit / scenario-feasibility credit / censored per-call credit (I26–I36):
    prior art (Fialho 2008, Maturana 2010) and not confirmed on fresh seeds.
  * Cost-aware early-reject scenario screening (I29–I31): not new.
  * Partition crossover over the variable interaction graph (H1, research/H1_PRIOR_ART_AUDIT_SR.md, I42): NO-GO.
  * Diversity-triggered hand-off GA -> CMA-ES/(1+1)-ES local intensifier with sigma0 from population dispersion
    (H3, research/H3_PRIOR_ART_AUDIT_SR.md): NO-GO, covered by EMDE 2008, MA-LS-Chains 2010, HSES 2018.
  * MILP certificate for capacity planning (I41): special case of known results.

## GAdapt mechanism (verify in code)
- Default: population_mutation = "cost_diversity,variable_columnar_diversity,parent_diversity";
  decision_variable_mutation = "variable_columnar_diversity,random"; crossover = blending; roulette parent selection;
  50% elitism; population 32.
- Gaussian mutation step (fraction of variable range): sigma = sigma_min + (sigma_max - sigma_min) * rho, clipped,
  sigma_min = 1e-3, sigma_max = 0.6, where rho is either
  * columnar diversity of that variable = stdev(log((v-min)+1)) / same at generation 0
    (gadapt/operations/decision_variable_update/variable_columnar_diversity_decision_variable_updater.py), or
  * relative cost diversity = mean pairwise |log(f_i + shift)| difference / same at generation 0, shift only when
    min f < 1 (gadapt/operations/population_update/cost_diversity_population_updater.py).
- Number of mutated candidates = (1 - relative cost diversity) * max (cost_diversity_candidate_solution_mutation_rate_determinator.py).
- Mutation is applied to non-elite/random candidates, not specifically to the best.

## Questions
1. From the mechanism above, derive (informally but concretely) WHY GAdapt converges 3–5 orders worse than CMA-ES on a
   smooth problem f = f* + (x-x*)^T H (x-x*). Consider: coupling of sigma to cost diversity (sigma ~ r^2?), dependence
   on f* (translation of f), the sigma_min floor, mutation not centred on the best, roulette selection on raw costs.
   Which of these is the dominant cause? Propose a cheap exploratory measurement that would discriminate them.
2. Propose up to 3 candidate research directions that could yield an ORIGINAL methodological contribution to GAdapt
   (method + falsifiable claim, ideally a provable property), each with:
   research question; closest known prior art (with DOI only if sure); the exact mathematical difference from it;
   falsifiable hypothesis; strongest baselines; kill criterion; your honest probability that novelty survives a
   systematic literature search.
3. If you believe no original GAdapt *method* contribution is realistically available, say so and say what the
   most defensible thesis framing is instead.
Keep the answer under ~1500 words.
