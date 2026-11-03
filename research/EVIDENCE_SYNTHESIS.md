# GAdapt evidence synthesis — one English entry point for historical results

**Evidence cut-off:** 2026-11-01, repository `owlCoder/gadapt`.  
**Nature:** a cross-study **review**, not a translated source report, rerun, meta-analysis, new experiment or preregistered result. Source protocols, raw archives and contradictory or negative conclusions remain authoritative. This file was prepared by reading the linked reports and the existing thesis drafts; statements must not be extended beyond the exact studied cells.

## Executive outcome

**There is a defensible empirical characterization of GAdapt, but no established original optimization algorithm, general superiority or production-ready infrastructure guarantee.** Evaluation efficiency, final accuracy, feasibility and tail risk favor different methods in different conditions. The original mentor benchmark and later shifted/rotated and discrete-ORPD tests must be reported **together**.

| Research question | Strongest evidence | Defensible outcome | Important restriction |
|---|---|---|---|
| Is GAdapt efficient on the mentor's original functions? | [I64-S0](ITERATION64_S0_REPORT_SR.md) | On 21 original cells with four methods, ECDF A=**0.698** for GAdapt and **0.651** for SciPy DE; frozen H64a supported | DE had a smaller final cell median in **14/21** cells; original stopping and equal budgets are different comparisons |
| Does that efficiency survive harder transformations? | [I64-E](ITERATION64_E_REPORT_SR.md), [I64-R](ITERATION64_R_REPORT_SR.md) | Across the extended E roster, A GAdapt=**0.6732**, IPOP=**0.7699**, BIPOP=**0.7688**. At matched shifts Q decreases GAdapt A by **0.0809** versus **0.0101** for IPOP | R uses 21 fixed function–dimension pairs, one sampled Q per pair; not all transformations or industrial problems |
| Can an opt-in GAdapt operator close the gap? | [E2](ITERATION64_E2_REPORT_SR.md), [E4](ITERATION64_E4_REPORT_SR.md), [C](ITERATION64_C_REPORT_SR.md) | Differential crossover fails its primary conditions; compensatory mutation's small change cannot be distinguished from negative controls; proposed diversity-coefficient signature is undecided | These experiments do not identify a universal mechanism |
| Is GAdapt→CMA a new or better general optimizer? | [E3](ITERATION64_E3_REPORT_SR.md), [A](ITERATION64_A_REPORT_SR.md), [I2](ITERATION64_I2_REPORT_SR.md) | Fixed 30/70 hybrid helps some synthetic cases; a GAdapt first stage contributes against random sampling in that **fixed** setup | Hybrid is not methodologically novel; preregistered E3 overall outcome is mixed; **ORPD transfer not confirmed** |
| Does GAdapt solve discrete infrastructure tasks robustly? | [I](ITERATION64_I_REPORT_SR.md), [I2](ITERATION64_I2_REPORT_SR.md) | At 12,000 actual PF calls over eight cells, GAdapt feasible fraction **0.746**, IPOP **0.771**; hybrid **0.742** | Small set of networks and 30 seeds; IPOP's ORPD CVaR **0.2518** vs hybrid **0.3772**; no industrial reliability |
| Can we trust optimization-library evaluation accounting? | [I49](legacy/flat/ITERATION49_REPORT_SR.md), [I50](legacy/flat/ITERATION50_REPORT_SR.md), [I52](legacy/flat/ITERATION52_REPORT_SR.md), [I55](legacy/flat/ITERATION55_REPORT_SR.md) | The audit found recorded/documented inconsistencies, with I49 positive prevalence finding **4/9** libraries and further transport to real AC dispatch in I52 | Prior instances of the underlying defects were already known; I50 revealed a nonspecific C1 detector; originality of integrated audit not established |
| Does constraint handling make GAdapt faster? | [I56](legacy/flat/ITERATION56_REPORT_SR.md), [I58](legacy/flat/ITERATION58_REPORT_SR.md), [I60](legacy/flat/ITERATION60_REPORT_SR.md), [I59](legacy/flat/ITERATION59_REPORT_SR.md) | I56 has a small localized adaptation × constraint-handling interaction, θ≈**+0.0205** [**0.0020, 0.0396**] | H58 and H60 failed to confirm speed improvements; I59 stopped at developmental NO-GO; the interaction was **not** independently confirmed |

