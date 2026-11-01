# GAdapt — full-checkout Python 3.12 core regression execution gate

**Date:** 2026-11-01. **Source state reviewed:** `main` at `13145d5dc437aee76d4d4f02d96a0f24fbb6568a`.
**Status:** reproducible **full-clone execution path prepared but NOT RUN on a real full checkout**. 
**Scope:** cheap migration compatibility, GAdapt import and historical I41/I63/I64/I65 tests. No scientific optimizer benchmark, freeze, held-out COCO, CI dispatch or change to `gadapt/`.

## Precisely verified in this session

- Tried `git ls-remote https://github.com/owlCoder/gadapt.git HEAD`: **failed** with `Could not resolve host: github.com`. Local checkout is only the previous I65 research-only directory, without `.git` or actual migrated historic files. Local installed Python: **3.13.5 only** (`uv python list --only-installed`); no Python 3.12, `hypothesis`, `cma` or `cocoex`. Thus no defensible full-repository regression verdict is available **yet**.
- Re-executed tracked, SHA-verified I65-only pytest files under 3.13: **88 passed, 3 xfailed**; all known reference negatives preserved. A separate earlier run of the local test glob reported 101 passes solely because it also included 13 untracked exploratory tests; those 13 are **not** attributed to the tracked I65 suite.
- Reconstructed the exact original committed compatibility tools locally: `restore_legacy_paths.py` Git blob `6908ce90ec1edb73ed7821f4ba8820617213bace`; `check_migration_git_tree.py` Git blob `cf4d7195d1687965a8df7609a19088ca91bb2ac1`.
- **10/10 new cheap synthetic tests PASS** (two real-Git test cases + eight orchestration tests, approximately 7 seconds). A disposable actual Git repo with **341 synthetic historic files** passed SHA/mode/view-tree verification, 341-file dry-run, **341 physical symlink restorations**, and idempotent second restore with `existing=341, created=0`. With **one corrupted canonical file among 341**, all aliases were withheld. Synthetic files were *not* historical I41/I63 data: this checks tool safety and scale, not historical runtime.
- Actual terminal log: SHA-256 `e0ca1647ff5ed69415536c62fc6795a10c9505e578cfeb11f7cc569191c1d9a8`, generated as `gadapt_full_gate_offline_validation_2026-11-01.txt` in the working artifact directory. The log includes full commands, local environment, 10-test and tracked I65 output; this log is evidence of only the scoped local run.

## A reproducible, bounded full-checkout runner

Added [`research/compat/run_full_clone_gate.py`](compat/run_full_clone_gate.py), and two synthetic regression modules:
[`test_full_alias_scale.py`](compat/test_full_alias_scale.py) and
[`test_full_clone_gate.py`](compat/test_full_clone_gate.py).

**Default operation is read-only**. It requires a real clean `main` checkout, complete Git ancestry including the pre-migration source commit, and a verified **Python 3.12 interpreter**. With `--run`, it performs an allowlisted 11-step sequence: compatibility synthetic tests, committed tree gate, 341-path hash preflight, opt-in symlink restoration, idempotence, GAdapt GA import, `pip freeze`, historical I41, I63, I64 core and full I65 pytest collection.

Each step has a **120-second hard timeout**, fail-fast classification, exact command/output and individual SHA-256 log. `gate.json` reports exit codes and the unchanged Git HEAD. It rejects missing source history, wrong Python, a dirty tracked checkout, wrong alias counts, skipped required tests, preflight mismatch, repeated reports, in-repo report destinations and timeouts. **No new optimization search**, hidden extra physical calls, automatic workflow dispatch or installation is performed by the runner.

The I64 core run intentionally uses `-k 'not pygad'`: external-mentor `MBENCH` PyGAD cases are explicitly *excluded*, not declared passed. These are separate optional compatibility tests requiring the external mentor code. This gate therefore means **local core regression**, *not* every optional external algorithm or the actual ORPD/COCO solver integration.

### How to execute in a real complete clone

```sh
# from the repository root on main, in a clean full-history checkout
python research/compat/run_full_clone_gate.py --python .venv/bin/python
python research/compat/run_full_clone_gate.py --python .venv/bin/python \
  --run --report-dir /tmp/gadapt-full-clone-gate
```

Alternatively, a new **manual-only** workflow
[`.github/workflows/research-full-clone-gate-manual.yml`](../.github/workflows/research-full-clone-gate-manual.yml)
performs `actions/checkout` with `fetch-depth: 0`, sets up Python 3.12, installs just the test dependencies, runs this script and uploads immutable-enough SHA-labeled logs. This workflow has **only** `workflow_dispatch`, **no** push, PR or schedule trigger, and an overall 15-minute job cap; **it has not been dispatched in this session**. Installing dependencies inside that expressly user-dispatched job is not an I65 optimization experiment.

To complete this gate, someone must **actually run** the manual workflow or the local Python-3.12 command and examine its resulting `gate.json` plus SHA logs. A mock runner's `PASS` in synthetic tests cannot stand in for a full-clone execution.

## Scientific NO-GO and remaining independent physical accounting

This gate does **not** instrument the internal calls of a real ORPD power-flow solver, certify independence of a separate witness model, install official COCO f21/f24 or demonstrate I65 candidate-C originality. Even a future full-clone `PASS` will settle only the **historic software compatibility** portion of the research gate. Explicitly instrument each underlying physical solver invocation, including failures, before claiming B physical calls; a Python objective wrapper can only count its own invocations. This needs a separate reviewed integration and independent oracle, not an extrapolation from the synthetic tests.

**Decision:** **PASS** for synthetic 341-scale migration tool behavior and existing isolated I65; **NOT_TESTED** for real full-clone Python 3.12 regression and physical nested solver accounting. `novelty not established / NO-FREEZE / COCO NOT_RUN`.
