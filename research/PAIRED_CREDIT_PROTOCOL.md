# Iteration 4: physically charged within-offspring mutation controls

**Frozen before the new benchmark executes, 2026-10-21.**
All changes are now made directly on `owlCoder/gadapt:main` under explicit
owner authorization. Never alter `bpzoran/gadapt`. Prior drafts #1 and #2
were merged to main only after the existing CI passed.

## Motivation and published precedent

The old UCB credit used an evaluated offspring's improvement over population
median. That *does not isolate the contribution of mutation*: the offspring's
parent/crossover history and unmeasured pre-mutation value confound operator
credit. Last iteration's UCB operator selection did **not** improve GAdapt:
8/8 early IEEE14 seeds gave 4 wins / 4 losses for feasibility-UCB versus
legacy at 110% load, and expanded GEANT historical plans gave UCB objective
1 win / 7 losses versus legacy. Neither is a confirmatory rejection.

Literature: AOS has long studied parent-vs-population credit benchmarks
(doi:10.1007/s00500-016-2126-x); temporal trial/control mechanisms also
exist (doi:10.1016/j.swevo.2021.101013, TAOS); *Leadership succession inspired
adaptive operator selection* (doi:10.1016/j.matcom.2025.01.007) explicitly
studies fairness between operators; bandit normalizations for scaled
optimization (doi:10.1080/0305215X.2025.2466119). These results PRECLUDE
claiming novelty solely from comparing offspring with a pre-mutation control.

## Exact opt-in mechanism

`mutation_credit_assignment="paired"`, together with
`mutation_operator_policy="uniform"` or `"ucb"`, enables a controlled local
estimate. Every newly selected offspring is evaluated **before** exactly one
variable mutation, using the user's actual objective. Its mutated version is
then evaluated through the ordinary GAdapt cost finder. Both evaluations are
charged to the same externally counted number of physical simulator calls.
The pre-mutation candidate is a counterfactual *local control for that
offspring*, not a separate optimization candidate in GA's internal population.
The selected best-so-far external evaluation recorder includes ANY evaluated
candidate, whether control or mutant, with that distinction recorded.

The user must provide `mutation_evaluation_counter`, a monotonically increasing
nonnegative integer callback reflecting actual physical evaluations. Each
direct control or standard objective call must increase it by exactly one;
post-budget requests must leave it unchanged. Without a physical baseline
OR a physically evaluated mutant, no paired reward is attributed.
For normalized violation comparisons, optionally provide an independent
`mutation_violation_function(values, score)` that reads *already cached*
evaluation metadata, returns nonnegative normalized violation or `None`
when no physically evaluated record exists. No extra uncounted solver calls.

Guards prevent the most obvious causal attribution mistakes: forced
`ensure_unique_individuals=False`, only one selected variable through
`number_of_mutation_decision_variables=1`, and
`candidate_solution_mutation="random"`. Forced pre-optimizer crossover
mutations have no paired baseline and do not receive paired credit.

Reward when objective-only: `clip((pre_score-post_score)/(1+abs(pre_score)),0,1)`.
When feasibility-aware: if baseline violates constraints, reward only positive
normalized reduction in violated constraints; if the baseline is feasible,
reward only objective improvement that maintains feasibility. These are
heuristic definitions, not proven optimal reward rules.

This **reduces** direct mutation/crossover attribution bias but does not
identify the causal effect of selecting one operator over another on the
final algorithm output, since the operator selection policy changes future
populations. In addition, one extra control evaluation per selected
mutant means fewer generations/offspring under an equal objective-call budget.
That budget tradeoff is intentional and essential to measure, not hide.

## Frozen pilot: real IEEE14 AC PF reference system

8 paired seeds (0..7), 240 actual PYPOWER AC evaluations per run, population
24, both 100% and 110% load. Fixed method family (8 methods):

1. `legacy` — original package defaults.
2. `legacy_single` — original operator composition with affine diversity,
   one-variable randomized mutation and uniqueness disabled, matching the
   alternative methods. The separate `legacy` arm retains log-relative default.
3. `uniform_offspring` — unpaired credit with same single-variable constraints.
4. `ucb_offspring` — population-median unpaired credit with same constraints.
5. `uniform_paired` — equal probability, paired local evaluation/credit.
6. `ucb_paired` — UCB and objective improvement from paired local evaluation.
7. `ucb_paired_feasibility` — paired normalized feasibility and objective credit.
8. `scipy_de` — SciPy differential evolution with same 240 AC evaluations.

No optimizer cost calls or feasibility feedback may create unmetered PF solves.
Log objective requests vs actual solves, baseline probes, completed pairs,
post-budget truncations, objective-best and physically verified feasible
losses, PF convergence failures and clock time. All completed runs, including
infeasibility, count in aggregate reliability. Primary exploratory outcome:
fraction of physically feasible runs, then paired rank of feasible-loss MW
(infeasible is ranked worse). Compare each method to `legacy_single`
with exact sign and Holm correction over 7 comparisons PER load.
Report Wilson binomial intervals, median/quantile losses conditional on
feasibility and paired bootstrap medians; no superiority claim at n=8.

Acceptance threshold is NOT numeric superiority on eight seeds.
A pilot can suggest a larger replication, but failure of the paired method
means rejecting or redesigning it. Bigger IEEE118/RTE, GÉANT and fully
independent chronological test remain indispensable before publication.

**Caveat:** Unit tests are not equivalent to running real engineering
problems. IEEE14 is a standardized test network, not production data.
