# Brief for Codex #27 — review the I57 proposal so it can be frozen BEFORE any I56 test result (read-only)

Proposal: research/ITERATION57_PROPOSAL_SR.md. Context: frozen I56 protocol research/ITERATION56_PROTOCOL.md and code
research/iteration56_cht_study.py (I57 reuses its instrument, targets, T and bootstrap). No I56 test result exists
yet (only development references). Tasks: (1) blocking design errors (fairness of baselines: CMAwM from `cmaes`
0.13.1 on grid indices, SciPy DE integrality with polish=False, random search; how each consumes exactly 3000 PF
calls; handling of the FR/SP scalars; seeds; whether rule 2 "best I56 arm chosen on I56 test data" is acceptable
with new seeds or must be replaced); (2) exact text for a frozen protocol (hypotheses or explicitly descriptive
comparison, contrasts, inference, budget); (3) anything a referee would demand that is missing (e.g. L-SHADE/jDE
availability in maintained packages). Max ~700 words. Read-only.
