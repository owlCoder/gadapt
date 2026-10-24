# Brief for Codex #14 — review of the implemented post hoc sensitivity and figure (read-only)

Implemented from your plan 013. Frozen plan: research/ITERATION52_SENSITIVITY_PLAN.md (commit ac5b781, before
computing). Code: research/iteration52_sensitivity.py, tests research/test_iteration52_sensitivity.py,
output research/results/iteration52/sensitivity.json. Paper: research/paper_integrity_audit/manuscript.md §6.4 (new
"Post hoc sensitivity" paragraph), §8 "Post hoc analyses", §10, Figure 1 caption. Figure script:
research/paper_integrity_audit/make_figure.py (new applicability mask; PNG fig_integrity_matrix.png).

1. Does the code implement the frozen plan exactly (definitions, joins, valid cells, D3x_diff, bounds)? Any
   deviation, bug, or silent choice not in the plan? Recompute key numbers independently (read-only Python,
   .venv/bin/python -I): control 19/21; matched-exposure distribution (17: 4e-5, 18: 0.40, 19: 0.50, 20: 0.10;
   E = 18.7); complete-only 17/18 and 7/7; bounds 17–20; archive B identical.
2. Is the manuscript wording accurate and not overstated given the plan's text rule ("survives, but without
   margin")? Anything a referee would still flag?
3. Figure: is the applicability mask correct for every library (C4 from documented_max; R1 x; R2/R3 f; r_applicable
   for Study 2; Nevergrad "?")? Any cell wrongly marked n/a or wrongly 0? Is Study 1 D3x/Study 2 D3x provenance right?
4. Status of 012's remaining PARTIAL points after this change.
Max ~600 words. Read-only.
