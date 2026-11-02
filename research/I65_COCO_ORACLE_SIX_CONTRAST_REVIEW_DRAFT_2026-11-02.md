# I65 official COCO oracle and six-contrast statistical specification — workstream D

**Date:** 2026-11-02. **Status: REVIEW DRAFT / NOT_FROZEN / NOT_RUN.** No cocoex installed or invoked by this workstream, no synthetic or held-out COCO objective evaluations, no optimizer runs, no human/mentor approval. The existing [I65 original unfrozen draft](ITERATION65_DRAFT_PROTOCOL_SR.md) is not edited or overridden.

## D1. Exact primary study design proposed by original draft (NOT authorized)

- Official **single-objective** `cocoex.Suite("bbob", "year: 2009", suite_options)`, functions **f21 Gallagher 101 Peaks** and **f24 Lunacek bi-Rastrigin**; native dimensions **2/10/20**; distinct held-out instances **6/7/8**. There are 2 × 3 × 3 = **18 primary cells**, each with nine previously proposed methods and 30 paired seed labels. Budget **B=12,000** objective attempts per run, reserving a separately charged terminal witness *within* B. Total primary design would involve 4,860 runs and at most 58,320,000 run attempts **if approved**. These counts are *mathematical scope of the prior DRAFT*, not executed work.
- Official primary sources: [COCO f21 Python usage](https://coco-platform.org/testsuites/bbob/functions/f21.html) and [COCO f24 Python usage](https://coco-platform.org/testsuites/bbob/functions/f24.html) give selectors such as `suite_name="bbob"`, `suite_instance="year: 2009"`, and `suite_options="function_indices: 21 instance_indices: 1-10 dimensions: 2,20"` (replace selector values only after explicit protocol approval). They distinguish this from `bbob-biobj`. **Their presence on a documentation page does NOT prove installed cocoex runtime, exact instance IDs, or certified f_opt.**
- The [official cocoex Problem API](https://numbbo.github.io/coco-doc/apidocs/cocoex/cocoex.Problem.html) documents `evaluations`, `id_triple`, `final_target_fvalue1`, and `best_observed_fvalue1` properties but leaves the final target value's precise optimum semantics undocumented on that page. **Never equate `final_target_fvalue1` with exact optimum without a separate verified oracle and witness.**
- **No peek:** official instances 6/7/8 and held-out results remain untouched. Any future permitted integration test must be explicitly **development-only** (instances 1/2/3) and must not silently incur hidden f_opt or setup costs.

## D2. Exact six simultaneous policy-C contrasts (prospective, not a finding)

Let `E` denote IPOP-CMA-ES and `D` the frozen fixed I64-E3 hybrid. At matched function, dimension, held-out instance and *paired seed label*, define `L=g/(1+g)` with valid nonnegative normalized gap `g`. `CVaR_0.10(L)` is the **worst 10% (upper tail)** of bad-loss values, so **lower is better**. With exactly 30 seeds, the empirical worst decile is the average of the **worst three**, a high-variance estimate. Let `A` be the original draft's fixed-B target-ECDF integral across its three targets; larger is better. Let `p` be the original draft's success rate of a **valid independently witnessed** `g ≤ 1e-2` final target; larger is better.

| ID | Predefined signed contrast `Δ` (positive favors C) | Boundary for one-sided simultaneous LOWER confidence bound (from original draft) |
|---|---|---|
| K1 | `CVaR(E) - CVaR(C)` | lower bound **> +0.01** |
| K2 | `CVaR(D) - CVaR(C)` | lower bound **> 0.00** |
| K3 | `A(C) - A(E)` | lower bound **≥ -0.03** |
| K4 | `A(C) - A(D)` | lower bound **≥ -0.03** |
| K5 | `p(C) - p(E)` | lower bound **≥ -0.05** |
| K6 | `p(C) - p(D)` | lower bound **≥ -0.05** |

This makes the originally incomplete **four-contrast** family explicitly **six** by including the two draft-required reach-rate noninferiority decisions. **All six belong to the same simultaneous one-sided error family**; calculating 95% bounds separately for each and ignoring multiplicity is unacceptable. The original DRAFT mentions a hierarchical instance/seed **max-t** paired bootstrap with 20,000 repeats and seed 65065. Before a FREEZE, a human statistics reviewer must approve exactly how `max-t` is studentized, how zeros/ties/failed witnesses and nonfinite data are handled, how seed nesting and pairing works, and what to do with degenerate bootstrap variance. A mere table of contrasts does not implement or validate that procedure.

### Inferential limitation that no bootstrap can hide

There are only **three held-out instances per function × dimension**. Thirty repeated optimizer seeds for a fixed instance are **not 30 independently sampled landscapes**. Treating all 90 seeds as 90 independent network/problem instances or bootstrapping individual seeds without the instance level yields pseudo-replication. Prespecify separate analyses with **instance as the primary unit**, **instance/seed hierarchical sensitivity**, and transparent confidence intervals that may be indecisive. If any required lower confidence bound crosses its limit: **UNDECIDED / NO-GO for a claim of practical improvement**, not a prompt to reselect seeds or rerun until positive.

## D3. Objective-offset normalization: explicit mathematical test, no COCO access

Assume `f_opt=0`, representative raw sample values `[1,2,3]` and a tested point `f(x)=1`. If one naively sets `s=median(f(x))=2`, then `g=(1-0)/2=0.5`. Shift objective and optimum both by +100; `f'_opt=100`, sampled values `[101,102,103]`. Then `s'=102`, while the **unchanged true gap** stays 1, yielding `g'=1/102`: **the metric changes under a meaningless additive offset**.

A *candidate* translation-invariant definition is `s=median(f(sample)-f_opt)`, with independent exact oracle optimum, finite samples, strictly positive scale and setup cost/seed/provenance. Here `s=2` under either objective shift. However **the original DRAFT did not formally approve this replacement**; no sampled f-opt or 4,096-point setup set was generated. A separate reviewer must resolve `s_i` semantics and nonfinite/zero/negative median policies in a new numbered prospective version BEFORE any holdout is accessed.

Likewise an improvement detector `Δf>eps_abs+eps_rel*max(1,|f_prev|)` with nonzero `eps_rel` is not invariant to adding an objective offset. `eps_rel=0` removes this *specific* offset dependence but leaves `eps_abs` sensitive to cost units. This is a **known elementary invariance check**, not a novel theorem.

## D4. Required prospective runtime/manifest gate for M4 + M5 + C6

**M4 oracle checks, development only after authorization:** lock cocoex version and source, single-objective suite identity, problem `id_triple` for each allowed development cell, native domain, dimensionality and instance, objective-value/counter semantics, separately sourced exact `f_opt`, cross-checked `f(x_opt)`, forbidden optimizer access to oracle values, setup-cost and callback-accounting path. If exact optimum cannot be retrieved/cross-validated, do not invent or approximate an official oracle to claim normalized gaps; block the confirmatory definition. **No such runtime check was performed here.**

**M5 statistical checks before ANY holdout:** signed six K1–K6 family, strong E/D/DE/CMA/BIPOP baselines, method identities, L and target definitions, failure/invalid `L=1` policy and audit trail, nested bootstrap algorithm, estimator aggregation across (f,d,instance), paired seeds and method-specific RNG stream derivation, minimum seed and instance replication, uncertainty over rare failure, stop and missing-result rules.

**C6 freeze checks:** all experimental data/case IDs and software hashes, exact B objective vs OPF/PF distinction, final witness reservation, setup oracle costs, reason for 4096 public setup evaluations, source manifest, reviewer approval and dated freeze commit. A numerical pass of one existing ORPD case is **not** a substitute.

## D5. Conservative decision

**GO:** documentation and independent mathematical audit of the six formal contrasts; no-COCO synthetic proof examples; supervisor review of holdout count and f_opt access.

**NO-GO:** downloading/evaluating held-out COCO problems, treating a `final_target_fvalue1` as certified f_opt, running the originally estimated ~78 million objective attempts, or publishing a post hoc normalizer/stats family. **M4=runtime NOT_RUN, M5=UNFROZEN, M6=UNAPPROVED; C6=UNDECIDED.**
