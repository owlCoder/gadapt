# GAdapt: supervisor decision package and I65 method-review gate

**Prepared:** 2026-11-01. **Baseline:** `owlCoder/gadapt`, `main` at `36ed79935743468d896d89be68e7daba8702bf94`.  
**Classification:** decision support / STATIC review; **not** supervisor approval, a new experimental result, a frozen protocol, or a certificate of scientific originality.  
**Research state:** `I65 = DRAFT / NO-FREEZE / COCO f21/f24 NOT_RUN`; algorithm-switching **novelty not established**.

## Decision requested of the supervisor

Can a dissertation consist of **reproducible, context-dependent empirical characterization of GAdapt** and an **independently validated evaluation-integrity/witness methodology**, with clearly limited claims? Or is a new optimization algorithm / theorem obligatory? If the latter, the proposed stagnation-triggered GAdapt→CMA policy is **NO-GO** under the present evidence; it cannot be declared novel by writing its code.

Research question: at the same number of *actual objective/physical power-flow calls*, what are GAdapt-M's strengths and failure modes versus SciPy DE, CMA-ES/IPOP/BIPOP and fixed GAdapt→CMA, including target attainment, tail risk and feasible independent witnesses? No arbitrary-function success guarantee or industrial approval follows.

## 1. Evidence to preserve, including negative results

| Existing study | What is supported within its test design | What may **not** be claimed |
|---|---|---|
| [I64-S0](ITERATION64_S0_REPORT_SR.md) | Mentor-setting early ECDF efficiency versus tested DE/PyGAD settings. | GAdapt is not universally more accurate: **DE lower final cell median in 14/21** cells, and generation counts are incomparable. |
| [I64-E](ITERATION64_E_REPORT_SR.md) | Equal 12,000 physical calls, transformed functions, CMA-family controls. | Frozen H64a was **opposite** for CMA, IPOP and BIPOP; no universal aggregate dominance. |
| [I64-R](ITERATION64_R_REPORT_SR.md) | At matched shift, orthogonal Q reduced GAdapt ECDF A by ~**0.081** vs ~**0.010** for IPOP. | Limited tested design; exact causal mutation mechanism unknown. |
| [I64-E3](ITERATION64_E3_REPORT_SR.md) and [I64-A](ITERATION64_A_REPORT_SR.md) | Fixed 30% GAdapt→70% CMA improves rotated outcomes over standalone M; GAdapt's first phase matters under the fixed initialization. | E3's full criterion failed; hybrid design itself is known and not a new algorithm. |
| [I64-I](ITERATION64_I_REPORT_SR.md), [I64-I2](ITERATION64_I2_REPORT_SR.md) | Discrete ORPD power-flow feasibility and quality are measurable. | **No confirmed ORPD superiority** of hybrid over M; hybrid tail worse than IPOP; I2 has a late-provenance-hash caveat. |
| [Other negative/STOP work](EVIDENCE_SYNTHESIS.md) and [I63](legacy/flat/ITERATION63_REPORT_SR.md) | E2/C/N negative/null findings and calibrated I63 STOP are part of the evidence. | No confirmed new rotation mechanism, label-order defect or I63 confirmatory replication. |

Use [the consolidated synthesis](EVIDENCE_SYNTHESIS.md) for the full result hierarchy and original source links. Synthetic original/shifted/rotated functions, official COCO instances and constrained ORPD are **different evidence domains**.

## 2. Closest existing methods, novelty and assumptions

IPOP/BIPOP population restarts, stagnation rules, memetic hybrids and portfolio switching predate I65; see the [prior-art audit](ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md) for closest works and DOI provenance. The proposed C differs as a particular **20-completed-generation trigger** and GAdapt first stage, not by a demonstrated new mathematical principle. **Novelty not established.** An external novelty reviewer must identify a precise, falsifiable distinction before any claim of a new optimizer.

