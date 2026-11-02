# I65 full computational-cost ledger and safety invariants — workstream C

**Date:** 2026-11-02. **DRAFT DESIGN FOR REVIEW, NOT AN IMPLEMENTED OR FROZEN BUDGET.** No new objective, OPF, PF or COCO evaluations were performed. Based on [original I65 physical cost decision draft](I65_PHYSICAL_COST_ACCOUNTING_DECISION_DRAFT_2026-11-02.md), original historical I56 and independently archived solver traces.

## A. Precise units; never add incomparable counters

| Counting unit | When charged | What is NOT included by definition |
|---|---|---|
| objective_attempt | Immediately before entering user objective/cost wrapper, including search probes and thrown calls | Cannot by itself reveal whether wrapper invoked zero, one or many AC solvers |
| runopf_entry | Immediately before every `pypower.api.runopf` attempt, labeled setup/search/interstage/terminal | Not internal OPF subsolves, Jacobian evaluations or grid observations |
| runpf_entry | Immediately before every `pypower.api.runpf` attempt, including failure and post-search checks | Not all internal numerical operations, independent numerical solver residuals or actual field trials |
| newton_residual_entry | Every invocation of new *NumPy* mismatch function, including 2 evaluations per central-difference Jacobian column and backtracking | Not interchangeable with a PF API call; asymmetric if PYPOWER internals are uninstrumented |
| terminal_witness_attempt | Explicit reserved reevaluation **after** the last search operation, with its source/model digest and feasibility outcome | Never a free B+1 check; interstage seeding witness is a separately named charge |
| wall_seconds and CPU_seconds | Direct observed process runtime incl. overhead / failures | Cannot be substituted for objective call count without a prespecified calibration |
| candidate_proposal | When a genotype is created, may hit cache or fail preflight | May not be an objective evaluation at all |

Each unit has an **explicit ledger counter**; reporting total `runopf + runpf + newton_residual` as a single number is semantically invalid without a signed, calibrated conversion rule. A PF is a *numerical physics simulation*, not a field measurement.

## B. Minimal append-only event schema (proposal only)

Each event must have: schema version; monotone event sequence; unique run ID; immutable checkout SHA; model/data SHA; phase in {setup, validation_probes, search, interstage, terminal, postrun}; parent objective event ID or null; event type; attempt index by type; resource reservation ordinal; result in {returned, converged, infeasible, nonfinite, exception, timeout, cancelled}; exception type or null; candidate numeric digest where relevant; elapsed monotonic duration; summary of the active I56 constraint components. Store the model/case SHA separately from source byte SHA and avoid reproducing licensed case arrays.

**No claim of completeness** merely from monkey-patching `pypower.api.runpf` and `runopf`: pre-imported function aliases, internal calls, native solver invocations, subprocesses and parallel workers may bypass those interception points. Fail-closed verdict: `API_ENTRIES_OBSERVED / INTERNAL_WORK_UNOBSERVED` until coverage is reviewed.

## C. Invariants and adversarial counterexamples

**I1 Sequential reservation.** With a sequential counter `n`, limit `B`, reserve before invocation if and only if `n < B`, then `n <= B` always and the `B+1`th invocation is impossible *through that boundary*. This is standard induction and **not an original theorem**. It requires all objective calls to pass through the same entrypoint.

**I2 Failure-inclusive.** Exception and timeout attempts consume their reservation. A wrapper that increments only on successful return falsely undercounts a failing call.

**I3 Witness-terminal.** At B=12,000, an objective-budget policy reserving one terminal witness may search at most 11,999 attempts; all interstage witnesses, initialization probes and algorithm-switch costs are also charged according to their own phase. If any search continues after a declared terminal witness, the earlier validation is not terminal.

**I4 Nested calls.** A wrapper can call `runpf` twice and `runopf` once in one objective attempt. Hence `objective_attempts=1` does **not** imply `runpf_entries=1` nor `total_solver_entries=1`. The resource vector is needed.

