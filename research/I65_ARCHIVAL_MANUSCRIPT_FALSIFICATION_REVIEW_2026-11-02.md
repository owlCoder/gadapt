# I65 archival manuscript claim verification and falsification review

**Date:** 2026-11-02. **Scope:** reproducibility of published manuscript-v0 claims against **existing immutable GitHub research JSON aggregates**, not new optimizer/PF/COCO experiments and **not** a re-run of statistical bootstrap algorithms.  
**Baseline Git HEAD examined:** `54e1094df528d4d4e4bfb5e7bb421dcf047e21b3`.  
**Machine-readable derived cross-check:** [`I65_ARCHIVED_CLAIM_RECHECK_2026-11-02.json`](I65_ARCHIVED_CLAIM_RECHECK_2026-11-02.json), independently generated from six raw repository JSON sources, with exact Git blob IDs, original counts, outcome labels and 5/5 passing invariants. All original source files remain **byte-identical**.

## A. Claims directly reproduced from existing aggregate archives

| v0 statement | Archival source / exact values | Source-level verdict |
|---|---|---|
| I49 original prevalence `4/9`, 95% `[0.14, 0.79]` | [I49 `integrity_audit.json`](results/iteration49/integrity_audit.json), Git blob `90c2cf30a8de715bd2bbb04055df48b031e2145d`: `4/9`, CI exact `[0.1369956623,0.7879914932]`, `COMMON` | **MATCH** |
| I50 initial `11/12` | [I50 aggregate](results/iteration50/integrity_audit.json), blob `6e421ccf858758533d782b7459778f7d83e421cc`: `11/12`, `REPLICATED`, CI `[0.6152038348,0.9978924068]` | **MATCH**, but **not an error rate** |
| I50 `4/12` when dropping C1 | [I50 classification](results/iteration50/classification.json), blob `c4a26682b2b47d7ff5cd8fee45f239feecc2fae8`: `4/12`, libraries evotorch, GFO, scikit-opt, SMAC; CI `[0.0992460911,0.6511244936]` | **MATCH**, **POST HOC**, not an independent preregistered main hypothesis |
| I50 `2/12` documented contradictions | Same classification source: GFO and SMAC, `2/12`, CI `[0.0208625255,0.4841377487]` | **MATCH** under its **specific documentation-contradiction rule**, not detector sensitivity |
| I52 cross-domain match `19/21` | [Original I52 aggregate](results/iteration52/integrity_dispatch.json), blob `c85b680cd536defc0d849d932855228c8223eb3c`: `19/21`, CI `[0.6962255931,0.9882506821]`, `H52 SUPPORTED`; disagree Nevergrad (10/15 environment errors) and SciPy DE (new R3, 5/15) | **MATCH**, with context/selection caveats |
| I55 21-library flags + strict H55d nonmatch | [I55 reclassification](results/iteration55/recompute.json), blob `759de302c9678b2319cdd2603f35fa38a5196eb0`: 8 libraries with non-C1 flags; `D3x_diff=[Nevergrad,SMAC]`; **exactly one** archive flag mismatch in emukit plateau 2D seed 6001, `C2:0→1` | **MATCH** for source-level classification; `620/620` seed-manipulation check appears in the original [I55 frozen report](legacy/flat/ITERATION55_REPORT_SR.md), **not separately recomputed from the full trace NPZ archive** |

**Source-level match is not an independent raw-experiment replication.** Original Clopper–Pearson intervals were also **independently recalculated from the published k/n counts** by exact-binomial-tail inversion (pure JavaScript, 80 bisection iterations per endpoint): **5/5 MATCH**, maximum absolute difference **1.5543122344752192e-15**. The exact [independent arithmetic ledger](I65_CP_INTERVAL_INDEPENDENT_RECHECK_2026-11-02.json) archives every original and recomputed endpoint. This confirms the interval **arithmetic**, **not** the statistical assumptions of sampled libraries, underlying raw trial data, causal findings, or a new optimizer run.

## B. Newly surfaced limitations requiring a mandatory manuscript addendum

### B1. Original I52 is still formally supported, but the 19/21 point ratio is not a universal transfer guarantee

The separately recorded [I52 post hoc sensitivity JSON](results/iteration52/sensitivity.json), blob `4c31e359c45af97afa5be68bc7e5c4c631c69a90`, gives:

