# I65 supervisor decision package — scope, originality, data provenance and budget

**Prepared:** 2026-11-02 for independent supervisor/reviewer judgment.  
**Status:** **DRAFT — NO DECISION SIGNED OR IMPUTED TO THE SUPERVISOR**.  
**Repository:** `owlCoder/gadapt`, research-only, historical GAdapt and archived results unchanged.  
**Decision requested:** a defensible dissertation/publication route **before** new candidate-C algorithm work, protocol freeze, ORPD optimization experiments or held-out COCO confirmation.

## Executive decision request

Choose whether the dissertation can center on a **carefully scoped empirical/evaluation-integrity and reproducibility contribution**, or whether it **requires an independently original new optimization method or theorem**. At present, **no novel I65 optimization method has been demonstrated**; the standard Newton solver, ECDF/call auditing, evaluator-reservation counts and existing selector/restart ideas are known prior art. **No approval for a new algorithmic claim or confirmatory experiment should be inferred from the successful software tests.**

### Evidence that can be defended, and the exact boundary

| Evidence | Verified actual result | Defensible claim | Unsupported broader interpretation |
|---|---|---|---|
| Full historical Python 3.12 compatibility | [Run #41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925) PASS; 341 original alias SHA checks; I41/I63/I64/I65 unit tests per archived gate | Correctness of selected original-source software regressions | All old optimizer experiments scientifically revalidated |
| Actual PYPOWER API attempt trace | [Run #41385833963](https://github.com/owlCoder/gadapt/actions/runs/41385833963) PASS | Setup/search/witness **API entrypoint** counts distinguish I56 candidate counts | Internal Newton iterations, all physical costs or independent oracle |
| NumPy AC equations and I56 constraints | [AC run #41395941943](https://github.com/owlCoder/gadapt/actions/runs/41395941943) PASS; [constraints run #41407293845](https://github.com/owlCoder/gadapt/actions/runs/41407293845) PASS | Reimplemented equations and four I56 penalties agree on one development state | General network feasibility or validated optimizer performance |
| Independent numerical AC PF, generator output and flows | [Newton run #41413792862](https://github.com/owlCoder/gadapt/actions/runs/41413792862) PASS; [dispatch run #41419711114](https://github.com/owlCoder/gadapt/actions/runs/41419711114) PASS; 47/47 tests | A **second independently coded numerical solver** reproduces case30 solution, PV/REF QG, slack PG, branch flows and penalties | Independent **physical** measurement, genuinely separate data/model, Q-limit enforced solution |
| Independent invalidity of fixed candidate | Independent I56 reactive penalty `0.5991137833375704` vs PYPOWER `0.5991137833375748`, both infeasible | The tested single fixed development midpoint violates original reactive limits | Entire optimizer or all case30 candidates are infeasible |
| Public data lineage and case model | [Run #41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142), 17/17 PASS; exact numeric hashes, 1 OPF setup, zero PF | Deterministic transformation from the **installed** PYPOWER 5.1.19 public case30 to the I58 case30/j1 input | Independent grid observations; exact equality to a specific external MATPOWER revision |
| Control-domain scope of case30/j1 | **6 VG + 0 selected TAP + 2 BS** controls in original I56 | This exact developmental case has **no eligible I56 transformer-tap decision variable** | The network has no physical transformers; all ORPD scenarios lack taps |

## Scientific sources and rights

The [MATPOWER case30 description](https://matpower.org/docs/ref/matpower4.1/case30.html) states it is **derived/modified** benchmark data based partly on Alsac & Stott (1974) and later generator data; the separately named [case_ieee30 description](https://matpower.org/docs/ref/matpower4.1/case_ieee30.html) identifies a different IEEE Common Data Format source. The tested **PYPOWER case30.py** source has SHA-256 `f7f8c565be22f30d4ba9facab8707072ef5dc3bacb6ea9ef57245c11e0bde9f6`. Exact external MATPOWER-version equivalence has **not** been tested. PYPOWER [release and license details](https://pypi.org/project/PYPOWER/5.1.19/) state case data are **excluded** from the three-clause BSD *code* license; no raw case arrays were re-published. Independent licensing/data-owner review may be necessary for distribution outside established academic benchmark practice.

### Questions requiring written decisions (C1–C6)

Record one of **Accept / Reject / Needs evidence / Out of scope**, an explicit rationale, responsible reviewer and decision date. **All fields currently UNDECIDED**.

| ID | Decision the supervisor must make | Proposed conservative default pending approval | Decision / rationale / signer |
|---|---|---|---|
| **C1 — originality/scope** | Is a rigorous empirical evaluation-integrity framework and explanatory comparison acceptable as the thesis's main scientific contribution, or is a new mathematical optimizer indispensable? | **No novel optimizer claim**; prioritize careful evaluation audit and context-dependent comparison | **UNDECIDED** |
| **C2 — cost resource** | Should ORPD budget track PF entrypoint and OPF setup separately (vector ceilings), or use an independently calibrated equivalent-cost metric? | Report `OPF_calls`, `PF_calls`, objective calls and witness counts separately; do not silently equate them | **UNDECIDED** |
| **C3 — internal complexity** | Are the independent Newton's residual calculations charged to a physical budget or treated as secondary computing work? | Secondary diagnostic until symmetric PYPOWER internals are also instrumented and cost-calibrated | **UNDECIDED** |
| **C4 — oracle/data independence** | Does numerical-software independence on *the same* AC model and transformed case30 satisfy the witness claim, or are independent measurements/model datasets mandatory? | **Insufficient evidence** for independent physical-model validation; claim only numerical-software independence | **UNDECIDED** |
| **C5 — feasibility** | Must confirmed numerical convergence always be paired with an independently recomputed operational-feasibility check and explicit infeasible flag? | Yes; preserve the observed reactive-infeasible candidate | **UNDECIDED** |
| **C6 — preregistration** | Which exact baselines, held-out cases, seeds, budgets, multiple comparisons, approval signatures and STOP criteria are required before any confirmation? | **No freeze**, no held-out COCO/ORPD runs without signed protocol | **UNDECIDED** |

Existing review questions referenced as **M1–M6** in the research handoffs also require independent supervisor closure. Their **authoritative wording and mapping to C1–C6 must be verified**; this package does not invent an M1–M6 definition or mark those gates passed.

## Falsifiable alternatives and publication strategy

**Route A — evaluation-integrity and reproducibility manuscript** (recommended for review, *not yet supervisor-approved*): report reproducible software invariants and failure modes, source provenance, genuine negative observations, two numerical AC solvers on one development network, and explicit limitations of candidate budgets. Distinguish established practical instrumentation (not new theory) from any demonstrably original, generalizable methodological advance. Against the strongest prior art in [the existing research decision memo](RESEARCH_DECISION_2026-11-01.md), supervisor/independent reviewers must decide what, if anything, is substantively original.

**Route B — empirical GAdapt comparison study**: synthesize frozen S0/E/R/A/I/I2/ORPD results using consistent original-vs-transformed functions, seed/instance uncertainty and strong CMA/DE/GA baselines, retaining negative E2/E4/C and STOP findings (I59/I61/I63). **No fabricated new results**; specify all remaining statistical weaknesses.

**Route C — new optimization method**: **NO-GO** unless a prior-art audit establishes a precise new mathematical difference, falsifiable performance hypothesis and theorem or mechanism claim with strong baselines, and the complete protocol is independently approved **before new implementation**. Simple stagnation-triggered GAdapt→CMA, IPOP/BIPOP restart or ordinary ECDF/AUC is not presently established as novel.

## Proposed minimum acceptance and reject conditions

**Acceptable narrow evidence:** downloadable exact original artifacts; model/source hashes; independent synthetic and one non-held-out case regression; explicit network transformation metadata; exact solver-call phase accounting; negative tests; independent numerical PF **on the same model only**, all truth-conditions labeled.

**Reject any manuscript claim** if it implies independent field measurements without them, says the fixed case30 midpoint is feasible, treats 325 internal Newton residual evaluations as 325 physical PF attempts, claims tap optimization was tested in case30/j1 despite **zero eligible TAP controls**, or retroactively treats candidate-C novelty/held-out COCO as established.

**Recommended next review materials:** [independent dispatch result](I65_INDEPENDENT_DISPATCH_RESULT_2026-11-02.md), [case30 source-lineage result](I65_CASE30_SOURCE_PROVENANCE_RESULT_2026-11-02.md), [physical-budget decision draft](I65_PHYSICAL_COST_ACCOUNTING_DECISION_DRAFT_2026-11-02.md), [research decision/prior art](RESEARCH_DECISION_2026-11-01.md), [latest PHD progress](PHD_PROGRESS.md).

## Decision-signature section — deliberately blank

**Reviewer:** _________________________  
**Affiliation/role:** _________________________  
**Decision date:** _________________________  
**Chosen scope:** ☐ Route A ☐ Route B ☐ Route C ☐ Further independent review  
**Assessment of novelty:** ☐ Not established ☐ Limited methodology claim (describe) ☐ Independent novel contribution accepted (exact claim required)  
**Additional external data/model required:** ☐ Yes ☐ No ☐ Undecided  
**C1–C6 rationale and restrictions:** _________________________  
**Approved computational-budget specification (attach):** _________________________  
**Approved precommitted dataset/seed/statistical protocol (attach):** _________________________  
**Permission to begin novel optimizer work:** ☐ No ☐ Yes, limited scope (specify)  
**Permission to run held-out COCO:** ☐ No ☐ Yes, preregistration ID (specify)

**Until signed approval is actually received: `novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN`.**
