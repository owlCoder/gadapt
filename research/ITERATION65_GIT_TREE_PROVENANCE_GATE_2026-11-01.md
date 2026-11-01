# I65 — committed Git-tree provenance gate after research migration

**Date:** 2026-11-01. **Scope:** `owlCoder/gadapt`; static Git-tree/read-only audit, not optimizer research or historical execution regression.  
**Checked main HEAD:** `aa47356fdec5551531dbd2135aec2e87b296de11`; tree `958a9f969eb9c772891459a9355464ecd730db60`.  
**Original pre-migration commit:** `0e7cacda2040643a41ff923dd2a71ffbc3f5dfef`; tree `c8ab0b56c61911fca4bbd227acbc83bd1e2fa468`.  
**Migration manifest Git blob:** `8afd04cc2bb9159989cae5d254fc793b5c2eca8e`.  
**Comparison baseline for unchanged outputs/core:** `ba1fc60138b6c5e88739549e09c2ac5820392231`.

## Verified findings (remote committed Git objects)

The original and current GitHub recursive trees were retrieved in full (`truncated=false`): **3,975** and **4,494** tree entries, respectively. A separate local JavaScript check of SHA-1 for Git's `blob <length>\0<content>` format was validated against the standard `abc` SHA-1 and the Git empty-blob SHA before comparing each symbolic-view blob to its **expected relative target-path string**.

| Invariant | Measured outcome |
|---|---|
| Manifest entries, unique old/canonical/view paths | **341 / 341 PASS**; no repeated or escaping paths |
| Original old-path blob SHA, mode and byte size vs manifest | **341 / 341 PASS** |
| Current canonical blob SHA, mode and byte size vs original | **341 / 341 PASS** |
| Curated view exists as mode `120000` with correct relative symlink-content SHA | **341 / 341 PASS** |
| Old root file still tracked when it should be relocated | **0** |
| Missing canonical/view, malformed paths or hash discrepancies | **0** |
| Old experimental output blobs under `research/results/` vs `ba1fc601` | **2,717 / 2,717 unchanged**, with intended documentation `results/README.md` modified |
| Tracked `gadapt/` blobs vs `ba1fc601` | **226 / 226 unchanged** |
| Tracked `research/i64/` blobs vs `ba1fc601` | **42 / 42 unchanged** |

**Why the `_SR.md` counts are not contradictory:** the present tracked tree contains 145 regular `_SR.md` blobs, including **24 extra archived original-language copies**. Excluding those archive copies leaves **121 content sources** (24 active English translations, 97 preserved original Serbian sources); the separate **107 symbolic `_SR.md` views** are aliases, not additional independent texts. [Language audit v2](LANGUAGE_AUDIT_2026-11-01.json) defines this counting rule.

## New repeatable read-only checker

- [`research/compat/check_migration_git_tree.py`](compat/check_migration_git_tree.py): parses `git ls-tree -r -z -l` of the manifest's source commit and current HEAD; checks each source/canonical/view triple, Git mode, SHA, byte size, old-path absence and relative symlink target SHA. **No local restore, Python optimizer imports, data rewrite, network, CI or expensive objective calls.**
- [`research/compat/test_migration_git_tree.py`](compat/test_migration_git_tree.py): six **synthetic** tests in small disposable Git repositories: valid case, modified canonical blob, misdirected view symlink, escaping path, wrong historical SHA and duplicate manifest entry. All **6/6 PASS** under local Python `unittest` on 2026-11-01.
- Local test-file SHA identity was verified against the Git blob produced for uploading the tested files: checker `cf4d7195d1687965a8df7609a19088ca91bb2ac1`, tests `cbde00da456c8f3fc6d706fba53c43aeaae5d924`.

After checking out this commit on a real machine:

```sh
python -m unittest discover -s research/compat -p 'test_migration_git_tree.py' -v
python research/compat/check_migration_git_tree.py
# Only after the read-only audit passes, and when explicitly doing the local runtime gate:
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

The checker uses **tracked committed state**, not the potentially modified working-tree content of the restored aliases. It validates history and tracked symlink text; it does **not** certify runtime import behavior, Python dependency availability, the actual local worktree bytes, or the correctness of a physical evaluator. The separate restore utility must still perform its own working-tree SHA preflight.

## Remaining execution gap and decision

The current analysis container has no checked-out GAdapt Git repository and cannot resolve `github.com` via DNS (`git ls-remote` failed). Thus the **real complete-clone** invocation of the new checker, 341-alias `--apply --verify`, and actual legacy I41/I63/I64 pytest runs remain **NOT_TESTED** here. The previous isolated 9/9 compatibility tests and 54/3 I65 instrumentation tests are historical results, **not** a new full-clone run.

**Gate verdict:** **PASS for committed-tree provenance, PARTIAL/NOT_TESTED for historical runtime compatibility.** I65 policy C novelty remains **NOT ESTABLISHED**; `NO-FREEZE / NOT_RUN`. The next accountable step is the nonexpensive local full-clone test sequence in [the migration gate](ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md), followed by independent GAdapt/CMA/COCO oracle integration and supervisor-scope decisions. Do not start confirmatory COCO or expensive GitHub Actions as a side effect of the provenance check.
