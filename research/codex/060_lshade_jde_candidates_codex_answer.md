**Recommend NiaPy 2.7.1’s L-SHADE, conditional on reference validation.** It combines recent maintenance, explicit Python 3.14 support, inspectable Python code, and an objective-level evaluation cap. This research was read-only; nothing was installed or modified.

Live shortlist, checked **24 October 2026**:

| Package / algorithms | Latest release; license | Budget, integers, seeding | Python 3.14 installation |
|---|---|---|---|
| **[NiaPy](https://pypi.org/project/niapy/)** — L-SHADE, jDE, iL-SHADE | **2.7.1; 2026-08-17; MIT** | `Task(max_evals=B)` checks before each objective call. Continuous candidates; supply integer decoding. Algorithm `seed=` uses NumPy Generator. | **Yes:** pure Python `py3-none-any` wheel; explicitly advertises 3.14. |
| **[MinionPy](https://pypi.org/project/minionpy/)** — L-SHADE, jSO; j2020 rather than original jDE | **1.9.1; 2026-08-25; MIT** | `maxevals` and `seed=`; **L-SHADE can overshoot by a batch**. External rounding needed; configurable bound repair. | **Yes:** native `cp314` wheels for macOS ARM64/x86-64, Linux x86-64 and Windows. |
| **[MEALPY](https://pypi.org/project/mealpy/)** — L-SHADE | **3.0.3; 2025-08-16; MIT** | `max_fe` checked after generations; needs hard wrapper. `IntegerVar` rounds on decoding; `solve(seed=…)`. | Pure Python wheel, but **released dependencies require NumPy ≤1.26.0**, incompatible with your NumPy 2.5 environment. |
| **[DetPy](https://pypi.org/project/detpy/)** — L-SHADE | **2.0.0; 2025-12-27; GPLv3 metadata**, versus MIT repository LICENSE | `max_nfe` has population-level accuracy; wrapper needed. Real-valued candidates require external rounding. Seed global NumPy/Python RNGs. | Pure Python wheel; metadata permits 3.14, but runtime/dependency compatibility remains unverified. |

Important implementation evidence: [NiaPy’s hard guard](https://github.com/NiaOrg/NiaPy/blob/v2.7.1/src/niapy/task.py), [Minion’s batch loop](https://github.com/khoirulmuzakka/Minion/blob/v1.9.1/minion/algorithms/de.cpp), [MEALPY’s released dependency pin](https://github.com/thieu1995/mealpy/blob/v3.0.3/requirements.txt), and [DetPy’s budget loop](https://github.com/Blazej-Zielinski/detpy/blob/main/detpy/DETAlgs/base.py). Wheel availability establishes packaging feasibility, not tested compatibility with your complete environment.

**CEC reproduction:** I found no verified reproduction of published L-SHADE/jDE/jSO result tables for these releases. NiaPy has [repeatability/custom-function/Griewank tests](https://github.com/NiaOrg/NiaPy/blob/master/tests/test_shade.py); MEALPY’s [SHADE tests](https://github.com/thieu1995/mealpy/blob/v3.0.3/tests/evolutionary_based/test_SHADE.py) chiefly check output types/shapes. Minion includes CEC functions and [budget/status tests](https://github.com/khoirulmuzakka/Minion/blob/v1.9.1/tests/test_minionpy.py); that does not establish published-performance reproduction.

Historical **PyADE** documentation lists L-SHADE/jSO, but `pyade-python` on PyPI and its original GitHub repository currently return 404; I would exclude it from maintained candidates.

**Tanabe 2024 changes the interpretation.** [The paper](https://arxiv.org/html/2404.03303v1), DOI **10.1145/3638529.3654019**, finds strong dependence on mutation and integer repair; SHADE’s parameter adaptation often performs poorly, while CoDE/CoBiDE controls and jDE controls can perform well. Its budgets extend to \(10^4D\), versus your roughly **39–1111 evaluations/dimension**. This supports testing, not assuming, L-SHADE superiority. The [author’s Python research code](https://github.com/ryojitanabe/de_bbobmixint) supplies Baldwinian/Lamarckian handling, but has no release, pip package, or explicit license; last push was April 2024.

Before use:

1. Pin NiaPy and dependencies; audit paper settings, including **initial population \(18D\)** rather than fixed library defaults.
2. Reproduce CEC2014 **F1, F9 and F17**, D=10/30, with official data and corrected author reference, using 51 runs. Preregister tolerances for mean error and dispersion; compare distributions, not identical seeds across languages.
3. Test budgets **3000, 3001 and 10000**, including initialization, duplicates and failed PF calls. Keep I57’s guard and obtain outcomes exclusively from its evaluator.
4. Reuse [I57 decoding](/Users/danijel/Desktop/gadapt/research/iteration57_external.py:50): `clip(rint(x),0,R−1)`, then `lo+k*step`. Freeze whether rounded values overwrite population coordinates.
5. Tune penalties/population choices only on development instances, then freeze.

A **150-line own implementation is not inherently safer**. Use it only after equivalent validation; target corrected **L-SHADE 1.0.1**—the [author documents an archive bug in 1.0.0](https://ryojitanabe.github.io/publication).

DOIs corroborated against author sources: L-SHADE **[10.1109/CEC.2014.6900380](https://doi.org/10.1109/CEC.2014.6900380)**; Brest et al. jDE **[10.1109/TEVC.2006.872133](https://doi.org/10.1109/TEVC.2006.872133)**. **Direct doi.org/Crossref retrieval was blocked, so registry verification remains incomplete.**