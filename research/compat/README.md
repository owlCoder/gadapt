# Restoring historical research paths safely

The 2026-11-01 migration moved 341 original root files byte-identically into `research/legacy/flat/`. Their source path, destination path and Git blob SHA are recorded in [the migration manifest](../MIGRATION_MANIFEST_2026-11-01.json).

The curated `studies/`, `tools/` and `literature/` symlinks are for **navigation only**. I56/I58/I61/I63 derive `HERE`, `REPO` and `OUT` from `__file__`, so executing them directly from `legacy/flat/` or the curated symlink view can change resource paths and invalidate provenance.

## Read-only committed-tree gate (new)

Before performing any worktree restore, first verify the exact historical blob,
file-mode and symlink-target provenance against committed Git history:

```sh
python -m unittest discover -s research/compat -p 'test_migration_git_tree.py' -v
python research/compat/check_migration_git_tree.py
```

The checker is read-only and needs only Python, Git and the full repository
history. Its six synthetic regression tests were passed in isolation; the real
full-clone invocation remains **NOT_TESTED** in the reporting environment.
See [the committed-tree audit](../ITERATION65_GIT_TREE_PROVENANCE_GATE_2026-11-01.md).

## Opt-in restoration in a full Git clone

```sh
python -m unittest discover -s research/compat -p 'test_migration_compat.py' -v
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

The first command runs **synthetic, inexpensive** standard-library regression tests. The second performs a read-only all-file preflight against the manifest and original Git blobs. The third creates **only missing old root aliases**. Any SHA mismatch, absent canonical file, duplicate path, user-file collision or conflicting symlink blocks mutation at preflight. The 341 precisely named aliases are ignored by `research/.gitignore`.

For historic runs, use `research/<original_name>.py` entrypoints after restoring aliases; do not implicitly import old modules from `legacy/flat/`. Preserve frozen sources and original experiment seed/evaluation accounting.

## End-to-end core regression gate (Python 3.12, opt-in)

A new [fail-closed runner](run_full_clone_gate.py) checks the **real full-history
Git checkout**, Python 3.12, all 341 original symlinks and inexpensive historical
I41/I63/I64 core and I65 tests. Default mode is **read-only**:

```sh
python research/compat/run_full_clone_gate.py --python .venv/bin/python
python research/compat/run_full_clone_gate.py --python .venv/bin/python \
  --run --report-dir /tmp/gadapt-full-clone-gate
```

The explicit `--run` opt-in restores only the 341 root aliases after preflight
and runs a short allowlisted suite with at most 120 seconds per command, preserving
individual hashed logs and a final `gate.json`. Full-history and clean checkout
checks prevent a misleading PASS; required test skips are also classified as
incomplete. The external-mentor PyGAD cases (`MBENCH`) are **excluded**, not passed.

For environments without Python 3.12 locally, a new
[manual-only Actions workflow](../../.github/workflows/research-full-clone-gate-manual.yml)
provides Python 3.12, complete history and archived logs. It must be explicitly
dispatched by a maintainer; it has **not** been run as part of this work.

The two new synthetic [341-path scale tests](test_full_alias_scale.py)
and [driver tests](test_full_clone_gate.py) both passed locally
(**10/10** cases total), but only a real full-clone run can close the runtime
gate. See the [gate report](../FULL_CLONE_EXECUTION_GATE_2026-11-01.md).

## Still not proven

The entire I41/I56/I61/I63/I64 historical regression suite has **not been run in a full clone** after migration. Synthetic compatibility tests are not a substitute for full optimization integration. The [gate report](../ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md) gives exact remaining commands and blockers.

## First real full-checkout attempt (2026-11-01)

[GitHub Actions run #41357664531](https://github.com/owlCoder/gadapt/actions/runs/41357664531)
**completed with FAILURE** at GA import. The full-history Python 3.12
checkout did actually pass all **341 Git provenance checks**, restored all
**341 historical aliases**, and passed **25 compatibility tests**. It did
not reach the actual historical I41/I63/I64/I65 suite.

The exact root cause was `.resolve()` on the `.venv/bin/python` symlink,
plus a separately introduced NumPy 2.x dependency conflict. Both were
corrected in the gate runner/workflow without touching GAdapt itself.
See [full log-based diagnosis](../FULL_CLONE_WORKFLOW_REPAIR_2026-11-01.md).
Only a subsequent independently verified run can close the remaining gate.

## Verified real full-clone core compatibility (2026-11-01)

The final automatic follow-up [run #41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925) 
**succeeded on Python 3.12** with all **11/11** real gate steps and their SHA-256 logs independently checked. On the complete pinned Git checkout, all **341** legacy paths restored with hash verification; I41 **11 passed**, I63 **17 passed**, I64 **15 passed / 4 external PyGAD deselected**, I65 **88 passed / 3 intentional xfails**. The earlier failure sections above remain historical records. See [the complete PASS report](../FULL_CLONE_REGRESSION_SUCCESS_2026-11-01.md).

**Remaining boundaries:** this is a defined core software regression, not an end-to-end rerun of every I56/I58/I61/MBENCH experiment, nor independent OPF/PF nested-physical-call accounting or witness-model certification.