## Historical sequence without document duplication

### 1. I41–I48: mechanisms, limits and falsification

- **I41 and I42:** Certified row reductions and the H1 structural VIG proposal did not pass their methodological/structural novelty gates. The [I42 report](legacy/flat/ITERATION42_REPORT_SR.md) explicitly gives **H1 NO-GO**, not an optimizer innovation.
- **I43–I46:** An evaluation/optimizer-operator deficit was investigated. [I43](legacy/flat/ITERATION43_REPORT_SR.md) remained **UNRESOLVED**; [I45](legacy/flat/ITERATION45_REPORT_SR.md) found GAdapt-specific weakness in 5/6 selected comparisons; [I46](legacy/flat/ITERATION46_REPORT_SR.md) did not isolate a causal component.
- **I47:** A linear diversity metric improved unit invariance as an opt-in engineering property but did **not** establish an AC-dispatch performance gain. See [I47](legacy/flat/ITERATION47_REPORT_SR.md).
- **I48:** On multimodal valve-point dispatch, IPOP-CMA-ES was significantly better than GAdapt on two of three evaluated instances. See [I48](legacy/flat/ITERATION48_REPORT_SR.md). This rules out a blanket GAdapt superiority narrative.

### 2. I49–I55: measurement integrity as a potentially publishable empirical line

- [I49](legacy/flat/ITERATION49_REPORT_SR.md) validated an audit tool against injected defects and reported classified findings in 4/9 libraries, with a wide Clopper–Pearson 95% interval [0.14, 0.79]. **None of the four individual findings was first discovered here.**
- [I50](legacy/flat/ITERATION50_REPORT_SR.md) introduced an independent new sample and found that the original C1 class was not sufficiently specific. This limits the scope of any claim about tool validity.
- [I52](legacy/flat/ITERATION52_REPORT_SR.md) applied instrumentation to real AC-dispatch objective evaluations and supported its prespecified transfer hypothesis. It also documents mechanisms in SciPy/scikit-opt rather than asserting a general new theory.
- [I55](legacy/flat/ITERATION55_REPORT_SR.md) provides corrected D3x and call-trace archive evidence, including reproducibility limitations. A standalone paper still needs independent detector-validity review, a clearly differentiated contribution and complete source/trace reproducibility.

### 3. I56–I63: constrained infrastructure optimization, with STOP outcomes retained

- [I56](legacy/flat/ITERATION56_REPORT_SR.md) identified a **small, local** interaction between adaptation and constraint handling under its preregistered design, concentrated in case14. It cannot establish a universal mechanism.
- [I57](legacy/flat/ITERATION57_REPORT_SR.md) was descriptive external context, not a confirmatory equivalence or superiority proof: CMA-ES with margins can be faster on case14, while GAdapt often shows more feasible hits on case57 under the tested model.
- [I58](legacy/flat/ITERATION58_REPORT_SR.md): FR versus penalty θ≈**−0.014** [**−0.035, +0.006**], outcome **N**. [I60](legacy/flat/ITERATION60_REPORT_SR.md): epsilon-handling θ≈**−0.011** [**−0.035, +0.012**], outcome **N**. Neither confirmed the anticipated acceleration.
- [I59](legacy/flat/ITERATION59_REPORT_SR.md) met a prespecified **development NO-GO**, so it supplies **no telecom confirmatory outcome**, not evidence of a negative confirmatory effect.
- [I61](legacy/flat/ITERATION61_REPORT_SR.md) and [I63](legacy/flat/ITERATION63_REPORT_SR.md) stopped on their frozen calibration gates: **no confirmatory replication** of H56a. [I63-D](legacy/flat/ITERATION63D_REPORT_SR.md) is *descriptive* only: θ₆₃=**0.0139**, 95% interval [**−0.0090, 0.0372**]; it did not supersede I63's STOP.

