# Brief for Codex #74 — I61 report skeleton written BEFORE its results (read-only, result-blind)
I61 is running (stage order gate -> dev_ref -> select_b -> fxt -> stopcheck -> rehearsal -> power -> test_ref -> test -> check
-> analyse). Do NOT open anything in research/results/iteration61/ except roster.json.gz and gate*.json.gz, and no i61 log.
Sources: research/ITERATION61_PROTOCOL.md (frozen), research/iteration61_replication.py (exact output keys of every stage:
select_b chosen/medians, fxt chosen, stopcheck decision, rehearsal criteria, power alternative/null/screening/confirmation/
null_calibration/chosen_n/passed, analysis H61 ci95 ci90 supported opposite equivalent, sensitivity, per_cell, exclusion_rate),
the I58 report research/ITERATION58_REPORT_SR.md as style template. Produce the skeleton: sections; decision rules quoted verbatim;
placeholder tables keyed to JSON paths; pre-written interpretation for EVERY branch (each STOP point: §2 roster, §5 no budget,
§6 incomplete FX-T, §7 rehearsal fail / tilt unattainable / ESS / n>480 / confirmation or null calibration fail, check failure;
and the analysis labels: supported, opposite, equivalent, supported+equivalent, inconclusive); and for each branch the
consequence for the thesis' central claim (H56a), given H58/H60/H59 = N/N/unavailable. Max ~1300 words.
