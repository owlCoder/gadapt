# Mentor summary (2026-10-24, late)

Status following the confirmatory I58, I60, and I59 studies (all frozen before observing their own results, with independent verification of solutions; reports appear under `research/ITERATION5*_REPORT_SR.md` and `ITERATION60_REPORT_SR.md`):

- **Practical acceleration from integrated constraint-handling techniques was not confirmed: H58/H60/H59 = N/N/unavailable.** For FR (I58), θ = −0.014 [−0.035, +0.006]; for ε (I60), θ = −0.011 [−0.035, +0.012]. Both confidence intervals include zero. I59 (telecom) was stopped by a prespecified development NO-GO rule; this is **not** a negative confirmatory outcome.
- **H56a (adaptation × constraint-handling technique interaction) is a small, local finding**, θ = +0.0205 [0.0020, 0.0396], mostly on case14. The conceptual replication I61 was frozen before examining these results and is in progress (approximately one day of computation; a legitimate outcome is a STOP due to inadequate power).
- **I57 (descriptive):** CMA-ES with margins was faster than GAdapt on case14 at R = 17/33; GAdapt was the only method that always found a feasible solution on case57. GAdapt's competitiveness was not established, and the thesis does not claim it.
- **The evaluation-integrity audit is the strongest candidate for a standalone contribution backbone:** tool plus studies I49–I52/I55 across 21 libraries, with transfer to AC dispatch. It requires a dedicated core thesis chapter and a rigorous assessment of the originality of the integration and detector validity.
- **An explicit assessment of whether the dissertation contains a sufficient original contribution is necessary.** The number of experiments, procedural discipline (preregistration and independent checks), and functioning software (opt-in `constraint_handling` in GAdapt) are not themselves sufficient.

Library status: `constraint_handling` (FR, ε, penalty, adaptive penalty) remains opt-in and the default behavior bit-identical (call sequence hash). There is no speed-based recommendation. Thesis claim audit: Codex 075 (integrated).
