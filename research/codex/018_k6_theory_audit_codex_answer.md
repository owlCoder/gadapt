**NO-GO as the main PhD contribution; conditional GO for a short theorem-feasibility exercise.** My subjective probabilities: **75%** for a correct, simplified result within weeks; **20%** for a publishable theoretical contribution; **under 10%** for a theorem that also establishes a useful infrastructure improvement.

**First, the brief misstates the implementation.** [`average_difference`](/Users/danijel/Desktop/gadapt/gadapt/utils/ga_utils.py:115) averages *adjacent sorted gaps*. These telescope. For \(s\ge2\) valid survivor costs, the default actually uses

\[
D_t=\frac{\log(c_{\max,t}+a_t)-\log(c_{\min,t}+a_t)}{s_t-1},
\qquad a_t=\max(0,1-c_{\min,t}).
\]

There is **no mean-magnitude division** in the [default log calculation](/Users/danijel/Desktop/gadapt/gadapt/operations/population_update/cost_diversity_population_updater.py:103). Thus, at fixed survivor count, this is normalized **log-range control**, insensitive to interior costs. Also, the columnar rule floors an **upper limit**, then [draws the actual variable count uniformly from 1 to that limit](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/candidate_solution_mutation/random_decision_variable_mutation_rate_determinator.py:19). It does not force every mutation to touch \(N/5\) variables.

The adversarial prior-art case is strong:

- **Ursem, DGEA (2002):** diversity controls switching between exploitation and mutation-driven exploration. The general “diversity deficit triggers exploration” principle is established. DOI: [10.1007/3-540-45712-7_45](https://link.springer.com/chapter/10.1007/3-540-45712-7_45).
- **Srinivas–Patnaik (1994):** population fitness statistics detect convergence and determine adaptive mutation/crossover probabilities. This is closer conceptually than genotype-diversity methods. DOI: [10.1109/21.286385](https://doi.org/10.1109/21.286385).
- **Fitness-based control remains active prior art:** FD-DE explicitly adapts parameters using fitness deviation; fitness-distance control additionally uses spatial information absent from GAdapt’s scalar range. DOIs: [10.1016/j.isatra.2023.05.005](https://www.sciencedirect.com/science/article/pii/S0019057823002227), [10.1016/j.neucom.2019.12.141](https://www.sciencedirect.com/science/article/pii/S0925231220316714).
- **Runtime theory is already substantial:** Rajabi–Witt’s stagnation detection, Doerr–Rajabi’s combination with heavy-tailed mutation, and Doerr–Doerr–Lengler’s success rules. DOIs: [10.1007/s00453-022-00933-z](https://arxiv.org/abs/2004.03266), [10.1016/j.tcs.2022.12.020](https://orbit.dtu.dk/en/publications/stagnation-detection-meets-fast-mutation-2/), [10.1007/s00453-021-00854-3](https://researchportal.ip-paris.fr/en/publications/self-adjusting-mutation-rates-with-provably-optimal-success-rules/).
- Sudholt surveys rigorous diversity/runtime results: [10.1007/978-3-030-29414-4_8](https://link.springer.com/chapter/10.1007/978-3-030-29414-4_8). Cobb’s 1990 triggered-hypermutation report is historical background; I verified no DOI or original-report trigger specification here.

**The mathematical distinction is real, but does not establish novelty.** GAdapt uses \(m_t=g(D(P_t)/D_0)\): current population spread plus an initial reference. Stagnation detection maintains a counter \(u_t\) of unsuccessful iterations and increases mutation strength after statistically calibrated waiting times. The same population can receive different stagnation settings after different histories; GAdapt’s cost trigger gives the same setting. Equal-cost, genetically diverse survivors immediately trigger maximal mutation allocation—even during progress—while heterogeneous survivors can suppress it throughout prolonged stagnation.

Crucially, **mutating more individuals does not itself increase mutation radius**. A runtime theorem therefore would not automatically be a stagnation-detection corollary. However, an asymptotic separation must arise from this different feedback mechanism, rather than an added mutation-strength controller or simply more evaluations. I found no exact theorem for this implemented log-range rule; originality remains **not established**.

**Best simplified model:** a mutation-only elitist **\((2+1)\) EA**: clone the best parent; apply the exact cost-trigger gate with \(M=1\); when enabled, use independent bit mutation \(p=1/n\); allow duplicates; omit immigration, crossover and columnar control; assume \(D_0>0\).

This is deliberately modest. A disabled mutation produces a best-parent clone, collapsing unequal survivor costs in one step and restoring mutation. OneMax should admit standard \(O(n\log n)\) analysis. On a fully occupied Jump\(_k\) local-optimum plateau, \(D_t=0\), so every offspring mutates and

\[
q=n^{-k}(1-1/n)^{n-k},\qquad E[T_{\rm escape}]=1/q=\Theta(n^k)
\]

for fixed \(k\): **the same plateau runtime as always-on static mutation**. This direct calculation undermines the proposed speedup story.

Use fitness levels, multiplicative drift, takeover/coupling arguments and geometric waiting times. The [level-based theorem](https://research.birmingham.ac.uk/en/publications/level-based-analysis-of-genetic-algorithms-and-other-search-proce/) requires checking its sampling hypotheses; exact mutation counts are not automatically compatible. LeadingOnes adds neutral-state complications; continuous sphere requires precision targets and mutation-scale analysis.

Infrastructure provides an honest **diagnostic connection**: equal costs can hide materially different network plans, and penalties or objective offsets can distort the trigger. A binary theorem cannot establish improved AC dispatch. Limit the initial effort to **one week, zero physical simulations**; stop unless it reveals a nontrivial separation or a broadly useful limitation beyond the elementary plateau result.