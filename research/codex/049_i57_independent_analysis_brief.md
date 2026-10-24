# Brief for Codex #49 — independent re-analysis of I57 results for the report (read-only)
I57 finished (protocol: research/ITERATION57_PROTOCOL.md, frozen; proposal ITERATION57_PROPOSAL_SR.md; driver
research/iteration57_external.py; I56 instrument research/iteration56_cht_study.py and ITERATION56_REPORT_SR.md).
Raw output: research/results/iteration56/i57.json.gz (keys test_ref_sha256, records); my analysis output:
research/results/iteration56/i57_analysis.json.gz. Do NOT import or run the driver's analyse code: write your OWN short
reader (python -B, read-only, no files written) from the protocol text and the record fields.
Tasks: (1) reproduce the 6 primary contrasts (mean T(method) - T(GAdapt), equal block weights, equal scenario weights
within block, paired whole-vector bootstrap inside network x R x scenario cells, 20000 reps, seed 57, 95% percentile)
and report any discrepancy with i57_analysis (point estimates must match exactly; CIs within MC noise if your RNG
differs — say which). (2) Per network x R block, for all 7 configurations: mean T, attainment rate, feasibility rate,
median best feasible loss; mark blocks where T = 1 for every config (non-informative, as in I56). (3) Check: 3000 real
PF calls per run, no exclusions, test_ref hash equals the archived I56 test_ref. (4) List the claims the frozen
protocol permits (descriptive only: no p-values, no superiority/equivalence) and 3-5 sentences of the most important
descriptive findings, plus any threat to validity you see (e.g. targets come from GAdapt reference runs). Output:
Markdown tables + findings, max ~1000 words. Keep CPU light (another study is running on 8 cores).
