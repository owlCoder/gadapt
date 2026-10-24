# Brief for Codex #37 — scoping a SECOND infrastructure domain for the constraint-handling validation (read-only, web on)
Context: research/ITERATION58_PROTOCOL.md validates GAdapt's opt-in constraint_handling on power-system ORPD only; a
committee will ask for breadth. Data available: topohub (Zenodo 10.5281/zenodo.19154525: SNDlib topologies with ORIGINAL
static demands; the temporal SNDlib TGZ is lost and must not be reconstructed), networkx/scipy in .venv.
Propose ONE second-domain problem where (a) decisions are naturally discrete grids (e.g. modular link capacities in
units of 10/40/100G, or integer facility counts), (b) feasibility is a nontrivial black-box check per evaluation (e.g.
multicommodity routing feasibility under capacities via an LP or shortest-path heuristic, or survivability under
single-link failure), (c) cost = capacity/installation cost, (d) evaluation is cheap enough for thousands of calls.
Give: exact formulation, evaluation procedure (deterministic; which solver), closest prior art with VERIFIED DOIs (GA for
SNDlib network design / capacity planning; evolutionary multi-layer design), the strongest baselines (MILP via
scipy.optimize.milp / HiGHS on small instances as reference optimum), which SNDlib instances fit, and a falsifiable
question mirroring H58 (FR vs penalty in GAdapt). Also: risks (degenerate T = 1 blocks seen in I56 dev; how to size budgets
and targets so blocks are informative WITHOUT tuning on test data). Max ~900 words. Read-only.
