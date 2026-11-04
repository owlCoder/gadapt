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