| Analysis | Observed or hypothetical match | Inferential classification |
|---|---|---|
| Original frozen I52 | **19/21**; required threshold **at least 17** | **PRECOMMITTED H52 SUPPORTED** |
| Complete-only libraries (15/15 usable dispatch cells) | **17/18**; confusion `S1D1=7, S1D0=0, S0D1=1, S0D0=10` | **POST HOC sensitivity**, not a new primary p-value |
| Bounds when all missing dispatch cells are left unknown | **17/21 to 20/21** | **POST HOC worst/best missingness assignments** |
| Equalized synthetic exposure to actual usable dispatch cells | Expected agreement **18.693592**, distribution support **17–20**, `P(agreement≥17)=1` | **POST HOC conditional resampling model**, NOT an experiment replication |

**Important logical correction:** because the *smallest missingness-bound agreement equals 17*, the original preregistered **17-of-21 threshold remains satisfied** under the listed missingness assignments. Calling the H52 threshold “not robust” or overturned would be incorrect. What is not justified is the **exact 19/21 proportion under all missing-cell completions**, universal generality, or inference that agreement diagnoses true defects. The sensitivity JSON itself records `not_uniformly_robust=false` for the stated decision. The conclusion must simultaneously say **the original result survives this particular sensitivity** and **the precise transfer fraction is conditional**.

In the complete-only confusion, seven findings recur among seven original synthetic-positive libraries, but the one new SciPy DE R3 appears among synthetic-negative libraries. This is a description of **flag agreement**, not independent manual ground-truth specificity or algorithmic correctness.

### B2. Strict JSON incompatibility in the original I49 artifact

The original [I49 `integrity_audit.json`](results/iteration49/integrity_audit.json) contains exactly **33 unquoted `Infinity` tokens**, all observed as `g1_max_normalized_diff`-style metrics. **IEEE 754 infinity is valid in some Python internal data structures but bare `Infinity` is not valid RFC 8259 JSON.** A strict JSON parser rejects this source; `JSON.parse` did reject it in our independent read.

The derivative [machine-readable summary](I65_ARCHIVED_CLAIM_RECHECK_2026-11-02.json) performs a documented **inspection-only** replacement of colon-delimited `Infinity/NaN` tokens by `null` in its in-memory parse. The primary `4/9` prevalence and the relevant summary fields do not contain such nonfinite numbers. No `null`-substituted source is passed off as the historical original, and the derivative does **not** present those values as re-estimated measurements. **All 33 original tokens and the Git blob are preserved unchanged.**

**Publication correction required:** data availability section must warn that the I49 original is *Python JSON-ish*, not strict JSON. If a strict copy is ever distributed, it must be a separately named, visibly derived file with a schema and verified transformation; the immutable original must remain accessible.

### B3. Avoid conflating library-level flag prevalence with evidence of undocumented bugs

I49’s `4/9` includes known or documented deviations; I50’s `11/12` includes a low-specificity corner flag `C1`. Hence neither is a population estimate of “software bugs”, “industrial incidents” or true detector precision/recall. The I50 secondary **documentation-contradiction** denominator `2/12` and post hoc non-C1 `4/12` quantify **different targets**. I52 library-level transfer primarily tests same status in distinct application functions; the 19/21 status is not a general external physical validation of electrical networks.

### B4. Mismatched levels of replication and reference standards

Source JSON aggregates can verify claimed outcomes and label definitions. They do **not** independently establish causal software mechanisms, which remain grounded in frozen reports/code, or calculate uncertainty for unobserved library sampling. I55 raw NPZ trace-by-trace replay was not performed in this phase. The independently implemented NumPy Newton result verifies numerical PF software on a fixed **PYPOWER-sourced input case**, not a separately sourced physical dataset.

## C. External publication novelty challenge — sources verified outside the repository

