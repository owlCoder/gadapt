# I40 PREREGISTRATION — temporal calibration of ONE permanent source modular capacity plan

**22 October 2026. Frozen BEFORE any I40 original SNDlib route optimization or holdout evaluation.** Repo `owlCoder/gadapt` only, upstream unchanged. This is a transparent evaluation of KNOWN split-conformal and robust reserve methods, NOT an assertion of novel doctoral methodology.

## Problem and temporal leakage

Use original source SNDlib Nobel-Germany 17 nodes / 26 edges / 272 directed pairs, 288 original five-minute matrices on 2005-02-15. Network SHA256 `35e58a3799d78d2ebfd2a557be2ba4a221ca17fc704cfdd13df56bb90c12a796`; matrix archive SHA256 `2c3ca706a8d5c9601eb4d144651816dfd956257c20f60111a8aceb5f07ab0100`. All 26 native 40-option menus MUST pass the I39 algebraic cost-equivalence gate: same source price as nonnegative integer modules of capacities 20 and 40; do not invent new source capacities. Keep I39 RESTRICTED unsplittable 2-path static routing / shared undirected capacities / source unit assumed Mbit/s model unchanged.

Split chronologically: **FIT 0..127 (128), CAL 128..191 (64), TEST 192..287 (96)**. Both static route policies use *only FIT*: (1) deterministic first least-hop route `z=0`, (2) exactly ONE `scipy.optimize.milp` HiGHS reference on FIT with 180-second time limit and target MIP relative gap 0.01, both using same source module model. Even if the solver is timed out, independently verify its feasible incumbent and valid dual bound and report its status. If solver gives no valid incumbent, record that and do not fabricate it. No GAdapt run is necessary for this **calibration-mechanism isolation** stage; original I39 GA weakness is retained as prior independent finding.

## Frozen deterministic calibration algorithm

For a FIXED FIT-derived route z, let `L[e,t](z)` be actual source-network traffic on edge e for frame t (both directions summed), and `a[e]=max_{t in FIT}L[e,t]`; E_used are edges traversed by at least one of the 272 fixed paths. Define source-physical capacity units `w[e]=max(20,a[e])` for e in E_used (fixed strictly from FIT). For all 64 CAL frames, define a **single network-wide** nonconformity score
`s[t]=max_{e in E_used} max(0,(L[e,t]-a[e])/w[e])`.
For target violation rate **alpha = 0.10**, split conformal order statistic `k=ceil((64+1)*(1-alpha))=59` (1-indexed): `qhat=sort(s_CAL)[k-1]`. The calibrated common permanently installed cap for each e is
`C[e] = minimum source-modular capacity (20*y20+40*y40) >= a[e]+qhat*w[e]` (zero for unused links); choose cheapest source-equivalent combination as in I39. This is ONE static deployment, never per-frame recourse, with the same z for all frames. If scores and capacities are all zero, retain zero-capacity modules. Use independent source module audit on every run.

**Mathematical containment theorem:** for any future demand frame with nonconformity score <=qhat, its link loads satisfy `L[e] <= a[e]+qhat*w[e] <= C[e]` on all used edges and zero elsewhere. This is deterministic for ANY traffic; hence the *event* of full-network feasibility contains the event of score <=qhat. Under conditional exchangeability of the 64 CAL scores and one future score GIVEN the FIT-derived fixed z and a,w, with no ties concerns, `P(all 26 edge caps feasible on next frame) >= k/(64+1)=59/65≈0.90769`. **THIS ASSUMPTION IS NOT VERIFIED ON 5-min CORRELATED 2005 DATA**; do NOT claim an unconditional or time-series-valid finite-sample service level. Relevant prior art: Oliveira et al. JMLR 2024 doi/url https://jmlr.org/papers/v25/23-1553.html and Barber & Pananjady ALT 2026 https://proceedings.mlr.press/v313/barber26a.html; classical budgeted robust optimization: Bertsimas & Sim 2004 https://doi.org/10.1287/opre.1030.0065. Novelty is NOT established by this algorithm.

## Five methods/policies per *fixed route z*, frozen before TEST

- `fit_only`: cheapest source modular cap satisfying all 128 FIT frames; no CAL.
- `calibrated_90_relative` (**primary proposed**) as above with `w=max(20,a)`, `k=59`.
- `calibrated_90_absolute`: identical k but replace `w=1` on all used edges. A simple non-learned sensitivity control, not optimized by TEST.
- `calibration_max_relative`: `qhat=max(s_CAL)` using same FIT-based relative weights, ensures all 64 CAL frames; more conservative.
- `fit_plus_cal_per_edge_max`: cheapest source modular caps satisfying ALL 192 FIT+CAL frames separately on each link (still same FIT route z; past-data robust upper-bound control). This consumes 64 calibration observations to set capacities, NOT for routing.

For each route and policy report same `FIT/CAL/TEST` three partitions: price, total source capacity, positive module counts, violating frames on each partition, maximum link capacity excess, fraction of 96 TEST frames served, and difference in source price versus fit_only. Do NOT optimize any hyperparameter or route using TEST. Only original network traffic; no synthetic demand.

Primary scientific DESCRIPTIVE comparison: for **MILP FIT-only route**, TEST violation count `calibrated_90_relative` versus `fit_only`, together with extra module price. Both outcomes must be reported; if worse or 0 gains, state so. Support controls on fixed-shortest route and absolute/cal-max/per-edge-max. Temporal frames are serially correlated, so do not report binomial p-values as if 96 observations were independent. No statistical novelty claims. No post-hoc re-calibration after seeing TEST.

## One-time execution

1. Commit this prereg before any I40 original solver or holdout calls.
2. Implement and unit test on SMALL synthetic traffic arrays (not official source).
3. One CI source gate (validate input SHA, module equivalence and 288 temporal slots).
4. One **PR-only** actual run computing 1 FIT MILP + exactly 2×5 permanent plans and full original raw JSON, no repeat-until-good; zero solution tuning based on outputs.
5. Record original CI artifact and retain negative outcomes; research into novel robust temporal methods requires a separate formal prior-art audit and independent multi-day dataset BEFORE doctoral novelty can be claimed.
