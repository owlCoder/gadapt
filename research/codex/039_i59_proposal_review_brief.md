# Brief for Codex #39 — review the I59 proposal for freezing before any development measurement (read-only)
Proposal: research/ITERATION59_PROPOSAL_SR.md (from your 037). Data: research/data/topohub_v1.5.1_sndlib/ (check the
JSON schema: nodes, edges with distances, demand entries; confirm the instance counts you quoted). (1) Blocking design
errors (module size q from the SP routing — leakage? f normalisation; elastic LP correctness and size; residual check;
MILP formulation size for the confirmation instances and whether HiGHS can certify within e.g. 1 h; budget/ε selection
rule; seeds; independence of development and confirmation; what if x^SP is already within ε of C* — trivial targets?);
(2) exact frozen protocol text in Serbian-compatible structure (mirror ITERATION58_PROTOCOL.md); (3) estimated CPU cost.
Max ~800 words. Read-only (read-only Python allowed to inspect JSON and time a few LPs).
