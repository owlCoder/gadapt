# I65 independent AC model/data admission screen — workstream B

**Date:** 2026-11-02. **SCREENING ONLY / NOT_RUN.** No external case downloaded, solved, converted or used for optimization. No signed supervisor approval. Existing numerical independence is software independence on a common case, not independent physical truth.

## Levels of independence

| Level | Distinct evidence required | Current result |
|---|---|---|
| L0 | Reproduction of frozen original network result | PASS only for one development case |
| L1 | Independently coded numerical AC PF using unsolved input case | PASS for one fixed case (GitHub Actions #41419711114) |
| L2 | Different, versioned case source with independently audited origin and legal rights | NOT_TESTED |
| L3 | Independently validated network data and model assumptions | NOT_ESTABLISHED |
| L4 | Traceable field measurements and equipment records, permission and calibration | NO DATA PROVIDED |

## Independent source candidates, read-only verified metadata

**PGLib-OPF**: [official library](https://github.com/power-grid-lib/pglib-opf), [reference baseline](https://github.com/power-grid-lib/pglib-opf/blob/master/BASELINE.md), [changes](https://github.com/power-grid-lib/pglib-opf/blob/master/CHANGELOG.md). Curation is attributed to an IEEE PES task force; it provides MATPOWER-format AC-OPF cases, source citations in headers, reference objectives and case files under **CC BY 4.0** (individual attribution must still be preserved). The baseline references v23.07, which is a reference version here, **not a statement of the latest release**. Because each release changes, pin actual tag/commit and archived original bytes before any study. Cases labeled API/SAD deliberately modify base demand/angle conditions; they are not independent physically measured networks. The [30-bus Alsac/Stott variant](https://github.com/power-grid-lib/pglib-opf/blob/master/pglib_opf_case30_as.m) explicitly shares a source family with historical PYPOWER case30; counting it as distinct physical provenance would be invalid. Different named cases such as the EPRI 39-bus case could be screened but require a source-header and original-provenance review before L2 admission.

**UW Power System Test Case Archive**: [UWEE PSTCA](https://labs.ece.uw.edu/pstca/) lists IEEE Common Data Format cases (including 30/57/118/300 buses). This is a separately maintained source archive for an external data-lineage audit. A CDF 30-bus input may still share original benchmark ancestry with MATLAB/PYPOWER case30. Per-file rights, conversion procedures and any measurements remain unverified. Do not equate different storage format with independent grid evidence.

**PowerModels.jl with Ipopt**: PGLib [reference baseline](https://github.com/power-grid-lib/pglib-opf/blob/master/BASELINE.md) gives AC-OPF objective values from a separate software stack. This strengthens numerical-software reproducibility but is not a separate network dataset. The AC-OPF optimum or objective is not automatically an ORPD discrete optimum with original fixed-PG decisions.

**Utility/operator measurement data**: not available in the repository. Require lawful data-owner authorization, timestamp/source identification, equipment/topology and limits, measurement calibration, anonymization policy and disclosure rights. No amount of numerical agreement can substitute for missing observational provenance.

## Proposed admission checklist, not an implemented protocol

1. **Identity and rights** — exact immutable source version and original file SHA-256, author/case header, license/attribution, data-owner contact where required, archived conversion recipe and all numeric units.
2. **Mathematics and equipment** — baseMVA, REF/PV/PQ encoding, disconnected buses/islands, generator status and multiple generators at one controlled bus, shunts, phase-shifting taps, branch charging, reactive/active generator bounds, thermal ratings and ANGMIN/ANGMAX phase-angle bounds.
3. **Current code limits** — the independent research-only Newton PF has no generator Q-limit enforcement or automatic PV-to-PQ switching. Independent generator reconstruction rejects multiple online generators at one controlled PV/REF bus because individual Q allocation is underdetermined. Do not silently merge generator rows or delete constraints to obtain convergence.
4. **ORPD-specific interpretation** — record actual eligible original I56 controls per case, not assumed transformer flexibility. In the previous case30/j1 input these are VG=6, TAP=0, BS=2. An external case requires its own approved grid/PG handoff, feasible-start, constraint and statistical design.
5. **Failure semantics** — PF convergence alone must not imply feasible dispatch. Report numerical, model-support, input-rights and operational-feasibility outcomes independently, including unsupported angular/capability constraints.

## Shortlist and independent-evidence limits

| Candidate | Potential use | Strict current status |
|---|---|---|
| PGLib 39-bus EPRI case, pinned revision | Different named AC-OPF model source and software portability | SCREEN ONLY; original origin and multi-gen topology not yet reviewed |
| PGLib 30-bus IEEE/Alsac-Stott variants | Source-family and conversion differences; historical comparison | SCREEN ONLY; shared ancestry, **not independent physical data** |
| UW IEEE CDF 30-bus | External archival source/format check | SCREEN ONLY; conversion and rights unverified |
| PGLib API/SAD variant | Adversarial thermal and phase-angle model testing | SCREEN ONLY; derived from base case, and historical I56 lacks angle-constraint coverage |

## Decision and falsification

A claim of **new physical measurements** fails without genuine observed owner-verified records. A claim of **independent data** fails if both files derive from the same source model with reformatting. A claim of **full physical feasibility** fails if Q capability, angular, voltage or thermal constraints are ignored or violated; the existing fixed case30 midpoint remains reactively infeasible. A claim of **general ORPD performance** fails if the new case has unsupported controls or if optimizer experiments are not separately approved.

**GO:** supervisor to choose the required L2/L3/L4 independence level, pin a permitted source, conduct source-header rights and topology review. **NO-GO:** run external optimization, change historical sources, represent transformed academic cases as field truth, or approve new algorithm results. M3/C4/C5 and M6/C1 remain unsigned.
