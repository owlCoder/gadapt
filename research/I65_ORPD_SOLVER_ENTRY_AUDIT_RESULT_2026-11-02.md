# I65 — measured PYPOWER solver API-entrypoints, full GitHub-run evidence

**Date:** 2026-11-02.  
**Status:** **PASS — bounded development-only solver-API-entrypoint accounting smoke; independent-model physical oracle NOT_ESTABLISHED.**  
**Run:** [GitHub Actions #41385833963](https://github.com/owlCoder/gadapt/actions/runs/41385833963), `completed / success`.  
**Code HEAD:** `9f94c0aaaf575db4e346f80033680882ee11770e`.  
**Artifact:** [i65-orpd-solver-entry-audit-41385833963](https://github.com/owlCoder/gadapt/actions/runs/41385833963/artifacts/13115008235), ZIP SHA-256 `a52b78502df58423c6ceb50f5118fb6012d2e352ff2bfc1ed2fb6bcf3fdabb5a`.

## 1. Preregistered narrow question, no optimizer experiment

The [pre-run phase/call specification](I65_ORPD_SOLVER_ENTRY_AUDIT_2026-11-02.md) predicted, for historical I58 development scenario `case30`, `j=1`, `resolution=17`, one admitted candidate and one independent Python checker:

| Phase | Expected `runopf` entries | Observed `runopf` | Expected `runpf` entries | Observed `runpf` |
|---|---:|---:|---:|---:|
| Scenario setup | 1 | **1** | 0 | **0** |
| Candidate search | 0 | **0** | 1 | **1** |
| I58 witness | 1 | **1** | 1 | **1** |
| **Total** | **2** | **2** | **2** | **2** |

The exact observed ordered event trace is:

```json
[
  {"index":1,"kind":"runopf","outcome":"returned","phase":"setup"},
  {"index":2,"kind":"runpf","outcome":"returned","phase":"search"},
  {"index":3,"kind":"runopf","outcome":"returned","phase":"witness"},
  {"index":4,"kind":"runpf","outcome":"returned","phase":"witness"}
]
```

The historical `Evaluator.calls` counter recorded **1** admitted search-candidate attempt while the narrowly instrumented PYPOWER API saw **4** total entries (two OPF + two PF including setup and witness). These are *different counting domains*: four solver API entries are not four candidate evaluations or internal Newton iterations.

The smoke reported `witness_valid_vector=true`, `witness_converged=true`. It did **not** test or assert `feasible=true` or validated numerical agreement against an independently implemented AC model. The witness uses the same PYPOWER implementation as the original evaluator.

## 2. Independent archived-evidence verification

Downloaded the original ZIP archive. Its computed SHA-256 matched the GitHub artifact digest exactly. Verified the four individual file digests from `hashes.sha256` against the **actual bytes**:

| Artifact file | Verified SHA-256 |
|---|---|
| `restore.log` | `b30a798b89b330808732f7473c8db60eeba02c2665c0ed53de7ebcf6f7f7278a` |
| `unit.log` | `e7fc9d7592774887b40c26a56b30d3f96190f56a8a6fef6454195508d738c78b` |
| `smoke.json` | `e3aa8f3a040a30de92900d816a07d0504e4026c7036c1f9d4c3a096bf0af1ee0` |
| `commit.txt` | `4d29680ae88f16398e9f0ebbdc15625d91bfe72b608fd5ddbc73cfe8290124e5` |

**4/4 log hashes PASS**, ZIP hash PASS. Recomputed the deterministic SHA-256 of the `audited_api_entries` object after removing its hash field, exactly using the recorded `sort_keys=True`, compact UTF-8 JSON serialization: `aea924d01ef9c9c99b6fb2f9d369b014c7681ef2bc520d93dfc4dcb304aa1ec8`, **match**.

The original `smoke.json` source Git blobs matched the known committed frozen modules:

| Source | Git blob |
|---|---|
| I56 `iteration56_orpd.py` | `43f2f279f7e6362250dc9277e58e0d939a98c12f` |
| I56 `iteration56_cht_study.py` | `462e08368b70d869015d1056366964b4d10b92e1` |
| I58 `iteration58_validation.py` | `9747faea9c31526a163bd8439c74708214c07a3c` |
| Research-only `orpd_solver_entry_audit.py` | `241412cf61d3e210a66e755be873d040c5c45b6f` |

The observed `restore.log` said `checked=341; planned=341; created=341; existing=0; mode=apply; hash_verification=enabled`. The `unit.log` recorded **8/8 PASS**, including exception-before-return accounting, API restoration, deterministic serialization and invalid/nested phase rejection. Actual runtime: Python `3.12.15`, NumPy `1.26.4`. The action's install step used `PYPOWER==5.1.19` with a successful `pip check`.

## 3. What is proven; what remains unproven

**Proven for the observed development case only:** the transparent wrapper counted **exactly the four visible `pypower.api.runopf/runpf` entrypoint invocations**, split as specified by phase and including the separate witness reconstruction. The mock-only unit tests demonstrate intended recording behavior even when the entrypoint raises an exception.

**NOT proven:** PYPOWER's internal nonlinear solver iterations/subsolves, all calls invoked from a different imported alias or during asynchronous/parallel execution, all startup/setup costs across arbitrary real runs, full physical B-cost equivalence, independent-implementation AC witness, numerical constraint feasibility on the candidate, or a new optimizer methodology. It would be wrong to infer that `B=12,000` search candidates represents at most 12,000 total solver entrypoints once setup and checking are included.

**NEXT STEP:** obtain reviewed independent-model feasibility and objective checks (not another function calling the same PYPOWER backend), define and freeze a scientifically explicit accounting convention for scenario setup, failures, internal subsolves and witness; if permitted, test this separately on a non-held-out case. Existing candidate C remains **novelty not established / NO-FREEZE / held-out COCO NOT_RUN**. No historical source, experimental result, default GAdapt algorithm or frozen protocol was modified.
