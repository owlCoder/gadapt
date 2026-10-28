# Brief for Codex #82 — prior-art gate + formalisation for direction 2 of Codex 081 (read-only, web search; Serbian Latin; max ~1200 words)
Candidate: inference about the comparison of two stochastic optimisers that is valid FOR EVERY reference optimum f* in a known interval [L,U]
(target = f*+eps, fixed-target hitting time with administrative censoring at budget B), with simultaneous control over the whole interval.
Motivation from our own record: in I61 the reference L* (continuous OPF / best of long runs) was not a certified optimum and the target was unreachable on
some scenarios; read research/ITERATION61_REPORT_SR.md, research/codex/077_i63_design_codex_answer.md.
Do: (1) literature search 2018-2026 for: target-choice sensitivity in fixed-target/ECDF analysis (Hansen et al. 10.1109/TEVC.2022.3210897; Lopez-Ibanez et al.
10.1109/TEVC.2024.3462758), simultaneous confidence bands / uniform inference over a threshold index in survival analysis (Kaplan-Meier bands, Hall-Wellner,
Nair; log-rank under varying thresholds), partial identification / sensitivity analysis (Manski bounds, Rosenbaum) applied to optimiser comparison, 'reference
solution uncertainty' / 'unknown optimum' in benchmarking. State for each: what the result gives and what it does NOT. (2) Formalise the exact estimand and a
provable property (what is the object over r in [L,U]; is Delta(r) a process in a threshold index whose simultaneous band follows from Hall-Wellner/
functional-CLT or from a union-over-breakpoints argument, and why this is or is not a one-line corollary of known results). (3) Verdict: NOVEL / NARROWLY NOVEL
(state the narrow part) / NOT ESTABLISHED; honest assessment whether this could be more than a tooling remark; GO/NO-GO for a 2-week gate. Verify DOIs; never invent.
