# I65-DRAFT — focused benchmark: stagnation, restart or GAdapt→CMA switching

**Date:** 2026-11-01  
**Status: DRAFT, NOT FROZEN, NOT PREREGISTERED AND NOT A RESULT.**  
**Dependencies:** `ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md`, `ITERATION65_INSTRUMENTATION_VALIDATION_SR.md`, I64-S0/E/E3/A/R/I/I2.  
**Repository:** `owlCoder/gadapt`; do not change upstream. No GAdapt defaults may be changed. Implementing a new algorithmic switching policy is prohibited until the `AGENTS.md` novelty gate is satisfied or an explicit decision permits a restricted engineering study. GitHub push/PR/CI actions require appropriate authorization.

## Q65: research question and precise contribution classification

Can a policy that redirects GAdapt's unused budget to CMA after 20 **completed** generations without significant improvement reduce the worst-decile error on landscapes without favorable global structure, **without unacceptable degradation of early convergence**, compared with prespecified IPOP-CMA-ES and the fixed I64-E3 hybrid? This is an **engineering empirical hypothesis**, not evidence of scientific originality. `novelty not established` for adaptive restarts, switching, portfolio methods and hybrids; see the audit.

Any final recommendation applies only to the tested distribution of instances, budget and quality requirements; never claim performance "guaranteed for every function."

## Scope and problem protocol

1. **Primary target set, distinct from I64-E:** official single-objective COCO `bbob` f21 (Gallagher 101 Peaks) and f24 (Lunacek bi-Rastrigin), dimensions D ∈ {2, 10, 20}, with three independent **held-out** COCO instances {6, 7, 8} for each function/dimension. This gives 2 × 3 × 3 = **18 primary cells**. Each instance has shifts and transformations defined internally by COCO and must not be replaced by an approximate formula. All methods receive the same native domain [-5, 5]^D, in identical physical units. Sources: https://coco-platform.org/testsuites/bbob/functions/f21.html and https://coco-platform.org/testsuites/bbob/functions/f24.html. The draft references `cocoex.Suite('bbob','year: 2009', ...)` per publicly described usage; verify the exact API during integration. **Do not use `bbob-biobj`**, whose f21/f24 labels refer to different function pairs.
2. **Controls:** Rastrigin and Styblinski–Tang in D ∈ {2, 10, 20}, with one fixed `shift` and one `rotm` using the **same translation o**, giving 2 × 3 × 2 = **12 control cells**. Use I64's `e_common.transform` geometry; generate Q by QR with public seed `np.random.default_rng([65, 3, cell])`. Archive Q and o; test `Q Qᵀ≈I`, the value at the known optimum, and whether the optimum is attainable inside the domain. Preserve additional 2D original/rotated reference probes for hardware validation only, **not** as confirmatory cells.
3. **Targeted external-Q diagnostic for COCO f21/f24:** only COCO instance 6 × D {2, 10, 20} × `shift`/`rotm` (12 diagnostic cells) × five A–E policies × 15 seeds. External coordinate changes are permitted **only if** an official COCO core in a separate oracle instance exposes verified `x_opt` and `f_opt` and `f(x_opt)` passes the witness check. Transform as `f(x_opt + 10 Qᵀ(y-o))`, `y∈[0,1]^D`, with Q=I for `shift` and paired Q/o otherwise. If this optimum access cannot be reproduced reliably, **do not improvise**: omit the 12 diagnostic cells and disclose the omission. Do not make a causal claim about added Q based on native COCO alone. The optimizer must never see oracle data; setup calls must be logged separately from run budgets.
4. **Development:** COCO instances {1, 2, 3} only (never {6, 7, 8}), dimensions 2, 10 and 20, with ten development seeds per cell. Execute only the work needed for integration checks, performance profiling and selection of permitted epsilon/detector variants. No held-out outcomes may be inspected before FREEZE and no periodic peeking at confirmation is allowed.
5. **Infrastructure:** do not reuse old ORPD cells as an independent new validation. A new ORPD/dispatch dataset requires a separate frozen design and an independent verification model. Report discrete dimensions separately; never imply that they are the same as f21/f24. Existing ORPD cells can serve only as compatibility diagnostics.

### Reference values and normalization

