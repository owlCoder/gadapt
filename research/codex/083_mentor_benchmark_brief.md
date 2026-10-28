# Brief for Codex #83 — mentor's benchmark (read-only; Serbian Latin; max ~1500 words)
New fact (user, 2026-10-28): the mentor's view is that GAdapt is good, beats all other algorithms except one, but is the more accurate one; he wants GAdapt
to be STABLE and applied in industry. The mentor's experiment is the public repo https://github.com/bpzoran/gadapt_experiments (cloned read-only at
/private/tmp/claude-501/-Users-danijel-Desktop-gadapt/37a2da25-38f4-4318-a2de-f78089e0f26f/scratchpad/ext/gadapt_experiments; older version in /private/tmp/claude-501/-Users-danijel-Desktop-gadapt/37a2da25-38f4-4318-a2de-f78089e0f26f/scratchpad/ext/GeneticAlgorithmExperiments). Read its README.md, research_experiments/runners/*.py, settings, use cases,
utils/significance.py. Also read research/ITERATION49_REPORT_SR.md and research/paper_integrity_audit/manuscript.md (our integrity-audit findings) and
research/ITERATION47_REPORT_SR.md (CMA-ES vs GAdapt on AC dispatch) and ITERATION57_REPORT_SR.md.
Deliver: (1) what claims the mentor's benchmark can and cannot support as designed (stagnation-based stop, budget in generations not evaluations, unrotated classical
functions with optimum at origin, PyGAD with custom operators, DE best1exp popsize...). List concrete validity threats and which are checkable from the code
(e.g. real evaluation counts per run per configuration, whether DE's popsize is aligned, whether any config evaluates more per generation, how REC/AUCC use generations,
rotation/shift sensitivity, 'stability' = SD of final fitness vs rare failures). (2) A preregistered EXTENSION that serves the mentor's goal (stable, accurate, industry use)
and is scientifically defensible: equal-evaluation budgets; added strong baselines (CMA-ES incl. IPOP/BIPOP, L-SHADE/jDE, a (1+1)-ES/random-restart local baseline); shifted/rotated variants
and infrastructure problems from our records (ORPD case14..118, AC dispatch); stability metrics with proper definitions (distribution of final gap, CVaR/worst decile, success
probability at fixed targets, ECDF, Wilcoxon + effect size, bootstrap CIs); and the specific question whether the claim 'GAdapt beats all but one algorithm yet is more
accurate' survives. Give the falsifiable hypotheses (both directions), the frozen design, and CPU budget at 10 cores. (3) What GAdapt library change (opt-in, default bit-identical)
would plausibly improve STABILITY (worst-decile quality), evidence from our records (e.g. min std-dev decay 1e-4 with decay 2.5 gave ~1.8 orders lower median gap at +20% evals, README/CLAUDE.md);
state whether a stability-oriented opt-in preset is worth a preregistered test. (4) Honest verdict: what contribution this is (replication+extension, not a new method), prior art for comparing
GA mutation strategies on classical functions, GO/NO-GO.