- [Ravber et al. (2025), *Performance Comparison of Single-Objective Evolutionary Algorithms Implemented in Different Frameworks*](https://informatica.vu.lt/journal/INFORMATICA/article/1384/text), DOI [10.15388/25-INFOR603](https://doi.org/10.15388/25-INFOR603), already compares **framework implementations** and accounts for cross-language numerical differences and objective-evaluation runtime profiles. I65 cannot claim to be the first fair framework comparison.
- [Ruscheinski et al. (2025), *SIMPROV: Provenance capturing for simulation studies*](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0327607), DOI [10.1371/journal.pone.0327607](https://doi.org/10.1371/journal.pone.0327607), already monitors heterogeneous simulation tools, including wrapped functions, and aggregates provenance. I65 cannot claim to be the first cross-tool trace/provenance collector.
- [Lehre & Sutton (2025), *Runtime Analysis with Variable Cost*](https://link.springer.com/article/10.1007/s00453-025-01307-x), DOI [10.1007/s00453-025-01307-x](https://doi.org/10.1007/s00453-025-01307-x), already provides mathematical analysis with heterogeneous fitness evaluation cost. I65 cannot claim the first variable-cost runtime model.

Publisher/official full texts confirm article identity, authors, dates, and title. **Direct Crossref API is unavailable** (three URL attempts returned access errors in this session), so the repository's specific Crossref-API verification gate remains `UNVERIFIED`. No claim of exhaustive world-priority search is made.

## D. Required manuscript change list

| Priority | Change | Status / risk |
|---|---|---|
| P0 | Put `19/21` original plus I52 complete-only `17/18` and missingness `17..20/21` together, explicitly preserving original H52 result | **New addendum required** |
| P0 | Distinguish I50 `11/12`, *post hoc* `4/12`, and docs-contradiction `2/12` everywhere (including abstract) | Existing v0 mostly correct; protect against marketing simplification |
| P0 | Disclose nonstandard I49 source JSON's **33 Infinity tokens** and exact parse/release policy | **New data-availability addendum required** |
| P0 | Never label case14/39/118 AC cases as field measurements or one fixed case30 as industrial certification | Existing v0 correctly restricts; retain |
| P1 | Confirm full I55 `620/620` control and `318/358` sequence-byte match by separately reprocessing original NPZ if a method reviewer requires it | **NOT_RECOMPUTED** in this phase |
| P1 | Independent Clopper–Pearson **binomial interval arithmetic from k/n has been completed (5/5 PASS)**. If the venue requires re-estimation from **raw individual cells** or original **bootstrap**, that additional archival work remains **NOT_RECOMPUTED**; it must not be misrepresented as a rerun of stochastic optimizer trials |
| P1 | Challenge exact novelty against Ravber/SIMPROV/variable-cost analysis and evaluate detector **specificity** using an approved label policy | **ORIGINALITY OPEN** |
| P2 | Move paper from Markdown to venue-specific manuscript template and bibliography after deciding target venue, authorship and attribution | **PENDING HUMAN CHOICE** |

## E. Reviewer / supervisor GO–NO-GO

**Research question:** Are the frozen flags and cross-domain reproducibility findings sufficiently well defined and specific to sustain a publication about *evaluation integrity*, including a false-positive analysis and a simulator-resource-accounting demonstration?

**Closest prior art:** Ravber et al. 2025, DOI `10.15388/25-INFOR603`; SIMPROV 2025, `10.1371/journal.pone.0327607`; variable-cost runtime 2025, `10.1007/s00453-025-01307-x`.

**Precise novelty claim:** **NOT_ESTABLISHED**; potential applied contribution is independent black-box validity checks combining explicit call, reported-best and feasibility evidence with proven specificity boundaries and demonstrated cross-domain transfer, **not** first-of-kind profiling/provenance.

**Formal assumptions:** source artifacts are unmodified and correctly labeled; library-level outcomes use consistent definitions; no hidden solver calls are silently equated with objective attempts; physical numerical convergence and operational feasibility are separate.

**Falsification:** opposite labeled cases, false C1 flags, malformed data and uncharged witness events invalidate any broad guarantee. All historical negatives must be reported.

**Strong baselines:** original no-C1 I50 flag policy, valid corner-point controls, wrapper-only objective logs, source-aware PF/OPF logs, independently reconstructed AC dispatch.

**Budget this review:** **zero new solver calls/objective evaluations**. Only GitHub read API and publisher lookup. No experiments, no new method.

**GO:** complete red/green **source-document consistency corrections**, seek independent raw-array method check and supervisor contribution scope decision. **NO-GO:** new held-out COCO, candidate-C implementation or arbitrary data repair before M6/C1 and M4/M5/C6 are signed. Current state `novelty NOT_ESTABLISHED / NO-FREEZE / COCO NOT_RUN`.
