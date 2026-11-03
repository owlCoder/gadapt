# Manuscript v0 — Context-Dependent GAdapt Efficiency, Orthogonal Coupling and AC Feasibility

**Prepared:** 2026-11-02. **Draft only**, no new research run, no statistical recomputation and no human/supervisor approval. All figures below come directly from the locked I64 studies; the original designs remain distinct, and cross-study comparisons are **descriptive unless an original study provides an approved contrast**.

> **Source-verification addendum, 2026-11-02:** The numerical statements below were rechecked against the seven frozen I64-S0/E/R/E3/A/I/I2 reports (exact Git source identities preserved in [the audit](I65_ARCHIVAL_MANUSCRIPT_FALSIFICATION_REVIEW_2026-11-02.md)). This is a **report-level verification**, not an independent reanalysis of the original stochastic runs or bootstrap. S0's efficiency-at-B and final accuracy-at-original-stop metrics remain fundamentally distinct.

## Abstract

Claims that a genetic algorithm is generally more efficient must distinguish computational calls from iterations, transformation sensitivity from algorithm-specific parameters, and objective-value success from feasible electrical dispatch. We synthesize frozen, pre-specified GAdapt studies using a mentor's original configuration, stronger CMA/DE baselines, controlled orthogonal transformations, a fixed GAdapt→CMA hybrid and discrete AC optimal reactive-power-dispatch simulations. In 21 original benchmark cells, GAdapt-M achieved a higher evaluation-based ECDF area than DE under the tested mentor conditions (`0.698` versus `0.651`), while DE had a better final cell median in 14/21 cells. Across an extended stronger-baseline roster and transformations, GAdapt-M had aggregate ECDF area `0.6732` versus `0.7699` for IPOP, and the prespecified overall H64a direction was opposite to the original superiority claim. A matched-shift experiment attributed a `0.0809` area drop in GAdapt, versus `0.0101` in IPOP, to an added Haar-orthogonal transformation across the fixed tested cells. A fixed GAdapt→CMA hybrid increased rotated-function performance but failed the full precommitted decision family. Its tail advantage did not transfer to eight discrete ORPD cells, where the hybrid's feasibility was `0.742` versus `0.771` for IPOP and its tail CVaR was worse (`0.3772` versus `0.2518`). These context-dependent observations motivate mechanism-specific hypotheses and independently charged simulator evaluations, **not** a universal algorithm advantage or a novel algorithmic policy.

## 1. Research question and null-safe interpretation

**Question:** Under actually counted objective calls, which *specific* transformations and operational-constraint contexts degrade or preserve GAdapt-M relative to strong DE/CMA-family baselines, and do synthetic-function improvements transfer to discrete power-flow-constrained tasks?

The aim is an accurate synthesis of bounded empirical evidence. Repeated genetic-algorithm switching, CMA restarts, ECDF and source provenance are known prior art, and these experiments are neither new random samples nor independent evidence of numerical-model field validity. Their source is the historical I64 program, not an I65 confirmatory study.

## 2. Frozen sources and non-interchangeable designs

| Study | Design and what can be inferred | Critical constraint |
|---|---|---|
| [S0](ITERATION64_S0_REPORT_SR.md) | Original mentor setup: 21 function–dimension cells × four configurations × 20 seeds; real call count vs generation count; original H64a supported in this **four-method** comparison | Comparator roster and stopping configuration differ from E; do not attribute cross-study differences purely to Q |
| [E](ITERATION64_E_REPORT_SR.md) | 63 transformed cells, nine configurations, 100 seeds, **equal 12,000 objective-call budgets**; 16 simultaneous contrasts | Strong CMA, IPOP and BIPOP overturn overall GAdapt advantage; do not extrapolate to every possible configuration |
| [R](ITERATION64_R_REPORT_SR.md) | Original (21) fixed function–dimension pairs and a *matched-shift* added Haar-orthogonal Q, 100 seeds, simultaneous four-contrast intervals | Q can reflect as well as rotate; inference conditional on selected matrices, cell mix and only two compared methods |
| [E3](ITERATION64_E3_REPORT_SR.md) | Fixed 30%-GAdapt / 70%-CMA search allocation versus E archival paired cells | Original+shift tail penalty violated a frozen criterion; no general novel hybrid |
| [A](ITERATION64_A_REPORT_SR.md) | Replaces initial 30% GAdapt by random sampling, keeping CMA phase setup fixed | Valid **within that setup**; CMA `sigma0=0.05` tailored for GAdapt initialization, possibly confounding pure seed-quality claims |
| [I](ITERATION64_I_REPORT_SR.md) | Eight discrete ORPD cells, 30 seeds, originally counted 12,000 numerical PF calls, feasibility + CVaR | Public AC simulator cases, not observed power-system operational trials |
| [I2](ITERATION64_I2_REPORT_SR.md) | Paired fixed hybrid on those same eight ORPD cells | Hybrid's tail comparison against IPOP has **opposite** outcome; do not retune to reverse it |

