# Brief for Codex #41 — review of the I59 stages vs the FROZEN protocol (read-only)
Protocol research/ITERATION59_PROTOCOL.md (+ clarifications). Code research/iteration59_telecom.py (stages appended after
your 040-reviewed core), tests research/test_iteration59_telecom.py (9/9). Smoke-tested from a patched library copy (G0/G1
same initial population, exact budgets). Check: seeds (p=0/1/2, i order), selection rule (smallest B then smallest eps,
pooled G0/G1 attainment 20–80% on EVERY development network, from 30k prefixes), validation NO-GO, MILP references and
certification gating (development before development runs; confirmation after (B, eps) frozen, before confirmation
runs), triviality flag, T and analysis (equal network weights, paired bootstrap WITHIN networks, 20000, seed 59),
persistent-failure rule, post-budget handling in G0/G1, the independent checker (independence, SP rule via
all_shortest_paths, routability threshold), anything missing vs the protocol (manifests/hashes, version pinning record).
Do NOT run MILPs on development/confirmation instances. Verdict RUN / FIX FIRST. Max ~600 words. Read-only.
