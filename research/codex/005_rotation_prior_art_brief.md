# Brief for Codex #5 — prior-art gate: correlation-learning / rotation-invariant variation in a diversity-adaptive GA (read-only)

Context: I53 part A (research/ITERATION53_REPORT_SR.md §1, research/codex/004_*) suggests (not established) that
GAdapt's remaining deficit on ill-conditioned/rotated problems comes from coordinate-wise variation (per-variable
Gaussian mutation, blending crossover with a per-coordinate coefficient) without correlation learning.
Before anyone proposes "give GAdapt rotation-invariant / correlation-learning variation" as a contribution,
establish prior art. Use web search. Cover at least: UNDX (Ono & Kobayashi 1997), SPX (Tsutsui et al. 1999),
PCX/G3 (Deb, Anand, Joshi 2002), rotation-invariant DE variants, CMA-ES-based mutation inside GAs,
eigen-coordinate crossover (e.g. Wang et al. / Guo et al. "eigenvector-based crossover" for DE),
covariance-matrix-guided GA mutation, linkage-learning real-valued GAs (RV-GOMEA), and anything that ties
correlation learning to a population-diversity-driven self-adaptation like GAdapt's.
For every item: full reference, DOI ONLY if sure (else UNVERIFIED), one line on what it covers.
End with: which variants are clearly prior art; whether ANY GAdapt-specific variant plausibly remains open and
the exact mathematical difference it would need; your probability. Max ~800 words. Read-only.
