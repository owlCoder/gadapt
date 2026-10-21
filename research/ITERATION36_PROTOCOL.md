# I36 frozen before ANY I36 true native AC: independent IEEE14 topology transfer for I34 GA censor-safe operator credit

**Date: 2026-10-22; separate from I35**, no topology/physics tuning from I35. On `owlCoder/gadapt:main` only. Upstream unchanged. The user asked to move to next iteration after I35; this protocol fixes its experimental design while I35 original IEEE118 job is being evaluated, to avoid cherry-picking.

**Objective:** test I34 `mutation_operator_credit="censored_verified_per_cost"` on a DISTINCT IEEE14 native original source network (previously studied in I17/I32, so **not a blind unseen network**), against an unchanged GAdapt legacy with exactly the SAME deterministic first-fail scenario evaluator; isolate operator selection mechanism and avoid the confounded `full` vs `stop` comparisons.

Physical problem EXACTLY identical to prior I32 `IEEE14OriginalSpatialLoad`: original `pypower.case14()`, original generator P/Q bounds, source bus VMIN/VMAX, positive RATE_A both ends and complex source KCL, native `pypower.runpf` actual AC calls. Original 9D non-slack 4 generator PG controls and all 5 generator VG controls with unchanged I17 source bounds. Synthetic load cases `nominal`, `odd_bus_plus1pct` (odd BUS_I demand 1.01 even .99), `even_bus_plus1pct` (reverse). No new source OPF freedom. Any new "verified feasible" means 3 actually run AC scenarios with all original P/Q/V/MVA/KCL constraints met, not guaranteed global optimum or safety of a real grid.

**Four arms, SAME three-source first-fail screening and censored ranking fitness:**
1. `legacy_fixed` original default GAdapt operator choice.
2. `ucb_objective_fixed` existing objective-UCB heuristic.
3. `uniform_censor_safe_fixed` new credit but no learned UCB selection (uniform random).
4. `ucb_censor_safe_fixed` new strict last-event observed-only credit, physical-counter actual 1/2/3; reward 1/3 solely for three truly source-feasible, zero for actually measured physical failure, unknown withheld. Callback never invokes new AC.

**12 entirely NEW paired seeds 2500..2511 inclusive**, four arms × 180 true source AC upper bound per method×seed, **maximum 8640 genuine original native AC**; population_size=12, log_relative diversity, candidate mutation cost_diversity,parent_diversity, generations 128, timeout240, exit when <3 true calls available. Same as I35 but IEEE14's 9D original source bounds instead of IEEE118 6D. Python+numpy seeds set once per method-run. No tuning when I35 finishes or when an I36 outcome is unfavorable.

**Primary:** seed-level binary success of >=1 completely source-feasible 3-scenario candidate, I34 new UCB vs original legacy, two-sided exact matched-discordance binomial/McNemar. **Secondary:** new UCB vs objective UCB, new UCB vs uniform with new credit. Holm correction for all three prespecified comparisons. Report full 2×2 seed pairings even if no discordants, all zero or mixed. True solver calls (including numerical non-convergent), skipped unmeasured scenarios, source residuals, operator reward counts, best *verified original source gencost* only among all-three feasible per-seed candidates; null if none. Claim no statistical superiority or scientific novelty without direct evidence. Method and seed are separate from earlier I32; not independent topology relative to I32.

**Order:** prereg first, code+synthetic no-native-AC tests, GitHub Actions preflight then ONE real 48-run original native IEEE14 PYPOWER batch, archive all original JSON logs and CSV in main, analyze paired statistics and negative findings honestly. DO NOT count synthetic unit trials as physical simulations, DO NOT repeat seeds as independent evidence, and DO NOT modify upstream `bpzoran/gadapt`.
