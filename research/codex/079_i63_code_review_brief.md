# Brief for Codex #79 — review of the I63 driver code BEFORE the gate (read-only; Serbian Latin; max ~1300 words)
Read research/ITERATION63_PROTOCOL.md (v2 frozen, 7c1f698), research/iteration63_replication.py, research/test_iteration63_replication.py,
and the I61 machinery it reuses (research/iteration61_replication.py). The driver imports iteration61_replication, overrides i61.TEST_SCENARIOS,
patches i61.build_manifest, and defines run63/check_item/normalizer_item at module level so spawned workers re-import it.
Deliver: (1) BLOCKING defects: any deviation from the frozen protocol; places where I61 code (OUT dir, seed_of, stage_gate fallback, preflight,
verify_chain/finish/publish, assert_paired, independent_check, tilt, wilson) behaves wrongly when reused with I63 scenarios/stages; spawn/pickle
hazards (does a spawned worker see the I63 scenarios? does the I61 `run` use the overridden scenario(j)?); provenance/freeze chain holes; the
decision function, tilt/ESS/strict-attainability logic, simulate_once / series / stage_power flow versus protocol section 6; calibration statistic; rehearsal
criteria (i)-(iv); analysis (equal weights, leave-one-network-out, expansion rule). (2) Exact replacement code for each blocking defect. (3) Anything
that could make a stage STOP spuriously for technical reasons (roster file keys, create-once collisions, missing hashes of CODE files, gate
requiring files). (4) Verdict: GATE NOW / FIX FIRST.
