# I56 development pilot (EXPLORATORY, development scenario only; not a hypothesis test)

Script: `research/iteration56_dev_pilot.py` (GAdapt defaults, static penalty losses + 1e3·Σviolations, step = grid
step, 3000 power flows, development scenario load_factor 0.95 / scenario seed 101 / spread 0.1). Purpose: check that
the ORPD instrument discriminates (feasibility is nontrivial and resolution-dependent) before writing the protocol.
These scenarios are excluded from the test set of I56.

Columns: case, load_factor, resolution R, seed, best feasible losses (MW; inf = none found), calls to first feasible,
continuous AC OPF losses with case taps/shunts (NOT a lower bound: taps/shunts are optimized here), seconds.

```
case14 0.95 33 3 9.028243366494728 113 9.094271142355009 11.1
case14 0.95 9 2 inf None 9.094271142355009 11.7
case14 0.95 9 1 inf None 9.094271142355009 12.3
case14 0.95 33 1 9.722335679825054 230 9.094271142355009 12.5
case14 0.95 33 2 9.089692700389104 52 9.094271142355009 12.8
case14 0.95 9 3 inf None 9.094271142355009 13.0
case57 0.95 9 2 15.258890733575253 547 14.299884753499587 14.5
case57 0.95 9 1 15.614719222854353 753 14.299884753499587 15.4
case57 0.95 9 3 14.944073574525273 675 14.299884753499587 14.9
case57 0.95 33 1 13.936304646554465 322 14.299884753499587 15.1
case57 0.95 33 2 14.030882321705159 626 14.299884753499587 14.9
case57 0.95 33 3 13.589310556644389 279 14.299884753499587 15.0
case118 0.95 9 2 inf None 77.74336762070119 17.0
case118 0.95 9 1 inf None 77.74336762070119 17.3
case118 0.95 9 3 inf None 77.74336762070119 16.6
case118 0.95 33 1 90.83235936836624 2505 77.74336762070119 15.9
case118 0.95 33 3 inf None 77.74336762070119 10.5
case118 0.95 33 2 inf None 77.74336762070119 12.1
```
Observation (descriptive): case57 feasible 6/6; case14 feasible only at R = 33 (3/3, none at R = 9); case118 1/6.
Two case118 runs ended in ~11 s instead of ~16 s (not yet explained; check whether GAdapt stopped before the budget).
