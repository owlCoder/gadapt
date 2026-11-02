# I65 — provenance of the ORPD `case30` input and preregistered source-lineage audit

**Date:** 2026-11-02. **Repository baseline:** `owlCoder/gadapt/main` at `4e922ae9b0eda6821b78f49837f1dc56c1cbde55`.  
**Decision:** strictly bounded integrity/data-lineage diagnostic **GO**; **scientific novelty NOT_ESTABLISHED**, no optimizer/COCO experiment, no protocol freeze.  
**At initial publication:** real full-history Python 3.12 data-lineage workflow **NOT_RUN**; prior 47/47 generator/dispatch CI PASS is independent and does not prove underlying dataset provenance.

## 1. The source network is a modified benchmark, not field measurements

The historical [I56 ORPD instrument](legacy/flat/iteration56_orpd.py) loads `getattr(pypower.api, case_name)()`. For I58 [`NETWORKS`](legacy/flat/iteration58_validation.py), its tested `case30` is a **PYPOWER-bundled 30-bus, six-generator numerical benchmark**, not a separately surveyed real electric grid.

Authoritative references:

- [MATPOWER `case30` source documentation](https://matpower.org/docs/ref/matpower4.1/case30.html) describes a 30-bus, six-generator **modified** benchmark based on Alsac and Stott (1974). Its stated transformations include rounding line parameters, rescaling/moving shunts and zeroing the load at bus 5; generator properties and economics derive partly from later references. These historical modifications are documented in MATPOWER, **not inferred from numeric matching in our runner**.
- [MATPOWER `case_ieee30` documentation](https://matpower.org/docs/ref/matpower4.1/case_ieee30.html) instead describes a case converted from the IEEE Common Data Format record, including the 1993 Washington archive. **Do not conflate `case30` with `case_ieee30` or treat either as new independent field measurements.**
- [PYPOWER 5.1.19 release](https://pypi.org/project/PYPOWER/5.1.19/) identifies the exact version pinned in recent Python 3.12 CI runs. The upstream [PYPOWER project](https://github.com/rwl/PYPOWER) states its **case data are excluded from the project's BSD software license** and can come from permissioned or public sources. **Do not copy the case arrays into this repository, relicense them or present them as original acquired data**.
- No byte-identical or row-by-row match of `PYPOWER 5.1.19 case30` to a specific `MATPOWER case30.m` commit has yet been established. **Source-family provenance is documented; exact external case-file equivalence is still UNVERIFIED.**

## 2. The historical transformation, exact I56/I58 research source semantics

The frozen [I56 `ORPD.__init__`](legacy/flat/iteration56_orpd.py) uses an **independent `np.random.RandomState(scenario_seed)`** to produce a per-bus common multiplier for both demand components:

```text
scale_i = load_factor * (1 + spread * (2*u_i - 1))
u_i = RandomState(seed).random_sample(number_of_buses)[i]
PD'_i = PD_i * scale_i
QD'_i = QD_i * scale_i
```

The frozen [I58 `make_problem`](legacy/flat/iteration58_validation.py) chooses `SCENARIOS[j]` and I56 `SPREAD`. For **the previously validated non-held-out development scenario `case30,j=1`**, the exact parameters are `load_factor=1.00`, `scenario_seed=302`, `SPREAD=0.10`, `RESOLUTION=17`. These factors are **synthetic model assumptions**, not observations. The continuous setup `runopf` runs on a copied demand-scaled case, then **only its solution's `PG` is handed back** into the I56 base case. Its OPF result is NOT a second independent physical generator dispatch. Generator VG, selected in-service TAP and original nonzero-BS controls are snapped onto the I56 nested grid, and these three input columns are changed to evaluate any fixed candidate. This is a **model transformation**; a numerical witness on the resulting operating point does not validate the original network inputs.

## 3. Strict, fail-closed implementation

Added [`research/i65/input_provenance_audit.py`](i65/input_provenance_audit.py) — standalone NumPy/Python implementation, no PYPOWER imports. A fingerprint is SHA-256 over canonical sorted field names, array dimensions and **exact float64 little-endian numeric bytes**, covering `baseMVA`, `bus`, `gen`, `branch` and optional `gencost`. Nonfinite numeric data, missing minimum model arrays and changed case fields fail closed. The checker compares **all columns** at all four software stages:

| Stage | Permitted change vs previous stage |
|---|---|
| `raw` | `pypower.api.case30()` as returned; no research-specific edits |
| `scaled` | **Only** `PD/QD` columns, following the historical `RandomState(302)` and `1.00 ± 10%` per-bus multipliers |
| `post_opf` | **Only** `gen[:, PG]` from the result of the historical one-time OPF setup |
| `controlled` | **Only** selected `gen[:, VG]`, `branch[:, TAP]`, `bus[:, BS]` selected by original I56/BusORPD control lists |

Any change in branch resistance/reactance, other load columns, generator Q bounds or statuses, line thermal limits, voltage bounds, gencost matrix or unexpected case keys fails. Overlapping/duplicate or invalid control indices also fail. SHA-256 and exact expected transformation counts are stored, **not** any licensed full case arrays.

**Methodological limitation:** frozen I56 does not expose a separate pre-OPF snapshot. The one-shot smoke **reconstructs** the pre-OPF scaled array from the raw PYPOWER case and the public I56 formula; comparing its later `post_opf` state tests the allowable transformation but does not prove the source path performed no transient unobserved steps. This is a **software provenance audit**, not physical provenance certification.

## 4. Synthetic falsification and one non-held-out model fingerprint

Added **17 small analytic/adversarial tests** [`test_input_provenance_audit.py`](i65/test_input_provenance_audit.py), including exact multi-stage success, deterministic fingerprint, bad seed/spread, altered demands, branch impedance, OPF QG, cost limits, candidate generator/branch/load changes, nonfinite values, invalid control indices and extra case keys. **Their Python 3.12 result is still NOT_RUN in this preflight.** They do not load a real network or call an optimizer.

A separate [single-case development-only smoke](i65/smoke_input_provenance_audit.py) checks one existing I58 `case30,j=1,R=17` scenario: **exactly one original `runopf` in setup; zero `runpf` and zero optimization search**. It records the SHA-256 of the **actual installed PYPOWER 5.1.19 `case30.py` source**, a canonical numeric fingerprint of original and transformed cases, the detected PYPOWER package version, historical source blobs and a difference test versus `case_ieee30` **only if that module is available**. Its absence is explicitly recorded as unavailable rather than invented evidence. It does not infer a match to a particular external MATPOWER source revision from the case name alone.

The [one-shot full-history CI workflow](../.github/workflows/research-i65-source-lineage-one-shot.yml) is directly bound to original manual root workflow `#41357664531` **attempt 9**, avoiding GitHub's `workflow_run` chain-depth limit, with 8-minute total and **120-second** smoke timeout, pinned Python `3.12`/NumPy `1.26.4`/PYPOWER `5.1.19`; it hashes raw files even on failure. The old-root pipeline's frozen venv problem is only an event trigger, not any result.

## 5. Science and supervisor decision

This audit can validate deterministic **software-model input lineage** and reveal unauthorized hidden transformations on a **public transformed benchmark**. It cannot establish physical measurements, a genuinely independent network model, historical equipment data provenance beyond source-family documentation, independent live-grid validation or novel optimization. Exact external `case30` data equivalence, generator-cost provenance and licensing details still require external data-owner or primary-source review.

**GO:** complete one small trace, archive exact installed version and hashes, describe every synthetic assumption, and ask the supervisor to decide whether a second independently coded numerical PF on this **same input data** suffices for the intended dissertation claim.

**NO-GO:** call `case30` measured grid truth, change the frozen input model or I56 control formula, infer novelty from fingerprinting, run additional candidate-C algorithms or held-out COCO, or freeze a statistical protocol without C1–C6/M1–M6 approval.

**NEXT STEP:** verify real one-shot CI outcome and independent byte-level ZIP/hash evidence; then prepare a **dated English supervisor decision package** identifying exact approvals and independent-data gaps, instead of trying more optimizer experiments. Status stays **DRAFT / NO-FREEZE / novelty not established / COCO NOT_RUN**.

## Actual result (2026-11-02)

The strictly precommitted [run #41422248142](https://github.com/owlCoder/gadapt/actions/runs/41422248142)
completed **SUCCESS** at Python 3.12.15/PYPOWER 5.1.19: **17/17**
adversarial tests PASS and exactly one setup OPF, zero PF/search.
The case30 source-file SHA and four distinct numeric stage fingerprints
were archived. Raw `case30` has **6 VG + 0 eligible TAP + 2 BS**
I56 control variables; it cannot demonstrate transformer tap-control
optimization. The alternative `case_ieee30` was **unavailable through
installed PYPOWER API**, so no numeric variant comparison was performed.
See [full measured result](I65_CASE30_SOURCE_PROVENANCE_RESULT_2026-11-02.md)
and [byte-identical raw output](I65_CASE30_INPUT_LINEAGE_SUCCESS_2026-11-02.json).
A separate [mentor decision package](I65_SUPERVISOR_DECISION_PACKAGE_2026-11-02.md)
remains unsigned/unapproved.
