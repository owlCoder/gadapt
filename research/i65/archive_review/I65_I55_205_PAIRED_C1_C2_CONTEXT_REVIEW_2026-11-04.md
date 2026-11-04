# I55 — Matched function-context audit of C1/C2 (205 complete original A-process strata)

**2026-11-04 — Post-hoc descriptive source audit; not a new optimization
experiment, diagnostic classifier validation or hypothesis test.**
Scientific state: **DRAFT / NO-FREEZE / NOT_ESTABLISHED**.

## Provenance and execution

The [isolated read-only GitHub Actions run 41799179972](https://github.com/owlCoder/gadapt/actions/runs/41799179972)
succeeded after an initial intentionally fail-closed workflow exposed a
counting assumption error. The corrected run has 77 passing synthetic/unit
tests (19+9+20+14+8+7), verified original full-clone 620/620 A-process
NPZ trace, SHA-256, objective-value and detector-flag replay, and
source-Git-pinned original 21-library cell JSON.

- Original source commit: `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`
- Original 620-NPZ manifest Git blob: `50ca2e96762447070a74309850cb1aa6586d3eb3`
- Original 620 attestation JSON SHA-256: `9a6a5a3d32120394798ccf47675aaff403b82062fac240267a47e327283fa111`
- Original 620 flag census JSON SHA-256: `a0bfb1bfeaa2979ae8f195ffbcde8c9ff2c45b0562f96ecdf7915e229963c4ea`
- Matched function context JSON SHA-256: `15ee37a184e6e5f0f308aaa89b5488796e1ffb9fbf2410bee1332b8c009cac99`
- Original Actions artifact ID: **13306399315**, ZIP SHA-256:
  `2bc75b3604e6d6b4c4d87a8f3aaf8c53a07705c6fa21911a724ab2b5c22d7233`

The reproducible script
[`i55_paired_function_context_audit.py`](i55_paired_function_context_audit.py)
fails closed unless the original raw 620-source attestation passes, then
authenticates each original 21 library cell JSON Git identity and
reconciles the entire 620-cell census. Seven synthetic/adversarial
regression tests passed. It does **not** execute any optimizer or a
physical or COCO experiment.

## Matched unit and denominator

For each fixed (library, dimension, original seed), compare *presence*
of a C1/C2 flag across the original `plateau`, `sphere`, and
`rastrigin` A-process traces. Nominal strata: 21 libraries × 2
dimensions × 5 seeds = **210**. The 10 original failed Nevergrad cells
occur in only **five shared incomplete strata**: 10D sphere and 10D
Rastrigin for seeds 6000–6004. The denominator of each complete-case
paired contrast is therefore **205**, NOT 200. Plateau sources from
those five incomplete strata are excluded from paired comparisons
but remain counted in the full 620-source census. The original
295,445 evaluation calls are NOT new optimization calls.

## Direct matched cell-presence comparisons

Each table entry counts one fixed library/dimension/seed pair,
not individual calls or independent software defects.

| Flag, paired functions | Only left | Only right | Both | Neither | Total |
|---|---:|---:|---:|---:|---:|
| C1, plateau vs sphere | 31 | 3 | 26 | 145 | 205 |
| C1, plateau vs Rastrigin | 34 | 0 | 23 | 148 | 205 |
| C1, sphere vs Rastrigin | 10 | 4 | 19 | 172 | 205 |
| C2, plateau vs sphere | 27 | 5 | 70 | 103 | 205 |
| C2, plateau vs Rastrigin | 25 | 1 | 72 | 107 | 205 |
| C2, sphere vs Rastrigin | 8 | 6 | 67 | 124 | 205 |

### Library-level heterogeneity

Within each library, compare the **number of matched cells with any flag**
(not event frequency). For C1 plateau/sphere, **5 libraries have more
plateau-positive cells, 0 have more sphere-positive cells, 16 tie**.
For C1 plateau/Rastrigin, the corresponding counts are **6/0/15**.
For C2 plateau/sphere, the counts are **4/1/16**. These ties are
important: the population aggregate is strongly affected by a
subset of libraries.

**Illustrative discordance of measures:** Emukit has C1 present in
8/10 plateau cells and 8/10 sphere cells (a library-level binary tie)
but **19** C1 events on plateau versus **200** on sphere. A cell-level
indicator and an event-count-weighted summary can point in different
directions; neither is a source-adjudicated defect label.

Aggregated across all original 620 valid A-source cells, **1,820/2,105**
C1 events occur on plateau, and **1,447/2,105** arise from BayBE +
Bofire alone. This is function/library composition, not an estimate of
the false-positive rate, sensitivity, specificity, or independent
library-population effect.

## Control interpretation

No p-values, intervals, causal attribution, defect precision/recall,
new optimizer claims or statistical generalization were computed.
The 21 libraries are not a random sample of a defined library
population; seed, function and library strata are not IID independent
draws. Evaluation-call budgets differ across libraries and some
functions. A paired descriptive contrast helps reveal this confounding
but does **not** remove it or identify true positives.

The published machine-readable summary is
[`I65_I55_205_STRATA_C1_C2_MATCHED_FUNCTION_SUMMARY_2026-11-04.json`](I65_I55_205_STRATA_C1_C2_MATCHED_FUNCTION_SUMMARY_2026-11-04.json).
The full raw paired per-library/per-dimension tally remains in the
GitHub Actions ZIP (content hash above).

## Off-Git I64-R source recovery search update

All **15 visible branch tips** returned by GitHub branch listing were
checked for the exact `research/results/iteration64_r` directory.
Four recent branches contained only `analysis.json.gz` and
`check_repro.json.gz`; the other 11 did not contain that directory.
No active branch tip exposed `run.json.gz` or `run_part_*.json.gz`.
A second paginated branch listing returned zero more branches.
This is a **branch-tip/path-level search only**, not proof that the
original off-Git source is absent from an experimental computer,
historical orphaned Git object, or inaccessible storage. The original
4,200-run R seed-level bootstrap remains BLOCKED on source recovery.

## Stop conditions

Original A′/B raw coordinate sequences, true detector specificity,
I64-R source, independent M3 physical witness check, signed human
M6/C1 originality decision and held-out COCO remain unclosed.
Do not merge a `DRAFT` research result as dissertation freeze.