## 3. Observed results

### 3.1 Original mentor comparison — efficiency is not final accuracy

The [S0 report](ITERATION64_S0_REPORT_SR.md) gives GAdapt aggregate `A=0.698`, SciPy DE `A=0.651`, and lower early-call best-so-far normalized gaps for the tested original group. Yet DE wins the *final* cell-median comparison in **14 of 21** original cells, as recorded in the [cross-study synthesis](EVIDENCE_SYNTHESIS.md). The observed mean calls per completed run also differ because of callback, validation and library-specific work. **The result is a conditional evaluation-efficiency advantage, not general accuracy superiority.**

### 3.2 Matched budgets and stronger baselines reverse the hierarchy

The [E report](ITERATION64_E_REPORT_SR.md) gives equal-cell-weight ECDF areas `A(GAdapt)=0.6732`, `A(CMA)=0.7618`, `A(IPOP)=0.7699`, `A(BIPOP)=0.7688`, `A(DE)=0.6396`. Sixteen simultaneous comparisons in the original precommitted H64a family yielded an **opposite** verdict. This demonstrates that a GAdapt favorable comparison within the original four-method mentor setup does not establish an advantage against optimized stronger CMA families under transformed objectives. It does **not** isolate *why* the cross-study hierarchy changes, because S0/E experimental contexts differ.

### 3.3 Controlled orthogonal perturbation isolates a limited Q effect

The [R report](ITERATION64_R_REPORT_SR.md) constructed a matching translation variant to isolate the effect of adding **Haar-orthogonal** Q within 21 fixed cases. For GAdapt, `A(shift)-A(rotm)=0.0809`, simultaneous interval **[0.0721,0.0897]**; for IPOP, the same contrast is `0.0101`, interval **[0.0036,0.0166]**. Their difference is `0.0708`, simultaneous interval **[0.0598,0.0818]**. The prespecified R hypotheses passed. It supports a **conditional effect of the tested Q transformations** and comparative sensitivity, not a universal assertion about rotations or a known causal GAdapt mutation mechanism.

### 3.4 Hybrid helps rotated synthetic cases but fails its total decision rule

The [E3 report](ITERATION64_E3_REPORT_SR.md) finds rotated-function `A(GAdapt)=0.6167`, `A(hybrid)=0.7196`, `A(IPOP)=0.7630`. The hybrid's A improvement relative to GAdapt is supported, as is a rotated tail improvement. But the non-rotated tail criterion was **opposite**, IPOP noninferiority was **undecided**, and the **overall frozen H64g outcome was NOT supported**. The [A ablation](ITERATION64_A_REPORT_SR.md) shows replacing the fixed first GAdapt stage with uniform samples harms that exact subsequent CMA arrangement, but this does not isolate a general causal advantage independent of the preset CMA step-size and restart settings. The hybrid is an established composition, **not a proven original I65 method**.

### 3.5 AC-dispatch transfer rejects a blanket hybrid advantage

The paired [I/I2 reports](ITERATION64_I_REPORT_SR.md), [I2](ITERATION64_I2_REPORT_SR.md) show 12,000 original numerical PF evaluations per ORPD run and eight cells. IPOP achieves aggregate feasibility **0.771** and tail CVaR **0.2518**; GAdapt-M **0.746** feasibility and CVaR **0.2973**; the fixed hybrid **0.742** feasibility and CVaR **0.3772**. The I2 criterion against GAdapt-M is **undecided**, while against IPOP it is **opposite**. The tested hybrid recipe cannot be recommended as a reliable AC-dispatch improvement from these results. The cases are synthetic/public network models and their original I56-style constraints do not certify all industrial power-engineering conditions.

Later independently coded NumPy Newton [dispatch verification](I65_INDEPENDENT_DISPATCH_RESULT_2026-11-02.md) on a single **previously used development midpoint** further demonstrated that two numerical PF solvers may converge while original reactive limit violation remains around **0.5991**, with `feasible=false` in both implementations. This is a **software-integrity follow-up, not a new optimization result**.

## 4. Scientific conclusion that survives adversarial review

