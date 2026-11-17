# Rust rewrite — parity and performance audit

**Status: native Rust library builds and its current contract tests pass; full
semantic/API equivalence with original Python GAdapt is NOT established.**

This is an engineering inventory, not a scientific performance claim. Source
of truth for the original Python implementation is `main`; its research
archive remains intact. This branch contains a native Rust implementation
with intentionally different public API (`GA::new/add/execute`).

## Implementation coverage

| Original Python subsystem / behavior | Rust rewrite | Parity limits |
| --- | --- | --- |
| Core `GA` API and execution | Implemented, Rust-native | Not source/ABI compatible with Python users |
| Decision variable bounds, steps and unique population | Implemented | Float-grid quantization and exact-integer semantics differ for edge cases |
| Initial sampling and reproducible seeding | Implemented | Distinct RNG from Python `random` and NumPy |
| Elitism, population, ranked incumbent | Implemented | Order/tie handling and some legacy generation details differ |
| Roulette, tournament, random, top-to-bottom parent selection | Implemented | `number_of_crossover_parents` is exposed but not applied to a separate mating pool |
| Uniform, blending, differential crossover | Implemented, coupled offspring | Sequence of draws and donor/limit behavior not bit-for-bit equivalent |
| Cost, parent and columnar diversity | Implemented, allocation-conscious | No float-for-float equivalence claim |
| Random, normal, mixed and extreme-pointed mutations | Implemented | Composed Python selectors, exact rate schedules and other named configurations differ |
| Stagnation-aware mutation focus and strict gene caps | Implemented | Some selector-specific Python semantics differ |
| Gated/ungated/permuted/resampled compensatory mutation | Implemented | Skips very high dimensions; grouped elite/mutation bookkeeping differs |
| Fixed/adaptive crossover probability policies | Implemented | Mixed policy draw granularity differs |
| Fixed/adaptive immigration, monitored restarts | Implemented | Precise Python scheduling and status counters differ |
| Penalty/adaptive-penalty/feasibility/epsilon constraints | Implemented | Float/integer extreme values, tie handling and epsilon bookkeeping differ |
| Verified budget, cached objectives, accepted incumbent | Implemented | Uncached validation default differs; careful physical solver accounting stays external |
| Discrete small-grid exhaustive checking | Implemented conservatively | No proof over grids beyond supported f64 quantization |
| Callback error and nonfinite handling | Implemented | Rust callbacks return `Result`; Python exceptions and type checks differ |
| Custom operator factories | Rust `GeneticHooks` | Python subclasses/factories cannot be loaded into Rust |
| Objective-reward UCB and uniform operator credit | Implemented for mixed mutation | Not every Python pairing/credit assignment variant |
| Scenario feasibility & censored verified true-call credit | Standalone `VerifiedCallRateBandit` | Not yet wired to automatic GA operator choice, no physical solver integration |
| Paired physical baseline evaluations | Not implemented in engine | Requires physically verified counter and budget integration |
| Legacy `GAResults` fields and exact API names | Partial Rust result struct | Not Python drop-in |
| Archived historical experiment reproduction | Not attempted | No claims on archived scientific outcomes |

## Optimizations implemented

1. Rust-native hot-path operators and deterministic local PRNG, with caching
   of the second Box–Muller Gaussian draw.
2. Streaming population diversity estimators without per-column scratch
   vectors. Auxiliary output memory scales with the number of decision
   variables; live population and per-candidate genomes remain allocated.
3. No per-candidate cache/uniqueness key allocation when the corresponding
   feature is disabled; two-pass weighted gene selection avoids a per-gene
   weight vector.
4. Compensatory elite correlations computed once per generation, not once
   per offspring; quadratic-memory linkage is skipped for >256 dimensions.
5. Strict true objective call accounting for the supported single-callback
   objective interface, and validity-first reporting rather than claiming
   unconstrained scalar fitness is feasible for constrained problems.

**Performance is not measured.** These are plausible computational
improvements, not proven relative speedup or improvement in solution quality.

## Acceptance criteria before asserting “full equivalent”

- Independently specify whether equivalence means public API, accepted
  features, numerical outputs within tolerance, stochastic distribution,
  or exact RNG sequences. They cannot all be assumed from the word “port”.
- Create Python-vs-Rust deterministic operator fixture tests: identical
  initial population vectors, explicit random draws, exact bounds and
  numerical corner cases; compare both generated offspring within declared
  numerical tolerance.
- Apply and test `number_of_crossover_parents`, composed rate/selector
  configurations, and the original factory's full operator mapping.
- Integrate paired assignment, scenario/censored credit and separately
  instrumented actual physical evaluation counters. For every censored or
  unknown event, require source-backed evidence; never infer physical
  success from a finite objective return.
- Test Rust and Python implementations across a frozen, predeclared set of
  objective functions, seeds, constraints, timeouts, budgets, and baseline
  metrics. Use identical **true evaluation budgets**. The documented
  prospective protocol in `main/RELIABILITY_ROADMAP.md` was not approved or
  run merely by writing this file.
- Profile real hotspots with a declared workload and record paired
  wall-clock and allocation measurements. An optimized Rust implementation
  may be faster on cheap objectives, while expensive physical fitness
  callbacks dominate execution time in other workloads.

## Running existing checks

```bash
cargo test --all-targets
cargo run --example rastrigin
cargo build --release
```

These checks test Rust implementation contracts. They **do not** certify
binary compatibility with GAdapt's original Python package or better
optimization reliability. New functionality stays isolated on `rust-rewrite`
until the full checklist has evidence.
