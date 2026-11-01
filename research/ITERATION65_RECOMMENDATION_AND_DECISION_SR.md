# I65 — final GO/NO-GO and practical recommendation (2026-11-01)

## Status of the original research session

The original session reviewed `AGENTS.md`, `PHD_PROGRESS.md`, and major I64 protocols/results on `owlCoder/gadapt:main`. At that time GitHub was not modified and upstream repositories were read-only. I65 was **not frozen**; confirmatory run count: **0**; there were no new COCO successes/failures or CVaR/ECDF comparisons. A DRAFT must not be represented as preregistration. Later archival and translation commits are separately documented.

## Evidence from earlier studies (not new experiments)

| Claim | Evidence in prior documents |
|---|---|
| GAdapt's early evaluation efficiency in the original mentor benchmark | I64-S0: GAdapt A=0.698, SciPy DE A=0.651; DE has a better final cell median in 14 of 21 cells. |
| Orthogonal-transformation sensitivity | I64-R, matched shift: GAdapt A loss = 0.0809 [0.0721, 0.0897] versus IPOP loss = 0.0101 [0.0036, 0.0166]. |
| Fixed GAdapt→CMA on synthetic functions | I64-E3: rotated A_hybrid=0.7196 versus A_G=0.6167, but the hybrid failed its overall prespecified decision criterion. |
| First-stage GAdapt contribution | I64-A: replacing the initial 30% GAdapt stage with random sampling worsens A in that fixed hybrid; this does not prove a new method. |
| Infrastructure feasibility | I64-I/I2: ORPD feasibility GAdapt=0.746, IPOP=0.771, hybrid=0.742. Hybrid advantage on ORPD was not confirmed, and IPOP CVaR=0.2518 is better than hybrid=0.3772 with a statistically supported I2 contrast. |

## Rules for practical evaluation

1. For new, strongly coupled/rotated continuous problems, use **IPOP-CMA-ES as a strong default evaluation reference**, alongside BIPOP and DE controls. This is a conservative starting shortlist, not proof of universal superiority.
2. GAdapt-M is a justified competitor where previously tested task structure and budget demonstrate good early efficiency. Given I64-R, there is no general recommendation for unknown rotated functions.
3. The fixed GAdapt→CMA hybrid is a legitimate candidate for an engineering pilot, **not** an unconditional industrial choice: I64-I2 did not confirm transfer of the synthetic benefit to ORPD.
4. Candidate C, the stagnation-triggered GAdapt→CMA method proposed in I65, has **no measurements**: **UNTESTED / NOT_RECOMMENDED** for deployment. For each infrastructure run, verify bounds, constraints, the returned objective value, and a defined fallback. If quality/feasibility cannot be demonstrated, report `NOT_SOLVED`.

## Gate decisions

| Gate | Decision |
|---|---|
| Methodological prior art | **NO-GO**: `novelty not established` (IPOP/BIPOP, restarts, portfolios, memetic/algorithm-switching strategies already exist) |
| I65 sandbox tests | **GO** for independent instrumentation review: 54 passing and three expected-failing tests |
| GAdapt/CMA/COCO integration | **BLOCKED / NOT_TESTED** in the local environment |
| I65 FREEZE | **NO-FREEZE**: independent review, environment lock, and validated COCO instances/optimizer adapters missing |
| Confirmatory I65 (18 COCO cells, nine optimizers) | **NOT_RUN**; neither a GO nor an empirical-quality NO-GO for candidate C is supported |
| Industrial reliability | **NO-GO** for readiness or universal-performance claims |

### What can 30 seeds tell us about rare failure probabilities?

Even with **zero observed failures** in 30 independent runs from one distribution, the exact one-sided 95% upper bound on failure probability is `1 - 0.05**(1/30)` ≈ **9.50%**. If all 90 runs across three instances could defensibly be treated as i.i.d., the analogous bound would be about **3.27%**, still far from a suitably rare industrial failure risk. Instances differ in this protocol, so 90 runs may not automatically be pooled as i.i.d. samples from one target problem. A common distributional model would have to be justified.

**Final conclusion at the time of this report:** I65 is a narrow, reproducible empirical hypothesis with a laboratory-validated instrumentation subset, **not** a confirmed novel optimizer. IPOP is a strong conservative control for the next real experiment; the untested stagnation hybrid is not recommended. It is also unjustified to claim empirical inferiority of candidate C, which has never been run.
