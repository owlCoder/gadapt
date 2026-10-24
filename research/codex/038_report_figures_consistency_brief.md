# Brief for Codex #38 — consistency check of the I56 report skeleton and figure script vs the analysis outputs (read-only)
Files: research/ITERATION56_REPORT_SR.md (skeleton, written before results), research/iteration56_figures.py,
research/iteration56_cht_study.py (analyse() writes results/iteration56/analysis.json.gz; test.json.gz). Check that every
quantity the report/figures will use exists in those outputs with the right meaning (e.g. figure 1 per-block intervals
are a simple within-block bootstrap, NOT the protocol's cell-stratified inference — must be labelled descriptive;
heatmap means are unweighted per block; attainment curves pool blocks), that nothing in the figures could be read as a
confirmatory test beyond H56a/H56b and Holm-corrected secondaries, and that the report states the degenerate-block power
caveat correctly. List concrete text/label fixes. Max ~500 words. Read-only.
