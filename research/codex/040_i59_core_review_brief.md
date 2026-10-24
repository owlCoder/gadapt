# Brief for Codex #40 — review of the I59 core code vs the FROZEN protocol (read-only)
Protocol: research/ITERATION59_PROTOCOL.md; clarifications research/ITERATION59_CLARIFICATIONS.md. Code:
research/iteration59_telecom.py, tests research/test_iteration59_telecom.py (4/4). Stages (dev selection, validation,
references, confirmation, analysis, independent checker, GAdapt G0/G1 runs) are NOT written yet. Check the core:
canonicalisation, demand handling (each entry once, s != t, v > 0), SP tie-break (BFS keeping the lexicographically
smallest predecessor chain — is that equal to "lexicographically smallest node sequence among min-hop paths"?), q and x_sp,
LP formulation (dropped last-node conservation row, signs of u, shared capacity both arcs, objective scaling), linprog
options (does `simplex_dual_edge_weight_strategy="devex"` exist for highs-ds in SciPy 1.18.1? any ignored option
warnings?), residual and full-demand checks, MILP formulation and the meaning of status 0 / gap fields in SciPy 1.18.1.
Do NOT run a MILP on development or confirmation instances. Verdict OK / FIX with concrete fixes. Max ~500 words. Read-only.
