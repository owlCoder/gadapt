# Full-clone Python 3.12 regression: independently verified PASS

**Date:** 2026-11-01. **Repository:** `owlCoder/gadapt`, `main`.  
**GitHub run:** [#41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925), `status=completed`, `conclusion=success`.  
**Exact tested commit:** `3c8ac0ee5853bcc098c9939b87a6e389f3b9733d`.  
**Actual environment:** GitHub Actions Ubuntu, full Git checkout including pre-migration ancestry, **CPython 3.12** virtualenv, `numpy==1.26.4`, `scipy==1.16.3`, `PYPOWER==5.1.19`, `cma==4.5.0`, `pytest==9.2.0`, `hypothesis==6.170.14`. `pip check` succeeded.

## Source evidence and digest validation

Workflow artifact: [gadapt-pypower-full-clone-41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925/artifacts/13104785848), compressed ZIP SHA-256:

`29bc26493dd1fd088d20e9391e1ba63cfd61df56ccea511fda1d9786c65905c8`

The original archive's `gate.json` was parsed locally. Every entry in the 11-step allowlisted sequence had `status=PASS` and exit code 0, and its recorded `log_sha256` was independently recalculated from the corresponding actual archived log bytes: **11/11 match**. This checks the chain of evidence for *the actual full repository*, not a replay of synthetic fixture data. No synthetic claim is substituted for real historical tests.

## Actual tests, with coverage limitations

| Step | Actual result |
|---|---|
| Synthetic migration + fail-closed driver tests | **PASS** |
| Original source, canonical blob and curated view integrity | **341/341 PASS** |
| Old-root symlink hash preflight | **341/341 PASS**, dry-run |
| Restore historic CLI paths | **341 newly created**, no errors |
| Repeat restore for idempotence | **341 existing, 0 newly created** |
| `from gadapt.ga import GA` using **actual .venv** | **PASS** |
| Installed environment freeze and dependency validation | **PASS** |
| `research/test_iteration41_certified_temporal_rows.py` and `research/test_iteration41_property_falsification.py` | **11 passed** |
| `research/test_iteration63_replication.py` | **17 passed** |
| `research/i64/test_e_common.py` and `research/i64/test_e_algos.py` | **15 passed, 4 intentionally deselected** (`-k 'not pygad'`) |
| Full `research/i65` pytest collection | **88 passed, 3 expected xfails** |

All three I65 expected negatives persist, with their original reasons: old stagnation monitor permits nonmonotone timestamps; old I64 budget undercounts raised evaluator attempts and snapshots mutated candidates after evaluation. Do **not** erase these negatives, edit frozen references or claim a new optimizer advantage.

The I64 `cma` test emitted one benign warning that matplotlib plotting was unavailable; it did not affect the comparison-free unit-test outcome. The four `PyGAD` cells requiring external `MBENCH` source are **EXCLUDED / NOT_TESTED**, not passed. This is a **defined core historical test gate**, not a claim that all I56/I58/I61 scripts, all earlier experimental seeds, every real AC simulator and external model are reproducible.

## Failure-to-resolution record

1. [#41357664531](https://github.com/owlCoder/gadapt/actions/runs/41357664531) exposed a `.venv/bin/python` symlink-dereferencing bug: the runner used system Python and GAdapt import failed with missing NumPy. The pip step also replaced GAdapt's pinned NumPy with incompatible NumPy 2.x.
2. [#41358375382](https://github.com/owlCoder/gadapt/actions/runs/41358375382) verified the fix: real GAdapt import and I41 (11 PASS); I63 showed that the environment omitted a needed `pypower` dependency (16 pass, 1 failure at scenario construction).
3. [#41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925) pinned NumPy/SciPy and installed `PYPOWER==5.1.19` in the correct Python 3.12 virtualenv. **All 11 stages PASSED** with SHA-verified log archive.

No automatic `robustness-tests.yml` push benchmark was triggered as a side effect of these repair commits (`[skip ci]`). A limited one-shot `workflow_run` listener and authorized reruns were used to independently execute the latest corrected commits. No held-out COCO f21/f24 or confirmatory optimizer study was run.

## What the PASS does *not* establish

The core regression certifies the exact included software and restored path tests on the recorded commit. It does not prove:

- that the I65 stagnation-switch policy is scientifically new or has been approved; **novelty not established, NO-FREEZE / NOT_RUN**;
- that objective callback count equals the total number of **physical AC power-flow/OPF solver calls** (including setup and witness or failed nested calls);
- an independent witness *model* instead of a different Python function using the same PYPOWER model;
- the scientific performance of GAdapt relative to DE/CMA/other methods on unrun COCO cells or fresh ORPD benchmarks.

The next responsible milestone is [the ORPD physical-solver accounting boundary review](I65_ORPD_SOLVER_CALL_BOUNDARY_2026-11-01.md), followed by a truly independent oracle and supervisor scope/novelty decisions. **No additional expensive optimization experiments are authorized by the core regression PASS.**
