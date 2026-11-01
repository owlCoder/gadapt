# Restoring historical research paths safely

The 2026-11-01 migration moved 341 original root files byte-identically into `research/legacy/flat/`. Their source path, destination path and Git blob SHA are recorded in [the migration manifest](../MIGRATION_MANIFEST_2026-11-01.json).

The curated `studies/`, `tools/` and `literature/` symlinks are for **navigation only**. I56/I58/I61/I63 derive `HERE`, `REPO` and `OUT` from `__file__`, so executing them directly from `legacy/flat/` or the curated symlink view can change resource paths and invalidate provenance.

## Opt-in restoration in a full Git clone

```sh
python -m unittest discover -s research/compat -p 'test_migration_compat.py' -v
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

The first command runs **synthetic, inexpensive** standard-library regression tests. The second performs a read-only all-file preflight against the manifest and original Git blobs. The third creates **only missing old root aliases**. Any SHA mismatch, absent canonical file, duplicate path, user-file collision or conflicting symlink blocks mutation at preflight. The 341 precisely named aliases are ignored by `research/.gitignore`.

For historic runs, use `research/<original_name>.py` entrypoints after restoring aliases; do not implicitly import old modules from `legacy/flat/`. Preserve frozen sources and original experiment seed/evaluation accounting.

## Still not proven

The entire I41/I56/I61/I63/I64 historical regression suite has **not been run in a full clone** after migration. Synthetic compatibility tests are not a substitute for full optimization integration. The [gate report](../ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md) gives exact remaining commands and blockers.
