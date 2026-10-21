# GAdapt — AOS iteration, frozen pilot protocol (2026-10-21)

**Status:** predeclared exploratory pilots; *not* a confirmatory dissertation test.
Branch `research/feasibility-credit-aos` derived from `research/robust-diversity-baseline@bd6bf785`.
No changes to upstream or fork main. The previous four-frame August inspection means the archive
as a whole is not pristine. The specific late-August timestamps below were not individually
analysed in earlier iteration artifacts. No future method tuning against these samples.

## Hypothesis and existing prior art

GAdapt's multi-mutator composition randomly permutes operators before drawing one;
its normalized diversity adjusts mutation rate/amplitude but does not update mutation
operator choice using actual offspring quality. This leaves a **measurable engineering gap**,
not yet a unique scientific novelty claim.

Relevant precedent:
- Fialho, Da Costa, Schoenauer, Sebag (2010), *Analyzing bandit-based adaptive operator
  selection mechanisms*, DOI 10.1007/s10472-010-9213-y: credit assignment + bandits.
- Da Costa, Fialho, Schoenauer, Sebag (2008), *Adaptive Operator Selection with
  Dynamic Multi-Armed Bandits*, DOI 10.1145/1389095.1389272.
- Li, Fialho, Kwong, Zhang (2014), *Adaptive Operator Selection With Bandits for a
  Multiobjective Evolutionary Algorithm Based on Decomposition*, DOI
  10.1109/TEVC.2013.2239648: sliding fitness-improvement windows.
- Zhang, Sanderson (2009), *JADE*, DOI 10.1109/TEVC.2009.2014613:
  adaptive DE/current-to-pbest/1 and optional archive.
- Tanabe, Fukunaga (2013), *SHADE*, DOI 10.1109/CEC.2013.6557555:
  success-history-based adaptation.
- Deb (2000), DOI 10.1016/S0045-7825(99)00389-8: constraint handling.
- Runarsson, Yao (2000), DOI 10.1109/4235.873238: stochastic ranking.

Thus UCB1 + reward + feasibility is **not a dissertation innovation by itself**.
A defensible distinct contribution would need calibrated or theoretically motivated,
bias-aware **constraint-benefit attribution** under shifting domains, and a broad
negative-control and independent-benchmark validation. The present implementation is
a baseline ablation platform to test whether this direction is even promising.

## Controller, its bias, and ablations

- `legacy`: completely unchanged original operator composition and diversity.
- `affine`: prior affine-only metric.
- `uniform_objective`: same set of mutation operators sampled uniformly, with
  tracked objective reward (negative-control ablation).
- `ucb_objective`: same reward but UCB1 policy; isolates learning from selection.
- `ucb_feasibility`: identical UCB1 policy with an explicit independent violation
  callback; isolates violation feedback from objective-only credit.
- `scipy_de`: matched actual physical solver calls, independent optimizer.

UCB1 is stationary whereas offspring improvements are nonstationary; its recent
64 observations are used for exploitation, while pull counts are cumulative. This
is **not** a formal nonstationary bandit solution. Credit uses the incumbent
population median as reference, and assigns evaluated offspring reward equally
to mutated variables; this is an observational proxy confounded by crossover,
parent selection, and variable interactions. No causal claim is warranted.
Objective credit = clipped positive normalized cost improvement. Feasibility
credit: infeasible offspring receive 0.5/(1+normalized violation); feasible
offspring receive 0.5+0.5*objective credit. This is lexicographic heuristics
with scale caveats, not proof of reliability. Logged selection/observation
counts distinguish sampled from evaluated mutants.

`mutation_operator_policy="legacy"` is the default. No legacy API values
change. Existing callbacks remain untouched on GA.clone(). Failure to evaluate
or a nonfinite callback is an error, never a successful new operator.

## IEEE14 AC pilot (executed only when CI runs)

Published IEEE14 benchmark, PYPOWER AC solver, loads 1.00 and 1.10; 8 paired
seeds, 240 physical calls, pop 24. A constraint callback reads already cached
PF outputs (0 new physical solves) and returns nonnegative excess of
v_max/0.001, q_max/0.1, thermal_max/0.1 above unity, or 1e12 on
nonconvergence. Every true PF call, callback read, unmatched lookup and
post-budget objective request is counted. An objective value of 1e8 is
returned to GAdapt after budget exhaustion without a PF call; it cannot
improve feasible incumbent. Validator endpoints consume real PF calls.
CMA-ES and AC-OPF reference methods are NOT yet present in this pilot.

Planned analysis: successes/total incl optimizer errors, Wilson 95% CI,
median and 90% quantile among physically feasible runs (conditional only),
paired win/tie/loss with infeasibility ranked worse than feasibility,
exact sign and McNemar tests, bootstrap paired MW CI conditional on both
feasible, Holm correction over five method comparisons per load.
At n=8, no rare-failure or superiority inference can be decisive.

## GÉANT extended chronological model / explicit sealed sample choices

Archive SHA256:
`92d72a808d6de9d26be66844c098d3f32d5b9bb6c69af170e82b73118faef0df`.

Development timestamps (12 total):
- 2005-05-05, 2005-06-15, 2005-07-20
- At 00:00, 06:00, 12:00 and 18:00 UTC/archive timestamps each day.

Later evaluation timestamps (32 total):
- 2005-08-20, 2005-08-22, 2005-08-24, 2005-08-26
- At 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00 and 21:00 each day.

No snapshot from August is used in objective optimization, calibration,
hyperparameter selection or operator feedback; each candidate's static
capacity installation must cover peak per-link demand across development
snapshots. After optimization, a static deployment plan is evaluated across
the 32 evaluation timestamps, with the *same single* precomputed training
volume calibration. Models are research assumptions, not actual GÉANT
production provisioning. Missing archive timestamps are errors; they must
not be silently replaced or selected after inspecting test costs.

Predeclared telecom ablations: legacy, affine, uniform-objective, UCB-objective,
SciPy DE at 240 actual objective calls and 8 paired seeds (pilot).
Feasibility-feedback UCB is deliberately **not** tested here: the model
allows unbounded capacity modules and has no independently justified hard
capacity feasibility criterion; inventing one based on observed costs
would be misleading. An independent physical link constraint or operator
requirement is needed first.

## Acceptance limits and next required study

All pilots are exploratory and may be discarded. Prior IEEE14 and GÉANT
results of affine diversity showed no general statistically confirmed advantage.
Any claimed dissertation novelty needs comparisons against established AOS,
JADE/SHADE and domain solvers, feasibility-independent validation,
50–100+ seeds based on power calculations, frozen multi-case holdouts,
effects with CIs and corrected p-values, repeated perturbations, and a
genuinely separate infrastructure family. No industrial-readiness claim.
