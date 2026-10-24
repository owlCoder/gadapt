# Brief for Codex #70 — draft I62 proposal: validated stronger baselines (L-SHADE / jDE) and a tuned penalty (read-only, web)
Context: Codex 052 rank 2 and Codex 060 (research/codex/060_lshade_jde_candidates_codex_answer.md: NiaPy 2.7.1 L-SHADE/jDE,
validation plan; Tanabe 2024 doi 10.1145/3638529.3654019: SHADE adaptation weak on mixed-integer, jDE controls good).
I57 (research/ITERATION57_REPORT_SR.md) and I58 (research/ITERATION58_REPORT_SR.md) are descriptive/primary results so far:
CMAwM fastest on several networks, GAdapt more often feasible on case57/case39. The thesis must not overclaim GAdapt's
competitiveness. Draft, in Serbian (Latin), a complete proposal + exact protocol text for I62 whose purpose is EXTERNAL
VALIDITY of the thesis' practical claims: (1) a validation stage for the chosen implementation(s) (CEC2014 F1/F9/F17 vs
published L-SHADE results, budget exactness incl. 3000/3001, integer decoding identical to I57); (2) a tuned static penalty
(weights {10, 100, 1000, 10000} chosen on development scenarios only) as the fair comparator for GAdapt's CHT options;
(3) instances: development and test scenarios disjoint from I56/I58/I61 (new seeds) on case30/case39/case24_ieee_rts and
case57; (4) a descriptive or confirmatory design — recommend which, with hypotheses if confirmatory (e.g. GAdapt+best CHT vs
L-SHADE/jDE at equal PF budget), outcome T at a development-chosen informative budget, seeds, power; (5) compute budget and
the code needed (reuse I57 adapters and I58 instrument). Verify any new DOI (Crossref) or mark unverified. Max ~1500 words.
