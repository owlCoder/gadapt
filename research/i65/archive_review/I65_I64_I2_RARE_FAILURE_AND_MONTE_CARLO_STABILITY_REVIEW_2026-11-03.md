# I65 — Rare-feasibility-failure uncertainty and bootstrap Monte Carlo stability in I64-I2

**Date:** 2026-11-03. **Status:** independent *post hoc* adversarial research audit, **NOT** an approved or preregistered new hypothesis. **Frozen evidence baseline:** `owlCoder/gadapt/main` commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`; the original `research/results/iteration64_i2/analysis.json.gz` Git blob is `2b38375126a43128dba37aaf7966b92eb6df8691`. No optimizer, GAdapt, CMA, PF/OPF, infrastructure solver or held-out COCO objective was run.

## Key result — two legitimate but different inferential questions

The **original** preregistered I64-I2 experiment tested a simultaneous family of four contrasts on **eight fixed ORPD cells × 30 paired seeds**. Its IPOP-minus-hybrid tail contrast is `CVaR(IPOP) − CVaR(H) = −0.125306761112`, with the original simultaneous interval `[-0.250223907, -0.000389615]`, and the frozen H64h2 verdict is **OPPOSITE**. Earlier work independently replayed the exact original 20,000-replicate seed-68 bootstrap, reproducing all 13 numerical quantities without difference. This remains authoritative for the fixed experiment.

A post hoc inspection singled out `case39/j=3`: the hybrid had **three** runs with no feasible candidate (`68003015`, `68003018`, `68003028`), while IPOP had **zero**. All 30 runs per configuration were technically completed, and this cell contributes `−0.125` of the original eight-cell tail contrast (`99.755%` of its signed magnitude). **Do not conflate the strength of the original CVaR inference with the evidence about a difference in raw feasible-hit frequency within this one cell.**

### Marginal failure-rate uncertainty within the selected cell

| Quantity | Exact value | Interpretation |
|---|---:|---|
| Hybrid failure rate | `3/30 = 10%` | Observed rate, not known probability |
| Hybrid 95% exact Clopper–Pearson interval | `[0.021117, 0.265288]` | Under independent same-cell seed sampling |
| IPOP failure rate | `0/30 = 0%` | Observed rate, not proof that failure is impossible |
| IPOP 95% exact Clopper–Pearson interval | `[0, 0.115703]` | Upper bound exceeds 11% |
| Paired discordances | 3 IPOP-only feasible, 0 hybrid-only feasible | Same 30 seed indices |
| Exact two-sided McNemar `p` | **`0.25`** | No separately established 5%-level single-cell feasibility-rate difference |
| Directional one-sided paired `p` | `0.125` | Exploratory and selection-unadjusted |

The Clopper–Pearson intervals are marginal, **not simultaneous** across algorithms or cells. McNemar's test targets paired *binary feasibility*, not CVaR magnitudes; furthermore, the cell was selected after reviewing the data. Neither test invalidates the frozen 8-cell H64h2 result. Equally, H64h2 should **not** be quoted as a single-cell significant difference in failure probability.

### A discrete top-three tail statistic

`CVaR_0.9` with 30 seeds is the arithmetic mean of the **three worst** per-run losses, where failure to find a feasible candidate maps to loss `L=1`. For the observed empirical hybrid distribution with three infeasible outcomes, a 30-with-replacement bootstrap draw has probability

`P[Binomial(30, 3/30) <= 2] = 0.4113512396`

of having fewer than three such failures. Thus the selected cell's bootstrap CVaR often drops below its observed value of 1.0. This **41.1% is a property of resampling the observed empirical distribution**, neither a p-value nor a predicted real-world failure rate. It illustrates the discrete/non-smooth behavior of the estimated tail with only 30 seeds.

### Monte Carlo *algorithmic* stability (not population generalization)

For this new robustness check, the original **four-contrast max-studentized** procedure was recomputed from the previously extracted and validated derived 8×3×30 `loss`/`feasible` arrays. The original `numpy.random.default_rng(68)` 20,000-replicate result again reproduces `t*=3.4133099733799344` and the original c3 upper bound to within numerical rounding. The same prespecified *algorithmic calculation* was then repeated with different RNG seeds solely as an exploratory stability diagnostic:

- **12 runs × 20,000** resamples (bootstrap seeds 68–79).
- **3 runs × 100,000** resamples (bootstrap seeds 68–70).
- All **15 of 15** resulting simultaneous c3 upper bounds were negative, ranging **`−0.000405267` to `−0.000324161`**. Larger bootstrap replication alone does not remove uncertainty from rare outcomes, the preselected cell set, or the AC model.

In separate post hoc point checks, deleting one of the three hybrid-failure seed indices reduces the original mean contrast from about `−0.1253` to about `−0.08364` while leaving it negative. Increasing the tail from 3 to 6 worst seeds changes the magnitude to `−0.0628624`; the dominant cell still accounts for approximately 99.42% of this signed contrast. Conversely, using **all 30** seeds as a mean loss gives contrast `−0.0293642`, with the dominant cell accounting for only about 42.57%. Tail definition is therefore scientifically central. None of these alterations is a registered alternative primary analysis.

## Implications for the doctoral manuscripts

1. **Separate three estimands:** anytime evaluation ECDF, worst-tail CVaR of normalized losses, and binary probability of ever finding a feasible solution. Numerical agreement on one does not imply equivalent evidence on another.
2. **Respect the original inferential decision:** H64h2 remains **OPPOSITE** for its registered four-contrast, eight-cell target. The negative tail interval is reproducible and insensitive to 20k/100k bootstrap simulation seeds, conditional on the original observations.
3. **Disclose cell selection and physical-model limitations:** this single cell was identified after observing outcomes; feasibility witness flags come from the archived I64 software checks, not new independent grid measurements.
4. **Do not assert a new algorithmic/theoretical contribution:** the exact binomial test, McNemar test, tail average, and bootstrap are established methods. The possible doctoral contribution is a well-validated, carefully delimited evaluation-integrity methodology, pending independent prior-art and mentor M6/C1 review.

## Reproduction

The read-only program [`i64_i2_rare_failure_audit.py`](i64_i2_rare_failure_audit.py) uses [`i64_i2_bootstrap_replay.py`](i64_i2_bootstrap_replay.py) and the existing pinned Git SHA-1 IDs in [`i64_i2_cell_influence.py`](i64_i2_cell_influence.py). It **rejects input arrays that fail to reproduce** the original archived primary contrast. From a full clone containing original `research/results/`:

```sh
python research/i65/archive_review/i64_i2_rare_failure_audit.py --repo-root . --output /tmp/i64_i2_rare_failure_audit.json
python -m unittest discover -s research/i65/archive_review -p 'test_i64_i2_rare_failure_audit.py' -v
```

A local **derived** 8×3×30 loss/feasibility file was used to run the numbers above because a complete local Git clone was not available in this session; that tiny derived array was independently matched against all four archived point contrasts in the preceding audit and is *not* presented as original compressed input. The `--repo-root` mode checks all 16 original per-cell files by pinned Git blobs. The generated [machine-readable ledger](I65_I64_I2_RARE_FAILURE_AND_MC_STABILITY_2026-11-03.json) records the 15 bootstrap variants, exact intervals and sensitivity cases; it is a derived audit, not a modified experimental archive.

**Permanent status:** `DRAFT / NO-FREEZE / COCO NOT_RUN / originality NOT_ESTABLISHED / M6-C1 pending`; no author or reviewer sign-off is implied.
