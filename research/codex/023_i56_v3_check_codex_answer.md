**Verdict: REVISE.** Read-only; no files changed.

Six blocking gaps from 022:

- Bootstrap — **RESOLVED:** fixed scenario strata/weights, conditioning and capped p-values.
- Seeds — **OPEN:** §2’s formula is collision-free, but §6 retains `900000+`.
- Dynamic timing/AP — **RESOLVED:** the cyclic order matches the [executor](/Users/danijel/Desktop/gadapt/gadapt/execution/ga_executor.py:78); counter resets prevent overlapping windows.
- FX eligibility — **OPEN:** the main formula handles empty pools, but FX-M’s later unconditional `max(1, …)` contradicts it.
- Development targets/power — **OPEN:** references and their budget are fixed; rehearsal still lacks scenario extrapolation and an explicit joint θ_a simulation.
- Early termination — **OPEN:** complete-unit exclusion is specified, but an entirely excluded scenario cell makes fixed-weight inference undefined.

Requested PARTIAL items:

- 1 — **OPEN:** contradictory FX-M count rule.
- 2 — **RESOLVED:** consistent merits/order feed subsequent selection.
- 3 — **OPEN:** empty-cell handling remains undefined.
- 5 — **RESOLVED:** bootstrap strata and p-value degeneracy fixed.
- 9 — **RESOLVED:** development targets and σ aggregation specified.
- 11 — **OPEN:** rehearsal differs from final inference, including 2,000 versus 20,000 inner resamples.

Exact fixes to [v3](/Users/danijel/Desktop/gadapt/research/ITERATION56_PROTOCOL.md):

1. §6: replace **“(tok 900000+)”** with **“(namena 3, s = 1, 2, prema §2)”**.

2. §5: replace **“Zaokruživanje k, v = max(1, round(·)).”** with **“Za k i v važe isključivo prethodno navedene formule, uključujući k = 0 za prazan skup.”**

3. §7: replace the simulation specification with:

   > Assume all four test scenarios within each block share its equally pooled development contrast distribution. Set r = d − mean_block(d), D = 2(1−1/3000), and choose δ_block so mean[clip(r+δ_block,−D,D)] = 0.05. Using RNG seed 56023, generate 2,000 complete synthetic experiments, independently sampling 10 contrasts per block×scenario cell from this bounded distribution. Apply the specified joint θ_a analysis with 20,000 stratified bootstrap resamples. Power is the fraction of θ_a intervals excluding zero; if below 80%, use 20 test seeds.

4. §3: append:

   > If any analysis cell is empty after exclusions, primary inference is unavailable. Run sensitivity analysis whenever this occurs or exclusions exceed 5%; restore excluded units, retain completed outcomes, and assign T=1 only to failed runs.

The reference-stream conflict, FX-M contradiction and empty-cell problem are new v3 blockers. No additional blocking error found in AP counters, the main k/v formulas, development-reference accounting or cyclic event order.