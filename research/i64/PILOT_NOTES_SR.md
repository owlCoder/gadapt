# I64 — Evaluation-call accounting diagnostic for the mentor's benchmark (NOT preregistered; design guidance only)

**Date:** 2026-10-28. Script: `mbench_count_diagnostic.py`, using mentor classes/operators and parameters from `gadapt_experiments@0e388356`, Sphere, population 64, stagnation 20, generation limit 600. GAdapt needs a shared counter because `GA.execute()` deep-copies the GA. Eight runs per configuration, seeds 0–7. This probe is **not scientific evidence** and does not change the protocol, except by confirming the need to account for actual objective-function calls.

The table retains the source report's numeric notation: the dot separates thousands in call counts, while a comma denotes decimals in other columns (e.g., 9.942 = 9,942 calls; 309,6 = 309.6 generations).

| Sphere | Configuration | Calls per run (mean) | Generations | Calls per generation | Mean final error |
|---|---|---|---|---|---|
| D=7 | GAdapt diversity | 9.942 | 309,6 | 32,1 | 9,4e−9 |
| D=7 | PyGAD random | 19.232 | 600 (limit) | 32,1 | 4,0e−9 |
| D=7 | PyGAD adaptive | 38.400 | 600 (limit) | 64,0 | 1,4e−7 |
| D=7 | SciPy DE | 11.447 | 177,9 | 64,4 | 1,8e−14 |
| D=2 | GAdapt diversity | 5.406 | 167,9 | 32,2 | 1,3e−14 |
| D=2 | PyGAD random | 19.232 | 600 (limit) | 32,1 | 2,2e−123 |
| D=2 | PyGAD adaptive | 38.400 | 600 (limit) | 64,0 | 7,7e−120 |
| D=2 | SciPy DE | 3.558 | 53,8 | 66,2 | 1,9e−19 |

**Descriptive observations from one function:** (1) Generations are not a common cost unit: DE and PyGAD adaptive use about 64 calls per generation, while GAdapt and PyGAD random use about 32. PyGAD adaptive uses twice the calls of PyGAD random for the same generation count. (2) Both PyGAD configurations reach the 600-generation cap because the fitness continues to improve slightly; their apparent "final accuracy at stopping" comes from 2–4 times GAdapt's evaluation budget. (3) On Sphere in this setup, SciPy DE is both faster and more accurate than GAdapt in physical calls. The mentor's claim that GAdapt is "more accurate than that one" is not supported here if the exception is DE; the actual algorithm and function need to be identified first.

This motivated I64-S: equal real-evaluation budgets, independent accounting, more functions, shifted/rotated variants and tail-risk metrics.
