# Brief for Codex #18 — adversarial audit + feasibility of K6 (theory of GAdapt's diversity rule) (read-only, web on)

Try to REFUTE originality, then judge whether a proof is feasible. GAdapt rule (read the code):
gadapt/operations/population_update/cost_diversity_population_updater.py and
gadapt/operations/mutation/population_mutation/cost_diversity_candidate_solution_mutation_rate_determinator.py:
number of mutated individuals per generation = round((1 − D_t/D_0) · M), D_t = mean pairwise |difference| of
log-shifted survivor costs (shift so min = 1), divided by the mean magnitude, D_0 the generation-0 value, clipped to
[0,1]. I.e. mutation intensity rises as survivor costs converge ("diversity-deficit-triggered mutation").
Also columnar diversity sets the number of mutated variables per individual (>= round(N/5)).

1. Prior art (DOIs you found): diversity-based parameter control (DGEA Ursem 2002; diversity-triggered
   mutation/hypermutation; triggered hypermutation Cobb 1990; stagnation-based restarts/heavy-tailed mutation
   after stagnation — stagnation detection (Rajabi & Witt 2020+), self-adjusting mutation rates theory (Doerr,
   Doerr, Lengler...), population diversity in runtime analysis (Sudholt survey), fitness-distance based control).
2. Is a runtime result for THIS rule (a population GA whose mutation pressure is driven by normalized cost spread of
   survivors) new? Stagnation detection (Rajabi & Witt; Doerr & Rajabi) seems close: rate increases after no
   improvement. What is the exact mathematical difference (spread of population costs vs generations without
   improvement)? Would a theorem like "on Jump_k / multimodal functions the diversity-deficit trigger yields
   expected runtime X, versus Y for static rates" be publishable novelty, or a corollary of stagnation detection?
3. Feasibility: which proof is realistically doable in weeks for a simplified (mu+lambda) model of the rule
   (OneMax, LeadingOnes, Jump, or a continuous sphere)? Name the drift/level-based tools.
4. Connection to infrastructure: is there any honest way to tie such a theorem to the PhD topic?
Verdict GO/NO-GO, probability, and the best simplified model. Max ~800 words. Read-only.
