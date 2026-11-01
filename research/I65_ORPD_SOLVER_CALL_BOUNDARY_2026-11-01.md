# I65 — ORPD Python-objective count versus physical solver-entrypoint count

**Date:** 2026-11-01. **Method:** read-only source review of original SHA-preserved I56/I58/I61 code (no benchmark, no new model).  
**Gate status:** **STATIC BOUNDARY IDENTIFIED; independent runtime nested-solver accounting NOT_TESTED**.  
**Source trees:** the original modules remain relocated byte-identically under `research/legacy/flat/`. Their logic is reachable from the original `research/<name>.py` aliases after the successfully validated 341-path restore.

## Verified call graph in historical source

- [`iteration56_orpd.py`](legacy/flat/iteration56_orpd.py) `ORPD.__init__` (lines 29–51) constructs the scenario and calls `pypower.api.runopf(...)` **once at the visible Python entrypoint** before storing the OPF baseline. This is **setup work**, outside any later `Evaluator.calls` count. Whether the OPF solver makes additional nested numerical iterations/subsolves is not measured by these source lines.
- [`iteration56_orpd.py`](legacy/flat/iteration56_orpd.py) `ORPD.evaluate` (lines 79–96) snaps a candidate, prepares a case and invokes `runpf(case, self.options)` inside a `try`. This is one visible `runpf` entrypoint for executions that **reach the call**. Exceptions may mark the result nonconverged; pre-call exceptions mean an outer objective attempt does not necessarily correspond to a completed PF solve.
- [`iteration56_cht_study.py`](legacy/flat/iteration56_cht_study.py) `Evaluator._call` (lines 132–156) increments `self.calls` **before** `self.problem.evaluate`. At budget exhaustion (lines 133–135), it returns a sentinel without entering the numerical model. Thus `Evaluator.calls` counts admitted Python objective attempts, not all setup/witness OPF calls and not necessarily lower-level iterative solver work.
- [`iteration58_validation.py`](legacy/flat/iteration58_validation.py) `BusORPD.evaluate` (lines 71–74) delegates to `ORPD.evaluate`, so its nominal search path reaches that same PF entrypoint once. However, [`independent_check`](legacy/flat/iteration58_validation.py) (lines 369–436) constructs a **fresh** case through `_independent_case`, which visibly calls `api.runopf` in its setup, then invokes `api.runpf` to recheck the candidate. Those calls are **not in the search evaluator's `calls` field**.
- [`iteration61_replication.py`](legacy/flat/iteration61_replication.py) `StopEvaluator._call` (lines 225–242) wraps `Evaluator._call` but does not introduce an independent physical-solver attempt ledger.

## Consequences

An illustrative original I58 workflow with *one scenario setup*, `n` search candidate calls all reaching `ORPD.evaluate`, and *one* separate `independent_check` has at least the following **visible API entrypoints**:

\[
N_{\mathrm{runopf}} = 1_{\mathrm{scenario\ setup}} + 1_{\mathrm{independent\ check\ setup}}, \qquad
N_{\mathrm{runpf}} = n_{\mathrm{search\ calls\ reaching\ solver}} + 1_{\mathrm{independent\ check}}.
\]

This is a **call-graph illustration**, **not a measured count for archived research results**. Actual experiments can construct more scenarios, skip evaluators, repeat witness checks, encounter pre-call errors or invoke nested solver steps. The equality between search Python-attempt count and actual completed PF solve count must not be assumed.

## Required narrow dynamic gate (before any I65 scientific freeze)

1. Instrument **both** `pypower.api.runopf` and `pypower.api.runpf` at their actual invoked import sites, counting **attempts before calling**, including exceptions, with a phase tag `setup/search/witness`. Be explicit that these are *solver API entrypoints*, **not internal Newton iterations or hidden PF solves inside OPF**.
2. Independently record the I56/I58 `Evaluator.calls` trace and `AuditedBudget.records` when applicable; reconcile each attempted optimization candidate with its numerical solver entrypoint, explicitly separating any pre-solve error.
3. Confirm that witness cost includes **both** a fresh OPF setup and PF check where `independent_check` is used, and distinguish a distinct Python function/model reconstruction from a truly independently implemented AC solver. A shared PYPOWER implementation is **not** independent-model validation.
4. Test one safe, non-held-out, low-dimensional PYPOWER case and a controlled failing-solver path with a fixed small maximum attempted-call budget. Archive exact Python/source versions, all source hashes, counted call entrypoints and raw finite/failure outcomes. Do not re-run historical optimization experiments or treat this as a novel algorithm.
5. Review I65's proposed final witness versus inter-stage checks and reconcile every solver attempt under a prespecified accounting policy. No I65 algorithm-C switch/COCO confirmation until protocol novelty, model-independent oracle and statistical freeze gates close.

**Verdict:** the full Git and software compatibility gate is now **PASS** (run `41358768925`), but `B` as counted in `Evaluator.calls` or the I65 wrapper has **not** been independently demonstrated to include setup and witness AC solver calls. The next claim about **physical** budgets must supply a separately observed solver-level trace, not infer it from the 341-path migration or the 88-pass unit test count.
