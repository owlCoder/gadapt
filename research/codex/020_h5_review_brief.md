# Brief for Codex #20 — review H5 proposal + resolve risk R1 (read-only, web search on)

Proposal: research/H5_PROPOSAL_SR.md (Serbian). Audit summary inside. Tasks:
1. R1: find and read (full text if at all reachable: publisher HTML, author copies, theses, ResearchGate, KNU/NTU
   repositories) Mallipeddi, Jeyadevi, Suganthan, Baskar 2012, Swarm Evol. Comput., 10.1016/j.swevo.2012.03.001,
   and Biswas et al. 2018 10.1016/j.engappai.2017.10.019. Did either vary parameter adaptation / control parameters
   as a factor, treat taps/shunts as discrete, or vary discretization? Quote what you find. Also search for any
   2015–2026 paper crossing constraint-handling technique with self-adaptive vs fixed parameters in OPF/ORPD/VVC.
2. Design critique: the "matched fixed" GAdapt arm (how to define fixed rates fairly without leaking information),
   how GAdapt's adaptation signal (log-range of survivor costs) should be defined under feasibility rules /
   stochastic ranking / epsilon (a scalar is needed) — propose 1 principled definition per CHT, frozen in advance;
   discrete grids for pypower cases (which device data exist in case14/30/57/118: tap ratios on branches, bus shunts
   Bs, generator Vg) and the IEEE PES 2014 OPF competition test bed (availability, discrete variables, budgets);
   power analysis for detecting an interaction; target definition (reference optimum).
3. Is this, honestly, enough for a PhD chapter? What would make the result most valuable for GAdapt users?
Verdict: proceed to protocol / revise / stop. Max ~1000 words. Read-only.