**I5 Parallel reservations.** Sequential proof cannot be directly extended to two concurrent workers reading `n=B-1` simultaneously. Atomic centralized reservations and provenance for each batch element are necessary before claiming B-hard safety.

**I6 Cost comparability.** If method A uses one objective attempt whose body invokes four internal PF solves while B uses one PF, a single wrapper-call budget is not equal numerical work. Conversely, identical PF-call quotas do not imply equal measured CPU time. The reviewer must explicitly approve a physical/numerical primary budget and report the others as covariates.

**I7 Negative feasibility.** `runpf returned` and `newton converged` do not imply accepted ORPD dispatch. The independently reproduced original fixed midpoint has reactive component `0.5991137833375704` versus PYPOWER `0.5991137833375748`, each above the original I56 limit `1e-6`: preserve `NUMERIC_CONVERGED / OPERATIONAL_INFEASIBLE`.

## D. Previously measured trace examples (NOT new observations)

| Already archived actual CI example | objective attempts | OPF entry attempts | PF entry attempts | Other numerical work |
|---|---:|---:|---:|---|
| [I65 solver-entry audit #41385833963](https://github.com/owlCoder/gadapt/actions/runs/41385833963): one I56 evaluator plus independent witness | 1 admitted search | 2, setup + rebuilt witness setup | 2, search + witness | PYPOWER internals unknown |
| [I56 operational constraint #41407293845](https://github.com/owlCoder/gadapt/actions/runs/41407293845) fixed midpoint | 1 original evaluator | 1 setup | 2, original evaluator + diagnostic | PYPOWER internals unknown |
| [Independent NumPy Newton #41413792862](https://github.com/owlCoder/gadapt/actions/runs/41413792862) | 0 optimizer search | 1 setup | 1 reference witness | **325 mathematical residual evaluations** of independently coded solver |
| [case30 source-lineage #41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142) | 0 optimizer search | 1 setup | 0 | no PF numerical solve |

**These rows are different experimental scripts**; they are not additive observations of one run and must not be combined into one aggregate resource number.

## E. Budget options awaiting signature, not operational choices

- **Option 1: objective-primary for official COCO**. Every true official objective call, setup probes and terminal witness must follow an approved attempt ledger. Exact COCO oracle evaluation semantics, f_opt access, 4,096 potential calibration calls and telemetry exclusions must be specified. The I65 proposed B=12,000 remains **DRAFT**.
- **Option 2: multi-resource ORPD**. Freeze separate upper bounds for OPF setup, PF during search, interstage PF, terminal witness PF, and total wall time, with a mandatory feasibility result. This is currently the least ambiguous audit representation; it is **not proof of equal optimizer opportunity**.
- **Option 3: calibrated equivalent-cost aggregate**. Only after independent calibration of OPF vs PF vs inner work, source/environment/hardware, uncertainty and failure costs. Do not choose a factor from the favorable results.
- **Option 4: report objective/PF/OPF/CPU/inner residuals together**, as a multi-dimensional Pareto profile without forcing a single ranking until the reviewer decides primary estimand.

## F. Reviewer acceptance matrix

**C2:** choose the unit(s) and whether setup/validation is inside or separately charged. **C3:** decide what internal numerical work means and whether asymmetric instrumentation is acceptable. **M2:** verify adapter boundary integration, initial all-min/all-max probes, DE and pycma partial ask/tell, B-1/B/B+1 and exception/batch behavior. **M3:** decide actual solver and feasibility witness boundaries. **C6/M5:** require a dated immutable statistical definition before any confirmatory run.

**GO:** desk review and synthetic-only semantics testing after approval. **NO-GO:** implementation of a new optimizer, unapproved PGLib/COCO runs, treating unrelated units as the same physical budget or calling this prospective ledger FROZEN. Reviewer/mentor fields remain `PENDING`.
