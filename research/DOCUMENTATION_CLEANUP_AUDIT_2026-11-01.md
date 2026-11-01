# Documentation and scientific-provenance cleanup audit — 2026-11-01

**Scope:** `owlCoder/gadapt`, starting at `ba1fc60138b6c5e88739549e09c2ac5820392231`. This audit documents **nonexperimental repository cleanup**, consolidation of historical results, and a new **methods/novelty decision record**, not new optimizer performance.

## Verified tree-level facts

| Invariant | Result |
|---|---|
| Historical migration content and view paths | **PASS:** all 341 canonical relocated files match the original Git blob SHA; all 341 curated paths are present as Git symlinks |
| Original empirical output archive | **PASS:** all 2,718 tracked blobs under `research/results/` including the documentation README were checked for identity except the intended English README rewrite; the **2,717 actual output blobs** are unchanged |
| Historical Serbian research reports | **PASS:** all 87 regular legacy `_SR.md` documents remain unmodified, plus ten regular thesis sources |
| Active translated reports and preserved Serbian originals | **PASS:** 24 English active documents retain their active content SHA, with original source blobs preserved at recorded archive paths |
| Optimizer core | **PASS:** 226 `gadapt/` tracked blobs unchanged |
| Research implementation | **PASS:** 42 `research/i64/` and ten `research/i65/` tracked blobs unchanged |
| Navigation and compatibility | English READMEs; legacy restoration scripts/tests were not modified; no branch migration or workflow change |
| New optimization experiments | **0**, no new COCO f21/f24 results, no preregistration FREEZE |
| Full migrated-clone Python regression | **NOT_TESTED** (no complete checked-out environment with locked dependencies in this session) |

## Correction to the original language audit

The earlier language inventory conflated **20 Git symlink aliases** under `research/legacy/flat/` with untranslated content documents. Correct count from tracked Git file modes: **121** actual `_SR.md` content documents, of which **24** have a complete English translation and **97** remain original Serbian (87 historical reports, ten thesis manuscripts). The total number of `_SR.md` symlinks is **107**: 20 legacy aliases and 87 navigational views. A full semantic-duplicate check was not performed; however, no two regular canonical `_SR.md` content files have identical Git blob SHA. The original v1 audit is archived unchanged at [v1](archive/LANGUAGE_AUDIT_V1_2026-11-01.json), with a corrected, object-mode-aware [v2](LANGUAGE_AUDIT_2026-11-01.json).

**Source documents were not deleted or hidden.** The user authorized merging and summarizing historical results; this was implemented as a [single English evidence synthesis](EVIDENCE_SYNTHESIS.md), an [English index of 87 originals](legacy/flat/INDEX_EN.md), and a [thesis chapter map](thesis/). English synopsis documents **do not impersonate full translations**.

## Newly consolidated navigation

- [Research homepage](README.md)
- [Evidence synthesis: I41–I65, with STOP and negative results](EVIDENCE_SYNTHESIS.md)
- [Independent prior-art/method decision record](RESEARCH_DECISION_2026-11-01.md)
- [English index of original historical reports](legacy/flat/INDEX_EN.md)
- [Thesis draft map](thesis/)
- [Language policy and v2 SHA/mode inventory](LANGUAGE_POLICY.md)
- [Raw outputs index](results/)
- [Historical CLI restore instructions](compat/)

All freshly authored navigation pages were checked for resolvable repository-relative Markdown links against the staged Git tree. **No broken local links found in the 13 newly edited or added principal indexes/syntheses.** This is not a claim of validating every archived historical Markdown link.

## Scientific continuation and gate

External publisher/project references supporting the new [decision memo](RESEARCH_DECISION_2026-11-01.md) include COCO performance assessment (2016), EAF interpretation (DOI `10.1109/TEVC.2024.3462758`), algorithm footprints (DOI `10.1016/j.swevo.2025.101895`) and benchmark methodology (DOI `10.1016/j.future.2024.05.021`). **Crossref API was not independently queried for these references in this phase**; see the exact links in the decision memo. No original algorithm novelty can be claimed from these sources.

**Immediate next independent gate:** use a complete locked checkout to run read-only SHA/layout checks and inexpensive I41/I63/I64 compatibility tests, review I65's physical-attempt/witness and simulator-oracle interfaces, and secure an explicit dissertation-scope decision. `I65 novelty not established`; `NO-FREEZE`; `NOT_RUN`. The 12,000-call prospective COCO protocol has not been launched.
