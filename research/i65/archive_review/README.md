# I65 archive verification and post-hoc influence review — integrated, 2026-11-03

**Status: REVIEW EVIDENCE, NOT A NEW FROZEN EXPERIMENT.** This directory integrates separate audits prepared on 2026-11-02 and 2026-11-03. All original source evidence refers to `owlCoder/gadapt` commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08` and uses pinned original Git **blob IDs**, not new optimizer/PF simulations. The integration commit only adds audit tools, reviews, derived ledgers and vector figures; frozen `research/results` / I49–I55 / I64 protocols are unchanged.

## Primary review outputs

- **I55:** [`I65_I55_CELL_LEVEL_RECHECK_2026-11-02.md`](I65_I55_CELL_LEVEL_RECHECK_2026-11-02.md) and [`I65_I55_NPZ_PAIRING_AND_SAMPLE_REPLAY_2026-11-02.md`](I65_I55_NPZ_PAIRING_AND_SAMPLE_REPLAY_2026-11-02.md). Historical I55 620/620 evaluable manipulation checks were reconstructed from 21 JSON cell archives; archived I50/I55 sequence-digest equality is **318/358**, with 2 original I50 bofire timeouts. Binary detector presence agreed in **357/358** comparable cells. One emukit `plateau,d=2,seed=6001` detector presence changed (C2: 0→1), and its raw C1 count changed 2→3. Do not confuse digest equality, count equality and Boolean presence equality. Original complete 620-trace NPZ replay **NOT RUN**. Four traces were independently byte-rehashed from NPZ, and ten emukit plateau traces had C1–C5 checked directly in the GitHub connector session.
- **I64 cross-study:** [`I65_CONTINUED_SCIENTIFIC_METHODS_REVIEW_2026-11-02.md`](I65_CONTINUED_SCIENTIFIC_METHODS_REVIEW_2026-11-02.md) and seven-analysis ledger. Original negative/undecided results remain original; archived CI values were arithmetically checked, not bootstrapped anew. S0 aggregate GAdapt A=0.698 vs DE A=0.651 does not imply uniformly best final accuracy; DE wins 14 of 21 original-stopping-point final-median cells, GAdapt 6, one tie.
- **I64 R/I2 post hoc influence:** [`I65_I64_R_I2_ADVERSARIAL_INFLUENCE_REVIEW_2026-11-03.md`](I65_I64_R_I2_ADVERSARIAL_INFLUENCE_REVIEW_2026-11-03.md), [source-anchored ledger](I65_I64_R_I2_INFLUENCE_LEDGER_2026-11-03.json), [R sensitivity SVG](I65_R_FAMILY_SENSITIVITY_2026-11-03.svg), and [I2 cell influence SVG](I65_I2_ORPD_CELL_INFLUENCE_2026-11-03.svg).
  - I64-R original c4 estimate 0.07079178, simultaneous CI [0.05981187,0.08177169], H64r3 **supported on 21 frozen cells**; post hoc removing the entire Rastrigin family yields c4 point 0.04086609, **without** a new interval or replacement verdict.
  - I64-I2 original tail difference CVaR(IPOP)−CVaR(hybrid) −0.12530676 with archived simultaneous interval [−0.25022391,−0.00038962], H64h2 **opposite**. From all 16 original run parts (8 cells × 30 paired seeds × 3 algorithms = **720 run outcomes**), `case39/j=3` contributes −0.125 of the full eight-cell mean (about **99.755%** of net negative point contrast). Seven-cell post hoc mean is −0.00035058, with **no new CI**. The hybrid lacked a feasible witness in that cell at seeds 68003015, 68003018, 68003028; IPOP had none missing. The `case39/j=4` CVaR=1 saturation across three methods hides distinct feasibility rates.

**Scientific integrity:** post hoc point sensitivity ≠ preregistered statistical decision; historical `witness_checked` ≠ new independent physics validation; archive arithmetic ≠ running original estimators; original algorithmic novelty **NOT_ESTABLISHED**; M6/C1 supervision **pending**, `NO-FREEZE`, held-out COCO `NOT_RUN`, manuscripts **draft only**.

## Local read-only reproduction

Use a complete clone of the *original* repo and verify the immutable source file Git blobs first (scripts fail closed on mismatches). New Python tools here do **not** execute optimizers or power-flow solvers; they only read existing archived data.

```bash
# From the repository root (uses numpy for NPZ and bootstrap tasks):
python -m pytest -q research/i65/archive_review
python research/i65/archive_review/i55_cell_archive_recheck.py --repo-root .
python research/i65/archive_review/i55_npz_cross_archive_verifier.py --repo-root . > i55_npz_full.json
python research/i65/archive_review/i55_i50_numeric_vs_boolean_audit.py --repo-root .
python research/i65/archive_review/i64_archival_recheck.py --repo-root .
python research/i65/archive_review/i64_s0_cell_ranking.py --repo-root .
python research/i65/archive_review/i64_r_family_sensitivity.py --repo-root . --output i64_r_sensitivity.json
python research/i65/archive_review/i64_i2_cell_influence.py --repo-root . --output i64_i2_influence.json
python research/i65/archive_review/i64_i2_bootstrap_replay.py --repo-root . --output i64_i2_bootstrap.json
# Last line replays 20,000 original-method bootstrap resamples, using numpy.
# It has synthetic tests, but was NOT executed on a full clone during preparation.
```

`i55_npz_full.json` and `i64_i2_bootstrap.json` are **prospective outputs**: absent until the corresponding full-clone commands succeed. Synthetic tests, staged reports and ledgers cannot be substituted for them. No expensive CI, optimizer, COCO or PF task should be triggered merely to review this documentation. `main` pushes may still trigger workflows despite `[skip ci]` in the commit message.

## Manuscript and decision chain

- [`I65_MANUSCRIPT_ADDENDA_READY_FOR_REVIEW_2026-11-02.md`](I65_MANUSCRIPT_ADDENDA_READY_FOR_REVIEW_2026-11-02.md) — archived-integrity methodological addendum.
- [`I65_MANUSCRIPT_INFLUENCE_ADDENDA_2026-11-03.md`](I65_MANUSCRIPT_INFLUENCE_ADDENDA_2026-11-03.md) — R/I2 post hoc paragraphs, subject to author/editor approval.
- [`I65_SUPERVISOR_REVIEW_DELTA_2026-11-03.md`](I65_SUPERVISOR_REVIEW_DELTA_2026-11-03.md) — precise novelty/scope blockers for human response.

Primary original reports remain authoritative and have not been modified in this integration.


## 2026-11-03 I64-I2 full archived-bootstrap replication COMPLETE

[Full scientific report](I65_I64_I2_EXACT_BOOTSTRAP_AND_POSTHOC_AUDIT_2026-11-03.md) · [13/13 original frozen values](I65_I64_I2_EXACT_BOOTSTRAP_RECHECK_2026-11-03.json) · [exploratory selected-cell bootstrap](I65_I64_I2_POSTHOC_DROPOUT_BOOTSTRAP_2026-11-03.json) · [read-only program](i64_i2_posthoc_dropout_bootstrap.py) · [synthetic unit tests](test_i64_i2_posthoc_dropout_bootstrap.py). The original matched 20,000-resample bootstrap now reproduced **exactly**; seven-cell deletion was selected POST HOC, not confirmatory. Combined local audit regression tests **87/87 PASS**. Raw full I55 620 NPZ replay NOT RUN; human originality approval pending.


### New 2026-11-03 rare-failure / Monte Carlo check

- [I64-I2 exact-binomial, paired-feasibility and bootstrap seed-stability review](I65_I64_I2_RARE_FAILURE_AND_MONTE_CARLO_STABILITY_REVIEW_2026-11-03.md), the corresponding [read-only Python implementation](i64_i2_rare_failure_audit.py), [tests](test_i64_i2_rare_failure_audit.py), and [machine-readable results](I65_I64_I2_RARE_FAILURE_AND_MC_STABILITY_2026-11-03.json). The original H64h2 CVaR decision **OPPOSITE** is unchanged; post hoc single-cell paired binary-feasibility McNemar `p=0.25` addresses a different estimand. Fifteen exploratory 20k/100k bootstrap variants retain negative original-method upper bounds. Run `python research/i65/archive_review/i64_i2_rare_failure_audit.py --repo-root . --output /tmp/rare_audit.json` from a complete clone. The `--repo-root` archival mode has **not** been executed in this environment; the derived arrays mode has been independently checked against frozen point contrasts. No experimental/optimizer code or frozen result was edited.


## 2026-11-03 original I64-R raw archive and family-stress check

- [Full scientific/provenance audit](I65_I64_R_OFFGIT_SOURCE_AND_FUNCTION_FAMILY_STRESS_2026-11-03.md), [family resampling ledger](I65_I64_R_FAMILY_VARIATION_STRESS_2026-11-03.json), [read-only original R source gate](i64_r_off_git_raw_recovery_gate.py), [nine-family stress script](i64_r_family_resampling_audit.py) and [usage](README_R_RECOVERY_AND_FAMILY_STRESS_2026-11-03.md).
- The original ~8 MB, 4,200-record `iteration64_r/run.json.gz` was **deliberately kept outside Git** (historical progress SHA abbreviation `f23046f6…3618`). The recorded original **seed-level R bootstrap is NOT independently replayed**. Do not infer that off-Git data have been destroyed or pass an abbreviated digest as full authenticity proof.
- Post hoc nine-function-family resampling (100,000 draws of archived aggregate family means) gives illustrative c4 2.5–97.5 percentiles [0.0115,0.1455]. **Not** a registered CI, not random population inference. **8/36** two-family deletions fall below c4=0.05; original H64r3 supported verdict applies only to the frozen design. Combined offline checks **108/108 PASS**, no new optimizers or simulators run.

## 2026-11-03 I52 source-class and chance-adjusted transfer check

- [Scientific report](I65_I52_CHANCE_CORRECTED_AND_CLASS_TRANSFER_REVIEW_2026-11-03.md), [read-only pinned-blob verifier](i52_transfer_compact.py), and [eight isolated tests](test_i52_transfer_compact.py). Original registered H52 19/21 is unchanged; *post hoc* Cohen kappa = 83/104 = 0.79808, class-pair Jaccard = 7/11, full 21-library confusion = 7 both-positive, 12 both-negative, 1 discordant each way. Complete-only kappa = 70/79 on 17/18.
- Run: python research/i65/archive_review/i52_transfer_compact.py . ; then python -m pytest -q research/i65/archive_review/test_i52_transfer_compact.py . **Source Git blob verification is fail-closed.** Local isolated tests 8/8 passed; the original raw-source local checkout mode was not run.



## 2026-11-03 — I55 A/A′/B control-conditioned hash-seed evidence

- [Original 620-valid-cell negative-control breakdown](I65_I55_CONTROL_CONDITIONED_HASH_SEED_REVIEW_2026-11-03.md): A=A′=B in **585** cells; A=A′≠B in **30 SMAC** cells; A≠A′ and A≠B in **5 Nevergrad** cells; A≠A′ and A=B in **0**; 10 original Nevergrad errors excluded.
- The existing [pinned I55 cell JSON verifier](i55_cell_archive_recheck.py) now counts all four patterns and fails closed if the original aggregate or library attribution changes; three [additional tests](test_i55_cell_archive_recheck.py) validate this. Separately a 17-test standalone extended checker was tested locally; the 620 raw NPZ byte replay remains NOT RUN. This is source-metadata classification, not a novel causal result or change to frozen H55a–d.


## 2026-11-03 — Complete I55 original NPZ Git-tree inventory (NOT full NPZ replay)

- [Source-level completeness and authenticity report](I65_I55_NPZ_GIT_ARCHIVE_COMPLETENESS_AND_PROVENANCE_2026-11-03.md) · [all 620 original Git blob IDs](I65_I55_ORIGINAL_620_NPZ_GIT_BLOB_MANIFEST_2026-11-03.json) · [read-only byte-authenticity gate](i55_npz_git_blob_manifest_gate.py) · [12 synthetic tests](test_i55_npz_git_blob_manifest_gate.py).
- Nontruncated original Git tree at `6b56fbc` and checked main head `a03606d` contain exactly 620 valid NPZ blobs across 21 libraries, totaling 12,319,037 compressed bytes, with **0 changed/added/deleted** original NPZ blobs. Ten absent Nevergrad files belong to historically failed sphere/rastrigin 10D cells; no valid source NPZ path is missing.
- Verified source **index**, not full original NPZ bytes or 620 `x/f/phase` arrays. The new gate runs on a full clone to authenticate 620 original bytes before the existing full trace/flag replay. Neither full-clone command was run in the network-blocked preparation container. No optimizer/PF/COCO rerun.


## 2026-11-03: original I55 620-NPZ provenance-to-detector attestation (prospective)

[Scientific limitations and gate report](I65_I55_ORIGINAL_620_NPZ_END_TO_END_ATTESTATION_GATE_2026-11-03.md) · [fail-closed Python orchestrator](i55_full_npz_attestation.py) · [13 synthetic gate tests](test_i55_full_npz_attestation.py) · [execution instructions](README_I55_FULL_NPZ_ATTESTATION_2026-11-03.md). Verifies original-manifest SHA, original full Git tree, all original NPZ bytes, then original A-process hash/flags and archived I50/I55 controls. GitHub Actions workflow is manual-only, NOT dispatched. All 620 original numerical traces have **NOT** been replayed. 25/25 combined local synthetic tests are **not** source-data replication; frozen I55/novelty statuses are unchanged.

## 2026-11-03 — Human M6/C1 scope and originality decision (pending)

- [English supervisor decision package with three explicit alternatives](I65_M6_C1_SUPERVISOR_DECISION_PACKAGE_2026-11-03.md) summarizes the original I49–I55/I52 and I64 frozen outcomes, positive/negative findings, post-hoc caveats, two draft-paper positions and the exact evidence required for an independent sign-off. No alternative has been selected; the document is NOT an approval or a new experimental protocol.
- Original 620 I55 NPZ arrays remain NOT fully replayed. Existing source-to-NPZ code had 35/35 local synthetic tests in this continuation, not full original data validation. The 620 valid recorded A hashes were distinct within each library but digest uniqueness is no claim about statistical independence.

## 2026-11-03 — Frozen I55 objective-value audit in the source-to-detector chain

- [Independent frozen objective-value oracle and fail-closed integration](I65_I55_FROZEN_OBJECTIVE_VALUE_ORACLE_AND_FAIL_CLOSED_CHAIN_2026-11-03.md), implemented in [source NPZ verifier](i55_npz_cross_archive_verifier.py), tested by [new oracle tests](test_i55_frozen_objective_oracle.py), with [end-to-end attestation](i55_full_npz_attestation.py) now explicitly requiring that all verified A-process calls pass original f(x) checking. The existing [manual-only workflow](../../../.github/workflows/research-i65-i55-full-npz-attestation-manual.yml) includes the new tests.
- **44/44 synthetic tests PASS locally** (8 new oracle, 10 adapted trace, 14 attestation, 12 manifest tests). The original full raw NPZ 620/620 numerical verification remains **NOT RUN** in this execution environment; no new optimizer/AC PF/COCO calls and no manual workflow dispatch. This adds stronger future falsification criteria, not a new preregistered result or novelty proof.


## 2026-11-03 source-byte I55 sample replay and finite objective-oracle repair

[One-original-NPZ numerical replay report](I65_I55_ONE_ORIGINAL_NPZ_RAW_REPLAY_AND_FINITE_ORACLE_2026-11-03.md) and [structured witness](I65_I55_ONE_ORIGINAL_NPZ_RAW_REPLAY_AND_FINITE_ORACLE_2026-11-03.json): original `baybe/plateau_2_6003.npz` Git SHA-1 verified, 200/200 original `f(x)` calls and frozen SHA-256 trace recomputed with zero flag mismatch, C1=188 and C2=186. Fixed an adversarial NaN/Inf false acceptance in the post hoc frozen-objective oracle, six new synthetic tests, **50/50** local regression pass. Full 620 original NPZ replay **NOT_RUN** (only 1/620); no optimization experiments run, no H55d or novelty status changed.

## 2026-11-03 research closeout / pending external gates

- [Evidence-bounded end-of-session closeout](I65_FINAL_EVIDENCE_CLOSURE_AND_OPEN_GATES_2026-11-03.md) and its [machine-readable 13-gate registry](I65_FINAL_EVIDENCE_CLOSURE_REGISTER_2026-11-03.json).
- Local audit regression 97 PASS, 0 FAIL, 2 SKIP (missing original archive/optional fixture for both skips). Original I55 raw replay: **1/620**; archived NPZ Git inventory **620/620**. Original I64-R off-Git 4200-run raw data not recovered; original I64-I2 statistical bootstrap reproduced. No new optimizers/PF/COCO.
- GitHub Issues disabled (HTTP 410) blocked the attempted one-time read-only issue-triggered attestation. No issue or run was created; the temporary workflow was removed. Original manual-only I55 attestation remains available for a repo operator.
- **Not closed:** independent error ground truth, independent ORPD model/witness validity, mentor originality/scope M6/C1 sign-off, source-level R replay, original full I55 NPZ replay, research freeze and prospective COCO authorization. Status **PARTIAL_TECHNICAL_CLOSURE_EXTERNAL_GATES_OPEN**.
