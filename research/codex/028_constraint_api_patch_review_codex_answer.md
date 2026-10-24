Read-only review completed; nothing applied or written. Loading the patch through an in-memory import overlay reproduced **64 passing tests**. An independent nine-run default call-sequence comparison also matched.

**BLOCKING**

- **Rule-based scalarization loses ordering.** With `f_ref=1`, feasible objectives `1e20` and `2e20` both map to `2.0`; violation `1e-20` also maps to `2.0`. Violations `1e16` and `1e20` map to `3.0`, tying failed evaluations. Stable sorting can therefore retain an infeasible candidate before a feasible one, or a failure before a valid candidate. Use explicit comparison keys for selection and a separate scalar for adaptation. [Patch:303](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:303)

- **Penalty arithmetic can generate unchecked nonfinite costs.** Finite `(objective=0, violation=1e308)` with the default weight produces `inf`, ranking worse than the failure sentinel. Adaptive weight doubling can overflow to `inf`; then even a feasible candidate produces `inf * 0 = NaN`. `_succ` remains true because validation precedes scalarization. Bound weight updates and validate the resulting cost before sorting/statistics. [Patch:279](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:279)

- **Cross-generation improvement compares different scales.** Adaptive penalty and epsilon change incumbent merits, but `previous_min_cost` and `previous_avg_cost` retain the preceding scale. An unchanged population can appear improved after a penalty decrease, resetting stagnation; genuine progress can appear worse after a penalty increase or epsilon tightening. This affects min/average exit checks, `generations_without_improvement`, mutation-floor decay, and adaptive immigration. Define a consistent progress measure or recompute comparison references under current parameters. [Patch:207](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:207)

**IMPORTANT**

- **Constructor-only compatibility checks are bypassable.** Setting `ga.constraint_handling="epsilon"` after construction permits `number_of_generations=-1`; I reproduced a successful run with epsilon never decaying. Later changes can likewise combine constraints with nonlegacy mutation policies, although the replacement finder omits every `controller.observe` call. Revalidate these combinations at execution time. [Patch:101](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:101)

- **Failed evaluations distort adaptation.** `sys.float_info.max` alone has a finite logarithm, so it does **not automatically break** default log diversity. Retained failures nevertheless dominate its range. Multiple sentinels can overflow the average-cost sum; mixed extreme signed costs can overflow `average_difference`, and the existing log shift can overflow or cancel to zero. Penalty-generated `inf`/`NaN` further corrupts these signals. FR/epsilon’s bounded merits also make adaptation sensitive to class transitions and saturation, while parent diversity uses raw merit gaps. Specify and test this signal policy. [Cost diversity updater](/Users/danijel/Desktop/gadapt/gadapt/operations/population_update/cost_diversity_population_updater.py:108)

- **Pair validation is inconsistent.** Probes check only tuple/list length: `("not numeric", -1)` passes. Runtime evaluation accepts any unpackable two-item iterable and converts strings/bools with `float()`. Use one shared pair validator for probes and evaluation, checking numeric values, finiteness, and nonnegative violation. [Patch:9](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:9)

- **Results depart from the design.** They report the current scalar winner, which penalty techniques—and epsilon before closure—can make infeasible despite feasible alternatives. There is no `feasible` field or separate best-feasible tracking. Resolve this contract against the design’s promised best feasible / least infeasible result. [Patch:32](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:32)

**MINOR**

- Both parameters have constructor arguments, properties/setters, docstrings, and README entries, but **neither reaches `GAOptions`**, contrary to `CLAUDE.md`. Current execution works because validation/factory read `GA` directly.
- README’s example runs. Update the probe description for pair returns; document policy incompatibility, adaptation on merits, and that early termination can leave epsilon positive. The design’s configurable schedule constants are currently hardcoded.

The event order otherwise matches the stated scheme. Logging, immigrant reevaluation, survivor/average slicing, and inherited history recording remain intact. Default mode executes new imports, setters, guards, and result initialization, but no constraint arithmetic or additional RNG/cost calls; I found no default search-identity regression.