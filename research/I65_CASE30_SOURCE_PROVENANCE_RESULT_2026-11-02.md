# I65 — real PYPOWER case30 input-lineage verification and public-data provenance

**Date:** 2026-11-02. **Verdict:** **PASS for exact deterministic software input transformation on one already-used development case; independent physical data/model provenance remains UNVERIFIED.**

**Tested code commit:** `0164c563c16e74cf8221437bb773d35bff184042` (own repo `owlCoder/gadapt/main`).  
**Real GitHub Actions:** [#41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142), `completed/success`, Python `3.12.15`, NumPy `1.26.4`, installed PYPOWER `5.1.19`.  
**Artifact:** [i65-source-lineage-41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142/artifacts/13129823351). Independently verified ZIP SHA-256 **`398461b12c5814ef69a8a9562f9c89cd2c9ad701b9690b868e33f8ee067a41c1`**.  
**Byte-identical original trace:** [`I65_CASE30_INPUT_LINEAGE_SUCCESS_2026-11-02.json`](I65_CASE30_INPUT_LINEAGE_SUCCESS_2026-11-02.json), Git blob `77decc8d77a2feb62062e8b28d158b75b2648cbb`, SHA-256 `92181a459bf87fbabbf37845edcfebce3dcf1be3f54b3105702ebc0f36a1210a`.

## 1. Original source and evidence classification

The installed public benchmark was `pypower.api.case30`, implemented in installed **`case30.py`**, whose actual local source-file SHA-256 is:

```
f7f8c565be22f30d4ba9facab8707072ef5dc3bacb6ea9ef57245c11e0bde9f6
```

This hash fingerprints the **installed PYPOWER case source**; it is **not** a claim that it matches the source bytes of an unspecified MATPOWER revision. Canonical numeric `case30` input fingerprint:

```
3b4e587cd94f2cfefc8cec384b3fec692eb74a75f38c9f757800d261d4b28c9c
```

The original [MATPOWER `case30` documentation](https://matpower.org/docs/ref/matpower4.1/case30.html) describes an **altered** 30-bus six-generator benchmark with historical alterations to parameters, shunts and loads, based on earlier literature. The [different `case_ieee30` dataset](https://matpower.org/docs/ref/matpower4.1/case_ieee30.html) derives from an IEEE Common Data Format archive. **The installed PYPOWER 5.1.19 `api` did not expose `case_ieee30` at the point tested; its numerical fingerprint and runtime numeric comparison are therefore `null / NOT_VERIFIED`.** Source descriptions differentiate the dataset families; a direct installed numerical comparison was **not** made.

The [PYPOWER release/license notice](https://pypi.org/project/PYPOWER/5.1.19/) explicitly excludes bundled case data from its BSD **software** license. This audit archives source/code hashes, shape and metadata only — **no complete benchmark input arrays and no new licensing claim**. This case is a **modified public academic model**, **not external independent live grid measurements**.

## 2. Measured deterministic ORPD lineage

[Prerecorded source and rules](I65_CASE30_SOURCE_PROVENANCE_PREFLIGHT_2026-11-02.md) specify the frozen I56/I58 sequence and reject any change except the indicated matrix columns. The single actual development `case30,j=1,R=17` run used load factor `1.0`, `spread=0.1`, `RandomState(seed=302)`, **one** `runopf` setup and zero `runpf`/search attempts.

Observed common per-bus `PD/QD` scaling-factor range: **min `0.9078525335363066`**, **max `1.0892233719610789`** across 30 bus rows. These are **seeded synthetic perturbations** in the model, not measured changes in power demand.

The auditor verified four separately hashed numeric stages:

| Stage | Exact SHA-256 fingerprint | Permitted change |
|---|---|---|
| Raw installed `case30` | `3b4e587cd94f2cfefc8cec384b3fec692eb74a75f38c9f757800d261d4b28c9c` | Baseline |
| Replayed demand-scaled case | `440acbf4ba6f06162c62fec3fc967a4618966e2bd580c355d07d5c2d56c0985c` | `PD/QD` only |
| Historical after OPF handoff | `bc5a7d98773089e271fe34023fac7fee475ebb6bd6df5f835e7ffa21c7f1ae58` | `PG` only |
| Candidate controls, **unsolved** | `a9ae44beb1309c2696a47175b25246aef83f639165635c74948ef3e86661b9a1` | Only selected `VG/TAP/BS` |

**Important qualification:** I56 does not persist an actual pre-OPF copy. The `scaled` stage in the table is independently **replayed** using the frozen `RandomState` recipe and then checked against the after-OPF arrays for all fields other than PG. This verifies the *observed final transformation* and the deterministic formula, not every transient internal OPF state.

### New result affecting scientific scope

The actual historical I56/I58 **eligible decision variables on this specific case** are:

| Type | Count | Interpretation |
|---|---:|---|
| Generator voltage setpoints (`VG`) | **6** | Six online generator-voltage controls |
| Transformer tap controls (`TAP`) | **0** | No branch meets the historical I56 selection rule `TAP != 0 AND BR_STATUS > 0` on this scenario |
| Adjustable shunt susceptances (`BS`) | **2** | Two nonzero-shunt bus controls |
| **Total raw I56 control entries** | **8** | I58 BusORPD can group per bus; this test reports original I56 counts |

**Consequently, this `case30` case alone cannot test the original algorithm's optimization of controllable tap ratios.** Do not infer that the network physically has no transformers; the *historical I56 control-selection rule* simply exposed zero eligible tap variables. Do not assert a new result on network equipment whose status was not directly studied.

## 3. Verifiable actual test evidence

Exactly **17/17** analytic/adversarial input-lineage tests passed on the real Python 3.12 runner. They reject an incorrect random seed, PD/QD mismatches, branch impedance or limits mutations, generator-cost edits, unauthorized QG/PG/control changes, duplicate indices, missing/extra fields and nonfinite input. The full Git-history compatibility restore verified **341** archived historical aliases with their original SHA. The one OPF entrypoint returned normally.

Recomputed all **4/4** individual `hashes.sha256` entries **from the original ZIP bytes**, plus the embedded `api_entrypoints` SHA-256:

| Original archive file | Verified SHA-256 |
|---|---|
| `restore.log` | `b30a798b89b330808732f7473c8db60eeba02c2665c0ed53de7ebcf6f7f7278a` |
| `unit.log` | `7d29c69dcf4c72a3f3ef9503a44a673478e10f8df1106faaf2af383943430a87` |
| `smoke.json` | `92181a459bf87fbabbf37845edcfebce3dcf1be3f54b3105702ebc0f36a1210a` |
| `commit.txt` | `7929bdca41b8de1b29e0a745f97f26df34291a79c398dc0fb03703639ffc7220` |

Independently recomputed internal event SHA **`07745245c2bb354e099271053217090fd3f8261918fec2fd800f135d0ce8cebd`**, matched exactly. Original source Git blobs also verified: `iteration56_orpd.py` `43f2f279f7e6362250dc9277e58e0d939a98c12f`; `iteration56_cht_study.py` `462e08368b70d869015d1056366964b4d10b92e1`; `iteration58_validation.py` `9747faea9c31526a163bd8439c74708214c07a3c`; new auditor `eaac7c8d84ab072b402b444e3ae16b3dc42dca05`.

## 4. What is closed and what is still open

**PASS — narrowly:** software **input-data provenance within the installed historical benchmark** for the studied development scenario: source file version and numeric identity, exact I56 demand/OPF/controls lineage, 17 falsification checks and a source-hash trail. This complements independently reproducing numerical AC voltage, generator dispatch and original reactive infeasibility in the earlier [47/47 dispatch result](I65_INDEPENDENT_DISPATCH_RESULT_2026-11-02.md), but does not extend that scientific feasibility result.

**NOT_VERIFIED / NO-FREEZE:** exact external dataset file identity against MATPOWER's historical revisions, independently collected network measurements, independent physical AC modeling, broader case networks, generator capability/thermal equipment validation, actual algorithmic novelty, unified OPF/PF/inner-Newton budget or held-out COCO f21/f24. In particular, the original reactive-infeasible development midpoint remains negative and cannot be rehabilitated by provenance hashing.

**NEXT STEP:** obtain dated [supervisor scope/novelty and budget decisions](I65_SUPERVISOR_DECISION_PACKAGE_2026-11-02.md), including confirmation whether a reproducible empirical/evaluation-integrity dissertation route is acceptable and whether data from a genuinely independent model/source are necessary. If these decisions are not authorized, stop before further algorithmic experimentation. I65 `novelty not established / DRAFT / NO-FREEZE / COCO NOT_RUN`.