### 4. I64: mentor benchmark replicated, extended and challenged

- **S0:** Real evaluation-call accounting separated search from validation, callbacks and PyGAD re-evaluations. GAdapt's better aggregate ECDF A does not mean it wins most final-median cells or is consistently more accurate. See [S0](ITERATION64_S0_REPORT_SR.md).
- **E:** Equal physical-call, stronger baselines reverse the main efficiency hierarchy: **IPOP/CMA/BIPOP outrank GAdapt** in aggregate A. See [E](ITERATION64_E_REPORT_SR.md).
- **R:** A matched-shift comparison supports greater loss for GAdapt from an added Haar-orthogonal Q. Haar Q can include reflection, so it is **not strictly rotation**; mechanisms were **not** isolated. See [R](ITERATION64_R_REPORT_SR.md).
- **E2/E4/C:** The opt-in fixes/mechanism claims did not pass their required decision families. See [E2](ITERATION64_E2_REPORT_SR.md), [E4](ITERATION64_E4_REPORT_SR.md), [C](ITERATION64_C_REPORT_SR.md).
- **E3/A:** A GAdapt→CMA hybrid improves some synthetic outcomes; the A ablation identifies a first-stage effect *conditional on the fixed σ₀=0.05 setup* rather than a universal GAdapt advantage. See [E3](ITERATION64_E3_REPORT_SR.md) and [A](ITERATION64_A_REPORT_SR.md).
- **I/I2:** On actual power-flow evaluations, the hybrid does not show confirmed superiority to GAdapt and has a worse tail than IPOP. I2's `i_run_sha256` provenance field was empty in the original archive and supplemented later, a discrepancy to disclose, not silently repair. See [I](ITERATION64_I_REPORT_SR.md), [I2](ITERATION64_I2_REPORT_SR.md).

### 5. I65: proposed only, not an observed optimizer

The [I65 DRAFT](ITERATION65_DRAFT_PROTOCOL_SR.md) proposes stopping, restarting or switching policies around a 20-*completed*-generation significant-improvement detector on held-out COCO f21/f24. [Prior art](ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md) already covers IPOP/BIPOP, memetic hybrids and switching. **`novelty not established`; no FREEZE; zero confirmatory f21/f24 runs.** A restricted instrumentation subset passed local synthetic checks, but GAdapt/CMA/COCO integration and true witness checks remain **NOT_TESTED**. See [instrumentation gate](ITERATION65_INSTRUMENTATION_GATE_REPORT_SR.md) and [migration gate](ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md).

## Quality and claim-control table

| Claim type | What may be stated | What may NOT be stated |
|---|---|---|
| Efficiency | Better ECDF area for GAdapt on *specific S0 cells* | Generally fastest across transformed functions |
| Accuracy | Better weighted aggregate cell medians in S0 at *original stopping* | More accurate than DE on most cells or at every budget |
| Stability | Some controlled tail and feasibility comparisons | Near-zero failure probability, deployment reliability or universal guarantee |
| Novelty | Specific empirical characterization and audit tooling as research contributions **subject to review** | New restart algorithm, first proof of EAF/ECDF or first ever evaluation-integrity detector |
| Scientific independence | Original sources, frozen negative outcomes and declared protocol deviations remain accessible | Recast I59/I61/I63 STOP as successful or failed confirmation |
| Industry | A constrained shortlist and independent verification workflow | Safe production ORPD optimizer without separate validation |

## Practical reuse

