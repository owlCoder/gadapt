# Brief for Codex #64 — adversarial code review of the I61 driver against the FROZEN protocol (read-only, result-blind)
Protocol (frozen 2dd0409): research/ITERATION61_PROTOCOL.md. Code: research/iteration61_replication.py, tests
research/test_iteration61_replication.py (7 pass). Reused frozen modules (must not be modified): research/iteration56_cht_study.py,
research/iteration56_orpd.py, research/iteration58_validation.py. Do NOT open any i58_test/check/analysis, i59_*, i60_* result
or log. Smoke check already done: 2 of the 54 gate tasks rerun bit-identically on the current library (v4).
Check every protocol clause against the code, section by section (§2 instances/OPF stops, §3 gate incl. run_plain and I56 tests,
§4 references/targets/STOP, §5 symmetric B rule, §6 FX-T (equal weights; ties), §7 rehearsal criteria, tilt (common lambda,
error, ESS), simulation (multinomial resampling equivalence to index resampling; series RNG; screening vs confirmation;
thresholds 825/36; Wilson), §8 estimator (95/90 from the same draws; labels; equal weights), §9 seeds and pairing assertion,
§10 stop-at-target (generated initial population, PF prefix through h, no PF after the target, 24 pairs, decisions
blocked/inconclusive/allowed, success definition), exclusions/sensitivity (denominators, per cell, restoration, flag),
provenance/freezing (manifest_frozen before test references; hashes), §10 independent checker (monkeypatched I58 checker:
correct scenario per j, process safety under Pool), §11 nothing. Also: anything that can STOP spuriously or silently
produce a wrong result; performance traps (e.g. check stage OPF per call). Blocking vs non-blocking, file:line, exact
fixes. Max ~1000 words.
