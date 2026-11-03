# I65 — independent archival follow-on review (2026-11-02)

**Source snapshot:** [`owlCoder/gadapt@6b56fbc53ffc4d275ecef5e911ea4663474c9a08`](https://github.com/owlCoder/gadapt/commit/6b56fbc53ffc4d275ecef5e911ea4663474c9a08). **Status:** research verification, no experiments, no scientific freeze. Original source files, experiments, protocols, result archives, and manuscripts in GitHub `main` were not changed. The current environment could read GitHub via a connected source, but a complete repository checkout was not accessible to the local Python runtime.

## 1. Audit results and exact verification levels

| Work | New measured evidence | What it does **not** establish |
|---|---|---|
| I55 21-library saved cell JSON consistency | Previously verified 630 cells, with 620 valid hash-seed-control records and 10 invalid Nevergrad cells | Independently reconstructed A/A′/B process call sequences |
| I50/I55 saved digest pairing | **318/358 identical**, 40 different (SMAC 30, emukit 10), two original I50 `bofire` timeouts | 358 fresh NPZ digest recalculations |
| I50/I55 **numeric** vs **binary** flags | **1/358 cells** differs numerically: emukit `plateau / d=2 / seed=6001`, `C1:2→3`, `C2:0→1`. Exactly **one** *binary presence* mismatch, in C2. | Equality of all traces; equality of all C/R numerical counts in the changed cell |
| Direct binary `.npz` inspection | Four archived `plateau / d=2 / seed=6001` files independently rehashed with SHA-256, all four match their recorded I55 digests; **all ten** emukit `plateau` NPZ files (`d=2,10`, five seeds each) independently reclassified for `C1–C5`, **10/10 match** | Full 620-trace NPZ replay or 620 independently rehashed sequence digests |
| I64 seven compressed analysis archives | Source Git blob IDs verified; **41/41** independently recomputed scalar/directional arithmetic and hypothesis-label checks agree with the extracted original analyses | New bootstrap resampling or independent stochastic trial replication |
| Local verifier regression | **37/37** tests passed across the archive-verifier, numeric/binary comparator, and I64 arithmetic code | Passing all checks on a full original repository checkout |

**Important H55d interpretation:** The historical `iteration55_recompute.py` compares `bool(old_flag)` with `bool(new_flag)`. The change `C1:2→3` has no binary-presence change (both nonzero), so the report correctly lists only `C2:0→1` as an H55d *presence-flag* disagreement. A statement that every exact numeric flag counter agrees outside the reported C2 value would be too broad. Direct NPZ reconstruction confirms **C1=3 and C2=1** for the I55 primary-process trace at that cell; I50's old JSON values are **C1=2 and C2=0**. Keep **H55d NOT SUPPORTED**.

**A critical ceiling on any future raw replay:** The protocol archived full `.npz` call sequences for primary process **A** only. Independent rehashing of A from `.npz` is possible. Fresh reconstruction of A′ and B sequence digests **from raw event sequences** is **not** possible from the current I55 NPZ archive alone (A′/B are represented by saved hashes and sentinel metadata). Do not call a full A-only NPZ rehash a complete independent three-process replay or a causal validation of `PYTHONHASHSEED` effects. The archived manipulation check is a consistency check of saved evidence, not a new rerun.

## 2. I64 scientific outcome — verified source-level numbers

Original seven gzip source Git blob identities are recorded in [`I65_I64_GITHUB_SEVEN_ANALYSIS_RECHECK_2026-11-02.json`](I65_I64_GITHUB_SEVEN_ANALYSIS_RECHECK_2026-11-02.json) with 41 passing arithmetic/directional checks. Those checks are recalculations of saved **aggregates and contrasts**, and the older 20,000-replicate bootstrap algorithms were **not rerun**.

- **S0:** original, limited-comparator ECDF area was `A(GAdapt)=0.6983036008230452` versus `A(DE)=0.6509895576131688`. A new direct reading of all **21** per-cell source-analysis records independently confirmed final cell-median advantage for **DE 14, GAdapt 6, tie 1**, whereas the per-cell area A favored **GAdapt 17, DE 4**. Both are defined within the original S0 stopping configuration; they are *different estimands* and must not be conflated or rebranded as an equal-budget final-accuracy ranking. Exact source identity and the direct comparison summary are in [`I65_I64_S0_CELL_RANKING_GITHUB_RECHECK_2026-11-02.json`](I65_I64_S0_CELL_RANKING_GITHUB_RECHECK_2026-11-02.json).
- **E:** equal-budget, stronger-baseline comparison has `A(GAdapt)=0.6732050137174209` versus `A(IPOP)=0.7698678429355281`, and `A(GAdapt)-A(IPOP)=-0.09666282921810702`, with a fully negative **archived** simultaneous confidence interval. The frozen overall verdict is **opposite**, not “generally superior.”
- **R:** the fixed Q-matched differential-loss contrast recomputed from original aggregate values is `0.07079177983539131` with archived simultaneous interval `[0.059811869725967554, 0.08177168994481507]`. The frozen positive H64r2/H64r3 conclusions hold **only for the selected functions, dimensions and orthogonal matrices**. Orthogonal Q is not necessarily a proper rotation; reflection is allowed.
- **E3:** the hybrid's rotated A improvement is `0.10290021604938274`, but its nonrotated 1.5×CVaR condition is **negative** (`−0.0006964276168909891`), with fully negative archived interval `[−0.0011091038824615844, −0.00028375135132039395]`. H64g2 is **opposite** and the complete frozen hybrid decision is **not supported**.
- **A:** the replaced-first-stage ablation's c1/c2 ECDF contrasts recompute to `0.13125542181069957` and `0.17786820987654323`, but the fixed CMA initial sigma choice constrains causal interpretation of the first-stage effect.
- **I:** primary H64c is **undecided**; H64d is **opposite**, from the original discrete ORPD study.
- **I2:** the hybrid's CVaR is `0.3771500251324287` versus IPOP `0.25184326402003326`, giving `CVaR(IPOP)−CVaR(H)=−0.12530676111239542` and a fully negative archived simultaneous interval `[−0.25022390683283424, −0.00038961539195656036]`. The feasibility contrast `P(H)−P(IPOP)=−0.029166666666666563` has interval `[−0.06427941895198026, 0.005946085618647137]` *crossing zero*; do **not** assert a separately established strict feasibility deterioration.

These are **conditional frozen study conclusions**, not new theoretical, universally valid or physical field-measurement claims.

## 3. Publication-ready scope corrections

**For Paper 1 (evaluation integrity):** explicitly define `flag-presence agreement` versus `exact event-count agreement`. Include the observed I50↔I55 comparison totals, two excluded I50 `bofire` timeouts, the emukit `C1:2→3` count change alongside the C2 binary change, and the A-only NPZ archival limit. Preserve I52's preregistered `19/21` threshold success and post hoc `17/18` complete-case and `17..20/21` missingness sensitivity. Never label the 33 bare I49 `Infinity` tokens as valid strict JSON, and never call flags independently adjudicated bugs without evidence.

**For Paper 2 (context-dependent GAdapt):** preserve S0's limited favorable aggregate with E's strong-baseline contrary outcome; label R's Q result conditional and not necessarily rotation-only; show E3's negative nonrotated tail contrast and I2's negative ORPD tail contrast together with their archived simultaneous intervals. State explicitly that I2 feasibility difference is not separately established at zero and that all bootstrap quantities are archival, not freshly re-estimated. An algorithmic originality claim remains **NOT_ESTABLISHED**.

## 4. Reproducible scripts and remaining gates

- `i55_i50_numeric_vs_boolean_audit.py` — verifies all 12 matched I50/I55 cell JSON sources by exact Git blobs; independently computes numeric-counter and Boolean-presence disagreements.
- `i64_archival_recheck.py` — verifies seven historical gzip Git blobs and recalculates 41 consistency checks directly from the full extracted analysis documents.
- `i64_s0_cell_ranking.py` — verifies the additional S0 14/6/1 final-median and 17/4/0 per-cell-A counts from 21 original descriptive records.
- `build_source_extracted_ledger.py` — produces the *current-turn* 41-check ledger using the selected source fields actually decoded through the GitHub connector, **not** a local full-clone replay.
- Existing `../i55_review/i55_npz_cross_archive_verifier.py` — read-only tool for all original I55 primary A NPZ files in a complete clone. Its former prospective 620/620 result remains **NOT_RUN** here.

On a separate **complete, unchanged checkout**, use:

```bash
python i64_archival_recheck.py --repo-root /path/to/gadapt > I65_I64_FULL_ANALYSIS_RECHECK.json
python i64_s0_cell_ranking.py --repo-root /path/to/gadapt > I65_I64_S0_CELL_RANKING_RECHECK.json
python i55_i50_numeric_vs_boolean_audit.py --repo-root /path/to/gadapt > I65_I55_EXACT_COUNTER_RECHECK.json
python i55_npz_cross_archive_verifier.py --repo-root /path/to/gadapt > I65_I55_FULL_A_NPZ_RECHECK.json
```

**No new algorithm experiments were done**. Remaining blockers: full primary-A NPZ replay; original I64 individual-seed/bootstraps if required by reviewer; precise prior-art differentiator; target venue and author approval; dated supervisor M6/C1–C6 decision. The historical status remains **`NO-FREEZE / COCO NOT_RUN / NOVELTY NOT_ESTABLISHED`**.
