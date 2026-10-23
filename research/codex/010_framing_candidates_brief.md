# Brief for Codex #10 — new contribution candidates INSIDE the chosen thesis framing (read-only)

Decision (user, 2026-10-23): thesis framing = "reliable evaluation and mechanistic diagnosis of adaptive optimization
software for infrastructure problems" (integrity audit I49–I52 + paper; diagnostic study I42–I48; causal test I53).
All "fix GAdapt's deficit" method candidates are NO-GO (research/DIRECTION_DECISION_2026-10-23_SR.md, codex/003,005,006,008).

Task: propose up to 3 candidate ORIGINAL methodological contributions that fit this framing and the evidence we have,
and gate each against prior art yourself (web search). Examples of the kind of question (do not limit yourself):
- I53-style oracle interventions as a general, validated protocol for CAUSAL decomposition of a performance gap between
  two optimizers (closure measure C, factorial oracle arms, frozen reference). Prior art to check: ablation analysis
  (Fawcett & Hoos), algorithm configuration/importance (fANOVA, Hutter et al.), component-wise analysis of
  metaheuristics (e.g. Bezerra/López-Ibáñez/Stützle modular frameworks), explainable benchmarking, landscape-aware
  performance attribution, counterfactual/oracle analyses in ML.
- Contract testing of optimizer libraries as metamorphic relations with statistical guarantees (sample size for a
  given detection probability, false-positive control across classes).
- Measurement validity for infrastructure benchmarks: penalized-score vs feasibility disagreement (I53 case118:
  same penalized score order, feasibility 2/12 vs 12/12) — when do penalized-score comparisons mislead?
For each: research question; closest prior art (DOI only if sure, else UNVERIFIED); exact difference; falsifiable
hypothesis; how our existing data/tools (I47–I53, the audit tool) give a head start; minimal next experiment and
budget; GO/NO-GO and probability. Max ~1300 words. Read-only.
