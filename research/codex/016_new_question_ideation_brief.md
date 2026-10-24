# Brief for Codex #16 — find a NEW research question for an original GAdapt contribution (read-only, web search on)

Situation. PhD on GAdapt (this repo: self-adaptive GA; see CLAUDE.md "Architecture"/"Behaviour") for infrastructure
optimization. The mentor requires an original, defensible scientific contribution that improves the REAL GAdapt.
The integrity-audit paper (research/paper_integrity_audit/) is judged an internal document, not the contribution.

Already rejected with verified prior art — do NOT re-propose variants of these:
- fixing GAdapt's convergence gap vs CMA-ES: step-size control from spread × success multiplier (AMBOA, AVS, SDR,
  RV-GOMEA), correlation/rotation learning (PCX, AREX, eigen-DE, CoBiDE, AMaLGaM), offspring-centred step controller
  + convergence theorem (da Silva et al. 2025), spectral restoration; certified interval crossover for AC flow;
  oracle-intervention diagnosis protocol; contract testing with detection guarantees; penalized-rank certificates;
- earlier: adaptive operator selection/bandit credit (Fialho 2008 etc.), censor-aware/cost-normalized credit,
  scenario-sampling credit (I26–I37), partition crossover on route choice (H1, I42), memetic local-search
  intensification (H3: EMDE 2008, MA-LS-Chains 2010, HSES 2018).
Key lesson (research/DIRECTION_DECISION_2026-10-23_SR.md): a new candidate must come from a DIFFERENT QUESTION, not
from repairing a known GAdapt weakness that already has a published remedy.

Evidence base: research/PHD_PROGRESS.md, ITERATION42–53 reports (diagnosis), I47 (CMA-ES 10^3–10^5 better on smooth
AC dispatch), I48 (multimodal: gap only 1.3–1.5×, GAdapt beats DE 2/3), I53 (oracle step closes ≤ 29% of gap).
Data available: pypower/MATPOWER cases, topohub topologies (Zenodo 10.5281/zenodo.19154525); unlimited CPU.

Task. Generate 8 candidate research questions where GAdapt's distinctive mechanisms (diversity-driven
self-adaptation, explicit per-variable value grids/steps, uniqueness of individuals, elitism + immigration,
population statistics) are naturally relevant to a REAL infrastructure need that existing methods serve poorly.
Think beyond "beat CMA-ES": e.g. structure of infrastructure problems (network graph, N-1 contingencies as
max-over-scenarios, multi-period coupling, evaluation failures/non-convergence, multi-fidelity DC/AC, discrete
devices, operator need for several diverse near-optimal plans, warm start between periods, exactness-preserving
speedups), or theory of GAdapt's own rules. For each candidate:
(a) question; (b) method sketch precise enough to implement; (c) closest prior art — search the web, give DOIs you
actually found; (d) exact mathematical/algorithmic difference; (e) a provable proposition if any; (f) strongest
baselines; (g) falsification experiment on available data; (h) novelty probability and cost.
Then rank the top 3 and say which ONE you would bet a PhD chapter on and why. Max ~1500 words. Read-only.
