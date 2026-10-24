**FIX FIRST.** Read-only and result-blind: excluded results/logs were not opened; no files changed.

The [v2 protocol](/Users/danijel/Desktop/gadapt/research/ITERATION61_PROTOCOL.md) correctly integrates the main Codex 061 fixes: conditional scope, R=17, symmetric B selection, global FX-T interpretation, reference caveats, exact 54-run gate, symmetric rehearsal criteria, and separate direction/equivalence labels. The revised B/n grids are coherent. Remaining fixes:

1. **§9: seed collisions are blocking.** With n≥160, `(j=2,s=101)` and `(j=3,s=1)` receive identical seeds. This introduces cross-scenario dependence ignored by the bootstrap. Replace the formula with:

   > `seed = 10⁷p + 10⁶i + 10⁴R + 10³j + s`. Assert uniqueness across distinct `(p,i,R,j,s)` tasks; reuse seeds only across paired branches/configurations intentionally. Reserve p=67 for stop-validation tasks.

2. **§10: early stopping conflicts with “insufficient calls = failure”; the 20-run check lacks coverage and acceptance rules.** Replace the stopping/check provision with:

   > After FX-T calibration and before rehearsal, compare full-budget and target-stopped runs for all three networks × both development scenarios × four branches, s=1, p=67: 24 pairs. Use identical initialization and randomness. Compare first-target h, including nonattainment, and exact PF-input/output prefixes through min(h,B_i). Record the target witness before stopping; make no subsequent PF call. Any mismatch blocks stopping; absent any attained target, validation is inconclusive and full-budget execution remains mandatory. A run completes successfully without execution errors when either a verified target is reached or B_i calls are exhausted. Earlier unexplained termination triggers retry.

   Also require identical **generated initial populations**, independently of how many members are evaluated before stopping.

3. **§10: define the exclusion denominator, retained records, and sensitivity’s authority.** The 5% threshold does not itself control attrition bias. Replace the exclusion/sensitivity sentences with:

   > Retry each failed branch once using its original seed; retain its successful retry, otherwise mark that branch unavailable. Exclude its entire four-branch unit from complete-case inference. Report excluded-unit counts and rates globally and per cell, using planned units after OPF exclusions as denominators. Perform sensitivity analysis after any exclusion, restoring all planned units, retaining successful branch outcomes and assigning T=1 only to unavailable branches. Flag global exclusion >5%. Sensitivity is descriptive and cannot restore primary inference when any cell is empty.

4. **§7: 20 vectors and ESS≥10 are planning safeguards, not validation of transfer to test scenarios.** Weight diagnostics and simulation mechanics remain unspecified. Add:

   > Require all 20 complete rehearsal vectors per network; otherwise STOP. The ≥20% attainment criterion means ≥4/20 per branch, pooled across development scenarios. For both targets θ=0.02 and θ=0, solve (1/3)Σ_iΣ_u w_iu d_iu=θ; require strict attainability, mean error≤10⁻⁸ and ESS_i=1/Σ_u w_iu²≥10. Report λ, weights, ESS, maximum weight and weighted branch-attainment rates. Independently sample n whole vectors with replacement for each eligible test cell from its network’s tilted pool. Power and null calibration are conditional on this empirical distribution and its assumed transfer; Wilson intervals quantify simulation uncertainty only.

5. **§7–8: 2,000-bootstrap simulation does not directly calibrate the final 20,000-bootstrap procedure.** Replace the simulation decision wording with:

   > Use 2,000 bootstrap repetitions for candidate screening. Independently confirm the selected n with 1,000 experiments using 20,000 repetitions, seed 61024; require ≥825 positive-primary conclusions. Independently calibrate θ=0 with 1,000 experiments and 20,000 repetitions, seed 61025; require ≤36 positive-primary conclusions. Failure means STOP without trying a larger n. Use two-sided 95% Wilson bounds. Initialize each series RNG once; do not reset bootstrap seed 61 inside simulated experiments. Use linear percentile interpolation throughout.

   “False positive” means **lower 95% bound >0**, not either directional label.

6. **§11: PF subtotal is approximately right; the time ceiling is wrong.** Replace with:

   > Base maximum excluding gates, validation and retries: 225.504 M PF calls (FX-T 11.664 M; rehearsal 2.880 M; test 207.360 M). Stop-validation adds ≤0.576 M. With gate≈0.2 M, approximately 226.3 M total: 207–283 CPU-hours at 3.3–4.5 ms/PF, ideally 20.7–28.3 hours on ten cores, excluding OPF, regression checks, simulation and overhead. These are estimates, not ceilings; retries add work.

Finally, §7’s attributed **240–430** range should read **257–465** to reproduce Codex 061’s Wilson-adjusted approximation.