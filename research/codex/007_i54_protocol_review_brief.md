# Brief for Codex #7 — review of the I54 protocol BEFORE freezing (read-only)

Read research/ITERATION54_PROTOCOL.md (Serbian) and, for context, research/ITERATION53_REPORT_SR.md and
research/iteration53_oracle_step.py (I54 code will reuse its Tracked, gadapt_run, cma_minimize, Dispatch).
I54 gives GAdapt the CMA-ES covariance shape from the reference run, centred at the box centre (no location leak),
to test whether missing correlation/scale learning explains the GAdapt–CMA gap on AC dispatch.

Find only problems that would make the result invalid or misleading: location leakage through the transform or the
y-box, box-clipping artefacts that could fake a gain or loss, whether a final CMA covariance at convergence is the
right geometry for a 3000-evaluation search from the box centre, determinism of re-running the reference, the WD
control, thresholds, Holm usage, budget accounting. Suggest concrete fixes. Max ~600 words, numbered, most severe
first; "no blocking issue" if none. Read-only.
