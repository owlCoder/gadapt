# Deep repository cleanup — archival handoff (2026-11-04)

**Pre-cleanup exact snapshot (complete):**
[Git commit `02ed2261397edb0b279f82f6e7af1271564ff579`](https://github.com/owlCoder/gadapt/commit/02ed2261397edb0b279f82f6e7af1271564ff579)

**Preserved full-content branch:**
[`archive/pre-reliability-cleanup-2026-11-04`](https://github.com/owlCoder/gadapt/tree/archive/pre-reliability-cleanup-2026-11-04)

The original tracked snapshot contained 4,543 files (approximately
345 MB of uncompressed Git tree blob contents). Of them 4,219 original
`research/` files occupied approximately 344 MB, including the
620 I55 A-process NPZ originals, historical E/R/I2 reports, I32/I7/I9
source/witness evidence, frozen experimental protocols, original negatives,
and 165 I65 archive-review inputs. The older checkout also contained
76 workflow files, 112 committed Python `__pycache__`/`*.pyc` blobs,
and a small research-specific `.agents/` directory.

**The active `main` checkout is now oriented to the actual GAdapt
package and its standard-library regression tests.** Historical research
data, original source code, reports and workflows are retained byte-for-byte
in the archive branch, and in the repository's existing Git history.
There is no claim that these original sources became unnecessary to
reproducible science: they remain essential to archival research.

Restore the *historical* source in a separate checkout, never overwrite
the active reliability branch:

```sh
git fetch origin archive/pre-reliability-cleanup-2026-11-04
git worktree add ../gadapt-research-archive \
  origin/archive/pre-reliability-cleanup-2026-11-04
```

Use `git show 02ed226:research/...` or the archive branch to inspect
frozen evidence, source manifests and negative results. **Old research
workflows do not run automatically on the new `main`.** Do not transplant
them into the library workflow or run physical/optimization benchmarks
without explicit research authorization and a prospectively approved
protocol.

The cleanup modifies no `gadapt/**/*.py` implementation or tracked
package-level test source. It is not a reliability improvement by itself.
Next work belongs to [the reliability-first roadmap](RELIABILITY_ROADMAP.md).

**Important limitation:** removing history from the active Git *tree*
drastically reduces the working checkout and new `main` archive size,
but does **not** rewrite Git history or necessarily shrink a full clone's
`.git` object store. The archived originals remain recoverable.

Scientific status: `DRAFT / NO-FREEZE / NOT_ESTABLISHED`.
