# Brief for Codex #13 — post hoc transfer sensitivity + figure applicability (read-only)

Context: your review 012 (research/codex/012_final_review_codex_answer.md) left two PARTIAL points that do not need
author decisions:
(a) Transfer interpretation (Study 4, I52): "matched-exposure and incomplete-library sensitivity analyses remain absent".
(b) Figure: "unavailable checks remain visually indistinguishable from clean negatives".

Files: research/ITERATION52_PROTOCOL.md, research/ITERATION52_REPORT_SR.md, research/results/iteration52/
(cells_<lib>.json, integrity_dispatch.json), synthetic results research/results/iteration49/, iteration50/,
iteration51/, iteration55/ (find what exists), manuscript research/paper_integrity_audit/manuscript.md §6.4,
figure script research/paper_integrity_audit/make_figure.py.

Tasks:
1. Inventory: which per-run (per-cell) flag records exist for the synthetic side of each of the 21 libraries and
   for dispatch? State exactly which sensitivity analyses are computable from ARCHIVED data only (no new runs, no
   reconstruction of missing data).
2. Propose a minimal, fully specified post hoc analysis plan (to be committed before computing, labeled post hoc,
   not a hypothesis test): e.g. (i) matched exposure = synthetic runs subsampled to the dispatch run count per
   library (exhaustive or fixed-seed resampling; say which and why), reporting the distribution of the 21-library
   agreement count; (ii) incomplete libraries = agreement among libraries with complete dispatch cells only, and
   worst/best-case bounds treating missing dispatch cells as positive/negative. Give exact definitions, denominators,
   and what result would change the paper's wording.
3. Figure: concrete proposal (from make_figure.py) to distinguish "not applicable / not available" from "0 findings"
   (hatching, grey, "n/a" glyph), compatible with grayscale print.
4. Anything in this plan that a TELO referee would call p-hacking or garden-of-forking-paths, and how to pre-empt it.
Max ~700 words. Read-only; you may run read-only Python (.venv/bin/python -I) to inspect JSON.
