# Brief for Codex #21 — blocking review of the I56 protocol DRAFT before freezing (read-only)

Draft: research/ITERATION56_PROTOCOL.md (Serbian). Context: research/H5_PROPOSAL_SR.md §10 (your 020 revision),
instrument research/iteration56_orpd.py, dev pilot research/results/iteration56_dev_pilot/README.md, GAdapt code
(gadapt/, esp. cost_finding/elitism_cost_finder.py, population_update/cost_diversity_population_updater.py,
candidate_solution_update/parent_diversity_candidate_solution_updater.py, sampling/roulette_wheel_sampling.py,
factory/ga_factory.py, execution/ga_executor.py).

Find BLOCKING errors (as in your 007 review) and important weaknesses:
1. Validity of the causal contrasts (AD-N vs FX-T vs FX-M; AD-C "common signal"): do they isolate what §1 claims?
   Does same seed really give the same initial population across arms (check GAdapt RNG use before generation 1)?
2. CHT scalarizations (§4): correct implementations of Deb/adaptive penalty/epsilon as cost_value? Re-scalarizing
   survivors each generation: where exactly in GAdapt (which hook) and does elitism/exit/uniqueness break?
   GAdapt's log-range on FR merits in (1,3): is the signal then degenerate? u(f)=f/(f+f_ref) ok?
3. Outcome and tests (§6–7): is the block-wise rank Y with a pooled Wilcoxon on d_u valid (rank dependence across
   arms within a block; pooling blocks)? Better alternative (ART-ANOVA, permutation test within block)? Is the
   reference L* design sound? Power statement right?
4. FX-M / FX-T: leakage, fairness, the declared tuning budget; is σ a fair "same operator" control for GAdapt's
   columnar-diversity Gaussian; what about crossover (blending) and the Gauss/reset mixture?
5. Anything that makes the result uninterpretable or trivially predictable; missing controls; budget sanity.
Give a list: BLOCKING / IMPORTANT / MINOR with concrete fixes. Max ~1000 words. Read-only (you may run read-only
Python with .venv/bin/python -I to inspect GAdapt behaviour, but do not write files).
