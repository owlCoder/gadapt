# Network-constrained infrastructure benchmark (exploratory)

The benchmark uses **pandapower**'s published IEEE 14-bus and IEEE 118-bus
test networks with the AC Newton–Raphson power-flow engine. It does not use
a synthetic mathematical sphere / Rastrigin function as the objective.

The control vector consists of generator voltage setpoints for a fixed subset
of generators (four on IEEE14, up to eight on IEEE118). We minimize
active network losses (MW), subject to a bus voltage window [0.94, 1.08] p.u.
and branch/transformer loading below 100%. We scale all base-case P/Q
demands by 1.0 or 1.15 for a sensitivity experiment. The optimizer gets a
penalty proportional to the aggregate physical violation, but final
feasibility is evaluated **again** by an independent AC power-flow run.
Q limits are enforced in the AC power-flow calculation.

This is an **engineering network simulation benchmark**, not validation
on live production utility measurements. IEEE network parameters are public
test systems, not evidence of a utility deployment. The candidate control
subset and thresholds have been specified *before* seeing experiment output
and are not universal operating prescriptions.

Compare GAdapt's unchanged metric, the experimental affine metric and SciPy
Differential Evolution using the same population size and approximately
matched objective evaluation budgets. The CSV discloses actual evaluations
and runtime. The algorithms may not consume EXACTLY equal evaluations due
to their internal evaluation schedules; normalize convergence curves by
evaluations in the final study. Four seeds are a smoke/pilot, NOT sufficient
statistical power for a dissertation.

## Reproduction

```bash
python -m pip install -e .
python -m pip install 'pandapower==2.14.11' 'scipy==1.13.1'
python research/ieee_grid_benchmark.py --runs 30 --ga-generations 60 \
  --output ieee_grid_results.csv
```

Metrics: final AC feasibility rate, loss among feasible runs, numerical
violation, number of objective evaluations, wall time, and AC convergence
status. Include failure cases in success-rate calculations; never silently
discard infeasible results.

Reference: https://pandapower.readthedocs.io/en/stable/networks/power_system_test_cases.html
