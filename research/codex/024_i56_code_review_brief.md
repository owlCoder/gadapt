# Brief for Codex #24 — blocking code review of the I56 study code vs the FROZEN protocol (read-only)

Frozen protocol: research/ITERATION56_PROTOCOL.md (commit 3f09eb9). Code: research/iteration56_cht_study.py,
tests research/test_iteration56_cht_study.py (5/5 pass; AD-N/SP is bit-identical to plain GAdapt on the same
scalar), instrument research/iteration56_orpd.py. Nothing has been run yet except smoke tests (300–600 calls on the
development scenario). Known: case57 test scenarios (1.10, 203) and (1.15, 204) fail OPF -> excluded per §2.

Check, citing lines: (1) every §3–§7 rule is implemented exactly (V tolerance, failures, stopping, event order
(1)–(6), AP counters, EC eps0/tau, FR/SPT merits, AD-C replacing BOTH signals incl. D_0 and the parent-cost
normalizer, FX exact counts and pool, FX-M median-of-medians, FX-T grid/ties, references, target, T, seeds,
contrasts, bootstrap strata/weights/p, Holm set of 5, power simulation, early-termination rerun and
complete-unit analysis); (2) bugs: GA.execute deep-copy (we return self in __deepcopy__ for Evaluator/CHT/factory —
anything else deep-copied that should be shared?), singleton CommonSignalParentDiversityUpdater, Instrument
monkeypatching (sigma hook patches a class in the worker process), post-budget handling, the 'initial' check,
the FX-T selection 'argmin over mean T', unit_contrasts keyed by seed (seeds are unique per unit?);
(3) choices made in code that the protocol does not state (e.g. development seeds 1–3 for FX-M/FX-T and 11–15 for
the rehearsal; case57 blocks with 2 scenarios) — acceptable or must be logged as deviations?
Verdict RUN / FIX FIRST with a concrete list. Max ~900 words. Read-only (read-only Python allowed).
