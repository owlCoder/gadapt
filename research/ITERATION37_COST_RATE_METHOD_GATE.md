# I37 Method Gate (22 October 2026): paid-call operator allocation, NO physical experiment authorized

This is a **method-definition and zero-domain-test gate**, **NOT** a preregistration for AC/routing evaluations. It is recorded before any I37 simulator experiment. The I34–I36 new UCB credit hypothesis has failed to demonstrate superiority on its prespecified primary test (each exact two-sided p=1). Do not tune that reward on the same networks. Never modify upstream `bpzoran/gadapt`.

## Falsifiable mathematical defect of the current I34 credit

Let Y=1 only when all N real source scenarios were explicitly verified feasible, Y=0 for a measured physical rejection. Let C be the number of true physical scenario evaluations (1..N), including failures. Existing I34 event reward is **Y/N** (and 0 for measured failure), so its expectation is p/N. The actual long-run verified-success throughput under stationary regenerative trials is **E[Y]/E[C] = p/mu**, NOT E[Y/C] and NOT p/N.

Concrete counterexample for N=3: both operators succeed with p=1/2, and a success always costs C=3. Operator A fails after one physical call; B fails after three. Both yield expected old credit 1/6. A has E[C]=2, throughput 1/4; B E[C]=3, throughput 1/6. **A offers 50% higher verified successes per actual physical call**, yet old mean reward cannot distinguish them. This is an algebraic counterexample, not new physical data and not a novelty claim.

## Opt-in algorithmic candidate: UCB on upper success / lower paid-call rate

For each operator i record n_i candidate outcomes (one uniquely attributed mutated decision variable per physically evaluated offspring), confirmed successes s_i, numeric/missing unknown u_i and sum of **actually observed** physical calls c_i. Failed candidate Y=0; unknown Y remains in [0,1], never a positive VERIFIED reward, but its physical cost still counts. Estimate lower observed success/call `s_i/c_i`, with upper hypothetical bound `(s_i+u_i)/c_i`; true full feedback not invented for unknowns.

For each i with n_i>0, use an explicitly exploratory score
```
b_i = sqrt(log(8*K*(t+1)^2 / delta) / (2*n_i))
p_i^U = min(1, (s_i+u_i)/n_i + b_i)
mu_i^L = max(1, c_i/n_i - (N-1)*b_i)
U_i = p_i^U / mu_i^L
```
where t=sum(n_j), K=number of mutation operators, delta fixed at 0.05; each operator with no observed outcome is explored first. These are Hoeffding-style optimistic estimates of the feasible-success/call ratio in a **stationary independent-arm** model (bounded C in [1,N]). In the real nonstationary GA these are heuristics: no causal credit identification or global optimizer regret theorem is claimed. Candidates with zero physical calls do not become training observations. Only a single unambiguously attributed mutator index per offspring is allowed; multiple-operator attribution fails closed rather than inventing causal allocation.

**Purpose:** remove a measurable *objective mismatch* of I34; test a better-defined budget allocation target. **Prior-art warning:** cost-sensitive multi-armed bandits, operator credit, early scenario rejection and optimistic confidence bounds all exist; THIS IS NOT ESTABLISHED ORIGINAL SCIENCE. The method is not a solution for minimizing verified economic cost, only for maximizing verified feasible offspring/call.

## Predeclared zero-domain tests

1. Algebraic example A vs B (old reward equal, throughput differs) and eventual optimistic index ordering after ample hypothetical observations.
2. Numerically unknown outcomes remain unverified but all already paid calls count; malformed status/counters raise errors.
3. Existing `legacy`, `uniform`, `ucb` behavior remains unchanged; newly added `ucb_true_call_rate` requires censor-safe scenario feedback.
4. One actual *GAdapt* synthetic in-core run with a mock scenario cost evaluator and monotone fake counter; **no PYPOWER, no Dijkstra, no real AC or telecom calls**. Runtime rejection if more than one decision-variable mutator is credited to the same offspring.

## Scientific GO/NO-GO (no new physical series before this is decided)

**GO for a real I37 protocol only if** we can specify an identifiable, substantial contribution beyond known cost-aware bandit/AOS literature; design a *fair same-score, same-AC-cost* experiment with `legacy_fixed`, old I34 UCB, cost-rate UCB, uniform/no-AOS, a strong feasible-first reference and a continuous predeclared objective (e.g., verified feasible designs per true physical call) with held-out original network/load data. Freeze seeds, complete physics/units, independence and Holm family **before** a single physical call.

**NO-GO for dissertation novelty** if this amounts to just a known UCB cost-normalization formula. In that case keep the corrective software/tests, cease iterations on this credit idea and explicitly choose a different formally novel research problem with the mentor. Do not market mathematical counterexample as doctoral contribution.
