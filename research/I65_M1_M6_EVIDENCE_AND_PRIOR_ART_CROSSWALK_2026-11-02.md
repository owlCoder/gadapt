# I65 — reconciliation of authoritative M1–M6 gates, scientific claims and verified prior art

**Date:** 2026-11-02. **Kind:** documentation-only, independent adversarial desk review; **NO new optimization/COCO/OPF/PF runs and NO code/method changes**.  
**Baseline:** `owlCoder/gadapt/main` `0aece5acd1b4702ff686e37187bbf2d4d214a857`.  
**Binding research decision:** `novelty not established / DRAFT / NO-FREEZE / held-out COCO NOT_RUN`. No human gate sign-off has been received or implied.

## 1. Critical documentary correction: M1–M6 already have exact source definitions

The latest [2026-11-02 mentor package](I65_SUPERVISOR_DECISION_PACKAGE_2026-11-02.md) says that the authoritative wording of M1–M6 must be verified. **It is already present** in the repository's older [`SUPERVISOR_DECISION_PACKAGE_2026-11-01.md`](SUPERVISOR_DECISION_PACKAGE_2026-11-01.md), in its **Section 3, table rows M1–M6**. Those definitions are a *human-review gate ledger*, not credentials already signed by a supervisor. We reuse their **actual wording** rather than deriving a new set of M1–M6 names.

