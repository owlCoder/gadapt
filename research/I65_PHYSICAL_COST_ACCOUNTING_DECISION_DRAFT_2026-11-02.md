# I65 — physical and numerical evaluation cost decision matrix (unfrozen draft)

**Date:** 2026-11-02. **Status:** **DECISION NEEDED — NOT FROZEN / NOT approved by mentor.** This memo does not authorize or implement candidate C, an optimization benchmark, or held-out COCO experiments. Original [I65 draft protocol](ITERATION65_DRAFT_PROTOCOL_SR.md) remains DRAFT; this is a prospective clarification, not a silent protocol amendment.

## Why a single "evaluation" number is ambiguous

We now have direct, SHA-verified development-only measurements of **different counting objects**:

1. [I65 Python objective audit](ITERATION65_WITNESS_TERMINAL_GATE_2026-11-01.md): `AuditedBudget.attempts` reserves one charge *before* each objective invocation, including failures and a separate terminal witness; it does not automatically see lower-level PF subcalls inside arbitrary user cost functions.
2. [Actual PYPOWER API-entrypoint trace](I65_ORPD_SOLVER_ENTRY_AUDIT_RESULT_2026-11-02.md): on a fixed I58 case30 candidate, one historical `Evaluator.calls` objective attempt plus scenario construction and a separately rechecked solution generated **2 `runopf` and 2 `runpf` entrypoints** across setup/search/witness.
3. [Actual two-numerical-solver comparison](I65_INDEPENDENT_NEWTON_RESULT_2026-11-02.md): the independent NumPy Newton implementation needed **325 mathematical residual evaluations** to converge in **3** damped Newton updates, while the *PYPOWER wrapper* recorded **1 `runopf` setup and 1 `runpf` witness**. These are **not** 325 PF API calls or 325 distinct network dispatch experiments.
4. [I56 constraint comparison](I65_ORPD_OPERATIONAL_CONSTRAINT_SUCCESS_2026-11-02.md): a converged `case30` numerical PF solution was **reactively infeasible** with I56 reactive penalty `0.5991137833375748`. A solver call's return, numerical convergence, feasibility and final witness validation are all **distinct predicates**.

A single scalar `B=12,000` cannot be claimed to cover all those resources without an explicit scientific definition and consistent instrumentation. In particular, declaring a "physical attempt" while excluding scenario OPF and terminal verification is ambiguous and potentially unfair.

## Mandatory prospective attempt ledger

For each run, record *each* of the following separately. Count an entrypoint **before** calling it, including thrown exceptions and nonconverged outcomes. Preserve monotonic event IDs, phase, candidate digest, duration and source/model digest.

| Ledger | Definition | Counts failed calls? | Role |
|---|---|---|---|
| `objective_attempts` | Wrapper-level calls to original objective / library fitness API, including preflight probes | Yes | Comparable scalar on COCO only when underlying objective calls have equivalent meaning |
| `runopf_attempts` | Actual OPF API **entrypoints** (e.g. initialization, model reconstruction, verification) | Yes | Distinct heavy-solver overhead |
| `runpf_attempts` | Actual AC PF API **entrypoints**, including search and independent rechecks | Yes | Distinct PF work |
| `newton_residual_evaluations` | Mathematical residual evaluations *within the instrumented new NumPy solver*; counted including finite-difference perturbations and line search | Yes | Implementation-specific numerical complexity diagnostic, **not** an invariant physical-evaluation unit |
| `search_candidates` | Genotypes proposed/inspected, distinct from objective attempts, reuses, rejected preflight and cache hits | N/A | Algorithm overhead/acceptance |
| `validated_terminal_witnesses` | Number and result of charged, post-search terminal independent witness checks | Yes | Required terminal certification predicate |
| `wall_seconds`, `cpu_seconds`, `solver_iterations` | Timed cost and solver-specific iterations where directly observed | Including timeouts | Separate supplementary consumption; should not be equated with PF API entrypoint count |

**Setup, search, interstage and final witness phases must always be explicit**, and the terminal witness is **terminal**: a search after a validated final witness invalidates the terminal claim. If the protocol needs an interstage witness to seed CMA, it must have a separately named, preregistered and charged **interstage** check, not re-use the final witness.

## Choices requiring mentor approval before methods development or freeze

- **C1 — applicability:** Is the proposed dissertation contribution a rigorous *evaluation-integrity and reliability framework*, or must it include a new original optimization method? If the latter is required, the current unapproved candidate C remains **NO-GO**. No independent numerical PF implementation by itself proves algorithm novelty.
- **C2 — budget unit:** For official COCO f21/f24, a wrapper-level objective invocation including final verification may be a natural primary attempt unit, subject to exact official API accounting. For ORPD, choose **explicit separate ceilings** on OPF and PF entrypoint calls (recommended for auditability), *or* a formally preregistered equivalent-cost measure with validated cost calibration. Do not treat OPF and PF as equal work without justification. A vector budget is a valid audit representation, but not automatically a fair optimization ranking.
- **C3 — numerical work:** Agree whether internal solver residual evaluations and Newton steps are reported as **secondary complexity diagnostics** (recommended), not optimizer objective attempts. If included in the primary resource budget, independently instrument the actual PYPOWER implementation too; counting only the new solver's 325 residuals would be an asymmetric comparison.
- **C4 — witness independence:** Decide whether separate software solving the *same* AC mathematical model and case data meets the claim's needs. The NumPy Newton implementation establishes **numerical software independence on one development network**; it does *not* establish independent physical modeling, field measurements, or model validity across diverse ORPD cases.
- **C5 — infeasibility:** A numerically converged PF result can still violate reactive, voltage, thermal or generator limits. Require feasibility and convergence as separate reported outputs and preserve the archived negative midpoint (reactive penalty `0.5991137833375748`).
- **C6 — freeze criteria:** Scope, baselines, seeds, dataset list, any cross-solver tolerance, exact COCO function selection, interval/selection bias controls and familywise multiple comparisons must be decided and committed **before** confirmatory or held-out runs. The I65 draft's original 12,000 objective-attempt ceiling is not silently changed by these discussions.

## Minimal safe progression and GO / NO-GO

**GO:** preserve negative tests, independently review model assumptions, prepare independent input provenance, devise a low-cost trace schema and a signed mentor decision sheet, test that tooling on synthetic/pre-used development cases. The [latest independent Newton smoke](I65_INDEPENDENT_NEWTON_SMOKE_2026-11-02.json) provides a reproducible numerical-solver cross-check but not a frozen evaluation-cost convention.

**NO-GO:** claim I65 novelty, count all numerical work as identical physical attempts, run a new optimizer switch, start a multi-seed ORPD benchmark or release official held-out COCO results before C1–C6 are resolved. Current status stays **novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN**.

**Decision artifact still required:** supervisor-approved, dated acceptance/rejection of C1–C6 (and pre-existing M1–M6), explicit choice of numerical/physical budget resource, and independent review of data/model and power-flow validation scope.
