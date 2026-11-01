# Research directory reorganization — 2026-11-01

**Status:** nondestructive migration of Git paths, not a new scientific study.

| Measure | Before | After |
|---|---:|---:|
| Files directly under `research/` | 379 | 38 before adding navigation indexes |
| Historical files moved without changing bytes | — | 341 |
| Topic/iteration symlink views | — | 341 |
| Generated `__pycache__` artifacts removed from Git | 64 | 0 under `research/` |
| Original raw output files in `results/` | 2717 | 2717 unchanged |

**Verifiable at the Git tree level:** the moved canonical files have the same Git blob SHA as before relocation. Raw experiment outputs and active I64/I65 reports were not relocated or recomputed by this migration. All original and destination paths are in [MIGRATION_MANIFEST](MIGRATION_MANIFEST_2026-11-01.json).

**Limitations:** original direct entrypoints `research/<name>.py` are not present without the opt-in local `compat --apply` restoration. This is a deliberate choice to keep the root navigable, but the full regression suite has not been executed. Historical prose links to explicit root paths and archived manifests may require an environment that restores the original paths. Frozen content-addressed provenance must not be silently revised. Expensive CI or confirmatory experiments must not be triggered as part of cleanup.

**Next gate:** independent offline replay of critical I64/I63 scripts in locked environments before considering any I65 implementation work.
