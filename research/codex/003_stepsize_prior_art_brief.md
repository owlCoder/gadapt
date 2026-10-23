# Brief for Codex #3 — prior-art gate (read-only), run in parallel with the I53 measurement

Context: I53 (research/ITERATION53_PROTOCOL.md) tests whether GAdapt's convergence deficit vs CMA-ES on AC economic
dispatch comes from its mutation operator: Gaussian step sigma set from population (columnar) diversity with a floor,
mixed 50/50 per coordinate with uniform resets, applied to offspring, not to the incumbent.

If I53 supports this, the obvious next step is to give GAdapt a step-size control that tracks progress while
keeping its diversity-driven design. BEFORE anyone proposes that as a contribution, establish the prior art.

Task: a focused literature search (use web search) for:
1. Real-coded GAs whose Gaussian mutation scale is driven by population diversity / spread, and analyses of
   their premature convergence or lack of linear convergence (incl. Gaussian EDA variance collapse:
   Shapiro 2005 10.1162/1063656053583414; Bosman & Thierens 2007 10.1145/1276958.1277067; Grahl et al. AVS/SDR).
2. Step-size control combined with diversity signals in GAs: success-based (1/5 rule) in GAs, CSA or
   two-point adaptation inside a GA, diversity-guided EAs (Ursem DGEA 2002), self-adaptive mutation in RCGAs.
3. Any work that combines a diversity-proportional scale with a success/progress-based correction factor
   (e.g. sigma = s_t * spread, s_t adapted by success rate) — this is the most likely candidate formula.
4. Known theory: linear convergence of comparison-based step-size adaptive search (Auger & Hansen), and whether
   a spread-proportional sigma alone can converge linearly on the sphere.

For every item give: full reference, DOI ONLY if you are sure (else UNVERIFIED), one line on what it already covers.
End with: which formula variants are clearly prior art, and whether ANY variant plausibly remains open (with your
probability). Max ~900 words. Read-only: do not edit files.
