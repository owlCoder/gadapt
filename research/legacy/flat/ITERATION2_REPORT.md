# Research iteration 2 — measured infrastructure robustness (2026-10-21)

**Status:** exploratory direct-GAdapt experiments, **not** a validated
dissertation innovation or deployment-ready infrastructure controller.

Repository: `owlCoder/gadapt` on `research/robust-diversity-baseline`.
Original upstream `bpzoran/gadapt` and the fork's `main` unchanged.

## New code in this iteration

1. `GA(cost_diversity_metric="affine_invariant")`: positive-affine-invariant
   fitness spread and recovery from degenerate initial spread; **opt-in**.
2. `GA(adaptive_immigration_patience=4, adaptive_immigration_percentage=25,
   adaptive_immigration_diversity_threshold=0.25)`: conditional immigration
   every fourth stagnant generation only when normalized fitness diversity
   is sufficiently low. **Opt-in**, default disabled; known GA techniques,
   not yet established as novel scientific contributions.
3. Physics-based AC load flow test on standardized IEEE 14-bus network using
   PYPOWER, with recorded genuine voltages, Q-generator output and branch
   MVA limits (only limits provided by original network data).
4. Historical, source-pinned **GÉANT** 22-node, 36-link, 462-demand SNDlib
   telecom traffic engineering model, with archived bandwidth demands and
   reference expansion-module costs/capacities.
5. Automated Python unit tests, physics checks, seeded benchmarks,
   feasibility rates, confidence intervals and baseline SciPy DE /
   random search.

## IEEE14 AC results

12 seeds, two load levels, 240 actual AC solver evaluations per run.
A feasible run means at least one candidate with independently computed
AC constraints satisfied to the stated tolerance; medians only among
feasible runs; unsuccessful runs are counted separately.

| Load | Method | Runs with feasible candidate | Median feasible loss (MW) |
|---|---|---:|---:|
| 1.00 | legacy | 12/12 | 14.343501 |
| 1.00 | affine | 12/12 | 14.378624 |
| 1.00 | scipy DE | 12/12 | 14.305458 |
| 1.10 | legacy | 11/12 | 17.961366 |
| 1.10 | affine | 11/12 | 18.196904 |
| 1.10 | scipy DE | 10/12 | 17.436417 |

Reference GitHub Action:
https://github.com/owlCoder/gadapt/actions/runs/39549392997

## GÉANT archived traffic results

Source: https://sndlib.put.poznan.pl/geant.overview.action
Pinned SHA256 of downloaded native source:
`ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed9023ed4b4f4ff`.

30 seeds, 360 objective evaluations per method, same published
network and traffic demand. Scenario objective: minimize cost of
installing capacity modules required by shortest routes controlled
via integer edge weights. **Engineering modeling choices** (shared
bidirectional link capacity, unlimited expansion modules, OSPF-like
path weights) are explicitly stated in the source code and are NOT
claims about GÉANT's installed equipment or operational traffic control.

| Method | Median model cost | Worst model cost |
|---|---:|---:|
| legacy GAdapt | 134391.5 | 138412 |
| GAdapt affine | 134677 | 138293 |
| GAdapt affine + adaptive immigration | 134784.5 | 137552 |
| scipy DE | 136867.5 | 141331 |
| random search | 140639 | 143018 |

Before adding restart (comparison affine vs original), on 30 paired
seeded runs: affine won 17, legacy won 11, 2 ties. Median paired
difference (affine minus original): -129 cost units, bootstrap 95%
CI [-517, 181], two-sided Wilcoxon exploratory p=0.600457. **Not
statistically convincing**. Note that paired difference of medians is
not the same as difference of the two separate medians above.
No inferential claim is made about the restart ablation yet.

Reference GitHub Actions:
https://github.com/owlCoder/gadapt/actions/runs/39550042217
https://github.com/owlCoder/gadapt/actions/runs/39550598905

## Externality / realism notes

The IEEE14 test case is a published reference network, **not live utility
operating data**. The GÉANT network topology and 2005 traffic data are
archived real-world inputs, but the route-weight and module-capacity
planning model is ours. The `case1888rte` offline French-network-derived
smoke experiment in this fork found no feasible solution for any of the
three methods with one seed/four generations; **there is no established
RTE success**. Do not cherry-pick favorable cases or claim deployment
readiness. Reference:
https://github.com/owlCoder/gadapt/actions/runs/39550318045

## What we have learned

- The new diversity measure corrects mathematical sensitivity to affine
  changes of objective scale and handles initially identical cost values.
- Those corrections **do not guarantee lower loss or better robustness**
  on real network tasks. The original GAdapt remains a strong baseline.
- Strong cross-domain, preregistered evaluation and failure-aware metrics
  are necessary; 12 runs are a pilot, 30 telecom runs give only limited
  power for rare-failure claims. The new restart experiment remains an
  ablation rather than a selected winning method.
- For a doctoral result, next investigate constraint-feasibility feedback,
  nonstationary objectives, robust statistics of diversity and measured
  benefit on larger, held-out independent infrastructure data. Novelty must
  be checked against existing literature; software features alone are
  insufficient.

## Next acceptance checks (not yet fulfilled)

- Scientific literature review and precise originality claim.
- Full equal-evaluation curves (not just final costs) across many scenarios.
- Preregistered 50–100+ independent seeds per condition if studying rare
  failures, with a sample-size calculation.
- SNDlib dynamics and independent operational traffic traces rather than
  only the published 4-month aggregate peak matrix.
- Independent nonlinear OPF/AC solver cross-check and real-data
  engineering expert validation.
- A genuinely untouched test case for final generalization.
- All claims scrutinized for feasibility rate, failure modes, worst-tail
  performance, resource cost, sensitivity and reproducibility.
