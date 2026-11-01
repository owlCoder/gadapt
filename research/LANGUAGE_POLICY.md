# Research documentation language and provenance policy

**English is the preferred language for all new research documents, README files, reports, issue drafts, and dissertation writing.** This rule applies from 2026-11-01 forward and does not modify frozen scientific data or pre-registration.

## Migration status

- The [language audit](LANGUAGE_AUDIT_2026-11-01.json) finds **141 canonical `_SR.md` documents** plus **107 symlink views** that point to existing historical content. Views are not independent duplicate research documents.
- **14 documents have been fully translated into English on their existing paths**, with their earlier Serbian Git blobs saved unchanged under `research/archive/serbian_originals/`. This approach preserves links from frozen protocols, reviews and progress logs. The legacy `_SR` basename remains for backward compatibility only; the **content** is English.
- **127 canonical documents remain untranslated Serbian originals.** They are **not** claimed to have an English counterpart. Do not delete them or replace them with a short English abstract pretending to be a complete translation. They remain available in legacy/thesis/current historical files.
- The navigational Markdown files in `research/studies/` have English descriptions; the links retain their frozen historical names. English-only navigation does not mean every linked historical file has been translated.

## Rules for future translations

1. Record the original Git blob SHA and original file path; preserve the exact original blob (and location) in `research/archive/serbian_originals/` or use its existing immutable `research/legacy/flat/` location.
2. Preserve **all** numeric results, metrics, hypothesis decisions, uncertainty intervals, tables, negative findings, caveats, formulas, and relative links. State `TRANSLATION`, not `REPLICATION` or `NEW RESULT`.
3. Convert the active document **in place** where links from frozen reports would otherwise break, even if its historical basename ends with `_SR`. Avoid creating `_EN` copies alongside the original: one active content path is preferred.
4. Treat thesis and mentor documents as scientific sources: a translation may clarify wording, but must not silently reconcile contradictions or alter historical statuses.
5. Do not remove existing Git symlink views or historic Markdown references solely to make counts look smaller. A content-hash and reference audit is required first.
6. Keep `PHD_PROGRESS.md` append-only for its historical handoff. New entries and English executive guidance should be in English; retroactively translating its historical content could destroy provenance.
7. Before claiming translation is finished, require `untranslated_sources = 0` in the auditable manifest **and** a full review of non-`_SR` Serbian-language documentation.

## Current result

This is a **partial, explicitly measured language cleanup**. Nothing was rerun; raw data, `gadapt/`, and upstream remain unchanged. [I64 results index](INDEX.md) and [study navigation](studies/) remain the entry points.
