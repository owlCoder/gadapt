# I55 — all 620 original NPZ source bytes: provenance gate

This addendum comprises the [archival completeness report](I65_I55_NPZ_GIT_ARCHIVE_COMPLETENESS_AND_PROVENANCE_2026-11-03.md), [620 original Git blob identities](I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json), [local read-only byte verification program](i55_npz_git_blob_manifest_gate.py), [12 synthetic regression tests](test_i55_npz_git_blob_manifest_gate.py) and [local test log](I65_I55_NPZ_GIT_PROVENANCE_LOCAL_TEST_LOG_2026-11-03.txt).

**Already checked in the original Git trees:** 21 libraries; 620 NPZ blobs; 12,319,037 compressed bytes; original source names, file sizes, blob identities; 10 expected Nevergrad failed cells; zero changes to the 620 files through inspected main head. This is a Git **index** authenticity/completeness audit, not the 620 full original NPZ raw-array replay.

To verify the actual 620 local source bytes in a full checkout and then redo the frozen numerical analyses:

```bash
python research/i65/archive_review/i55_npz_git_blob_manifest_gate.py --repo-root . --output /tmp/i55_npz_git_gate.json
python research/i65/archive_review/i55_npz_cross_archive_verifier.py --repo-root . > /tmp/i55_npz_replay.json
```

Do not mark full replay complete until **both** `full_git_blob_pass` and `npz.full_raw_trace_pass` are true and all errors are empty. These read-only tools never run a new optimizer or power-flow evaluation.
