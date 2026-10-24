# Brief for Codex #62 — check I61 protocol draft v2 before freezing (read-only, result-blind)
Draft: research/ITERATION61_PROTOCOL.md (v2, integrates your Codex 061 review research/codex/061_i61_proposal_review_codex_answer.md
into the Codex 055 proposal research/ITERATION61_PROPOSAL_SR.md). Do NOT open i58_test/check/analysis, i59_*, i60_* results or
logs. Changes vs your text: n grid extended to {80,160,240,320,480} (your power estimate), B grid {3000,6000,12000} with
12000-call selection trajectories (cost cap), simulation uses 2000 bootstrap reps per simulated experiment, explicit budget.
Check: (1) every Codex 061 fix present and correct; (2) remaining blocking issues (esp. stop-at-first-target equivalence check,
the 5% exclusion/sensitivity rule, the power simulation with 20 vectors per network and ESS >= 10, null calibration); (3)
arithmetic of §11; (4) is anything in v2 ambiguous enough that two implementers would code it differently — list and give
exact wording. Verdict FREEZE / FIX FIRST, with exact replacement text. Max ~700 words.
