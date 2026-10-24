# Brief for Codex #19 — gap-first: mine OPEN problems declared by the community (read-only, web search on)

Context: 11 GAdapt method candidates rejected with verified prior art (research/IDEATION_2026-10-24_CLAUDE_BLIND_SR.md,
research/DIRECTION_DECISION_2026-10-23_SR.md). Inventing mechanisms and auditing them keeps failing. New approach:
start from problems that recent literature EXPLICITLY states are open.

1. Find 10–15 explicit open problems / future-work statements (quote the sentence, give paper + DOI you actually
   found, 2021–2026 preferred) from surveys, roadmaps and benchmark papers on: evolutionary / metaheuristic
   optimization for power systems (OPF, SCOPF, unit commitment, distribution reconfiguration, Volt/VAR with discrete
   taps/shunts), telecom/transport network design, mixed-integer black-box optimization, and evolutionary
   computation benchmarking of real-world problems (e.g. IEEE CEC/GECCO real-world competitions, "Benchmarking
   in optimization: best practice and open issues" Bartz-Beielstein et al. 2020).
2. For each: is it still open (any 2024–2026 paper that closed it?), does a population GA with explicit per-variable
   value grids, diversity-driven self-adaptation, elitism and immigration (GAdapt) have a NATURAL handle on it, and
   what concrete, falsifiable PhD question follows. Prefer problems where CMA-ES/BO are structurally unsuited
   (discrete devices, mixed variables, hard combinatorial structure, many feasible-region islands, need for diverse
   alternatives, non-convergent simulators).
3. Rank the top 3 by (still open) × (GAdapt fit) × (testable with public data: MATPOWER/pypower, pandapower
   networks, topohub, SNDlib instances without the lost temporal TGZ) and state for each the decisive baseline.
Max ~1200 words. Read-only. Verify DOIs; mark anything unverified.
