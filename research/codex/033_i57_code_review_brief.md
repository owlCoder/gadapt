# Brief for Codex #33 — blocking code review of the I57 code vs its FROZEN protocol (read-only)

Protocol: research/ITERATION57_PROTOCOL.md (frozen). Code: research/iteration57_external.py, tests
research/test_iteration57_external.py (2/2). It reuses research/iteration56_cht_study.py (Evaluator, CHT, make_target,
references, instances, bootstrap). It will be started automatically right after the I56 analysis (scratchpad
i57_chain.sh) — I can still edit it now (I56 does not import it).
Check exactly: CMAwM settings (mean, sigma, bounds, steps, seed; x_for_eval evaluated, x_for_tell told; last generation
without partial tell), SciPy DE arguments (all listed in the protocol; `rng=` vs `seed=` in SciPy 1.18.1; integrality;
the budget exception before call 3001; does DE call the function in its init beyond popsize*d? any vectorized/`polish`
surprise), random search, GAdapt arm via i56._run (purpose-5 seed, AD-N), that every successful run makes exactly 3000
runpf calls, ok flag / rerun, the FR scalar applied explicitly, analysis (6 contrasts, equal block/scenario weights,
complete paired vectors, seed 57, no p-values), the test_ref hash archived BEFORE runs (now it is computed after the
runs — fix?), anything else. Verdict RUN / FIX FIRST with concrete fixes. Max ~600 words. Read-only (read-only Python ok).
