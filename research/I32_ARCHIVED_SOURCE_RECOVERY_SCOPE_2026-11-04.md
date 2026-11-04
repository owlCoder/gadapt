# I32 archival source recovery — read-only scope (2026-11-04)

**DRAFT; NO-FREEZE; no new PF/OPF, optimizer or COCO experiments.**

The main branch at commit `8d376a720afe2704af5efdb39777dac7a2c5e742`
does not contain the I32 source and six directly or transitively required
historical files. Their exact Git contents were recovered from the
`research/i32-ci-visible` branch, with matching identities also confirmed
on several I33/I34 historical branches.

| Historical original file | Git blob SHA-1 |
|---|---|
| research/iteration9_source_generators.py | 0b9d84ca20cca07f2220ae075809d12ec4640b39 |
| research/iteration11_original_matpower_native_pf.py | 957fd79c19a7d5f5c0250f6961164e904631928e |
| research/iteration14_original_acopf.py | db6739aca49a5bcc0fbf999938b72f348c95aecd |
| research/iteration17_ieee14_gadapt_economic_pf.py | 6cf71cf01117d82aa09768c5a2b3aef7fbf908af |
| research/iteration32_ieee14_topology_transfer.py | 6bf2f68b04e38545cd60ca73feb129d6337ee0fa |
| research/test_iteration32_ieee14_topology_transfer.py | 407bad17a429de3ac861f10558c9f7b0e99f16de |
| research/ITERATION32_PROTOCOL.md | 69d3c367669df34f07713c4ffc06345ccd48e960 |

Every file is restored **with its original bytes**, not reconstructed by
regenerating any research run. New workflow authentication explicitly checks
the seven blob hashes, limits automatic CI to relevant source paths,
and patches upstream PYPOWER runpf and runopf entrypoints to fail if a
source-only unit test inadvertently invokes a native AC solver.

The historical **72-run physical experiment remains SKIPPED** during PR
and push CI and requires explicit affirmative `workflow_dispatch`
opt-in `authorize_original_72_native_ac_runs=true`. No such authorization
is given in this branch or by the I55 review.

**Closure must be conditional on a successful independent source-only CI
run.** This branch does not itself independently replicate the original
physical I32 findings, verify a fresh engineering witness, or establish
algorithm novelty. The separate I55 #14 draft, I64-R external source,
A-prime/B raw traces, detector specificity, held-out COCO and M6/C1
human originality decision remain unchanged: **NOT ESTABLISHED**.

## Reproducibility gate

CI must authenticate all seven historical Git blobs and pass the original
zero-native-AC unit tests under patched PYPOWER runpf/runopf. Its two jobs
must show **source-only success** and **physical experiment SKIPPED**.
A CI success does **not** constitute independent AC witness validation.

## 2026-11-04 verified completion of technical source-only recovery

The [separate I32 source-only CI run](https://github.com/owlCoder/gadapt/actions/runs/41812770932)
**PASSED** on code/workflow head `d47b29bcfaab6998fb879e0b84e9aaacc5b789d6`:
all seven historical source Git blobs authenticated, **19/19 original
zero-native-AC tests passed** under the PYPOWER runpf/runopf prohibiting
patch, and the original **72-physical-run job SKIPPED**. Its success is
a source/CI repair, not independent electrical-physics verification.

I also downloaded and SHA-256 authenticated the original Oct 21
[GitHub Actions run 39686171613](https://github.com/owlCoder/gadapt/actions/runs/39686171613)
artifact (ID `12386702402`, ZIP SHA-256
`c2a84c57571841737c7a9f006091a4a97097fe6843d42265ef3ccbd84937f782`).
A standard-library **read-only** validator checked **72 archival
method/seed rows, 72 JSON-vs-CSV rows, 216 per-scenario accounting
partitions, 6 original method summaries, 5 original paired exact
binomial contrasts, and 51 archived source witness schemas and
recorded average costs**. It reconciled the **12,913 historic AC
invocations** within 12,960 frozen budget; no solver was rerun.
The original outcome JSON SHA-256 is
`a8e707cc6044390213f8c9112ab59ab47f8a30321b28a669e2624d5c0df4d534`.
The fresh accounting JSON SHA-256 is
`0aab72ad0789532178b0046ff83e600a5980425550c9ffa5af3fba08fc71499a`.
See [machine-readable evidence ledger](I32_ORIGINAL_SOURCE_AND_72RUN_ARCHIVE_RECONCILIATION_2026-11-04.json).

**Transparent CI safety disclosure:** While opening this separate I32
PR, an unrelated pre-existing automatic `exploratory-benchmark` job
ran **12 × 120 generations** in robustness workflow
[41812770943](https://github.com/owlCoder/gadapt/actions/runs/41812770943).
It was **not** the I32 physical experiment and its outputs are **not
scientific evidence**. The job cannot be undone; immediately afterward
I copied the **SHA-identical, manual-opt-in-only**
`robustness-tests.yml` fix already verified in I55 PR #14
(Git blob `32774ed66c7e16a7851195463f67b023234ee5b9`)
into this I32 PR. Subsequent PR/push events cannot automatically
run that optimizer benchmark. No optimizer/PF/OPF/COCO experiment was
**intentionally** requested by the source-recovery audit.

**Technical closure:** historical source identified and preserved
byte-identically, original archived accounting checked, new source CI
19/19 PASS. **Scientific nonclosure:** no new independent AC witness
validation, original GAdapt novelty, I64-R seed-level source, M6/C1
human signoff, A-prime/B raw or held-out COCO. The PR is a **draft
proposal** and not merged into `main`.

## Final PR-level CI isolation check (requested on latest code line)

The last source-test success was on code head
`d47b29bcfaab6998fb879e0b84e9aaacc5b789d6`; intervening
changes concerned this note, the original-archive accounting ledger
and the manual-only exploratory-benchmark guard. The original seven
restored Git source blobs and the I32 zero-AC CI procedure are
unchanged. A fresh GitHub Actions check of the final draft proposal
must show (1) all seven authenticated original blobs, (2) 19/19
zero-native-AC tests PASS, (3) physical 72-run job SKIPPED,
(4) exploratory robustness benchmark SKIPPED.
