# Brief for Codex #67 — adversarial review of the I58 check amendment D1 BEFORE it is run (read-only)
Situation: the post-I57 chain ran I58 refs -> test -> check; the ORIGINAL check (research/iteration58_validation.py stage_check)
FAILED: failures by kind {'returned_G0': 33, 'returned_G1': 34}, ALL on case300 (descriptive network), all with
check valid=True, converged=False; the instrument's returned values are the failure convention (G0 min_cost = 2 f_ref + 1000*10;
G1 best_objective = 2 f_ref, best_violation 10, feasible False). All reference, first-target and best-feasible witnesses
passed. The I58 analysis has NOT been run and no H58 outcome (T values, analysis) has been looked at.
Proposed amendment: research/iteration58_check_amendment.py (new file; iteration58_validation.py unchanged because its hash
is in the I58 provenance and analyse() compares it). Also the same gap fixed in research/iteration60_epsilon.py stage_check
before any I60 run (`git diff HEAD -- research/iteration60_epsilon.py`).
You MAY read research/results/iteration56/i58_check.json.gz (the original failing check) and the 'returned' fields of
i58_test.json.gz / i58_refs.json.gz records, but NOT T3000/T10000/first_target values and do not compute any H58 contrast.
Check: (1) is the diagnosis right (agreement, not disagreement) and is the amendment a legitimate, non-outcome-driven
correction (it cannot change H58: case300 is not primary — verify in the protocol/analyse code)? (2) is the amended rule
correct and not weaker than intended for converged solutions; is f_ref recomputed independently and does it match the
instrument's opf_losses? (3) the row-by-row guard (only failed returned rows may flip to pass); (4) the I60 fix; (5) exact
deviation text for the I58 report (Serbian). Verdict RUN / FIX FIRST. Max ~600 words.
