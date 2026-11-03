# I65: Independent I50↔I55 archive pairing and selective raw NPZ replay

**Review date:** 2026-11-02  
**Repository:** [`owlCoder/gadapt`](https://github.com/owlCoder/gadapt)  
**Source commit:** `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`  
**Evidence class:** existing archived data only; **no optimizer/PF/OPF/COCO runs**, no source or experiment changes.  
**Reproduction level:** **COMPLETE** for 12-library I50↔I55 JSON digest pairing; **SELECTIVE** for four I55 raw NPZ files; **NOT RUN** for an end-to-end 620-NPZ replay.

## 1. Independently reproduced the exact 318/358 I50↔I55 sequence-hash claim

Read original 12 `research/results/iteration50/cells_<library>.json` and matching `research/results/iteration55/cells_<library>.json` files through connected GitHub at the pinned commit. For each matching (`function`, `d`, `seed`) pair, compare the saved `hash` value **only where both trial rows have no error and contain hashes**. This logic does not use the I55 `recompute.json`'s answer and does not declare any failed trial equal by default.

| Library | Matching | Differing | Excluded | Comparable |
|---|---:|---:|---:|---:|
| baybe | 30 | 0 | 0 | 30 |
| bayes_opt | 30 | 0 | 0 | 30 |
| bofire | 28 | 0 | 2 | 28 |
| cmaes | 30 | 0 | 0 | 30 |
| emukit | 20 | 10 | 0 | 30 |
| evolopy | 30 | 0 | 0 | 30 |
| evotorch | 30 | 0 | 0 | 30 |
| evox | 30 | 0 | 0 | 30 |
| gfo | 30 | 0 | 0 | 30 |
| niapy | 30 | 0 | 0 | 30 |
| scikit_opt | 30 | 0 | 0 | 30 |
| smac | 0 | 30 | 0 | 30 |
| **TOTAL** | **318** | **40** | **2** | **358** |

The **two excluded cells** are original I50 `bofire` timeouts on `rastrigin`, `d=10`, seeds `6001` and `6004` (the later I55 rows have no error). Exactly **10** emukit rows disagree, **all at `d=2`**: plateau seeds `6000–6004`, rastrigin seeds `6001,6003`, sphere seeds `6001,6003,6004`. **All 30 SMAC** sequence hashes differ between I50 and I55. No other differences were seen among the comparable rows.

**Scientific scope:** this confirms the published **318/358 comparison of already archived hexdigests**, not a recreation of I50's originally lost individual call arrays. Never use `318/358` to claim perfect replay or general software correctness.

## 2. Independent check of the emukit post hoc diagnostic

Independently compared the actual `hash` fields from all 10 rows of `results/iteration55_posthoc/emukit_veclib.json` to the original I50 and I55 cell rows. **10/10 diagnostic hashes equal the matching original I50 hash**, and **10/10 differ from the unmodified I55 trace hash**. All ten post hoc rows record `veclib_threads=1`. This is verified from **hash data**, not by trusting the diagnostic's `matches_i50_archive` boolean.

The observation supports an environment-thread sensitivity explanation. It is **not** an independently rerun randomized causal experiment; the original O3 and strict H55d failure remain unchanged. Especially, the emukit plateau `d=2`, seed `6001` archived `C2:0→1` difference remains a recorded **nonmatch**.

## 3. Four original NPZ archives decoded and SHA-256 independently reconstructed

A separate read-only verification retrieved four original binary NPZ files via GitHub, decoded base64, ZIP DEFLATE-compressed NPY arrays and recalculated the **historical I49 SHA-256 sequence hash** from each coordinate row, the Python-compatible string representation of each `plateau` objective value, and the ASCII phase name (`search` / `post`). The saved `hash` field was used as a comparator, not as an input. Plateau values are integer-valued float64, so the original Python `repr(float)` encoding is unambiguous.

| NPZ archive (plateau, d=2, seed=6001) | Calls | Git blob SHA | Independently recomputed SHA-256 |
|---|---:|---|---|
| `cmaes/plateau_2_6001.npz` | 198 | `a0530d20e23a39bd8b6ee315656c8ea107840f57` | `0f100f9e0fdf8d404198a99dab493a080396904da05398e1d9b45655e4572e1d` |
| `smac/plateau_2_6001.npz` | 200 | `4b2d59bfaf0013167433455af0d191b930031a43` | `32452b42f5154ccf3a1b238d691ee5c3bd093a8ec707beb29a022c457894cc0f` |
| `emukit/plateau_2_6001.npz` | 200 | `4199ba47cb359746d25aa1d3ca20b3b6ed9d1f75` | `d6b49883de718d74ad7f2829d7a61747f1eeb20de0d0b89377918b6c02c36cb1` |
| `baybe/plateau_2_6001.npz` | 200 | `06d4eca956f44f50a2e3a41133bd57831949e7ab` | `dd00bb71bbd29ba6590718195d86cd739c9de34208ead247a6d53186d4fd42a0` |

**All four recomputed SHA-256 hashes exactly equal the corresponding I55 `cells_<library>.json` values.** This is evidence of real raw-NPZ inspection, but does **not** establish an exhaustive 620-file replay or an independent raw-flag count.

## 4. Complete read-only NPZ verification script supplied — not run across all 620

The bundled `i55_npz_cross_archive_verifier.py` loads I55 raw NPZ `x/f/phase` arrays with `allow_pickle=False`, independently rehashes every objective trace and derives C1/C2/C3/C4/C5/R1/R2/R3/D2 flags without importing optimizer adapters. It also rechecks the 318/358 I50/I55 digest pairing and 10/10 emukit post hoc identities. Input original JSON Git blob IDs are pinned; unexpectedly large or malformed NPZ files are rejected.

**Ten synthetic offline unit tests passed.** This checks the verifier logic on fabricated tiny fixtures, not its full archival performance. To run against a full clone with NumPy installed:

```bash
python i55_npz_cross_archive_verifier.py --repo-root /path/to/gadapt \
  > I65_I55_NPZ_COMPLETE_RECHECK.json
```

Do not mark an all-archive NPZ replay as complete unless the generated JSON has `npz.checked=620`, `npz.errors=[]`, and `npz.full_raw_trace_pass=true`. Its full execution is **NOT_RUN** in this review.

## 5. Reviewer-facing conclusion / GO–NO-GO

- **Confirmed now:** I50↔I55 saved-digest pairing **318/358**; exact 40-mismatch/two-timeout decomposition; emukit post hoc digest reconciliation **10/10**; independently reconstructed SHA-256 from **four original NPZ archives**.
- **Still pending:** complete 620-NPZ decoding and reclassification, full raw I50 replay (original individual traces absent), I64 individual stochastic-run/bootstrap recomputation, blinded detection specificity, doctoral M6/C1 novelty/scope decision.
- **Never change:** strict I55 H55d remains **NOT SUPPORTED**; I50 and I55 disagree in the archived emukit C2 case; novelty remains **NOT ESTABLISHED**. Archive consistency does not demonstrate ground-truth detector validity or industrial power-network reliability.

**GO:** independent methods reviewer runs full NPZ verifier read-only and inspects discrepancies. **NO-GO:** new optimizer/COCO/PF/OPF experiments, data repair or protocol freeze before human review. Status: `DRAFT / NO-FREEZE / COCO NOT_RUN`.
