**Verdict: REVISE.** [v2](/Users/danijel/Desktop/gadapt/research/ITERATION56_PROTOCOL.md) resolves much of 021, but several definitions still prevent freezing. No files changed.

1. **PARTIAL** — Exact selectors replace random upper bounds, but empty-pool handling and candidate sampling remain unspecified.
2. **PARTIAL** — Re-scalarization before truncation is fixed; refreshing merits, ordering and signals before parent selection is missing.
3. **PARTIAL** — Generation-only stopping and wrapper outcomes are specified; under-budget runs lack an analysis rule.
4. **RESOLVED** — Category-level tolerance, finite failure conventions and explicit exclusion from ε-feasibility are consistent.
5. **PARTIAL** — Paired time contrasts replace pooled ranks, but bootstrap strata and p-value edge cases need correction.
6. **RESOLVED** — Mediation is disclaimed; both signal normalizers and the SP encoding control are specified.
7. **RESOLVED** — Positivity checks and range/normalization diagnostics address the substantive concerns.
8. **RESOLVED** — Fixed σ preserves the operator, and attribution concerns the whole adaptive mutation policy.
9. **PARTIAL** — Pooling, weighting and tuning ties are specified; development targets and within-generation σ aggregation remain unclear.
10. **RESOLVED** — References span CHTs; negative gaps, absolute-plus-relative targets and no-reference fallback are explicit.
11. **PARTIAL** — Multiplicity and descriptive H56c are fixed; the proposed power simulation is not executable as specified.
12. **RESOLVED** — Initial-population assertions and separate processes are retained.
13. **RESOLVED** — Comparators are explicitly excluded; the base budget correctly totals **32.40 million PF calls**.

**New blocking problems / remaining specification gaps exposed by v2:**

- **Bootstrap target and p-values (§7).** Scenarios are fixed design cells, but resampling units within network×R randomizes their proportions. For inference conditional on these scenarios, resample complete paired arm vectors within network×R×scenario, retaining fixed scenario weights. State conditioning on frozen tuning/reference results. The stated p formula also returns **2** when every contrast is zero; define valid tie/degeneracy handling and cap p at 1.

- **Seed collisions under the permitted enlargement (§§2,7).** With 20 seeds, scenario \(j\), seed 11 equals scenario \(j+1\), seed 1. Enumeration gives **720 units but only 450 distinct seeds**. Use collision-free tuple encoding or explicit stream allocation covering development, references and both sample sizes.

- **Dynamic timing and AP counters (§4).** AP’s three-generation trigger does not specify resetting versus overlapping windows. EC defines τ at generation start, while the cost-finder recipe freezes parameters after evaluating offspring. Moreover, [the executor selects parents before invoking the cost finder](/Users/danijel/Desktop/gadapt/gadapt/execution/ga_executor.py:84). Freeze one event order: update parameters from completed history, refresh incumbent merits/order/signals, select parents, then evaluate and truncate consistently.

- **FX eligibility can be zero (§5).** [The actual pool](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/population_mutation/base_candidate_solution_mutation_selector.py:85) contains current-generation candidates with NaN cost, excluding immigrants and already-mutated offspring—including crossover-repair mutants. Specify uniform candidate sampling without replacement, \(k=0\) for an empty pool, and \(k\le|pool|\). Otherwise `max(1, round(...))` contradicts exact-count feasibility and FX-M’s fraction can divide by zero.

- **Development targets and power are circular/incomplete (§§5–7,10).** FX-T needs development T before references are scheduled; development references are absent from the 288-run budget. Generate and freeze development targets first. FX-T development covers only R=17, so final-analysis contrast distributions at R=9/33 are unavailable. Variance alone cannot specify a bounded, tied-outcome power simulation; freeze its distribution/extrapolation assumptions and simulation procedure.

- **Early termination (§§3,6).** Merely flagging an under-budget run does not define its primary outcome. Prespecify failure handling; assigning T=1 would conflate execution failure with complete-budget nonattainment.

ε₀ before truncation is sound; ε₀=0 simply collapses EC to FR. Capped T is valid as restricted attainment time.