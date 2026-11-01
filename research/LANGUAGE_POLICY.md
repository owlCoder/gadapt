# Research documentation language, deduplication and provenance

English is the preferred language for all **new** active research documentation, doctoral writing and summaries. Old research records remain independently verifiable evidence rather than being rewritten to make outcomes appear positive.

## Corrected audit (2026-11-01)

| Classification | Git objects | Meaning |
|---|---:|---|
| Actual canonical `_SR.md` content documents | **121** | Regular Git blobs outside `archive/` and curated view folders |
| Fully translated on their original active paths | **24** | English active content with byte-identical Serbian source under `archive/serbian_originals/` |
| Untranslated actual documents | **97** | **87** historical source reports in `legacy/flat/`, **10** thesis drafts in `thesis/` |
| Active-root aliases under `legacy/flat/` | **20** | Git symlinks back to active root sources, not untranslated content |
| Curated navigational aliases | **87** | Git symlinks pointing at underlying files, not additional science |
| All tracked `_SR.md` symlinks | **107** | 20 root aliases + 87 navigation views |

This corrects the v1 mistake where 20 symlinks were counted as 20 untranslated documents. The [unaltered v1 audit](archive/LANGUAGE_AUDIT_V1_2026-11-01.json) and [corrected v2 audit](LANGUAGE_AUDIT_2026-11-01.json) retain path/mode/SHA provenance. No two actual canonical content documents in the audited group share a Git blob SHA. This does not rule out *semantic* overlap.

## Canonical writing and linking

1. Keep a single English [evidence synthesis](EVIDENCE_SYNTHESIS.md) and an explicit [research decision](RESEARCH_DECISION_2026-11-01.md) for cross-study claims. Keep frozen reports untouched, including negative, STOP and inconclusive findings.
2. For a **full** translation, preserve all numeric results, statistical uncertainty, formulas, hypotheses, negative findings and limitations; archive the exact Serbian blob. A shortened English review is a distinct synthesis, **never** a full translation.
3. Retain historical `_SR` path names for compatibility with frozen protocols, citations and scripts. The suffix does not prove the language of the current file. Avoid mass-renaming analysis-generated reports without an output-path and link audit.
4. Git symlinks are navigational aliases, not duplicate scientific content. Never delete solely to reduce a count of filenames.
5. Restore legacy `research/<name>.py` entrypoints using [compatibility instructions](compat/) before executing them in a complete clone. Never execute historical code directly from `studies/` or `legacy/flat/` when it uses `__file__`-dependent paths.
6. `PHD_PROGRESS.md` is append-only historical provenance. New handoffs use English; old records remain as originally written.
7. Neither documentation cleanup nor previously reported ECDF/CVaR measurements demonstrate original optimizer novelty or industrial readiness.

## Untranslated content

The 87 historical reports remain in [legacy/flat/](legacy/flat/), browsable by [studies/](studies/); ten thesis sources remain in [thesis/](thesis/) with an English chapter map. These sources are intentionally retained, **not mislabeled as translated or deleted**. Their English summary is a navigational/evidence product, not a substitute for independent reanalysis.

Research status: I65 `DRAFT / NO-FREEZE / NOT_RUN`; `novelty not established`.