**Supported within the fixed studies:** GAdapt's behavior is **strongly conditional** on baseline roster, budget accounting, objective transformation and feasibility rules. An actual matched Q design supports higher sensitivity of GAdapt than IPOP on selected problems. A phase-based hybrid can improve some synthetic ECDF outcomes but did **not** deliver approved overall or ORPD-tail superiority. Negative and stopped studies cannot be rewritten as positive confirmation.

**Not supported:** universal optimizer superiority, a novel GAdapt→CMA switching mechanism, causal identification of an internal GAdapt component responsible for Q sensitivity, field-measured network feasibility, strong generalization from three new held-out COCO instances, or a frozen I65 statistical protocol.

## 5. Proposed future methodological improvement, NOT executed

For independent peer review, a future protocol could explicitly preregister *matched* transformations, physical resource-vector budgets, independent AC oracle requirements, baselines GAdapt-M/DE/CMA/IPOP/BIPOP, and model-class diversity. It should separate **function/instance randomness** from **algorithm-seed randomness** and report both objective-call and wall-time sensitivity without conflating them. The previously proposed I65 held-out f21/f24 study is **NO-FREEZE** and cannot be used as a substitute for missing causal-mechanism evidence.

## 6. Publication position

This is a potential descriptive/empirical thesis chapter, **not an experimentally validated novel method**. The mentor must decide whether this class of context-specific negative-aware study meets the institution's doctoral-originality requirement. The [recommended resolution](I65_RESEARCH_RESOLUTION_RECOMMENDATION_2026-11-02.md) prioritizes a separate evaluation-integrity manuscript with direct measurement and specificity falsification as the more clearly defensible methodological contribution. No new GAdapt package code, official held-out COCO runs or optimizer search is authorized by this draft.

## 7. Source verification and interpretation addendum — 2026-11-02

The values here were checked against original source reports, not recomputed from full archived `research/results/iteration64_*` datasets. The Git source blobs are `S0=fcb755f7f91190b40cfcd6ba1b2d6c3f6ae18b45`, `E=6471553e1aa9830559963bd0a2bf853a51d931ad`, `R=fa26f19346edcc63245f7953ecd659e822c922a9`, `E3=db84414824490bc9bb0c67b6b5463dd945acdb9c`, `A=60df2b027444c028abf513a70fa40e0fc42434b1`, `I=d834ff48fe4ed253a8cefa4c931a564b23a268f8`, `I2=714b6d1d1e330ce83276aec8e4a8ebef20ff9973`.

**S0 estimands differ:** `A=0.698` (GAdapt) versus `A=0.651` (DE) is evaluation-based *anytime ECDF through 12,000 physical calls*. The final median statement **DE wins 14/21 cell medians** is based on the algorithms' **original stopping points**, not a matched final budget. This distinction is explicit in the frozen [S0 conclusion](ITERATION64_S0_REPORT_SR.md). The observed main claim cannot be rephrased as “GAdapt universally achieves better equal-budget final accuracy.” The original mentor-run comparator setup also incurred hidden validation/callback calls; do not substitute generation count for physical evaluations.

**E is a stronger but distinct design:** its result `A=0.6732` versus IPOP `0.7699` reflects **63 cells, nine methods, 100 seeds and equal 12,000 calls**, with its actual statistical comparison family. Contrasting this with S0 identifies *design-conditioned ranks*, not a controlled causal difference caused solely by adding baselines.

**R isolates the Q contrast only within the matched-shift design:** the precommitted difference-in-effects `0.0708` and simultaneous interval `[0.0598,0.0818]` hold for the **21 studied function-dimension pairs and their fixed Haar-orthogonal matrices**. Q may contain a reflection; “pure rotation” would overstate the model.

**E3 and I2 protect the negative conclusion:** E3's overall hybrid hypothesis was not supported; the I2 experiment reported an opposite hybrid-vs-IPOP **tail** conclusion. These are different response surfaces and feasible-set definitions, not an independently proven causal transfer coefficient.

**Research validity:** no trial/seed labels were retrieved or resampled in this review; bootstrap confidence intervals retain their original provenance and limits. Novelty and independent physical-grid validation remain **NOT_ESTABLISHED**, with no I65 candidate-C or held-out COCO execution.

## 2026-11-03 — Post hoc function-family and ORPD cell influence (draft)