For literature, cite the **underlying frozen report**, not this synthesis as if it were primary evidence. For doctoral writing, align [thesis chapter map](thesis/) and [supervisor briefing](MENTOR_SUMMARY_2026-10-28_SR.md). For execution, use [legacy compatibility](compat/) and only run cheap tests after full-clone verification; do not rerun experiments to seek positive results. For the current decision gate, see [Research direction](RESEARCH_DECISION_2026-11-01.md).

## 2026-11-03 — Source-anchored I55 and I64 post hoc sensitivity integration

[New integrated audit](i65/archive_review/README.md) and [scientific summary](I65_MAIN_INTEGRATION_AND_THESIS_SUMMARY_2026-11-03.md) provide read-only independent consistency checks without changing registered results. For I55, full call-digest equality I50/I55 is 318/358, while binary C/R presence equality is 357/358; one emukit C2 presence changes 0 to 1 and its raw C1 count changes 2 to 3. Only four NPZ files were independently rehashed and ten emukit plateau traces reclassified; the complete 620-trace NPZ replay is not yet run. For I64-R, registered fixed-design c4 = 0.07079 remains supported with original interval, but post hoc leave-Rastrigin-out point c4 = 0.04087 (no new CI). For I64-I2, the predeclared opposite tail conclusion remains intact, but a single ORPD case39/j=3 cell explains about 99.755% of the signed negative point contrast; three hybrid seeds lacked feasible witnesses. Neither observation is a new registered inference, an algorithmic novelty proof or model-independent physical validation. Local synthetic and derived-ledger suite: 77/77 pass; full source bootstrap not rerun.


### I65 archival statistical replay update — 2026-11-03

The *original* I64-I2 20,000-draw matched bootstrap is independently reproduced from source-derived archived outcomes: all 13 numeric estimates/bounds/critical t* match exactly. Registered H64h2 stays OPPOSITE. A separately selected **post hoc** seven-cell bootstrap after removing case39/j=3 yields an exploratory IPOP-minus-hybrid CVaR interval [-0.001306191,+0.000605023] which includes zero. This does not replace or contradict the original fixed eight-cell inference and is not corrected for choosing the excluded cell after seeing the data. See [exact replay and limitations](i65/archive_review/I65_I64_I2_EXACT_BOOTSTRAP_AND_POSTHOC_AUDIT_2026-11-03.md).


### 2026-11-03 supplementary I64-I2 uncertainty audit (post hoc, not original confirmation)

The [source-anchored rare-failure report](i65/archive_review/I65_I64_I2_RARE_FAILURE_AND_MONTE_CARLO_STABILITY_REVIEW_2026-11-03.md) separates the frozen **eight-cell H64h2=OPPOSITE CVaR tail conclusion** from the distinct and much less precisely estimated probability of finding a feasible solution in one influential cell. That selected cell has three hybrid feasible-hit failures versus zero for IPOP (30 paired seeds); exact two-sided paired McNemar **p=0.25**, without correction for selecting the cell from outcomes. Thus the CVaR finding does not establish a statistically significant difference in that single cell's binary failure frequency. Twelve 20k and three 100k re-seeded original-method bootstrap computations over previously archived outcomes retained a negative simultaneous CVaR upper bound. This conditional numerical stability does **not** generalize beyond the fixed cells, nor establish optimizer originality. Source code, original negative findings and protocols remain unchanged.


## 2026-11-03 I64-R archival sufficiency and function-family stress addendum