| Original reviewer gate (2026-11-01 source) | Engineering evidence accrued by 2026-11-02 | Correct current disposition without human approval | Related 2026-11-02 question |
|---|---|---|---|
| **M1 — full-clone compatibility:** original source hashes, 341 restored aliases, inexpensive I41/I63/I64 full-clone regression | Actual Python 3.12 [#41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925) **completed/success** on 341 hash-restored aliases and selected legacy tests; the older ledger's `NOT_TESTED` label is stale as a *technical-run status* | **TECHNICAL_EVIDENCE_PASS; independent reviewer ACCEPTANCE UNSIGNED.** Keep the known expected xfails and omitted optional dependencies in scope | Not directly C1–C6; prerequisite for all |
| **M2 — adapter instrumentation:** completed GA generation, DE callback/init, pycma ask/tell and partial generations, B−1/B/B+1, failed/nonfinite attempts, within-budget terminal witness, two-process replay | Isolated I65 budget tests and selected SciPy smoke and terminal-witness tests have passed; a complete approved GAdapt/SciPy/pycma integration demonstration in one frozen experimental adapter remains absent | **PARTIAL / INTEGRATION REVIEW BLOCKED** | C2, C3, C6 |
| **M3 — independent infrastructure oracle:** distinguish PF/OPF entrypoints from wrapper calls, numerical faults, feasibility, constraints and independent physics witness | Genuine [API trace #41385833963](https://github.com/owlCoder/gadapt/actions/runs/41385833963); [Newton #41413792862](https://github.com/owlCoder/gadapt/actions/runs/41413792862); [dispatch #41419711114](https://github.com/owlCoder/gadapt/actions/runs/41419711114); [case30 lineage #41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142), all narrowly PASS | **NUMERICAL SOFTWARE INDEPENDENCE ESTABLISHED ON ONE DEVELOPMENT CASE; PHYSICAL DATA/MODEL INDEPENDENCE NOT_ESTABLISHED.** Original fixed candidate remains reactively infeasible (independent penalty 0.5991137833375704) | C2, C3, C4, C5 |
| **M4 — official COCO oracle:** distinguish single-objective `bbob` f21/f24 from `bbob-biobj`, prove domain/instance/optimum/fopt access | Written official-function identification only; no new `cocoex` runtime or held-out access and no certified normalization scale | **RUNTIME NOT_TESTED / GO TO FREEZE BLOCKED** | C6 |
| **M5 — statistical/freeze reviewer:** six simultaneous C–E/C–D contrasts including reach-rate noninferiority, failure policy and nested instance/seed uncertainty | [I65 DRAFT](ITERATION65_DRAFT_PROTOCOL_SR.md) proposes four directly specified max-t contrasts, but its reach-rate pair remains a **required family expansion before FREEZE**; 3 held-out instances cannot support broad generalization | **UNFROZEN / HUMAN STATISTICAL REVIEW PENDING** | C6 |
| **M6 — supervisor originality/scope:** explicit dissertation sufficiency decision for empirical and evaluation-integrity work or a new method | [Nov 1](RESEARCH_DECISION_2026-11-01.md) and [Nov 2](I65_SUPERVISOR_DECISION_PACKAGE_2026-11-02.md) reject ungrounded originality; no signed decision | **PENDING HUMAN DECISION / NO OPTIMIZER NOVELTY CLAIM** | C1 |

**Key distinction:** `technical check completed` ≠ `independent reviewer accepted the scientific claim` ≠ `supervisor approved a doctorate thesis scope or freeze`.

## 2. Prior-art adversarial desk check (2026-11-02)

The following *publisher/official-project/DBLP landing records* were independently located in this review; **the Crossref API itself could not be accessed in this environment**. Accordingly the table verifies the landing metadata and technical existence, **not Crossref registration through the required API**. This is a targeted prior-art challenge, not a comprehensive systematic review.

| Established method/idea | Direct source/DOI landing | Which candidate claim it undercuts |
|---|---|---|
| IPOP-CMA-ES, larger population after repeated restarts | Auger & Hansen, *A Restart CMA Evolution Strategy with Increasing Population Size*, CEC 2005, [DOI 10.1109/CEC.2005.1554902](https://doi.org/10.1109/CEC.2005.1554902), matched with DBLP bibliographic record | Claims that population-increasing CMA restarts or CMA restart alone are new |
| BIPOP-CMA-ES, interleaving two population-size restart modes | Hansen, *Benchmarking a BI-population CMA-ES on the BBOB-2009 Function Testbed*, GECCO 2009, [DOI 10.1145/1570256.1570333](https://doi.org/10.1145/1570256.1570333), independently listed by the CMA-ES official project | Claims that simple restart portfolios or switching between population regimes are novel |
| Target-based evaluation-count runtimes, ECDF and anytime performance | Hansen, Auger, Brockhoff, D. Tušar & T. Tušar, *COCO: Performance Assessment*, [arXiv:1605.03560](https://arxiv.org/abs/1605.03560), [official COCO documentation](https://numbbo.github.io/coco-doc/perf-assessment/) | Novelty attributed solely to ECDF/AUC, censored time-to-target, or counting objective calls |
| EAF as alternative to target-based ECDF; area over curves as an anytime summary | López-Ibáñez et al., IEEE TEVC, publisher [DOI 10.1109/TEVC.2024.3462758](https://doi.org/10.1109/TEVC.2024.3462758) | Novelty solely from EAF-based summaries or an anytime curve area |
| Reporting/replication challenges for evolutionary computation | *Reproducibility in Evolutionary Computation*, ACM TELO, [DOI 10.1145/3466624](https://doi.org/10.1145/3466624) | Claim that environment/source hashes or reproduction by themselves constitute a new general theorem |
| Evaluation framework for algorithm comparison | *A Methodology for Comparing Optimization Algorithms for Auto-Tuning*, Future Generation Computer Systems, [DOI 10.1016/j.future.2024.05.021](https://doi.org/10.1016/j.future.2024.05.021) | Unsupported priority for a generic algorithm comparison methodology |
| Landscape-feature benchmarking footprints | *Benchmarking Footprints of Continuous Black-Box Optimization Algorithms*, Swarm and Evolutionary Computation, [DOI 10.1016/j.swevo.2025.101895](https://doi.org/10.1016/j.swevo.2025.101895) | Unsupported priority for algorithm-specific failure footprints |

**Actual conclusion:** previous practice covers restart/CMA, portfolios, target-based ECDF, EAF, standard benchmarking and reproducibility principles. The current proposed GAdapt→CMA stagnation transition has **no demonstrated precise mathematical difference** sufficiently justified as a doctoral-level novel optimizer. A scoped **empirical/instrument-integrity** dissertation may nevertheless be feasible **only if accepted by the supervisor**, using carefully characterized evidence and no priority claims beyond verified facts. Independent-source novelty vetting has not been completed.

## 3. Formal normalization counterexample — prerequisite for M4/M5

The older [`SUPERVISOR_DECISION_PACKAGE_2026-11-01.md`](SUPERVISOR_DECISION_PACKAGE_2026-11-01.md) warns that the I65 draft's `s_i` scale is described as a median of 4,096 uniform sampled **values** without clearly stating *excess over `f_opt`*. To make the scientific failure condition explicit:

Assume a deterministic minimization function with three illustrative sampled values `[1,2,3]` and optimum `f_opt=0`. If `s = median(f(x)) = 2`, then the sample of cost `f(x)=1` has `g=(1-0)/2=1/2`. Now shift **the same optimization task** by an arbitrary constant `c=100`: `f'(x)=f(x)+100` and `f'_opt=100`. The *uncentered* denominator becomes `median(f'(x))=102`, so `g'=(101-100)/102=1/102` even though all optimizer comparisons and objective gaps are identical. **The metric is not invariant to an additive objective offset.**

If instead the scale is the **median of sampled gaps** `median(f(x)-f_opt)`, its value is `2` both before and after that same shift, so the normalized gap is unchanged. This sufficiency statement needs explicit conditions: `f_opt` must be independently certified and unavailable to the optimizer; every sampled finite value and `s_i>0` must be checked; setup calls must be disclosed; and no held-out samples or results may be used to decide the rule. **This analysis does not amend the I65 DRAFT** or authorize 4,096 setup calls.

The exact number 3 here is a *proof counterexample*, **not** a run of COCO, real empirical sample, new normalization recommendation already approved, or retrospective rescaling of archived results. An independently reviewed prospective M4/M5 change and a new actual freeze decision would be needed.

## 4. Explicit routing to the existing unsigned C1–C6 decision package

- **C1 ← M6:** define the thesis's original scientific contribution and whether existing empirical/integrity results suffice.
- **C2 & C3 ← M2 + M3:** decide accounting boundary, setup OPF, search PF, terminal/interstage witness, exceptions and inner Newton function calls. 325 independent Newton residual evaluations **do not equal** 325 external physical PF calls.
- **C4 ← M3:** decide whether two separate numerical solvers using one classical AC model and **the same** public case satisfy *software-independence only* or whether a separately sourced physical case is indispensable.
- **C5 ← M3:** distinguish `CONVERGED` from the **independently replicated reactive infeasibility** of the original fixed `case30/j1` midpoint.
- **C6 ← M2 + M4 + M5:** before any holdout freeze approve one official `bbob` oracle, exact `f_opt`, scale derivation, all six simultaneous contrasts, seed/instance dependence, budget and final-witness semantics.
- **M1** supplies the technical full-clone regression prerequisite but has **no stand-alone novelty or human approval implication**.

## 5. Current GO / NO-GO and next request

**Research question:** are the existing independently verified, negative-aware GAdapt evaluations plus instrumentation and public-data transformation evidence sufficient for a scoped empirical dissertation; if not, which precise original theorem/method and independent external grid data must be newly justified?  
**Precise novelty claim:** `NOT_ESTABLISHED`; classical Newton, restart CMA, ECDF/AUC, source provenance and obvious sequential reservations are known techniques.  
**Formal assumption/falsification:** one Python objective may trigger many solver calls; a valid witness requires explicit charged resource accounting, independently documented model assumptions and full feasibility checks. The known fixed midpoint violates reactive constraints. Any alleged model-independent claim fails if both solvers use the same mathematical network source.  
**Strong baselines:** GAdapt-M, SciPy DE, CMA-ES, IPOP, BIPOP and frozen E3 hybrid for a **future approved** study.  
**Computational budget:** **zero new optimizer/objective/PF/OPF experiments in this review**. Prospective 12,000/3,000 per-run attempt budget remains DRAFT, not redefined.  
**GO:** supervisor's signed originality/scope and M1–M6/C1–C6 decision, independent data-source review, approval of budget/normalization/statistics with immutable versioned source.  
**NO-GO:** new policy C code, any held-out COCO f21/f24 run, re-running an experiment to force a positive result, or reporting a protocol as FROZEN without actual dated human authorization.

**NEXT STEP:** present [the revised unsigned supervisor package](I65_SUPERVISOR_DECISION_PACKAGE_2026-11-02.md) together with this evidence crosswalk and request the dated reviewer disposition `PENDING / APPROVE_SCOPED_EMPIRICAL / REQUEST_CHANGES / NO_GO`. Until a real decision is received: **NO-FREEZE / COCO NOT_RUN / originality NOT_ESTABLISHED**.
