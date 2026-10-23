# Brief for Codex #8 — systematic prior-art gate for the strongest remaining GAdapt method candidate (read-only)

Context: research/DIRECTION_DECISION_2026-10-23_SR.md, your answers 003 and 005, research/ITERATION53_REPORT_SR.md.
Standard step-size fixes and correlation learning are prior art. Two narrow candidates remain:
 (C1) an offspring-centred step-size controller for a diversity-adaptive GA (GAdapt: mutation applied to offspring,
      not to the incumbent; sigma from population/columnar diversity) WITH a new convergence result (e.g. linear
      convergence on the sphere / convex quadratic for the finite-population GA with elitism and this controller);
 (C2) your "spectral restoration" law Sigma_i = sigma^2 [C + beta (1-D_f)(1-D_p,i)(tau I - C)_+].

Task:
1. Make each candidate mathematically precise enough to be falsifiable (state the update equations, assumptions,
   and the exact theorem that would constitute the contribution).
2. Systematic search (web): runtime/convergence analyses of real-coded GAs / EDAs with elitism and adaptive
   variance (e.g. Jägersküpper, Auger & Hansen, Akimoto, Beyer, Glasmachers; convergence of (mu+lambda)/(mu,lambda)
   with recombination; drift analysis on the sphere; EDA convergence with variance scaling; spectral/eigenvalue
   restoration, "eigenvalue clipping", covariance repair, AMaLGaM AVS, IPOP restarts, sep-CMA, active CMA).
   Report the closest result for each candidate and the EXACT remaining mathematical difference.
3. GO / NO-GO for each, probability, and — if GO — a minimal falsification plan (synthetic first, then I47/I53 dispatch)
   with strongest baselines and budget.
DOIs ONLY if sure (else UNVERIFIED). Max ~1200 words. Read-only.
