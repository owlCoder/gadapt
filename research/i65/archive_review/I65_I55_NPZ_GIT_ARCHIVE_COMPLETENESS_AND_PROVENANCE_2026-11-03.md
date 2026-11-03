# I65 — I55 original NPZ archive completeness and Git-byte provenance (2026-11-03)

**Completed Git-tree inventory; NOT completed 620-NPZ numerical replay.** This independent retrospective audit performs no optimizer, PF/OPF, or held-out COCO experiment.

## Source-level result

Compared **nontruncated** recursive Git trees at the original I55 archival baseline `6b56fbc53ffc4d275ecef5e911ea4663474c9a08` (root tree `f88d221152fcb4157a8e1151a11b53cdfe8180b7`) and the previous `main` head `a03606d84768264424ccc59e40eb113d29b468d2`. Every regular Git blob under `research/results/iteration55/traces/` was matched by relative path, exact Git blob SHA-1 and compressed byte size.

| Audit property | Directly observed |
|---|---:|
| Library directories | 21 |
| Original NPZ source blobs | **620** |
| Total original compressed NPZ bytes | **12,319,037** |
| Full-library coverage | 20 libraries × 30 cells = 600 |
| Nevergrad | 20 of 30 intended cells |
| Expected absent Nevergrad NPZ files | **10**, sphere and Rastrigin at dimension 10, seeds 6000–6004 |
| Missing files among the 620 valid original cells | **0** |
| Unexpected or duplicate relative paths | **0** |
| Git NPZ blob SHA-1 or size changes between original baseline and inspected main | **0** |
| NPZ paths added or removed between these Git trees | **0** |

The ten missing Nevergrad files correspond exactly to **historically failed** runs (the ten invalid observations), not to newly lost successful traces. All original 620 valid NPZ blobs are still versioned on GitHub.

## New pinned binary authenticity gate

The new [original 620-blob manifest](I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json) stores each original file's relative path, original Git blob SHA-1 and exact byte size, with the baseline source commit and root tree. The fail-closed standalone [Git blob gate](i55_npz_git_blob_manifest_gate.py) has **12 synthetic tests** in [test_i55_npz_git_blob_manifest_gate.py](test_i55_npz_git_blob_manifest_gate.py).

The gate has two sharply different verification levels:

- `--index-only`: validates the complete 620-entry source roster and metadata without opening original NPZ bytes. This level was performed using the original Git tree in the connector and cross-checked on the derived manifest.
- `--repo-root <full-clone>`: locally reads **all 620 original compressed NPZ files**, verifies each raw Git blob SHA-1 and size, and rejects missing, substituted or mutated bytes. The program and synthetic fixtures have been tested, but this **full original-byte gate has NOT run here**, because the working container cannot download GitHub files.
- After the original-byte gate passes, independently run the existing [NPZ trace replay script](i55_npz_cross_archive_verifier.py), which parses the `x/f/phase` arrays and recomputes recorded sequence hashes and detector flags. **Original 620/620 NPZ numerical replay remains NOT RUN.**

```sh
python research/i65/archive_review/i55_npz_git_blob_manifest_gate.py --index-only
python research/i65/archive_review/i55_npz_git_blob_manifest_gate.py --repo-root . --output /tmp/i55_git_blob_gate.json
# only when full_git_blob_pass == true:
python research/i65/archive_review/i55_npz_cross_archive_verifier.py --repo-root . > /tmp/i55_complete_raw_replay.json
python -m unittest discover -s research/i65/archive_review -p 'test_i55_npz_git_blob_manifest_gate.py' -v
```

The original I55 metadata/detector archive remains authoritative. Previously verified source-level A/A'/B categories are 585 stable, 30 SMAC hash-seed-conditioned, and five Nevergrad cases unstable even at the same hash seed; the original H55a–c supported and H55d NOT supported decisions are unchanged. The 620-node Git inventory is **not** evidence of detector specificity or causal mechanism validity.

**Doctoral status unchanged:** both papers `DRAFT`; `NO-FREEZE`; held-out `COCO NOT_RUN`; `NOVELTY NOT_ESTABLISHED`; independent M6/C1 human decision unsigned. Original frozen traces and results were not modified.
