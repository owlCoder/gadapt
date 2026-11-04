# I65: 126 additional original I55 NPZ raw replays, 181/620 cumulative (2026-11-04)

**Status: ARCHIVAL SOURCE AUDIT; NOT THE COMPLETE 620-NPZ ATTESTATION.** The original 126 binary NPZ files were decoded through the connected GitHub repository and independently checked with the pinned read-only JavaScript decoder. No optimizer, power flow, or held-out COCO experiment was run. These checks do not establish doctoral originality or independent detector specificity.

## New verified evidence and denominators

- Previous 2026-11-03 archival witness sets: **55/620 original valid A-process NPZ files**, **24,298 archived objective calls**, including earlier five direct replays and 50 separate source replays.
- This phase: **126 new, nonoverlapping NPZ source traces**, covering all **21 libraries**, **61,152 actual archived objective calls**, and **2,549,393 compressed NPZ bytes**. Exactly six new valid source files per library; both dimensions and all three original test function families are represented where source files exist. Nevergrad 10D sphere/Rastrigin jobs failed historically, so only existing valid Nevergrad files were selected.
- Aggregate of archived original raw-source replays: **181/620** and **85,450 original objective calls**. **439 valid original NPZ files remain unreplayed.** These are distinct source files; the 10 historical failed Nevergrad cells are outside the valid NPZ count.
- For all 126 newly selected NPZs, the Git blob SHA-1 and source size matched the original 620-record frozen manifest, the original coordinate/function/phase SHA-256 digest matched the archived `cells_*.json`, all C1âC5, R1âR3 and D2 flag counts matched, and every saved `f(x)` agreed with the original frozen sphere, Rastrigin, or plateau definition using the historical `float32` policy for EvoX/EvoTorch. **126/126 pass**, zero flagged replay discrepancies. All 21 six-cell evidence files are preserved on GitHub at commit `625c4a1ac3a4844f62583af9f38c58480157f3cf`.

The **21 source witness Git blob identities** and 126 exact paths are in [the machine-readable index](I65_I55_NEXT_126_SOURCE_REPLAY_INDEX_2026-11-04.json). The original source commit `6b56fbc53ffc4d275ecef5e911ea4663474c9a08`, immutable original 620-NPZ manifest Git blob `50ca2e96762447070a74309850cb1aa6586d3eb3`, prior 55-index blob `1418207f25a3745c4caacdd2fdb63359dc227b04` and replay-engine blob `076ac19beef2514eef9985c86eac071ca9975b8d` were independently required.

## Independent after-the-fact reconciliation

The [read-only evidence reconciler](i55_181_npz_evidence_reconcile.py) independently checks the 21 archived replay JSON files against the pinned 620-file manifest, the earlier 55-source index, and every one of the 21 immutable original `cells_<library>.json` blobs. It rejects duplicate NPZ paths, false PASS indicators, unexpected numeric precision, incorrect byte identities and sizes, modified full-call SHA-256 digests, changed C/R/D2 counts, missing batches and inflated source-call totals. A full checkout permits:

```sh
python research/i65/archive_review/i55_181_npz_evidence_reconcile.py --repo-root . --output /tmp/i55-181-witness-reconciliation.json
```

The new reconciler itself was tested with **14/14 synthetic adversarial tests PASS**. The previously published pure-JS raw NPZ reader passes **9/9 Python test cases plus 7 additional subtests**, as checked in this continuation. These unit tests do **not** constitute another replay of the 126 binary source files. The 21 batches were also independently re-read as Git blobs in the connector after staging; their frozen path roster, per-library call totals and absence of false positive pass indicators were checked. The source file index and all new replays are disjoint from the earlier 55.

## Selected library-level source-call counts (six NPZs per library)

| Library | Original calls | Git blob of archived witness |
|---|---:|---|
| `baybe` | 1,200 | `27dd0a9a85d10e169eace8f3a0a6fe174b0b2d05` |
| `bayes_opt` | 1,020 | `623f9670506fd748d9ae7311d26651bfef800b5f` |
| `bofire` | 1,200 | `eb1d4d75dc08cbbce32749d87310128c93cfbab7` |
| `cma` | 3,808 | `fb22e93ef1a1aa10ca7e7a1ddb633604a5af2330` |
| `cmaes` | 1,194 | `1efbf0756be0f7c656399d979eb9aa8a19b86b0d` |
| `deap` | 3,747 | `c8f42f44cf8ecdb12324844533db7352cca4bf4f` |
| `emukit` | 1,200 | `cb735d577939657a6c260883e142f8c00006589a` |
| `evolopy` | 906 | `ef1d5455633c5ee21ef04f72e4728271f404d093` |
| `evotorch` | 1,194 | `d6790e5b00d9812b173af88962c5d379b8874980` |
| `evox` | 1,200 | `63538fb15759271ec19728af7f3f87f25a48046a` |
| `geneticalgorithm` | 4,176 | `12408e0bfbab38a8fa99bf507d8fe8306ca088d2` |
| `gfo` | 1,191 | `3db3ef1f31be91c2c7db251a0eadb274e0ed206a` |
| `nevergrad` | 6,000 | `3b605b1bae3155ab496e1e8ae2ec0c384d348523` |
| `niapy` | 1,200 | `2558a0f40b91d592aabc530ace32eb2af93429d3` |
| `optuna` | 6,000 | `f3ea53ab3663103dc8f563b9584cdd51623bfe72` |
| `pygad` | 6,126 | `cc83ee900c00fc794c2e44211695b60e69d39c67` |
| `pymoo` | 6,000 | `59ec0c57eac1f16083666f8141e98b09b6130a51` |
| `pyswarms` | 5,700 | `915e9fe8e9ff9331a8f83fedecd52d202be54a61` |
| `scikit_opt` | 1,806 | `64f1c7da5a6f0bceb73bab3fdf8ee6a7bf7acb23` |
| `scipy_de` | 5,084 | `479d2d7417bc51ff37215294dcd5639c03de1b93` |
| `smac` | 1,200 | `69348d519b3543d5e4449ef28bc7747b1e6549b5` |

**New source call total:** 61,152. **New compressed bytes:** 2,549,393. These counts are descriptive totals of archived objective evaluations, not experimental sample-size inferences. Do not count extra validation probes or compare them to optimizer iterations.

## Limits and research disposition

The raw SHA-256 replay and objective oracle are validated for 181 A-process original NPZs, **not all 620**. Original A-prime and B raw coordinate-value sequences are not contained in these A-process NPZ files; the archived metadata comparison of A/A-prime/B digests is a separate limited evidence type. No algorithmic causal root cause, universal defect specificity, statistical independence, human originality sign-off or full-clone reproducibility certificate follows from this subset.

The original I55a/b/c **SUPPORTED**, H55d **NOT SUPPORTED** and I52/I64 negative results remain unchanged. The 4,200-run original I64-R `run.json.gz` remains off Git and unverified. The M6/C1 decision is unsigned; scientific status stays **DRAFT / NO-FREEZE / originality NOT_ESTABLISHED / COCO NOT_RUN**. Next mechanical target is source-replay of the remaining **439 NPZ**; seek the off-Git R source and independent scientific review rather than inventing new experiments.
