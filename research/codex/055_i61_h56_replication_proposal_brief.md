# Brief for Codex #55 — draft the I61 proposal: replication of the H56a interaction on held-out networks (read-only)
Codex 052 (research/codex/052_thesis_outcome_map_codex_answer.md) ranks as the single most needed study, regardless of
H58/H60/H59: an independent replication of the H56a interaction (adaptive vs tuned fixed mutation policy x FR vs static
penalty) on networks other than case14/57/118, with a development-chosen INFORMATIVE budget (I56: 6/9 blocks had T = 1 for
every arm, the estimate rested on case14 R=17). Sources: research/ITERATION56_PROTOCOL.md, ITERATION56_CLARIFICATIONS.md,
ITERATION56_REPORT_SR.md, research/iteration56_cht_study.py (FX-M/FX-T calibration, CHT cost finder, shared signal),
ITERATION58_PROTOCOL.md and research/iteration58_validation.py (fresh-network instrument: case30, case39, case24_ieee_rts,
one VG per generator bus, scenarios 301-303 = I58 TEST scenarios). Do NOT open any i58_/i59_/i60_ result or log.
Write, in Serbian (Latin), a complete proposal + exact frozen-protocol text for I61: (1) networks and DEVELOPMENT
scenarios disjoint from the I58 test scenarios (new scenario seeds/loads), and whether reusing the I58 networks is
legitimate once I58 results are known (H61 is a different contrast; argue both ways, recommend); (2) a pre-specified
development rule choosing budget B and resolution R per network so that blocks are informative (e.g. median T of the
reference arm in [0.3, 0.8] on development scenarios), frozen before any test run; (3) arms: AD-N/SP, AD-N/FR,
FX-T/SP, FX-T/FR with FX-T calibrated only on development scenarios exactly as in I56; (4) H61 = sign-consistent
replication of theta_a > 0 with the I56 estimator, plus an equivalence-style statement of what a non-replication means;
seeds, power simulation that does NOT impute degenerate blocks (the I56 power-simulation weakness), budget in PF calls and
CPU-hours (10 cores, ~2.5-3 ms per PF on case30-scale networks; check iteration58 code for timings), stop rules;
(5) the code changes needed (reuse I56/I58 modules; list functions), and the risk that the library epsilon/FR patch v4
changes the I56 instrument (I56 used its own CHT cost finder, not the library) — which one should I61 use and why.
Max ~1500 words.
