# I65 — I52 cross-domain transfer: chance-adjusted agreement and exact class identity

**Date:** 2026-11-03. **Status:** additional POST HOC, strictly read-only descriptive check; not a new preregistered hypothesis, independent detector ground truth, new AC solver run or dissertation originality determination. The original H52 SUPPORTED verdict is unchanged.

## Original evidence

The original archive is [I52 integrity_dispatch.json](https://github.com/owlCoder/gadapt/blob/6e16903f7b5635f0d0b60667b5524358cd48ac94/research/results/iteration52/integrity_dispatch.json), Git blob c85b680cd536defc0d849d932855228c8223eb3c. The archived later, openly post hoc [I52 sensitivity.json](https://github.com/owlCoder/gadapt/blob/6e16903f7b5635f0d0b60667b5524358cd48ac94/research/results/iteration52/sensitivity.json) has Git blob 4c31e359c45af97afa5be68bc7e5c4c631c69a90. Both exact blob IDs are checked in the new independent read-only script. The previously frozen I52 protocol set H52's binary per-library matching threshold at 17 of 21; C1 and C2 are not counted in the audited non-C1/non-C2 status set. GAdapt is excluded as a C1-positive control.

## Original binary status, independently reconstructed

| Synthetic result | AC positive | AC negative |
|---|---:|---:|
| Positive | 7 | 1 |
| Negative | 1 | 12 |

The original status agreement remains **19/21 = 90.476%**, with exactly Nevergrad (synthetic positive/dispatch negative, 10 of 15 dispatch attempts errored) and SciPy DE (synthetic negative/new dispatch R3) discordant.

For the observed 8-positive/13-negative marginals in each domain, chance-expected agreement is exactly 233/441 = 0.5283446712, and descriptive **Cohen's kappa = 83/104 = 0.7980769231**. Positive-specific agreement is 7/8 = 0.875 and negative-specific agreement is 12/13 = 0.9230769. These are inter-domain agreements of existing classifications, **not** diagnostic sensitivity/specificity, software-defect prevalence, independent adjudication or a p-value.

## Exact class identity is narrower than binary status

The source contains ten synthetic (library, class) pairs and eight AC pairs. **Seven pairs recur**: cma/C4, deap/C3, evotorch/C3, gfo/R2, pygad/C5, scikit_opt/R3 and smac/D3x. Synthetic-only: gfo/R3, nevergrad/D3 and nevergrad/D3x. AC-only: scipy_de/R3. Thus exact pair-level **Jaccard identity is 7/11 = 0.6363636364**, distinct from 19/21 library-status agreement. GFO is a concrete example of a library whose overall positive status agrees even though its R3 class does not recur. These class differences were already documented in the historical I52 report; the chance-adjusted and Jaccard summaries are newly calculated post hoc descriptors, not new software bugs.

## Incomplete observations and limitations

The original post hoc sensitivity source has three incomplete libraries: Nevergrad, bayes_opt and bofire. For the 18 complete libraries, binary agreement is 17/18 and descriptive kappa is exactly 70/79 = 0.8860759494. The historical missingness assignments span 17..20 agreements out of 21; their lower bound equals the original precommitted threshold. This does not prove missing-at-random behavior, generalization to all packages, causal equivalence between synthetic and AC inputs or external physical-model validity.

The I50 preregistered 11/12 headline falls to 4/12 after the explicitly POST HOC exclusion of nonspecific C1; this negative control remains binding. Neither the high I52 transfer fraction nor the new kappa rescues C1 specificity or demonstrates a novel detector.

## Technical reproduction and research status

[Read-only verifier](i52_transfer_compact.py) and [eight isolated unit tests](test_i52_transfer_compact.py) were prepared and passed locally. The verifier checks the original **Git blob identities** and its expected historical controls, refusing modified inputs:

    python research/i65/archive_review/i52_transfer_compact.py .
    python -m pytest -q research/i65/archive_review/test_i52_transfer_compact.py

The original two frozen JSON files were directly inspected using the connected GitHub source reader; executing the verifier in a complete local clone was not possible in this session. No original I49–I55 or I64 result/protocol/optimizer was changed; no PF/OPF, held-out COCO or optimizer was run. Both manuscripts remain DRAFT, NO-FREEZE, originality NOT_ESTABLISHED, M6/C1 unsigned.
