# Brief for Codex #84 — review of research/ITERATION64_PROTOCOL.md draft (read-only; Serbian Latin; max ~1300 words)
Read the draft, research/codex/083_mentor_benchmark_codex_answer.md (your design), the mentor's repo clone at /private/tmp/claude-501/-Users-danijel-Desktop-gadapt/37a2da25-38f4-4318-a2de-f78089e0f26f/scratchpad/ext/gadapt_experiments (research_experiments/runners/*.py,
functions/, settings, plugins), research/ITERATION63_PROTOCOL.md + research/iteration63_replication.py (how we freeze/gate), README.md GAdapt parameters.
Deliver: (1) BLOCKING defects of the I64-S protocol: ambiguity; rule that can pass/fail trivially; wrong estimand (gap normalisation across functions with different scales: define g exactly,
including f*, scale, rotated/shifted cases and 'Rosenbrock narrow range'); definition of 'GAdapt beats all but at most one' operationalised via ECDF-area with exact tie/multiplicity handling (11 configs, which
tests, family-wise control); exact definition of CVaR with n=100 (ties), L=g/(1+g) ; seeds; stopping by an external wrapper at exactly 12,000 REAL calls for GAdapt (probe calls, validation
calls ga.execute does all-min/all-max, duplicates), PyGAD (initial population evaluations, best_solution() re-evals), SciPy DE (callback re-eval), CMA families (pycma maxfevals, restarts) — specify how a wrapper aborts a run
(exception vs exit_function) without changing returned-solution semantics and how 'best so far' is taken from the call trace; (2) what must be decided from development data only vs frozen now (e.g.
CMA/IPOP/BIPOP settings, (1+1)-ES restart rule, GAdapt parameter mapping of the PyGAD operators); (3) a minimal, cheapest first phase 'I64-S0' that can run on ONE core in ~1-2 CPU hours and decisively answers
whether the mentor's ranking claim (his own 4 configs, original stagnation rule) is reproduced with real evaluation counts — give exact cells/seeds; (4) CPU estimate per phase using GAdapt overhead (~1 ms per generation at pop 32x10 vars; give formula);
(5) verdict FREEZE AFTER FIXES / REDESIGN with exact replacement text for every blocking item.
