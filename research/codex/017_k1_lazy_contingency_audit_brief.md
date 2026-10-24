# Brief for Codex #17 — adversarial prior-art audit of Claude's candidate K1 (read-only, web search on)

Try to REFUTE originality. Candidate K1 (research/IDEATION_2026-10-24_CLAUDE_BLIND_SR.md):
N-1 security-constrained dispatch, cost F(x) = c(x) + P · max_{k=1..K} v_k(x), each v_k one AC power flow.
In a population GA (GAdapt: elitism keeps the best p%, survivor statistics drive adaptation, rank-based parent
selection — check gadapt/operations/ for what decisions actually need exact costs), evaluate contingencies lazily:
partial maxima are lower bounds; stop evaluating an individual once its lower bound proves it cannot enter the
elite set; order contingencies by a population-learned criticality; claim: the elite set and the best cost are
IDENTICAL to full evaluation (exactness), with fewer AC solves. Note: gadapt/operations/cost_finding/
sequential_scenario_budget_cost.py already does first-fail early stopping on feasibility (self-declared known).

1. Closest prior art with DOIs you actually found: racing / early termination of fitness evaluation in EAs,
   exact/lossless partial evaluation, worst-case / minimax EAs (lazy scenario evaluation), contingency filtering /
   screening in SCOPF (incl. with metaheuristics), branch-and-bound style pruning in population methods, "lazy
   constraint" evaluation in EAs.
2. Exact mathematical difference that remains, if any. Is "selection-exact lazy max-evaluation" already a known
   lemma? What would GAdapt need to change (selection, statistics) for the exactness to hold, and does that change
   behaviour (then it is not exact w.r.t. default GAdapt)?
3. Verdict: GO / NO-GO for originality, novelty probability, and the strongest baseline that would kill it.
Max ~700 words. Read-only.
