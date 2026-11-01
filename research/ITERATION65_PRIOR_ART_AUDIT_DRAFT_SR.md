# I65 — audit of existing evidence and prior art (DRAFT, 2026-11-01)

**Status:** independent working audit; `novelty not established`; at the time of drafting, no GitHub repository changes and no new optimizer experiments. The working repo was `owlCoder/gadapt:main`; `bpzoran/gadapt` and `bpzoran/gadapt_experiments` were read-only. Sources inspected included `AGENTS.md`, `PHD_PROGRESS.md` through the 2026-10-30 handoff, `MENTOR_MEETING_NOTES_SR.md`, `MENTOR_SUMMARY_2026-10-28_SR.md`, `ITERATION64_PROTOCOL.md`, `ITERATION64_S0_REPORT_SR.md`, I64-E/E3/A/R/I/I2 reports, E/E3 specifications, and the original I64 E/E3 benchmark modules. Not every old raw archive was independently reviewed, and the audit does not claim to have reproduced all prior analyses.

## 1. Existing-evidence matrix: why earlier experiments must not be repeated

| Study | Established in its fixed design | Negative, contradictory, or unresolved findings |
|---|---|---|
| I64-S0 | Mentor benchmark replication: 21 cells, four methods, 20 seeds, 1,680 runs. GAdapt-M A=0.698; DE A=0.651. | DE has a better final cell median in 14/21 cells. The original generation counts are not equivalent to objective calls. S0 is not BBOB. |
| I64-E | 12,000 actual calls, shifted/rotated functions, 63 cells, nine methods. GAdapt-M A=0.6732, IPOP=0.7699, BIPOP=0.7688, DE=0.6396. | Frozen H64a outcome is opposite; the CMA family has greater aggregate evaluation efficiency, without universal infrastructure superiority. |
| I64-E3 | First 30% of the budget GAdapt, remaining 70% CMA. On rotated cells, hybrid A=0.7196 versus M A=0.6167. | H64g2 opposite because of worse nonrotated tail; H64g3 undecided against IPOP; the hybrid is not a novel method. |
| I64-A | Replacing the initial 30% phase with random sampling reduces A by 0.131 under Q and 0.178 without Q. | This is conditional on a fixed CMA initialization at `sigma0=0.05`, not a general independent advantage for GAdapt. |
| I64-R | Same-shift paired design. Additional Q reduces GAdapt A by 0.0809 [0.0721, 0.0897] and IPOP A by 0.0101 [0.0036, 0.0166]. | Do not generalize from 21 fixed Q choices and one function roster. The causal mechanism remains unidentified. |
| I64-I | Discrete ORPD, eight cells × 30 seeds and 12,000 physical PF calls: GAdapt feasibility 0.746, IPOP 0.771. | GAdapt–CMA/IPOP/BIPOP intervals contain zero. Two cells are nearly infeasible. References are not certified discrete optima. |
| I64-I2 | ORPD hybrid feasibility 0.742, CVaR 0.3772. | Better tail than GAdapt-M unconfirmed; worse than IPOP (0.2518). Provenance caveat: `i_run_sha256` blank in the archived I2 file, checked subsequently. |
| I64-E2/E4/C/N (context) | Differential crossover and compensatory mutation have not been shown to close the gap; the C mechanism was unsupported, and the N Potts probe found no anticipated label-dependence defect. | Do not add or retune variants merely because existing results are negative. |

**Active handoff at the time of this audit:** `PHD_PROGRESS.md` ended with the 2026-10-30 status: a supervisor decision about dissertation scope was still pending and no new method was confirmed. An older "NEXT STEP" is not authorization to run an expensive confirmatory experiment.

## 2. Existing instrumentation

- `research/i64/e_common.py`: reference `Budget`, `BudgetReached(BaseException)`, incumbent witness and evaluation events. Verified Git blob SHA: `3aab99773a7e4a95b7972a3c8061c50bd471618d`.
- `research/i64/e_algos.py`: GAdapt-M, DE `best1exp` with 64 initial candidates, CMA restarts, IPOP, BIPOP and other methods. CMA operates on the unit cube; GAdapt/DE use native coordinates. GAdapt's sensitivity to unit changes is a known comparison issue.
- `research/i64/e3_algo.py`: the fixed GAdapt→CMA hybrid already exists. It must not be reimplemented under a new name and represented as a novel method.
- GAdapt's original `exit_check="min_cost", max_attempt_no=20` is not equivalent to the proposed *significant-improvement* criterion with two epsilons. SciPy's `tol` measures population-value dispersion, not completed-generation stagnation. All compared methods require comparable **physical call** accounting, not generation counts.

