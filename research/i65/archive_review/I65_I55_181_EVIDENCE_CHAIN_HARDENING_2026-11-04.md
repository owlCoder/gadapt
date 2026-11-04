# I55 181-source evidence-chain hardening — 2026-11-04

**Status: archival provenance control, not a new raw NPZ reproduction.**
Scientific disposition remains **DRAFT / NO-FREEZE / originality NOT_ESTABLISHED / COCO NOT_RUN**.

## Original public anchors (verified through connected GitHub)

- `main` starting HEAD: `8d376a720afe2704af5efdb39777dac7a2c5e742`.
- Original 620-NPZ source manifest Git blob: `50ca2e96762447070a74309850cb1aa6586d3eb3`.
- Preexisting 55-source evidence index Git blob: `1418207f25a3745c4caacdd2fdb63359dc227b04`.
- Published 126-source evidence index Git blob: `63d02f2e03483babe67f95adc9414dc886c5b12f`.
- Frozen original replay engine Git blob: `076ac19beef2514eef9985c86eac071ca9975b8d`.
- Original I55 source commit: `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`.

## Fresh GitHub-side reinspection

The 21 new archival batch files were fetched independently through the
GitHub connection and compared with the published per-library blob SHA-1
values in the SHA-pinned 126-source index. Each batch's library, ordinal,
six source records, objective-call sum and source-byte sum were compared
with the index; each source path, original NPZ Git blob SHA-1 and byte size
were compared with the frozen 620-entry manifest; duplicate paths were
checked against the prior 55-source roster.

| Subset | Batch blobs | Distinct records | Objective calls | Source compressed bytes | Findings |
|---|---:|---:|---:|---:|---:|
| Batch 01–10 | 10/10 | 60 | 16,669 | 842,035 | 0 |
| Batch 11–21 | 11/11 | 66 | 44,483 | 1,707,358 | 0 |
| **Total** | **21/21** | **126** | **61,152** | **2,549,393** | **0** |

This authenticates published **JSON evidence identities and manifest
references**, not independent numerical re-execution against binary NPZ
content. Existing raw replay coverage remains **181/620**, with **439**
unreplayed originals and **85,450** objective evaluations in the archived
replay ledger.

## Reconciler integrity gap identified and closed on review branch

The earlier `i55_181_npz_evidence_reconcile.py` authenticated the frozen
620 manifest, prior 55 index and original per-library cells metadata. But
`audit_full_checkout()` directly JSON-parsed the 21 new batch files,
without authenticating their Git blob identities against the published
126-source index. An altered batch field not otherwise inspected by
`reconcile()` (e.g., `objective_max_absolute_error`) could leave the
reconciliation result reporting PASS. **This is a verification coverage
gap, not evidence that any archived batch was tampered with.**

The revised read-only loader `load_pinned_batches()`:

1. Pins the 126-source index's raw Git blob SHA-1, schema and provenance.
2. Pins every new batch's raw Git blob SHA-1 against that index before
   accepting any of its content.
3. Checks indexed batch order, library ownership, unique NPZ paths,
   exact correspondence with the earlier 55, source-call/byte aggregates,
   claimed total coverage and failed-replay counts.
4. Passes authenticated batch records into the preexisting independent
   original-cell digest, detector-flag and objective-call reconciliation.
5. Adds explicit index/batch-identity authentication markers to the
   machine-readable reconciliation result only after successful checking.

Five additional synthetic adversarial tests cover intact input,
unchecked-field mutation of a batch, unpinned index mutation, an
internally re-pinned but incorrect source roster, and an inflated
internally re-pinned objective-call total. These are **test definitions**;
they are not new source NPZ replays. They still require execution in a
checkout or CI before claiming a test-run PASS.

## How to verify in a complete local checkout

```sh
python -m unittest discover -s research/i65/archive_review -p 'test_i55_181_npz*py'
python research/i65/archive_review/i55_181_npz_evidence_reconcile.py \
    --repo-root . --output /tmp/i55-181-authenticated-evidence-chain.json
```

Run the strict 620-original read-only full NPZ source attestation separately
only on a full original Git checkout. Neither this review nor the new
synthetic tests prove a new A-process raw NPZ replay, an A-prime/B raw
replay, access to the off-Git 4,200-run I64-R archive, or M6/C1 sign-off.
No optimization, PF or COCO experiment was launched.
