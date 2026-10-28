# Brief for Codex #81 — ideation round 2 with web search (read-only; Serbian Latin; max ~1500 words)
Goal: a defensible ORIGINAL scientific contribution to GAdapt-style self-adaptive GAs for infrastructure optimization (mentor requirement). 14 candidates
are already rejected with verified prior art — read research/IDEATION_2026-10-24_CLAUDE_BLIND_SR.md, H3/H4/H5/H6 audits, ORACLE_DIAGNOSIS_PRIOR_ART_AUDIT_SR.md,
DIRECTION_DECISION_2026-10-23_SR.md, codex/076 and 019 answers, research/thesis/CH1 — do NOT re-propose them or renamed versions
(step-size control with diversity, correlation learning, certified crossover, cost-signal invariance/threshold laws, oracle diagnosis, partition crossover,
CHT x adaptation main effect on discrete ORPD, etc.). Read gadapt/ (README.md, CLAUDE.md "Behaviour to keep in mind") for what GAdapt actually does:
discrete value grids (ga.add(min,max,step)), uniqueness enforcement of individuals, cost-diversity / columnar-diversity / parent-diversity driven mutation and
crossover probabilities, elitism %, pure Python.
Constraints: no new CPU-heavy runs are possible for ~25 h (a study occupies the machine); we need directions whose prior-art gate and formal
statement can be done now. Propose 5 NEW directions, each from a different angle, e.g.: (1) problem-structure exploitation specific to discrete-grid infrastructure
variables (e.g. unique-individual enforcement as a search-space-coverage / duplicate-avoidance mechanism: does uniqueness change convergence
theory or evaluation cost on expensive simulators? exact-statistics, 'saturation of discrete spaces'); (2) evaluation-budget economics for expensive simulators
(surrogate-free early termination, partial evaluation / multi-fidelity inside a self-adaptive GA, caching/duplicate avoidance guarantees); (3) a
theory result about self-adaptive diversity-driven mutation on grids (runtime, drift, fixed-target) that is NOT the rank-invariance/penalty angle; (4)
a methodology contribution about statistical comparison/reporting of stochastic optimisers on infrastructure problems with a validated tool and a
provable property; (5) a different infrastructure domain where GAdapt's features matter (water distribution, microgrid sizing, transit network design),
with an open problem found in 2021-2026 surveys. For each: closest prior art (DOIs, verify via search), the precise mathematical/empirical gap or 'not established',
the falsification experiment and its CPU budget, and GO/NO-GO for a prior-art-gate only. Rank them. Be strict; never invent citations; say explicitly
when search could not verify something.
