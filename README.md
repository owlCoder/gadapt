# GAdapt — Rust rewrite

This branch is a **native Rust** rewrite of the GAdapt self-adaptive genetic algorithm library. It has no Python, NumPy, PyO3, or runtime dependency on a Python interpreter. The public API is Rust-native rather than a drop-in replacement for the legacy Python API.

The previous Python implementation remains on the repository's `main` branch; its historical research archive and attribution have not been modified. Original authorship: [bpzoran/gadapt](https://github.com/bpzoran/gadapt); this research fork is maintained by owlCoder.

## Build

```bash
cargo test --all-targets
cargo run --example rastrigin
cargo build --release
```

## Usage

```rust
use gadapt::{GA, ExitCriterion};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut ga = GA::new(|x: &[f64]| (x[0] - 2.0).powi(2) + (x[1] + 1.0).powi(2));
    ga.add(-5.0, 5.0, None)?;
    ga.add(-5.0, 5.0, Some(0.01))?;
    ga.options.number_of_generations = Some(100);
    ga.options.exit_criterion = ExitCriterion::Generations;
    ga.options.seed = 1234;
    let result = ga.execute()?;
    println!("best objective: {:?}; parameters: {:?}", result.best_objective, result.result_values);
    Ok(())
}
```

Constrained objectives return an explicit nonnegative aggregate violation, **zero only when feasible**:

```rust
use gadapt::GA;

let mut ga = GA::constrained(|x| {
    let objective = (x[0] - 2.0).powi(2);
    let violation = (x[0] - 1.0).max(0.0);
    (objective, violation)
});
ga.add(-2.0, 3.0, None).unwrap();
ga.options.max_evaluations = Some(2048);
ga.options.acceptable_cost = Some(1.0);
ga.options.reliability_mode = true;
let result = ga.execute().unwrap();
println!("{:?}", result.solution_status);
```

For fallible callbacks, use `GA::try_new(|xs| -> Result<Fitness,String> { ... })`. Callback errors and nonfinite evaluations count against the actual evaluation budget and are rejected as invalid. In reliability mode, the best *evaluated* feasible candidate is preserved in the returned result, even if scalar selection or restarts remove it from the current population.

## Components

- Decision variables: bounded real-valued and step-quantized.
- Population with selection (roulette, tournament, random, top-to-bottom), elitism, blending/uniform/differential crossover, and normal/random/mixed/extreme mutation.
- Diversity tracking: columnar and cost metrics; mutation amount and intensity respond to population diversity.
- Constraint handling: penalty, adaptive penalty, feasibility rules, epsilon ranking.
- Controlled immigration and optional stagnation-based restart retaining the verified incumbent.
- Deterministic seeded pseudo-random generator with no ambient global RNG.
- Optional evaluation cache (only enable for stationary, deterministic objective functions).
- Hard actual-call budget, invalid-evaluation accounting, separate feasibility and quality status.
- Optional exhaustive finite-grid certification via `options.discrete_certification = true` in reliability mode; only proves absence when all points were validly evaluated.

## Compatibility and scientific caution

**This is a new Rust implementation, not an established bit-for-bit or feature-complete behavioral port of the Python implementation.** In particular it does not yet implement the legacy custom Python factory/plugin interface, scenario-physical-solver credit attribution or all experimental operator-credit variants. The random stream, default mutation schedules, and numerical behavior can differ. The native Rust test suite verifies contracts, **not** superiority or optimizer reliability across problem classes. No performance or solution-quality claims are made without a pre-approved paired-seed benchmark protocol.

To reproduce archived research, consult the original research archive branch rather than applying this rewrite to historical results.

### Additional native compatibility options

`Options::max_mutated_variables`, `max_mutated_candidates`, `strict_mutation_decision_variable_limit`, `mutation_focus_generations`, `mutation_focus_exploration_probability`, and `adaptive_immigration_diversity_threshold` expose the corresponding configuration controls. The mutation candidate count cap is enforced for regular offspring; forced mutations and uniqueness recovery may exceed it, as in Python. The Rust RNG remains different from Python/NumPy. Normal mutation's stagnation-based standard deviation decay and focus are implemented as opt-in controls.

### Opt-in compensatory mutation

Set `ga.options.compensatory_mutation = Some(CompensatoryMode::Gated)` for elite-correlation-linked variable mutation. Ungated, permuted, and conditional-Gaussian resample controls are also available. Correlations are computed once per generation and require at least `dimensions + 2` valid elites; gated mode also requires 3 members in each split. To bound memory and avoid disproportionate overhead in large-dimensional optimization, linkage is disabled above 256 dimensions.

### Allocation-aware execution

The engine only tracks per-candidate bitwise keys when uniqueness is enabled, and only creates evaluation cache keys if caching is explicitly enabled. With a fully stepped discrete variable set, uniqueness is now enabled by default, matching the Python default. Set `options.auto_unique_for_discrete = false` to disable the automatic behavior. Finite-grid absence certification refuses grids whose decimal quantization cannot be conservatively verified.

### Physical-scenario operator-credit accounting

A pure-Rust `VerifiedCallRateBandit` now exposes the Python research branch's optimistic verified-success-per-**actual physical scenario call** heuristic. Callers must supply independently measured `PhysicalObservation` records; success requires all scenarios checked with zero violation. Unknown and censored trials incur paid-call cost without becoming certified successes. This standalone controller is not yet wired into automatic GA mutation selection; do not confuse wrapper objective-call counts with actual external solver calls.

### Stagnation refresh and restart

The Rust engine now accepts `reliability_refresh_patience`, `reliability_refresh_percentage`, and `reliability_restart_after_refreshes` (all opt-in). Refreshes preserve the best genuinely evaluated incumbent and use the same evaluation budget. A full restart is attempted only when enough actual calls remain to evaluate an entire fresh population. `stagnation_refreshes` and `reliability_restarts` are reported independently; unlike a clean CI run, they are not evidence of improved solution quality.

### Custom native Rust operators

Implement the `GeneticHooks` trait and call `ga.set_hooks(hooks)` to override parent selection, crossover and/or mutation independently. Defaults fall back to the in-crate implementations, and custom operators still pass through bounded objective accounting and validation. This is a Rust-native extensibility mechanism, not binary compatibility with Python's user-defined GA factories.
