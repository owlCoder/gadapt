# I65 — Research-layout migration compatibility gate (2026-11-01)

**Status: PARTIAL GO for the path-restoration tool; NO-GO for claiming full historical regression compatibility.** This is not a new optimization benchmark and does not change GA defaults, COCO results or frozen research protocols.

## Scope and verification

1. **GitHub provenance:** before migration, head `0e7cacda2040643a41ff923dd2a71ffbc3f5dfef`; after migration, head `92a31c109edf60810e383833bac1bf8d7430d603`. Verified: 341 original research-root files were relocated with **identical Git blob SHA**; 2,717 historical raw output files remained unchanged; 64 generated `__pycache__` objects were removed from tracked sources.
2. **Critical static review of GitHub sources:** I56 `iteration56_cht_study.py`, I58 `iteration58_validation.py`, I61 `iteration61_replication.py` and I63 `iteration63_replication.py` derive `HERE` and/or `REPO` from `os.path.abspath(__file__)`; `OUT` in I56/I61/I63 is location-dependent. Running modules directly from `research/legacy/flat/` or `research/studies/iNN/` is **not** equivalent to using the historical CLI paths.
3. **Correction:** `research/__init__.py` no longer silently adds `legacy/flat` to the package import search path. The historical root symlinks must be restored explicitly, opt-in, before importing active legacy modules.
4. **Restoration tool `research/compat/restore_legacy_paths.py`:** a complete preflight over all 341 entries before creating the first link; optional original Git blob SHA verification; fail-closed behavior for existing user files, conflicting symlinks or wrong hashes; idempotent operation. `research/.gitignore` names exactly the 341 legacy aliases, keeping local Git status readable.
5. **Cheap local synthetic tests** (Python standard library, Git, temporary directories): `python -m unittest discover -s research/compat -p test_migration_compat.py -v` → **9/9 PASS**. They cover dry-run behavior, idempotent apply, no overwrite of user data, conflicting symlinks, missing canonical files, preflight on mismatched hashes, duplicate aliases, old `HERE`/`REPO` semantics, and reading through GitHub navigation symlinks. These are **not tests of real I41 or I63 objective functions**.
6. **Local I65 instrumentation tests rerun:** `python -m pytest -q -rx research/i65/test_*.py` → **54 passed, 3 xfailed**, covering old I64 failed-attempt undercounting, mutable-input witness snapshots and the original stagnation timestamp/monotonicity guard. The result was **not** measured inside the full migrated repository clone.
7. Source-code provenance: local passing Python sources were checked against their staged Git blob SHA values. `restore_legacy_paths.py` = `6908ce90ec1edb73ed7821f4ba8820617213bace`; `test_migration_compat.py` = `1d369d0f91b2b674a34403c3416d7e3d8aa7e54a`.

## Outstanding blockers and next physical gate

The execution environment had no complete Git clone of the library or installed `cocoex`, `cma`, and `gadapt`. The connector could read/write GitHub source files but could not run the full repository. Therefore **none** of these operations were executed in that environment: the full 341-file `--apply --verify` restore, actual `research/test_iteration41_*.py` runs, `research/test_iteration63_replication.py`, I64 regression scripts or original GA import tests. Their status must be `NOT_TESTED`.

The final gate on a computer with a full Git clone and locked dependencies, **without expensive optimizer runs**, is:

```sh
python -m unittest discover -s research/compat -p 'test_migration_compat.py' -v
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
python -m pytest -q research/test_iteration41_*.py
python -m pytest -q research/test_iteration63_replication.py
python -m pytest -q research/i64/test_e_common.py research/i64/test_e_algos.py
```

Research `FREEZE` remains blocked: `I65 novelty not established` and GAdapt/CMA/COCO integration `NOT_TESTED`. The overall decision is **GO for local synthetic instrumentation tests, NO-GO for claiming complete regression compatibility** until the complete-clone checks have passed.