The original I64-R seed-conditional, four-contrast simultaneous test remains supported on 21 fixed function/dimension pairs and orthogonal Q matrices: c4 = 0.070791780, original 95% simultaneous CI [0.059811870, 0.081771690]. A NEW EXPLORATORY leave-one-family-out point calculation using the original function weights, renormalized after dropping each family, yields c4 = 0.040866088 without the Rastrigin family, versus c4 = 0.055752905 without Styblinski-Tang. There is no new subset confidence interval or replacement H64r3 decision. This reveals dependence on the chosen benchmark families, not a general causal mechanism.

The original I64-I2 simultaneous tail result for the full eight-cell ORPD set remains H64h2 opposite: CVaR(IPOP) minus CVaR(hybrid) = -0.125306761 with archived interval [-0.250223907, -0.000389615]. Direct recomputation from 16 original compressed I/I2 per-cell archives covering 720 run outcomes finds that case39 / j=3 contributes -0.125 of the eight-cell mean (approximately 99.755% of its net signed negative value). IPOP is feasible 30/30 in that cell, versus hybrid 27/30, with the three original no-feasible-witness hybrid seeds 68003015, 68003018 and 68003028. Removing this cell gives a post hoc seven-cell point -0.000350584 with no new simultaneous interval. In case39 / j=4 all three CVaR values saturate at 1 even though feasible counts differ (GAdapt 0/30, hybrid 1/30, IPOP 5/30). Both CVaR and feasibility are necessary for interpretation. All conclusions are limited to registered tasks, and no optimizer, physical PF validation, full NPZ or bootstrap experiment was rerun. Source-level tables and figures: [I64 influence report](i65/archive_review/I65_I64_R_I2_ADVERSARIAL_INFLUENCE_REVIEW_2026-11-03.md).


## 8. Exact I64-I2 bootstrap reproducibility and post hoc cell-sensitivity addendum — 2026-11-03

From 720 original archived I64-I/I2 outcomes, the independent 20,000-sample paired bootstrap using default_rng(68) matched **all 13 frozen numerical values exactly** (four estimates, eight simultaneous interval endpoints and t*=3.4133099733799344). This verifies the archived statistics but does NOT replay optimizer/PF/OPF trajectories or independent physical witnesses. Original H64h1=UNDECIDED and H64h2=OPPOSITE remain unchanged.

The original eight-cell IPOP-minus-hybrid tail contrast was -0.125306761, registered CI [-0.250223907,-0.000389615]. One inspected ORPD cell (case39/j=3) contributes roughly 99.755% of the negative signed total. Excluding that cell **post hoc** and running a separate 20,000-draw seed-only simultaneous max-t bootstrap gives -0.000350584, exploratory interval [-0.001306191,+0.000605023]. Its selected seven-cell GAdapt-minus-hybrid contrast is +0.003933286, exploratory interval [+0.002046149,+0.005820422]. Because exclusion was selected after inspecting results, both intervals reflect a changed estimand and have NO adjustment for cell selection; they must NOT be used to replace prespecified H64h1/H64h2, claim an independently confirmed hybrid advantage or establish optimizer novelty. [Source-anchored audit](i65/archive_review/I65_I64_I2_EXACT_BOOTSTRAP_AND_POSTHOC_AUDIT_2026-11-03.md).


## 8. Addendum — rare-failure uncertainty and tail-estimand sensitivity (2026-11-03)

The [independent I64-I2 rare-failure audit](i65/archive_review/I65_I64_I2_RARE_FAILURE_AND_MONTE_CARLO_STABILITY_REVIEW_2026-11-03.md) clarifies a distinction relevant to the paper's scientific conclusions. The registered H64h2 `OPPOSITE` verdict remains supported by the original, independently reproduced simultaneous eight-cell CVaR interval; the negative upper bound also persisted in **12 × 20,000 and 3 × 100,000** exploratory matched bootstrap replications using different RNG seeds. This is stability of *Monte Carlo approximation conditional on the archived outcomes*, not proof across additional power-network instances.

In the single post hoc selected influential cell `case39/j=3`, the hybrid fails to return a feasible candidate in three of 30 seeds and IPOP in zero of 30. Exact marginal 95% binomial intervals for **failure probability** are `[0.0211,0.2653]` and `[0,0.1157]`; exact paired two-sided McNemar is `p=0.25`. The cell-specific binary-feasibility comparison is therefore **not independently established** as significant at 5%, and is a *different* statistical question from the original registered CVaR contrast. The worst-three-of-thirty CVaR aggregates failure severities discretely; exploratory use of worst-six or all-thirty losses changes the magnitude and the fraction contributed by that influential cell. None of these post hoc comparisons changes the archived H64h2 result, adds independent power-engineering field validation, or establishes new algorithmic originality.
