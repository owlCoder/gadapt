# Brief for Codex #61 — adversarial review of the I61 proposal before freezing (read-only, result-blind)
Proposal: research/ITERATION61_PROPOSAL_SR.md (my notes at the top + Codex 055 draft). Do NOT open any i58_test/check/analysis,
i59_*, i60_* result or log (I58 references/manifests are allowed only if needed for timing). Sources: I56 protocol,
clarifications, report, research/iteration56_cht_study.py, research/iteration58_validation.py (BusORPD, witnesses).
Act as a hostile reviewer: (1) blocking design errors (confounds, leakage between development and test, the B/R selection
rule depending on the contrast, FX-T calibration transferred from R=17 to other R, single global FX-T vector across 3
networks, reference arms); (2) is the power-simulation construction (exponential tilting of observed d to reach theta=0.02)
sound, and does it avoid the I56 imputation weakness? Is n in {20,40,60,80} with Wilson lower bound >= 0.8 realistic for
an effect of 0.02, or is the study likely to STOP — estimate from I56 rehearsal/test variance (research/results/iteration56
I56 files ARE allowed); (3) decision: is the equivalence zone [-0.02, 0.02] with a 90% interval coherent with the primary
rule, and what exactly will the thesis be allowed to say in each case; (4) instrument gate: can the I56 instrument run on
the current v4 library bit-identically (reason from code: CHTCostFinder/StudyFactory vs v4 changes in ga_executor,
ga_factory, ga_options, validator)? propose the exact gate (which archived I56 units to rerun, what must match);
(5) cost realism (PF timing on case30/39/24 vs case14/57/118); a cheaper design with the same inferential value?
(6) exact frozen-protocol text with all fixes, Serbian. Max ~1500 words.
