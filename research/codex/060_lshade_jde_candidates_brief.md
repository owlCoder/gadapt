# Brief for Codex #60 — stronger baseline: maintained L-SHADE / jDE implementations for mixed-integer black-box (read-only, web)
Context: Codex 052 rank 2 (research/codex/052_thesis_outcome_map_codex_answer.md): a validated L-SHADE/jDE competitor plus a
tuned penalty is needed for wider practical claims; I57 (research/ITERATION57_PROTOCOL.md, ITERATION57_REPORT_SR.md) excluded
them because implementations would need separate validation. Environment: Python 3.14, NumPy 2.5, SciPy 1.18 (.venv);
budgets 3000-10000 evaluations; discrete grid controls (integer indices 0..R-1), 9-77 variables; cost = AC power flow.
Using live search: list maintained Python implementations of L-SHADE, jSO, jDE, (and Tanabe 2024 recommendations for
mixed-integer, doi 10.1145/3638529.3654019) — package, version, last release date, license, whether it supports a hard
evaluation budget, integer handling (rounding/repair), seeding, pip-installability on Python 3.14 (wheels / pure Python), and
whether it reproduces published CEC results (any test suite). Recommend ONE with justification, and a validation plan
before use (e.g. reproduce reference results on 2-3 CEC functions within tolerance; budget-exactness wrapper like I57; integer
decoding identical to I57). Alternatively: is a ~150-line own L-SHADE implementation validated against the authors' C++/MATLAB
reference safer? Verify DOIs (Tanabe & Fukunaga 2014 L-SHADE, Brest 2006 jDE) on doi.org/Crossref. Max ~700 words.
