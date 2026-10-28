# Brief for Codex #78 — review of the I63 DRAFT protocol before freezing (read-only; Serbian Latin; max ~1400 words)
Read research/ITERATION63_PROTOCOL.md (draft), research/codex/077_i63_design_codex_answer.md (your design), research/ITERATION61_PROTOCOL.md,
research/iteration61_replication.py, iteration56_cht_study.py, iteration58_validation.py.
Deliver: (1) BLOCKING defects in the draft (ambiguity, a rule that can pass trivially or never pass, estimator/bootstrap inconsistencies, power-simulation
design, ties/infeasibility handling, seeds/hash/provenance holes, anything that lets a post-hoc choice enter) with exact replacement text;
(2) whether the W rule with the 0.001 tie threshold and the three transfer-assumption power variants is coherent and implementable (state the exact
simulation algorithm: how a tilted pool is sampled to n whole four-vectors per confirmation cell, and how the 90%/95% CIs are computed);
(3) the exact FX-T calibration statistic (does 'mean win score against the other 26 configs' use the same seed/scenario pairing; formula);
(4) whether best-feasible-among-first-B-evaluations from the evaluator (not the GA result) is available in the I56/I61 instrument without modifying
frozen modules (cite lines) and what an I63 driver must add; (5) verdict FREEZE / FREEZE AFTER FIXES / REDESIGN.
