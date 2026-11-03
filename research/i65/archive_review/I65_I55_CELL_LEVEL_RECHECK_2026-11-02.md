# I65 independent I55 archived **cell-record** cross-check — 2026-11-02

**Repository state examined:** `owlCoder/gadapt`, `main` at `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`. **No new experiment; no change to historical archives; no protocol freeze.** This reanalysis is intentionally narrower than the unresolved NPZ replay.

## Verified directly from individual I55 JSON source cells

The 21 historical `research/results/iteration55/cells_<library>.json` files were read separately through the connected GitHub source. They contain **630 cells** (30 per library). **620 cells** record successful triple-process comparisons; **10 Nevergrad cells** (sphere/rastrigin, d=10, five seeds each) have the archived NumPy `TypeError` and are **excluded**, not treated as reproducible runs. All **620/620 evaluable cells** have a successful manipulation control. As an extra precision guard, the original decimal sentinel literals were compared as exact strings in all **630** source records, avoiding JavaScript float rounding of signed 64-bit integers; all 630 show the same-seed equality and changed-seed difference. On all evaluable records, the baseline and same-hash-seed sentinel values agree, and their changed-hash-seed counterparts differ.

Crucially, rather than only accepting stored `D3` / `D3x_same` / `D3x_diff` labels, we **re-derived each label** from the archived `hash`, `hash_rerun`, `hash_same`, and `hash_diff` digest pairs. All three derived indicators match their stored indicator in **every one of the 620 evaluable cells**. This is a complete consistency check over the *cell-level metadata*, **not a recomputation of SHA-256 from the NPZ point arrays**.

| Cell-level observation | Independent result | Interpretation |
|---|---:|---|
| Total 21 × 30 | **630** | Historical cohort, not 630 successful comparisons |
| Evaluable / invalid | **620 / 10** | 10 Nevergrad failures preserved as invalid |
| Hash-seed sentinel control | **620/620 PASS** | Manipulation effective among evaluable cells |
| `D3x_diff`: SMAC | **30/30** | Changed hash seed changes archived call-sequence digest |
| `D3x_same`: SMAC | **0/30** | Same hash seed matches archived call-sequence digest |
| `D3x_diff`: Nevergrad | **5/20** | Some mismatches under changed hash seed, with residual same-seed mismatches |
| `D3x_same` and `D3`: Nevergrad | **5/20 each** | Not clean evidence of exclusive hash-seed causation |
| `D3x_diff`: remaining 19 libraries | **0** | No positive archived flags across these recorded cells |
| All re-derived `D3` / `D3x_*` labels | **0 mismatches** | Internally consistent with archived digests |

These observations match the I55 frozen report's H55a–H55c outcomes. **H55d remains NOT SUPPORTED**: the one emukit C2 mismatch in `recompute.json` was not independently recreated from NPZ, so this review does not change that negative verdict.

## Provenance and reproducibility

The adjacent machine-readable JSON lists all **21 exact source Git blob SHA-1 IDs** plus the original `recompute.json` ID, detailed per-library counts and explicit check scope. The portable Python3 standard-library-only `i55_cell_archive_recheck.py` uses Git blob identity checks and fails closed on a changed input, duplicate cells, ineffective sentinel manipulation, invalid digest, or a mismatched re-derived flag. Eight synthetic positive/negative unit tests have passed locally. **The portable script's end-to-end run against a full local clone was NOT performed in this session**, because no local clone/network download was available; the actual 21-file verification used the GitHub connector and equivalent comparison rules.

To re-run in a checked-out copy of the repository, place the script and test under `research/i65/`, then execute:

```sh
python -m unittest discover -s research/i65 -p 'test_i55_cell_archive_recheck.py' -v
python research/i65/i55_cell_archive_recheck.py > i55_recheck_output.json
```

If the original files have been modified, the verifier will raise `ArchiveMismatch` on Git blob identity. Do not overwrite historical JSON. The artifact is a **derived result**, never a substitute for any original archive.

## Explicitly outstanding before submission

1. Recompute sequence digests from the archived NPZ objective arrays under documented serialization, and independently reproduce the reported **318/358** byte-level sequence equality to I50 (currently NOT_RECOMPUTED).
2. Recompute the single archived **emukit plateau d=2 seed=6001 C2** disagreement from raw NPZ traces and inspect original `VECLIB_MAXIMUM_THREADS` confound (currently NOT_RECOMPUTED).
3. If requested, independently re-estimate the original I64 effect/CI bootstrap from individual stochastic runs and obtain an external methods review. No additional held-out COCO or ORPD optimization experiment is authorized by this audit.

**Research decision:** better manuscript traceability, **not a novel algorithm/theorem or approval**. Preserve `NO-FREEZE`, `COCO NOT_RUN`, `novelty NOT_ESTABLISHED`, and the outstanding M6/C1 supervisor decision.
