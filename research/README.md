# GAdapt research — start here

**Updated: 2026-11-01.** [Research progress and handoff](PHD_PROGRESS.md) and [repository rules](../AGENTS.md) govern all decisions. Previous experimental results have not been rerun or revised as part of documentation cleanup.

## Navigation

- [**Studies I02–I65 by iteration**](studies/) — protocols, reports and historical code.
- [**Raw results**](results/) — existing sources unchanged; [data policy](DATA_POLICY.md).
- [**Literature and prior-art audits**](literature/) — novelty gates and negative hypotheses.
- [**Dissertation and research decisions**](overview/) · [Infrastructure domains](domains/).
- [**Research tools**](tools/) · [I64 code](i64/) · [I65 instrumentation](i65/).
- [**Mentor meeting notes**](MENTOR_MEETING_NOTES_SR.md) · [Mentor summary](MENTOR_SUMMARY_2026-10-28_SR.md) (active English translations; historical `_SR` names retained).
- [**Research reviews**](codex/) · [Thesis](thesis/) (historical Serbian drafts).
- [**Original historical materials**](legacy/) · [Compatibility tools](compat/) · [Migration map](MIGRATION_MANIFEST_2026-11-01.json).
- [**Consolidated evidence and negative results**](EVIDENCE_SYNTHESIS.md) · [**Research direction and decision gate**](RESEARCH_DECISION_2026-11-01.md) · [**Supervisor decision package**](SUPERVISOR_DECISION_PACKAGE_2026-11-01.md).
- [**English-language documentation policy**](LANGUAGE_POLICY.md) · [Per-document translation audit](LANGUAGE_AUDIT_2026-11-01.json).

## Current research status

- I64-S0/E/E3/A/R/I/I2: previously evaluated with mixed and negative findings, including orthogonal-transformation sensitivity and lack of confirmed ORPD benefit for the fixed hybrid. [Read I64 reports](studies/i64/).
- **I65: DRAFT / NO-FREEZE / COCO f21/f24 NOT_RUN.** Instrumentation tests do not establish optimizer superiority. [Read I65 documents](studies/i65/).
- Research originality and industrial reliability are **not established** by the current I65 proposals.

## Documentation migration

The 341 historical root files were moved without changes to their Git blob SHAs; curated topic views use symlinks. English is now the documentation language. Historical `_SR` suffixes may remain on English-translated active files **only for backward link compatibility**. As of this audit, **24 of 121 regular content `_SR.md` documents have complete English translations**, with Serbian originals archived unchanged. **97** Serbian original sources remain (87 historical and ten thesis manuscripts); **107** symlinks are navigational views, not additional content. The obsolete count included 20 aliases as content. No claim of full translation is made.

To reproduce an older CLI, **do not execute it from the curated Git symlink view**. Restore original root aliases first:

```sh
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

**Full-clone historical core regression now verified:** [GitHub Actions #41358768925](https://github.com/owlCoder/gadapt/actions/runs/41358768925), Python 3.12, 341 restored aliases, I41 11 PASS, I63 17 PASS, I64 15 PASS (4 external PyGAD tests intentionally excluded), I65 88 PASS / 3 expected XFAIL. See [SHA-verified full-clone report](FULL_CLONE_REGRESSION_SUCCESS_2026-11-01.md). The earlier [compatibility-gate draft](ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md) remains for historical traceability. Physical OPF/PF solver entrypoint counts and an independent witness model are **still unverified**, as documented in [ORPD accounting audit](I65_ORPD_SOLVER_CALL_BOUNDARY_2026-11-01.md).