## 3. Closest prior art and limits on novelty claims

| Source and DOI | Existing method / finding | Relationship to proposed candidate |
|---|---|---|
| Auger & Hansen (2005), `10.1109/CEC.2005.1554902` | CMA-ES restarts with an increasing population (IPOP). | Restart as such is **known**, not novel. |
| Hansen (2009), `10.1145/1570256.1570333` | BIPOP uses two population/budget regimes. | Portfolio restart policy is **known**. |
| Wineberg & Opawale (2018), `10.13164/mendel.2018.1.017` | Stagnation criteria for IPOP-like DE restarts; `EqualFunValHist`. | Further evidence that stagnation detection and restart are established ideas. |
| Zhang et al. (2023), `10.1109/MCI.2022.3222057` | Switching time between metaheuristics controlled by (deep) Q-learning, including univariate HSES → CMA. | Sequential algorithm switching is **known**; a fixed 20-generation rule is a simpler engineering case. |
| Scientific Reports (2021), `10.1038/s41598-021-04549-1` | IR-CMA-ES switches to a DE redistribution phase after CMA stagnation. | Related stagnation-triggered algorithm switching, in the opposite direction. Novelty remains unestablished. |
| Muñoz, Sun, Kirley & Halgamuge (2015), `10.1016/j.ins.2015.05.010` | Review of algorithm selection, portfolios, hybrids and landscape features for black-box optimization. | Problem-feature-based algorithm selection is established prior art. |
| Krasnogor & Smith (2005), `10.1109/TEVC.2005.850260` | Memetic and hybrid algorithms; already cited in I64-E3. | Global-to-local GAdapt→CMA hybrid is an established design pattern. |

**DOI provenance:** the DOI associations were checked against the indexing/publisher pages linked below (using the original publisher for the Scientific Reports item). Direct Crossref API verification was unavailable during this audit; this is not a claim of a further independent Crossref audit. The review is not an exhaustive systematic literature survey.

**Sources:**
- https://dblp.org/rec/conf/cec/AugerH05.html
- https://cma-es.github.io/index.html
- https://explore.metascienceobservatory.org/papers/W2097263684
- https://ib-b2b.test.infv.eu/index.php/mendel/article/view/14
- https://scholarlypublications.universiteitleiden.nl/handle/1887/3721895
- https://www.nature.com/articles/s41598-021-04549-1
- https://research.monash.edu/en/publications/algorithm-selection-for-black-box-continuous-optimization-problem/
- https://github.com/owlCoder/gadapt/blob/main/research/ITERATION64_E3_SPEC.md

## 4. Scientific gate

- **Research question:** can a simple, prespecified stagnation rule improve the final tail at 12,000 calls on f21/f24 compared with fixed E3 and IPOP?
- **Precise novelty claim:** `novelty not established`. Simple optimizer switching or restart is not a new algorithmic contribution. There is no basis for claiming a new doctoral-level optimizer.
- **Formal assumptions:** `f: X → R ∪ {nonfinite}` is deterministic for a fixed instance; an evaluator uses sequential attempt accounting; each attempt reserves one unit of B; budgets and seed logs are truthful.
- **Instrumentation bound, NOT a scientific theorem contribution:** if `n` is checked against `B` and incremented **before** each invocation, induction gives `n ≤ B`, with no call beyond the Bth reserved attempt. Parallel/batched evaluation requires atomic reservation for every element; do not assume the sequential argument applies there.
- **Falsification:** no improvement, or worse tail relative to IPOP/E3; unsuccessful independent witness checking; unfair physical-call counts; switching before 20 completed generations; held-out instances reversing the putative advantage.
- **GO/NO-GO:** GO only for a cheap instrumentation gate and independent review of a restricted *empirical* protocol. **NO-GO for a novelty claim**. Under `AGENTS.md`, STOP before implementing a new algorithmic intervention until the novelty gate is separately resolved. Do not freeze or run expensive confirmation simply to obtain a positive outcome.
