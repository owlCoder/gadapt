Read-only inspection completed; no files changed and no sensitivity outcomes computed.

**1. Archived inventory.** Counts below are successful/scheduled cells; GAdapt is excluded throughout.

| Synthetic source | Libraries and coverage |
|---|---|
| I49 `integrity_audit.json` contains individual `cells`; I51 `d3x.json` contains keyed D3/D3x records | pymoo, DEAP, PyGAD, geneticalgorithm, Optuna, PySwarms, cma, SciPy DE: **30/30 each**; Nevergrad: **20/30**. I49/I51 cell keys and failure locations match exactly. |
| I50 `cells_<lib>.json` contains individual flags, including D3/D3x | baybe, bayes_opt, cmaes, emukit, EvoloPy, evotorch, evox, GFO, NiaPy, scikit-opt, SMAC: **30/30 each**; bofire: **28/30**. |
| I55 `cells_<lib>.json` | All 21 libraries: **30/30 valid each except Nevergrad, 20/30**; 620 retained traces. D3/D3x-same/D3x-diff are separate fields. |

I52 has individual flags in `cells_<lib>.json`: **15/15 for 18 libraries**, Nevergrad **5/15**, bayes_opt and bofire **10/15 each**; **295/315 overall**. Successful cells have available D3x comparisons. `integrity_dispatch.json` supplies aggregates. The failed-environment archive supplies no additional measured exposure.

Thus archived data support matched-cell-count concordance, complete-library restriction, missing-cell bounds, confusion matrices and class-specific recurrence. They do **not** support recovering failed cells, reproducing historical dispatch classifications from full traces, or matching objectives/dimensions. I55 supports a separate corrected-synthetic sensitivity, not controlled hash-seed evidence for dispatch.

**2. Proposed specification to commit before calculation.** Label everything “post hoc descriptive sensitivity; not a hypothesis test”; preserve the original H52 result.

Use \(K=\{\mathrm{C3,C4,C5,R1,R2,R3,D2,D3,D3x}\}\). A cell is positive iff any available flag in \(K\) exceeds zero. Exclude C1/C2; unavailable checks are not verified negatives. For Study 1, join I49 flags with **I51 D3x only** by `(library,function,d,seed)`; retain jointly successful cells. This is a composite historical record, not one execution.

For library \(l\), let \(n_l\) be successful synthetic cells, \(k_l\) positive synthetic cells, \(m_l\) successful dispatch cells, and \(D_l\) observed dispatch positivity.

- **Matched exposure:** independently choose a uniform subset of \(m_l\) synthetic cells without replacement. Compute the **exact exhaustive distribution analytically**, avoiding seeds and Monte Carlo error:
  \[
  q_l=P(S_l=0)=\binom{n_l-k_l}{m_l}/\binom{n_l}{m_l}.
  \]
  Agreement probability is \(q_l\) when \(D_l=0\), otherwise \(1-q_l\). Convolve the 21 Bernoulli distributions; report all probabilities for agreement count \(A=0,\ldots,21\), support, expectation and descriptive mass \(P(A\ge17)\). This matches successful-cell counts only.
- **Incomplete libraries:** retain the original full-archive synthetic status \(S_l\). Report agreement `/18` among libraries with all 15 dispatch cells completed, alongside its confusion matrix and positive recurrence denominator \(\sum_{\text{complete}}S_l\).
- **Missing-cell bounds:** define \(D_l^-=D_l\), \(D_l^+=D_l\lor(m_l<15)\). Lower/upper agreement bounds are \(\sum_l\min/\max_{d\in\{D_l^-,D_l^+\}}\mathbf1(S_l=d)\), denominator **21**. Report all-missing-negative and all-missing-positive scenarios too; these need not themselves be the extrema.
- Repeat these specifications separately with valid I55 records, mapping D3x to **D3x-diff**; do not pool archives.

If matched-exposure support includes counts below 17, or the missingness lower bound is below 17, say “≥80% agreement is not uniformly robust to this sensitivity.” Always retain detection-concordance wording and separate positive recurrence.

**3. Figure.** In [make_figure.py](/Users/danijel/Desktop/gadapt/research/paper_integrity_audit/make_figure.py:51), replace `counts.get(cls) or 0` with explicit availability masks: white **`0`** for assessed negatives; grey diagonal hatching plus **`n/a`** for inapplicable checks; grey **`?`** where applicability was not archived. Mask R1–R3 for baybe, bofire, cmaes and emukit using `r_applicable`; derive C4 applicability from frozen adapter `documented_max` rules. Show assessed denominators and partial coverage. Preserve documentation outlines and add a grayscale legend.

**4. Referee risks.** Outcome-aware archive choice, stratification, exclusions and thresholds create researcher discretion. Commit all choices above, disclose prior outcome knowledge, publish every specified output, and avoid significance claims. Exact subsampling describes retained observations; it does not establish exchangeability or remove informative failure.