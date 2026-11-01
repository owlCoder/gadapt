# GAdapt research — start here

**Updated: 2026-11-01.** [Research progress and handoff](PHD_PROGRESS.md) and [repository rules](../AGENTS.md) govern all decisions. Previous experimental results have not been rerun or revised as part of documentation cleanup.

## Navigation

- [**Studies I02–I65 by iteration**](studies/) — protocols, reports and historical code.
- [**Raw results**](results/) — existing sources unchanged; [data policy](DATA_POLICY.md).
- [**Literature and prior-art audits**](literature/) — novelty gates and negative hypotheses.
- [**Dissertation and research decisions**](overview/) · [Infrastructure domains](domains/).
- [**Research tools**](tools/) · [I64 code](i64/) · [I65 instrumentation](i65/).
- [**Mentor meeting notes**](MENTOR_MEETING_NOTES_SR.md) · [Mentor summary](MENTOR_SUMMARY_2026-10-28_SR.md) (both currently Serbian sources).
- [**Research reviews**](codex/) · [Thesis](thesis/) (historical Serbian drafts).
- [**Original historical materials**](legacy/) · [Compatibility tools](compat/) · [Migration map](MIGRATION_MANIFEST_2026-11-01.json).
- [**Consolidated evidence and negative results**](EVIDENCE_SYNTHESIS.md) · [**Research direction and decision gate**](RESEARCH_DECISION_2026-11-01.md).
- [**English-language documentation policy**](LANGUAGE_POLICY.md) · [Per-document translation audit](LANGUAGE_AUDIT_2026-11-01.json).

## Current research status

- I64-S0/E/E3/A/R/I/I2: previously evaluated with mixed and negative findings, including orthogonal-transformation sensitivity and lack of confirmed ORPD benefit for the fixed hybrid. [Read I64 reports](studies/i64/).
- **I65: DRAFT / NO-FREEZE / COCO f21/f24 NOT_RUN.** Instrumentation tests do not establish optimizer superiority. [Read I65 documents](studies/i65/).
- Research originality and industrial reliability are **not established** by the current I65 proposals.

## Documentation migration

The 341 historical root files were moved without changes to their Git blob SHAs; curated topic views use symlinks. English is now the documentation language. Historical `_SR` suffixes may remain on English-translated active files **only for backward link compatibility**. As of this audit, **14 of 141 canonical `_SR.md` documents have complete English translations**, with Serbian originals archived unchanged. No claim of full translation is made.

To reproduce an older CLI, **do not execute it from the curated Git symlink view**. Restore original root aliases first:

```sh
python research/compat/restore_legacy_paths.py --verify
python research/compat/restore_legacy_paths.py --apply --verify
```

Full historical regression after migration has not yet been demonstrated. [Compatibility gate report](ITERATION65_MIGRATION_COMPAT_GATE_2026-11-01_SR.md) (Serbian, not yet translated).
