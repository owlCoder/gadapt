**All six point estimates match `i57_analysis` exactly.** I used an independent, read-only `.venv/bin/python -B` reader, without importing study modules or running the driver’s analysis. Computation used one process with numerical-library threads limited to one; no files were written.

Following the [frozen protocol](/Users/danijel/Desktop/gadapt/research/ITERATION57_PROTOCOL.md), estimates give equal weight to nine blocks and equal weight to retained scenarios within each block. Bootstrap sampling preserved the complete seven-configuration vector within each network × R × scenario cell: 20,000 replicates, seed 57, NumPy PCG64, percentile intervals.

| Method − GAdapt | Estimate, exact match | Independent 95% CI | Archived 95% CI |
|---|---:|---:|---:|
| CMAwM/SP | −0.10104537037037037 | [−0.117302, −0.084228] | [−0.117232, −0.084140] |
| CMAwM/FR | −0.10538518518518518 | [−0.123937, −0.086020] | [−0.123657, −0.085998] |
| DE/SP | +0.011544444444444446 | [−0.004891, +0.028550] | [−0.004763, +0.028607] |
| DE/FR | +0.008396296296296298 | [−0.008858, +0.026221] | [−0.008902, +0.026005] |
| Random/SP | +0.05950555555555556 | [+0.044579, +0.074943] | [+0.044775, +0.075090] |
| Random/FR | +0.057242592592592595 | [+0.042143, +0.073173] | [+0.042108, +0.073115] |

Negative values indicate lower observed capped time for the external method. My cell-major, joint-vector draw order gives a different random stream; the largest CI endpoint difference is **0.000281 T**, consistent with Monte Carlo noise.

Block summaries below use **mean T / attainment % / feasibility % / median best feasible loss (MW)**. Attainment uses `first_target != null`; feasibility means at least one feasible evaluation. Loss medians include only runs finding feasibility; “—” means none. Each configuration has 40 runs per case14/case118 block and 20 per case57 block. Random supplies one shared trajectory for both contrasts.

**case14**

| Configuration | R = 9 | R = 17 | R = 33 |
|---|---|---|---|
| GAdapt/SP | 0.9799 / 2.5 / 15 / 10.772 | 0.7139 / 52.5 / 100 / 9.512 | 0.7623 / 60 / 100 / 9.530 |
| GAdapt/FR | 0.9624 / 7.5 / 25 / 10.630 | 0.7246 / 50 / 100 / 9.533 | 0.8109 / 47.5 / 100 / 9.555 |
| CMAwM/SP | 1.0000 / 0 / 7.5 / 11.013 | 0.2309 / 95 / 97.5 / 9.475 | 0.3157 / 92.5 / 100 / 9.471 |
| CMAwM/FR | 1.0000 / 0 / 10 / 10.995 | 0.2325 / 95 / 97.5 / 9.475 | 0.3022 / 92.5 / 100 / 9.457 |
| DE/SP | 1.0000 / 0 / 17.5 / 10.746 | 0.6884 / 87.5 / 100 / 9.483 | 0.8716 / 50 / 100 / 9.510 |
| DE/FR | 1.0000 / 0 / 15 / 10.858 | 0.6973 / 92.5 / 100 / 9.488 | 0.8547 / 62.5 / 100 / 9.477 |
| Random | 1.0000 / 0 / 2.5 / 11.038 | 1.0000 / 0 / 85 / 9.930 | 0.9916 / 2.5 / 90 / 9.843 |

**case57**

| Configuration | R = 9 † | R = 17 | R = 33 |
|---|---|---|---|
| GAdapt/SP | 1.0000 / 0 / 100 / 16.632 | 1.0000 / 0 / 100 / 15.408 | 1.0000 / 0 / 100 / 15.604 |
| GAdapt/FR | 1.0000 / 0 / 100 / 16.106 | 1.0000 / 0 / 100 / 16.329 | 0.9786 / 5 / 100 / 16.037 |
| CMAwM/SP | 1.0000 / 0 / 70 / 16.870 | 1.0000 / 0 / 85 / 17.077 | 1.0000 / 0 / 75 / 16.462 |
| CMAwM/FR | 1.0000 / 0 / 45 / 17.098 | 0.9932 / 5 / 100 / 16.336 | 1.0000 / 0 / 80 / 16.640 |
| DE/SP | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| DE/FR | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| Random | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |

**case118**

| Configuration | R = 9 † | R = 17 † | R = 33 † |
|---|---|---|---|
| GAdapt/SP | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 2.5 / 90.420 |
| GAdapt/FR | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| CMAwM/SP | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| CMAwM/FR | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| DE/SP | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| DE/FR | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |
| Random | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — | 1.0000 / 0 / 0 / — |

† **Non-informative for T contrasts:** every run of every configuration has T = 1. These four blocks retain their prescribed weights.

| Integrity check | Independent result |
|---|---|
| Expected coverage | 2,100 runs; 300 complete paired units; no missing, extra, or duplicate records |
| Budget | Every run records exactly 3,000 calls; 6,300,000 total |
| Execution | All `ok` and complete; zero wrapper errors, reruns, or recorded PF failures |
| Exclusions | Zero I57 run/unit exclusions; inherited case57 scenarios 1.10 and 1.15 remain excluded |
| Outcomes/references | Stored T, feasibility, attainment and all 30 task references agree with independent reconstruction |
| Provenance | All four manifest code/protocol hashes match current files |

The evaluator’s counted path performs one actual `runpf` per evaluation, including repeated candidates; cached scalarization adds none. The archived I56 `test_ref.json.gz` SHA-256 matches the raw output, analysis and pre-run manifest:

`3ada162bc9bbbd58900c03bd31dedb0647725759f8a10f52cc3dcde111780d2b`

The protocol permits descriptive comparisons of these fixed configurations, instances, targets and budget; the six weighted contrasts with pointwise intervals; and separate attainment, feasibility and feasible-loss summaries. It permits no p-values, significance declarations, superiority/equivalence claims, new-method claim, or generalization beyond these instances.

CMAwM’s lower observed mean T is concentrated in case14 at R17/R33, where attainment reaches 92.5–95%, versus 47.5–60% for GAdapt. DE’s aggregate contrasts are slightly positive, despite its higher case14/R17 attainment, illustrating that attainment and capped time describe different aspects of performance. On case57, GAdapt finds feasibility in every run, while DE and Random never do; only two target attainments occur across all configurations and resolutions. No configuration attains a case118 target, and its sole feasible result is one GAdapt/SP run at R33.

Threats include targets derived from GAdapt reference runs, best-known references rather than optima, and four cells using feasibility-only targets. Extensive budget censoring limits discrimination; conditional loss medians also compare different feasible subsets. Equal PF budgets do not establish equal runtime or tuning effort.