The [new I64-R read-only audit](i65/archive_review/I65_I64_R_OFFGIT_SOURCE_AND_FUNCTION_FAMILY_STRESS_2026-11-03.md) establishes that the original 4,200-run `rotm` R archive (~8 MB) was **intentionally stored outside Git** (historical 2026-10-29 progress log), while `analysis.json.gz` and `check_repro.json.gz` are tracked. Thus the original seed-level 20,000-draw R simultaneous bootstrap **has not been independently replayed** from the current Git checkout, even though 21 reported per-pair point means can be reweighted and original conclusions remain H64r1/r2/r3 **SUPPORTED** for the frozen design. Post hoc leave-two-function-family-out stress has **8/36** c4 estimates below 0.05; an illustrative 100,000-resample nine-family percentile envelope [0.0115,0.1455] **is not a CI** because function families were selected deliberately. By contrast the I64-I2 original bootstrap was independently replayed. Recover original off-Git R source and full trusted digest; do not fabricate substitute measurements or infer a novel optimizer theorem.

## 2026-11-03 — I52 independent chance-adjusted and exact-class transfer review

A read-only new [I52 class-transfer audit](i65/archive_review/I65_I52_CHANCE_CORRECTED_AND_CLASS_TRANSFER_REVIEW_2026-11-03.md) reclassified the original 21 eligible libraries from frozen source classifications. It reproduces the registered H52 19/21 status matches and computes *post hoc* Cohen kappa 83/104 = 0.7980769 (7 true-positive classifications in both domains, 12 negative in both, one discordant in each direction). At exact (library,class) identity, only 7/10 synthetic class pairs recur on AC dispatch and there are eight AC class pairs, giving Jaccard 7/11. Complete-only 17/18 has descriptive kappa 70/79; missingness range 17..20/21 retains the original >=17 threshold. **Do not report agreement as ground-truth detector specificity, independent defect validation, or a new preregistered result.** The original I50 post hoc C1 exclusion 4/12 and all I55/COCO/novelty caveats remain binding.



### 2026-11-03 — I55 negative-control interpretation tightened

The [independently audited original 620 valid I55 cell digests](i65/archive_review/I65_I55_CONTROL_CONDITIONED_HASH_SEED_REVIEW_2026-11-03.md) separate 30 SMAC cells with stable same-seed controls but different-seed trace divergence from five Nevergrad cells divergent with **both** same and different hash seeds. Another 585 cells are stable in both comparisons; 10 errors remain outside the valid denominator. Do not interpret all 35 cross-seed differences as 35 identified seed effects. This decomposition is post hoc source validation of mechanisms **already discussed in the original I55 report**; all original registered decisions remain intact. Complete raw 620-NPZ trace replay and independent detector specificity are still missing.


### I55 provenance addendum — 2026-11-03

An independent untruncated Git-tree inventory confirms exactly **620 original I55 NPZ blobs** (12,319,037 compressed bytes, 21 libraries) are still present in the repository, with **zero changed path/blob identities** between frozen original commit `6b56fbc` and previously inspected `main`. Ten absent Nevergrad files correspond to historical failed runs. The [620-entry Git blob manifest and read-only byte gate](i65/archive_review/I65_I55_NPZ_GIT_ARCHIVE_COMPLETENESS_AND_PROVENANCE_2026-11-03.md) support a future fully authenticated trace replay without rerunning optimization; full 620 source bytes, `x/f/phase` arrays and detector flags **have not yet been rechecked in this container**. This is an archive reproducibility audit, not independent software defect ground truth or a preregistered positive test.


### I65 — I55 620-NPZ source chain (2026-11-03; full numerical replay NOT RUN)

The pinned original source tree still contains 620 unchanged I55 NPZ files (12,319,037 compressed bytes). A new fail-closed four-stage runner now authenticates the original file manifest, independently queries the frozen original Git tree, verifies all local binary bytes, and then invokes the original A-trace SHA-256 and flag replay. It can execute via a manual-only GitHub Actions workflow; this action has NOT been dispatched, and the all-620 raw numerical replay remains NOT_RUN. 25/25 synthetic code-gate checks passed locally. The archived A-prime and B process traces are not contained in the 620 A-process NPZ files. Do not convert this infrastructure check into new experimental support, new detector-specificity evidence or a changed H55d verdict.
