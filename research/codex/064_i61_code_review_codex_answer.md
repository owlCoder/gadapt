**FIX FIRST.** The statistical core matches the frozen protocol, but execution and provenance have blocking gaps. Review remained read-only and result-blind; no prohibited results or logs were opened. The protocol matches commit `2dd0409`, and the seven I61 tests pass.

**Blocking findings**

1. **§2 — Test eligibility is determined too late.** [iteration61_replication.py:326](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:326) checks only development scenarios before development references. Test OPFs first run at [line 535](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:535), after budget selection, FX-T calibration, and rehearsal. Thus development proceeds even when a network has no eligible test scenario.  
   **Fix:** preflight all 15 scenarios before development, enforce both eligibility requirements, persist the eligible/excluded sets, and reuse that frozen roster throughout.

2. **§3 — Required fallback gate and gate-result hashes are absent.** [iteration61_replication.py:293](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:293) correctly schedules 54 archived tasks, fresh processes, SP `run_plain`, and I56 regression tests. On failure, however, it only exits; it never gates `17e9ce7` in a separate tree. Neither the gate results nor their archived input are hash-bound into downstream provenance.  
   **Fix:** implement the isolated fallback path, retain both outcomes, and bind hashes of the archive, gate results, regression-test source/output, instrument, library, and environment into the selected gate manifest.

3. **§10 — The freeze can be overwritten, and frozen provenance is not enforced.** [iteration61_replication.py:580](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:580) unconditionally overwrites `manifest_frozen.json` whenever `test_ref` runs. [line 590](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:590) verifies choices and development-file hashes, but never compares the frozen provenance with the current build. Re-gating a changed build can therefore permit old development/reference artifacts to feed a new test build.  
   **Fix:** make freezing create-once; require a new experiment directory for another freeze. Compare frozen provenance with every subsequent stage, validate producer manifests for consumed artifacts, and verify input hashes and provenance again after long-running stages.

4. **§10 — Analysis can accept different references from those consumed by the test.** [iteration61_replication.py:614](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:614) saves `test_ref_sha256`, but neither checker nor analysis enforces it. The checker validates current L* witnesses while checking targets against each task’s embedded, potentially older reference. Analysis merely binds the checker to the current files ([line 711](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:711)). An in-memory probe reproduced acceptance of mismatched consumed/current reference hashes.  
   **Fix:** before checking or analysing, require the saved consumed-reference hash to equal the current reference-file hash; also assert agreement among task references, test references, and the reference artifact.

5. **§4/§10 — A legitimate zero-witness experiment is rejected spuriously.** [iteration61_replication.py:683](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:683) and [line 711](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:711) reject zero checker rows. Successful references may all lack feasible solutions, giving feasibility-only targets; successful tests may then never attain feasibility. That produces valid `T=1` observations with no required witnesses. An in-memory probe reproduced this rejection.  
   **Fix:** derive the expected witness set explicitly. Accept an empty verified set when the expected set is empty; reject missing expected witnesses.

6. **§10 — Independent witness coverage omits development.** [iteration61_replication.py:644](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:644) checks only test-reference L* witnesses and test records. Development L*, stop-validation targets, and reported rehearsal best solutions receive no independent verification, although §10 does not restrict its witness requirement to test artifacts.  
   **Fix:** apply the checker to these development artifacts too, binding its outputs to their hashes and blocking conclusions on verification failure.

**Non-blocking findings**

- **§7 diagnostics:** [line 502](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:502) reports λ, weights, error, ESS, and maximum weights, but omits required weighted attainment rates by arm. Derive these from the corresponding rehearsal vectors for both tilts.
- **§9 assertions:** pairing is asserted for rehearsal/test only. Add population assertions to other paired stages, including FX-T configurations. The exhaustive seed-uniqueness test passes.
- **§10 exclusions:** [line 725](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:725) reports per-cell counts without rates. Add rates and derive planned units from the frozen roster × `n`, rather than observed records, so wholly missing units/cells cannot disappear.
- **§3 strictness:** field comparison uses Python numeric equality, not explicit floating-point bit comparison. Use recursive, type-aware binary comparison for the promised bit-level gate.

**Clauses verified**

- **§§2–4:** network order, R, scenario constants, spread, BusORPD mapping, inherited CHT/PF handling, reference tasks/budgets, successful-reference L*, feasibility fallback, and no-success STOP match.
- **§§5–6:** all four budget medians must pass; smallest B wins. Complete, balanced FX-T calibration gives equal weights; `argmin` selects the first tied grid index. Frozen selectors/operators are reused.
- **§7:** rehearsal completeness, medians, pooled ≥4/20 attainment and positive variance match. Common-λ tilt, strict attainability, error and ESS checks match. Multinomial resampling is distributionally equivalent for this linear contrast; series RNGs continue without per-experiment reset. Screening, independent confirmation/null series, 825/36 thresholds, Wilson bounds, and linear percentiles match.
- **§8:** equal network/scenario weights, paired stratified bootstrap, shared 95%/90% draws, and separate strict direction/equivalence labels match.
- **§10 stopping:** generated populations, PF prefixes through h, no PF after target, 24 pairs, all three decisions, full-budget fallback, completion checks, fresh processes, and one retry match. Sensitivity preserves successful branches and restores unavailable branches to `T=1`; empty cells block primary inference and >5% is flagged.
- The checker’s per-j monkeypatch, restoration, and process-local cache are sound. It rebuilds OPF once per worker/cell, **not per witness**. §11 adds no implementation requirement.