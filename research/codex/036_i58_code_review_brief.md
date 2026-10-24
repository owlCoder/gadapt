# Brief for Codex #36 — blocking code review of the I58 code vs its FROZEN protocol (read-only)
Protocol: research/ITERATION58_PROTOCOL.md. Code: research/iteration58_validation.py, tests research/test_iteration58_validation.py
(3/3). It runs AFTER I56/I57 and after the library patch research/patches/constraint_api.patch (v4) is applied; it was
smoke-tested from a patched copy (G0/G1 same initial population, exact budgets). Check: BusORPD (one VG per generator bus;
the evaluate() trick that temporarily swaps lo/hi/step to reuse the frozen I56 instrument — correct? safer alternative
without editing iteration56_orpd.py, which the running I56 imports), G0 vs G1 (same build, settings, scalar f+1000V vs pair),
seeds p=6/7, single 10000-call trajectory with T3000 and T10000, references from all five methods, the analysis (equal
weights per network and remaining scenario via the remapped cells passed to i56.bootstrap — correct?), empty-cell /
sensitivity rules, the G0/G1 initial-population assertion, the independent checker (truly independent of the instrument?
same formulas re-derived from pypower indices?), manifest/hash timing. Verdict RUN / FIX FIRST. Max ~600 words. Read-only.
