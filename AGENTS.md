# GAdapt — active repository agent instructions

This is the **lean Python genetic-algorithm library** branch.
Read [RELIABILITY_ROADMAP.md](RELIABILITY_ROADMAP.md) and
[ARCHIVE.md](ARCHIVE.md) before starting optimization or research work.

## Primary goal
Improve the probability that GAdapt returns a **feasible, sufficiently
good solution within a fixed verified evaluation budget**, especially
reducing catastrophic worst-seed outcomes, while keeping the original
library API and defaults backward compatible until explicitly approved.

## Repository layout
- `gadapt/` — package implementation, Python 3.10+, NumPy 1.26.4.
- `tests/` — stdlib `unittest` regression and synthetic-contract tests.
- `.github/workflows/robustness-tests.yml` — automatically checks the
  package across Python 3.10, 3.11 and 3.12; **no optimizer benchmarks**.
- `archive/pre-reliability-cleanup-2026-11-04` — the entire original
  research source and original Git-tracked data; baseline commit
  `02ed2261397edb0b279f82f6e7af1271564ff579`.
  The original research sources and workflows were *moved off main*,
  **not deleted from the repository's Git history**.

## Safety and quality requirements
1. Never overwrite, fabricate, or regenerate historical research data.
2. Do not claim an algorithmic advantage from clean CI, synthetic
   tests, old archives, anecdotal runs, or a post-hoc selected result.
3. No new optimization benchmarks, objective evaluations, PF/AC/OPF,
   expensive CI, or held-out COCO without specific user authorization
   and an approved protocol, seeds, budget, baselines and metric.
4. Separate an execution that returns successfully from a run that
   reaches a problem-specific quality threshold; track feasibility,
   total true objective calls and failed/timeout cases.
5. Prefer backward-compatible, **opt-in** reliability features.
   Never silently change the original optimizer defaults, consume
   extra objective calls, or discard a validated best-ever incumbent.
6. Guard every implementation change with deterministic tests, then
   validate the standard regression suite. Keep expensive experiments
   out of automatic GitHub Actions.
7. Source control changes target only the user's `owlCoder/gadapt`
   repository; never modify upstream `bpzoran/gadapt`.
8. Historical research is **DRAFT / NO-FREEZE / NOT_ESTABLISHED**;
   M3/M5/M6/C1 scientific signoffs and original off-Git I64-R data
   are still missing. Historical original E/R/I55/I32 evidence is
   available in the archived branch.

## Architecture
- Public API: `gadapt/ga.py` (`GA.execute()`, `ga.add()`).
- Runtime: `gadapt/execution/ga_executor.py`.
- Model: `gadapt/ga_model/`; factories: `gadapt/factory/`.
- Selection/crossover/mutation/exit/immigration/cost:
  `gadapt/operations/`.
- Cost failure and constraint feasibility:
  `gadapt/operations/cost_finding/` and
  `gadapt/utils/constraint_handling.py`.
- Preserve existing user custom factories and defaults.

## Verification
```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

For numerical performance comparisons use **approved paired-seed,
fixed actual objective-budget** runs, not only generation count or wall
time. The current suite does **not** prove general optimizer reliability.
