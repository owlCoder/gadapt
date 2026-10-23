# Brief for Codex #9 — independent peer review of the integrity-audit manuscript (read-only)

Act as a demanding reviewer for ACM Transactions on Evolutionary Learning and Optimization (TELO).
Manuscript: research/paper_integrity_audit/manuscript.md (+ figure script make_figure.py in the same folder).
Supporting reports: research/ITERATION49..52_REPORT_SR.md (Serbian), research/H4_PRIOR_ART_AUDIT_SR.md,
raw results under research/results/iteration49..52/.

Deliver a referee report: summary (3 lines), recommendation (accept / minor / major / reject) with reason,
MAJOR issues (each: problem, where, why it matters, concrete fix), MINOR issues, and a check list of every
numerical claim in the abstract against the raw JSON (state which ones you verified and how).
Be strict on: novelty claim vs prior art, statistical claims (CIs, denominators), whether the definitions of the
integrity classes are reproducible from the text alone, threats to validity, and any claim that overreaches the data.
Max ~1500 words. Read-only: you may run read-only Python to recompute numbers; do not edit files.