Target-based ECDFs and physical-call benchmarking are established COCO practice. An alternative EAF/anytime analysis has been published ([DOI 10.1109/TEVC.2024.3462758](https://doi.org/10.1109/TEVC.2024.3462758)); algorithm footprints ([10.1016/j.swevo.2025.101895](https://doi.org/10.1016/j.swevo.2025.101895)) and standardized auto-tuning comparisons ([10.1016/j.future.2024.05.021](https://doi.org/10.1016/j.future.2024.05.021)) are likewise prior art. Publisher and DOI landing pages were examined; **Crossref API verification was not completed** and this is not an exhaustive independent systematic review.

**Simple bound, not a new optimization theorem:** in a sequential, single-solver-call evaluator, if `n < B` is checked and `n` is incremented **before** any physical attempt, induction ensures `0 ≤ n ≤ B`. This assumes *every* physical attempt passes through the boundary. Nested power-flow calls, uncaptured callbacks, batching and multiprocessing are outside the proof.

The raw-cost significance criterion `Δ > eps_abs + eps_rel·max(1, |best_previous|)` is not invariant to adding a constant to an objective if `eps_rel > 0`. Setting `eps_rel=0` avoids that offset sensitivity, but absolute epsilon still varies with cost units. This is a methodological limitation, not a doctoral novelty.

## 3. Independent gate ledger (who must sign off)

| Reviewer gate | Specific acceptance evidence required | Current finding |
|---|---|---|
| **M1 — full-clone compatibility** | Check migrated source hashes, opt-in restore all 341 root aliases, and execute *inexpensive* historical I41/I63/I64 tests in a pinned, complete local clone. | **NOT_TESTED**. Prior isolated 9/9 migration checks do not establish full compatibility. |
| **M2 — adapter instrumentation** | GAdapt **completed-generation** boundary; SciPy DE init/callback/termination; pycma `ask/tell`, partial generations, restart; actual B−1/B/B+1, failed/nonfinite attempts and two-process replay; validate final witness *within* B. | Isolated research-only budget/stagnation and SciPy smoke tests, **no GAdapt/CMA integration approval**. |
| **M3 — independent infrastructure oracle** | Define actual power-flow solver calls vs Python wrapper calls, numerical faults, feasibility, constraints and truly independent witness/physics validation. | **NOT_ESTABLISHED** for a new I65 infrastructure task. |
| **M4 — COCO oracle** | Use official single-objective `bbob` f21 Gallagher 101 Peaks and f24 Lunacek, not `bbob-biobj`; independently test domain, instances, known minima and access to exact `f_opt`. | Function identities supported by [official BBOB definitions](https://numbbo.github.io/temp-doc-bbob/bbob/def.html); **runtime NOT_TESTED**. |
| **M5 — statistics/freeze reviewer** | Freeze six simultaneous C vs E(IPOP)/D(E3) contrasts including reach-rate noninferiority, failure policy and instance/seed uncertainty; enforce no held-out peeking. | Only four contrasts fully formulated in DRAFT; three held-out instances limit rare-failure and instance-generalization claims. |
| **M6 — supervisor/novelty reviewer** | Decide dissertation originality threshold and whether restricted empirical and integrity-tool contributions qualify. | **PENDING**, never inferred from a positive software test. |

**Technical ambiguities blocking a freeze:** The [I65 DRAFT](ITERATION65_DRAFT_PROTOCOL_SR.md) says `s_i` is a median from 4,096 uniform samples. Specify *exactly* whether this is a median of excess costs `f(x)-f_opt`, how zero/nonfinite values are handled, and how setup costs/hashes are recorded. Taking the median of uncentered objective values would make the scale depend on an arbitrary COCO objective offset. Verify this *before* seeing held-out outcomes.

The `AuditedBudget.verify()` interface in [the research-only code](i65/audited_budget.py) checks that the witness callable is not the same object as the search callable; **callable identity is not proof that their underlying physical models are independent**. Require separate model/code provenance and adversarial mismatch tests. At `B=3000`, a snapshot is **provisional** if its independent witness is only done later inside the full `B=12000` run. Keep wall-clock and hardware time separately from physical-call counts, especially for expensive simulators.

## 4. Reproducibility runbook — not executed here

Only on a full clone in a locked environment, inspect commands for test-only collection before execution:

```sh
python -m unittest discover -s research/compat -p 'test_migration_compat.py' -v
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
python -m pytest -q research/test_iteration41_*.py
python -m pytest -q research/test_iteration63_replication.py
python -m pytest -q research/i64/test_e_common.py research/i64/test_e_algos.py
python -m pytest -q research/i65/test_*.py
```

Record checkout SHA, restored alias count, exact dependency/pip freeze versions, test selection and outcomes, stderr/stdout digests, file hashes and blockers. **Do not mark any of these commands PASS until executed in the real clone.** Direct execution from `legacy/flat` or curated `studies/` is not a valid replay when `__file__` determines provenance. The current environment has no full checked-out clone and its network could not resolve github.com; these commands therefore remain **NOT_TESTED** here.

## 5. Resource envelope, falsification, practical decisions

The unfrozen design has nine policies, `B=12000`, secondary same-trace `B=3000`; 18 COCO cells × 9 policies × 30 seeds = 4,860 primary runs, plus 12 control cells × 9 × 15 = 1,620 runs: **77,760,000 maximum per-run physical calls**. Optional extra-Q diagnostics raise this to **88,560,000**, excluding separately accounted setup/development. The proposed **120 CPU-hour cap is not a validated estimate**. None of these large confirmation runs is authorized by this document.

For a future falsifiable policy C comparison, the strong controls are GAdapt-M, SciPy DE, CMA, IPOP, BIPOP and **fixed I64-E3 GAdapt→CMA**. Predeclare failure cases: no CVaR benefit, excess early-ECDF loss, degraded reach rate, missing feasible validated witnesses, over-budget attempts, or an interaction that disappears on held-out instances. Contradictory and undecided outcomes must remain, with no rerun to obtain significance.

**Preferred route A:** write a bounded empirical GAdapt study from existing frozen S0/E/R/A/E3/I/I2 evidence with negative and STOP cases and qualified inference. **Preferred route B:** separately review evaluation-integrity instrumentation against existing prior art and test specificity/transfer (I50/I52); originality is **not automatic**. **Route C:** NO-GO for claiming a new algorithm; engineering pilot only after independent scope approval and instrument gates.

For operational infrastructure, the sequence is input validation → optimization → independent feasibility/physics/witness check → preset fallback → `NOT_SOLVED` if unresolved. Never accept an infeasible point because the library reports success.

## 6. Questions for an explicit human decision

1. Is route A, route B, their combination, or neither doctorate-sufficient? What **exact original claim** and target venue are required?
2. Which human experts will close M1–M5, including power-flow oracle independence and statistical sample limitations?
3. Is **development-only** adapter testing allowed after those gates? Confirmation and expensive CI remain excluded.
4. If a new optimizer is mandatory, may current I65 C be formally recorded **NO-GO** and replaced only after a separate precise prior-art/mathematical proposal?

**Human disposition:** `PENDING / APPROVE_SCOPED_EMPIRICAL / REQUEST_CHANGES / NO_GO`. No decision, approval or signature is implied.

## Sources and honesty boundary

Repository: [rules](../AGENTS.md), [latest handoff](PHD_PROGRESS.md), [research decision](RESEARCH_DECISION_2026-11-01.md), [I65 instrumentation gate](ITERATION65_INSTRUMENTATION_GATE_REPORT_SR.md), [migration gate](ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md), [evidence synthesis](EVIDENCE_SYNTHESIS.md) and original linked reports. API reference: [SciPy differential evolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html). Static review does **not** constitute full historical regression, human-independent review, proof of a new algorithm or an actual COCO run.