Define `g=max(0,(f_best - f_opt)/s_i)` and `L=g/(1+g)`, as in I64. All methods in one cell must use the same denominator `s_i`. For COCO obtain `f_opt` from a verified, official oracle using a separate analysis path. **Do not** treat `problem.final_target_fvalue1` as the exact optimum without checking whether it incorporates a target tolerance.

Set `s_i` to the median from 4,096 uniform sample points generated before running optimizers, using a public setup seed without any optimization attempt. Archive all values and their SHA. These 4,096 setup evaluations are separately disclosed public benchmark-construction costs, **not** calls charged to each optimizer. Do not use `f_opt` or `s_i` in search/restart decisions unless the policy explicitly charges that information to every run. If recomputation reveals `g < -1e-12` on the normalized scale or `s_i ≤ 0`, STOP. Without a certified discrete optimum, do not describe a relative ORPD gap to continuous OPF as a "certified gap."

## Algorithm roster — all nine primary methods

| ID | Policy / status | Fair-comparison requirements |
|---|---|---|
| M | GAdapt-M as in I64-E (population 64, mentor's operators), natural termination/restart if B remains | Do not alter GA defaults or retune. |
| DE | SciPy `differential_evolution`, `best1exp`, 64 truly evaluated initial candidates, `mutation=(0.5,1)`, `recombination=.7`, `polish=False`, seeded `rng` | Set `tol=0,atol=0`; library convergence is not the stagnation detector. Charge any repeated evaluation. |
| CMA | pycma CMA-ES with constant-population restart | Freeze I64-E parameters. |
| E | pycma IPOP-CMA-ES | Primary strong baseline. |
| BIPOP | pycma BIPOP-CMA-ES | Additional strong portfolio baseline. |
| A | GAdapt-M plus common detector; terminal STOP on STAGNATION | Do not consume artificial calls to fill B. Report unused budget. ECDF curve stays constant after STOP. |
| B | GAdapt-M plus STAGNATION → restart the **same** GAdapt-M | Fresh RNG substream, the same total B, global incumbent retained, at most one restart per STAGNATION. |
| C | GAdapt-M plus STAGNATION → CMA-ES for all remaining B | Warm-start from best validated GAdapt witness; `sigma0=0.05` as in E3; document subsequent natural CMA restarts per E3. Without stagnation, run only GAdapt. One-way transition, no oscillation. |
| D | Fixed I64-E3 hybrid: 30% GAdapt → 70% CMA-ES, `sigma0=0.05`; follow E3's restart policy afterward | Strong baseline; do not change the allocation after seeing confirmation. |

**Additional ablation:** the STAGNATION definition is shared across algorithms for telemetry, but A/B/C make decisions based on **GAdapt** completed generations. Internal DE/CMA/IPOP/BIPOP generations are not equivalent. Physical `nfev` is the comparison metric. An alternate stagnation rule expressed as "no progress for N evaluations" may be used only if separately preregistered. DE and CMA restart schedules must be documented explicitly.

## Stagnation semantics and state

At the end of a completed generation t, let `best_previous` be the global best finite objective value through t−1 and `best_current` through t:

`delta = best_previous - best_current`  
`improved = delta > eps_abs + eps_rel*max(1,abs(best_previous))`

If `improved`, reset the counter to zero; otherwise increment it. After **exactly 20 consecutive completed generations** without a significant improvement, log one `STAGNATION` event (physical `nfev` timestamp, generation, phase, `best_y`, `best_f`). Initial population evaluations are charged but do not constitute the first completed generation. Switching at a partial generation truncated by B is prohibited. STAGNATION must not be treated as `SUCCESS`. A restart resets the stagnation counter, **not** the global incumbent.

**DRAFT epsilon roster for development:** `(eps_abs,eps_rel)∈{(0,0),(1e-10,0),(1e-8,0)}`, applied to raw objective values without access to `f_opt`. Primary candidate `eps_rel=0` avoids COCO's arbitrary instance-dependent additive `f_opt` shift, which would contaminate raw relative tolerances. If a normalized implementable centering `b_t` for `eps_rel>0` is developed before FREEZE, charge every calibration probe and freeze its rule in advance. Select **one** pair and prespecified selection rule in the frozen protocol using development data only; do not reselect based on confirmation. Distinguish statuses `INVALID_RESULT`, `FAILED`, `BUDGET_EXHAUSTED`, `STOPPED_STAGNATION`, `SUCCESS_VALIDATED` and `NOT_SOLVED`.

## Physical evaluation budgets and accounting

- **B = 12,000 physical evaluator attempts per run**, including population initialization, GAdapt `GA.execute()` all-min/max probes, validation, callbacks, repair, polishing, recomputation, algorithm switching and restarts. Reserve **at least one of those B slots for an independent final witness**: search may consume at most 11,999 calls, then an independent objective reevaluates the final reported best candidate inside B. Do not reuse a library cached cost. With no witness or a failed check, record `NOT_SOLVED` or `INVALID_RESULT` rather than hiding a B+1 call. If a policy stops early, perform its witness check before termination. `B=3,000` is a **snapshot of the same search trace**, not a new run; flag the snapshot as provisional/unvalidated if its independent witness has not yet occurred. Policy A can consume fewer than B; report `unused_B`.
- Require a monotonically increasing `physical_attempt` counter, reservation before invocation, `n≤B`, and logs for `attempted`, `returned_finite`, `nonfinite`, `exception`, `callback`, `recheck`, `phase`, and `candidate`. The final independent witness is a charged, labeled call inside B. `time-to-target` must distinguish a search hit from independently verified success. Any additional out-of-run scientific rechecks have a separate disclosed physical-call budget; they cannot be silently represented as within the optimizer's B=12k calls. If one Python objective call internally invokes multiple physical solvers, define and expose the true solver-call cost. Copy input vectors before invoking an objective; library `success=True` is never a replacement for an independent witness.
- Algorithms may have equal call quotas but different counts of completed generations. On partial CMA generations at the B boundary, do **not** call `tell` with fabricated objective values or propagate invalid state.

## Sample size, seeds, maximum calls and CPU cap

- **Held-out native COCO:** 18 cells × nine methods × 30 seeds = **4,860 runs**, at most 58,320,000 attempts.
- **Analytic controls:** 12 cells × nine methods × 15 seeds = **1,620 runs**, at most 19,440,000 attempts.
- **Optional prespecified added-Q diagnostic:** 12 cells × five A–E methods × 15 seeds = **900 runs**, at most 10,800,000 attempts. Primary plus controls cap = **77,760,000**; including diagnostics = **88,560,000**. Policy A may use fewer calls. Development, setup and within-run reserved witness are separately accounted for as defined above.
- **Seed rule:** `seed(stage,c,s)=65_000_000+1_000_000*stage+1_000*c+s`; `stage=1` for development and `stage=3` for confirmation; `s=1..10` development, `s=1..30` held-out, `s=1..15` controls. Paired (cell, seed) labels are identical across methods. COCO instances {1,2,3} are development and {6,7,8} confirmatory. Method-specific library RNG streams are deterministically derived from the master seed plus method ID and must be frozen explicitly. **The same seed does not imply an identical realized population across methods.**
- **CPU plan:** before a large run, carry out a development-only profiling pilot costing at most 0.5 CPU-hour in a locked environment. Measure actual `t_f` and method overhead for each dimensionality/algorithm. The target of 24–72 CPU-hours for primary+controls is an **estimate, not a guarantee**; the hard confirmatory cap is **120 CPU-hours**. If projected cost exceeds that cap, STOP and approve a revised specification **before looking at held-out data**; do not silently reduce seed counts. Use at most four workers and `maxtasksperchild=1` to isolate RNG contamination; no automatic GitHub Actions jobs. Archive each cell separately, create-once; resume only missing completed-and-locked cells; store SHA-256 for every partition.

## Metrics and statistical contrasts

- For thresholds `τ∈{1e−2,1e−4,1e−6}`, `T_tau` is the **first physical attempt** with `g≤τ`, or ∞ if none. Define `A = (1/(3B)) ∑τ max(0,B−T_tau+1)`. Report `P(hit by B)` and `P(hit by 3000)`, ECDF curves and AUC by physical evaluations, and censored time-to-target.
- Report final `g` and `L=g/(1+g)`, cell median and quantiles q10/q90/q95, and CVaR of the worst 10% of L. With 30 seeds, CVaR is the worst three and must carry an explicit precision caveat. Set `L=1` when there is no finite witness. Report outcome, failure/invalid/overrun/recheck-mismatch rates separately. For ORPD, assess **feasibility before quality**; calculate a gap only for feasible solutions where a reference is defined.
- Primary COCO weights are equal by f21/f24, D and held-out instance. Controls and the added-Q diagnostic **do not enter the primary decision**. At the CVaR level, seeds are paired by `(f,d,instance,s)`. Do not treat a mixture of instances and seeds as independently sampled task types for generalization.
- Prespecified family of contrasts **C versus E and D** on native f21/f24: `CVaR(ref)−CVaR(C)` (positive favors C) and `A(C)−A(ref)` (positive favors C), `ref∈{E,D}`. Four simultaneous one-sided 95% lower bounds, via max-t paired bootstrap with 20,000 repetitions and seed 65065. Use hierarchical instance/seed resampling and report sensitivity to treating the COCO instance as the replication unit. Three instances provide weak support for universal generalization.
- **GO for restricted practical selection of C** only when *all* of the following hold: (i) lower simultaneous bounds for `CVaR(E)−CVaR(C)` > +0.01 **and** `CVaR(D)−CVaR(C)` > 0.00; (ii) lower simultaneous bounds for `A(C)−A(E)` and `A(C)−A(D)` are ≥ −0.03; (iii) `P(g≤1e-2)` declines by no more than 0.05 relative to either reference under simultaneous bounds in the same family — **expand the family to six contrasts before FREEZE**; (iv) no budget overrun, unaccepted witness or hidden invalid result; (v) no ORPD confirmation is claimed without a separately frozen infrastructure study. If a decision limit fails, **NO-GO** for recommending C. If confidence intervals cross a limit, report **UNDECIDED**, without retuning or rerunning solely to obtain a positive outcome. All-pair secondary contrasts, cell medians, control-CVaR and the 3,000-call snapshot are descriptive.

## FREEZE gate (strictly before the first held-out evaluation)

1. **Literature and supervisor decision:** `novelty not established`. Permit only a narrow empirical engineering study or an independently established novel mathematical differentiator with a verifiable theorem claim. Otherwise stop implementing policy C under `AGENTS.md`.
2. Independent implementation and methods review, especially the original reference `Budget` exception and witness issues. Integration gates for B−1/B/B+1, exceptions, NaN, ties, initialization, callbacks, two-process replay, `f(y=o)=fopt` transformation check, true COCO `f_opt`, Q orthogonality and independent reevaluation. Protect the official COCO oracle from optimizer information leakage.
3. Lock Python, NumPy, SciPy, pycma, cocoex, GAdapt and transform-library versions for all methods; SHA-256 of source tree, Git commit, environment variables, CPU model, `pip freeze`, `PYTHONHASHSEED`, seeds, transforms, COCO IDs, `f_opt`, `s_i`, selected eps values and CMA restart schedule. Archive `manifest_freeze.json`, its own SHA and a commit **before** code/confirmatory results under the repository's frozen-protocol rules. Incomplete manifest means **NO-FREEZE**.
4. Pass the development-only pipeline check. Do not preview initial confirmatory seeds (the S0 pre-run exposure is a documented risk). One complete confirmation, no post hoc selection using held-out data.
5. Print `FROZEN: <commit>, <manifest_sha256>, <review_reference>, <date>` **only after actually freezing**. Those fields are intentionally unfilled in this DRAFT.

## Infrastructure deployment validation and statuses

Input → deterministic decoding/validation → optimizer with B → independent checks of bounds, discrete step grids, AC power-flow constraints and independently recomputed cost under the *same model*. If all conditions and a predefined quality requirement pass, return `SUCCESS_VALIDATED`; otherwise, if budget remains, use an explicitly preregistered fallback (e.g., independently certified safe base state or previously approved configuration, including the true cost of verifying it). If neither works, return `NOT_SOLVED`. Fallback needs its own safety evidence; it is not automatically an optimum. Report failures, unresolved AC power-flow checks and feasibility separately. No industrial guarantee is claimed.

**Current decision:** GO for audit and cheap instrumentation validation; NO-GO for an original-method novelty claim; FREEZE and held-out COCO benchmarking remain **BLOCKED** until all gates above are satisfied. No new optimizer results have been measured.
