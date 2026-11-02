# I65 — independent AC generator and operational-dispatch reconstruction: verified result

**Date:** 2026-11-02.  
**Gate:** **PASS for independent numerical reconstruction on one pre-used, non-held-out I58 case30/j1 fixed-midpoint scenario**, not independent physical measurements, general PF solver certification, or a new optimizer contribution.  
**GitHub Actions:** [run #41419711114](https://github.com/owlCoder/gadapt/actions/runs/41419711114), `completed / success`, tested main commit `644caf5b11e677282e79a7aa6e58345fbd2203fd`.  
**Artifact:** [i65-independent-dispatch-41419711114](https://github.com/owlCoder/gadapt/actions/runs/41419711114/artifacts/13129760733), ZIP SHA-256 `bae00649d6d1c24cc6a1a05240feb99e6178065a809fb95c10339184be33019a`.  
**Byte-preserved raw result:** [`I65_INDEPENDENT_DISPATCH_SUCCESS_2026-11-02.json`](I65_INDEPENDENT_DISPATCH_SUCCESS_2026-11-02.json), Git blob `b89a97202cd1149f395f9113350f312d95d3f7a1`, SHA-256 `30cb445a646d115b3e87a4821de67ae85e123082f92de518365ba4afb1e91f46`.

## 1. Precommitted hypothesis and result

The [pre-run protocol](I65_INDEPENDENT_DISPATCH_PREFLIGHT_2026-11-02.md) limited the check to one previously studied `case30`, scenario `j=1`, grid `R=17`, fixed snapped midpoint, with **no algorithmic search**. NumPy-only [`independent_ac_newton.py`](i65/independent_ac_newton.py) solved the **unsolved input** network from a flat start; the new [`independent_ac_dispatch.py`](i65/independent_ac_dispatch.py) reconstructed individual REF/PV generator reactive powers, slack active generation and both-end complex branch powers **before** any PYPOWER solved state was available. Then a single independent reference PYPOWER `runpf` was used only for cross-comparison. The previously verified independent AC residual and four I56-compatible constraint formulas were applied to the NumPy-reconstructed state.

| Preregistered check | Maximum allowed | Actual observed | Outcome |
|---|---:|---:|---|
| All fast analytic/adversarial tests | 14 new + 16 Newton + 17 constraints | **47/47 PASS** | PASS |
| Active generator `QG` difference | `0.001 MVAr` | **`6.714628852932947e-12 MVAr`** | PASS |
| Reference generator `PG` difference | `0.001 MW` | **`8.881784197001252e-13 MW`** | PASS |
| Max from-end complex branch-flow difference | `0.001 MVA` | **`5.932425511178245e-12 MVA`** | PASS |
| Max to-end complex branch-flow difference | `0.001 MVA` | **`6.0066922763819755e-12 MVA`** | PASS |
| Four I56 component differences | each `1e-6` dimensionless/mixed original unit | **0** voltage, **`4.440892098500626e-15`** reactive, **0** slack, **0** thermal | PASS |
| Independently reconstructed nodal mismatch | `0.001 MVA` | **`1.5329557338532702e-08 MVA`** | PASS |
| Separately checked branch-flow residual | `1e-5 MVA` | **0.0 MVA** | PASS |
| Solver API entries | setup OPF=1, witness PF=1, search=0 | **1 + 1; 0 search** | PASS |
| Feasibility of fixed midpoint | Preserve observed `feasible=false` | **Both independent and PYPOWER: `false`** | Preserved |

The separate Newton computation converged in **3 iterations** and performed **325 mathematical mismatch/residual evaluations**; these are not 325 external PYPOWER PF entrypoints. PYPOWER also converged.

**Crucial physically meaningful negative:** the reconstructed I56 reactive limit penalty is **`0.5991137833375704`**, whereas original PYPOWER's is **`0.5991137833375748`**. Difference is `4.440892098500626e-15`; each is dramatically above I56 feasibility tolerance `1e-6`. Voltage, slack and thermal components are zero in both. Therefore the solver's numeric convergence **does not make this original fixed candidate operationally feasible**. This is not evidence of GAdapt optimization failure, as no candidate optimization was executed.

## 2. Actual source and evidence integrity

Independently downloaded the GitHub ZIP. Recomputed its exact SHA-256 digest and checked every line in `hashes.sha256` against the **original bytes inside the ZIP**. **All 6/6 passed**:

| Artifact file | Independent SHA-256 |
|---|---|
| `constraints_unit.log` | `198cbb2e6050054fe7f0e2ae2201e0ac283c93bb16c0539b8ae144ebe7b73f85` |
| `dispatch_unit.log` | `5f28edc667b5b93b067bea83c7747b68af09748d6b53c6782574fcc1a11ace3b` |
| `newton_unit.log` | `8cea4d6b4656016190b4c0c80d1aef77053681ae1137c4400c12dfd1b5c470bd` |
| `restore.log` | `b30a798b89b330808732f7473c8db60eeba02c2665c0ed53de7ebcf6f7f7278a` |
| `smoke.json` | `30cb445a646d115b3e87a4821de67ae85e123082f92de518365ba4afb1e91f46` |
| `commit.txt` | `5c71213df42e3358c4a9383306e360f5583caddbdac325390affa34fe424fb7c` |

The internal solver event SHA-256 of the compact, sorted-key JSON (without its digest member) independently recomputed to `8d372ca753d6a75584519a6a712e01b23e3df43df555d56267cddc641938935f`, exactly matching the event log. The original source Git blobs written into raw JSON match the versioned sources:

- Frozen `iteration56_orpd.py`: `43f2f279f7e6362250dc9277e58e0d939a98c12f`
- Frozen `iteration58_validation.py`: `9747faea9c31526a163bd8439c74708214c07a3c`
- Separate NumPy Newton solver: `268d0406a90fe7d314d4e01311ea2f4376084b2b`
- New standalone generator/flow reconstruction: `36aa3c819a6abde58153f27d7dd5efa5bcbf0ccc`
- Independently coded AC residual equations: `8e6bb1b4cf78578c15315be3b4cff127bc2c8036`
- Independent four I56 constraints: `120244c35c610ac48b515df4ef86791eb6466e3f`

The full historical 341-root aliases were restored with source-hash validation (`checked=341; planned=341; created=341; existing=0; mode=apply; hash_verification=enabled`). This is an actual Python **3.12.15**, NumPy **1.26.4**, PYPOWER **5.1.19** runner, not a synthetic Git-tree assertion.

## 3. Scientific scope and fail-closed boundaries

**Proven in this one fixed development case:** two separate numerical AC solver/software paths agree not only on voltage, angle and loss, but also on **solved generator outputs** `QG`, reference `PG`, both-end branch flows, nodal/flow residual and the four archived I56 limit penalties. The negative reactive infeasibility has been independently reproduced at numerical precision. The new implementation rejects ambiguous individual Q allocations on multi-generator PV/REF buses and online PQ-bus generator cases.

**Not proven:** independent physical grid measurements, an independently sourced model/dataset, Q-limit-enforcing PF, generator capability curves, additional operational limits beyond original I56's four aggregates, arbitrary networks including islanded/parallel-generator cases, OPF or original I65 algorithm novelty. Separate Newton's 325 residual evaluations cannot be silently charged as 325 `runpf` entrypoints or used to rewrite the DRAFT physical budget. The method is standard AC Newton and the underlying model/data remain shared.

**NEXT STEP:** supervisory C1–C6 / M1–M6 originality, model-independent-oracle sufficiency and resource-budget decisions; then explicit separate network-data provenance and unsupported-topology gate if permitted. No candidate-C optimization, multi-seed benchmark, held-out COCO f21/f24, or scientific protocol freeze is authorized by this PASS. I65 remains **novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN**.
