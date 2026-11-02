# I65 independent prior-art challenge — parallel workstream A

**Review date:** 2026-11-02. **Status:** TARGETED DESK AUDIT, NOT AN EXHAUSTIVE NOVELTY SEARCH. **No new algorithm code or experimental runs.** Baseline `main` at `3c5b68b5705f8de55d285dce30dec12589294e84`.

## Research claim under challenge

Can the doctoral contribution be **an empirical, evidence- and failure-aware characterization of GAdapt**, plus tools that reveal hidden solver evaluation costs and improper feasibility claims? Or is the proposed stagnation-triggered GAdapt→CMA a distinct new optimization algorithm?

**Result:** restarting CMA, portfolios of restarts, benchmark-runtime ECDF/EAF summaries, and replication guidelines have strong direct precedents. The current I65 switch policy is **not established as novel**; infrastructure-specific packaging and negative empirical findings can be described as an applied research contribution only if the supervisor/venue accepts the scope and a reviewer checks substantive differentiation.

## Direct sources inspected and claim boundaries

| Claim challenged | Direct paper / project source | Evidence / DOI verification level | Consequence |
|---|---|---|---|
| Increasing-population CMA restarts are a novel I65 primitive | Auger & Hansen (2005), *A Restart CMA Evolution Strategy with Increasing Population Size*, [DOI:10.1109/CEC.2005.1554902](https://doi.org/10.1109/CEC.2005.1554902), [DBLP record](https://dblp.org/rec/conf/cec/AugerH05.html), [author-hosted paper](https://cma-es.github.io/cec2005/cec2005ipopcmaes.pdf) | Author/DBLP bibliographic records corroborate identifier; Crossref API NOT_ACCESSIBLE | IPOP restart is **prior art**, so reimplementing it is not the thesis's original algorithm |
| A portfolio of large/small CMA restarts is a novel I65 primitive | Hansen (2009), *Benchmarking a BI-population CMA-ES on the BBOB-2009 Function Testbed*, [DOI:10.1145/1570256.1570333](https://doi.org/10.1145/1570256.1570333), [official CMA-ES paper index](https://cma-es.github.io/index.html) | Official project bibliographic record plus DOI external metadata; Crossref API NOT_ACCESSIBLE | BIPOP with two interleaved restart modes is established; generic hybrid/portfolio is insufficient novelty |
| Objective-call ECDF and any-time target curves are new to I65 | Hansen, Auger, Brockhoff, D. Tušar & T. Tušar (2016), [*COCO: Performance Assessment*](https://numbbo.github.io/coco-doc/perf-assessment/), [arXiv:1605.03560](https://arxiv.org/abs/1605.03560) | Official COCO project + primary preprint | Time-to-target measured by **objective evaluations**, censoring and ECDFs predate I65 |
| EAF or area under best-so-far trajectories is an original evaluation metric | *Using the Empirical Attainment Function for Analyzing Single-Objective Black-Box Optimization Algorithms*, [IEEE DOI:10.1109/TEVC.2024.3462758](https://doi.org/10.1109/TEVC.2024.3462758) | IEEE/publisher DOI landing reviewed; Crossref API NOT_ACCESSIBLE | EAF/ECDF/area relationships are prior art; these can be comparison tools, not a claimed invention |
| Source hashing/replay or reproducibility taxonomy is an I65 theory contribution | López-Ibáñez, Branke & Paquete (2021), [*Reproducibility in Evolutionary Computation*, ACM DOI:10.1145/3466624](https://doi.org/10.1145/3466624) | ACM publisher DOI landing reviewed | Repeatability, reproduction and replicability are already separated; a same-data numerical solver validates software replication, **not independent physical truth** |
| Systematic benchmark comparability and time budgeting are first proposed here | *A Methodology for Comparing Optimization Algorithms for Auto-Tuning*, [Elsevier DOI:10.1016/j.future.2024.05.021](https://doi.org/10.1016/j.future.2024.05.021) | Publisher page reviewed; applies specifically to auto-tuning and elapsed-time budgets, so **not equivalent** to an ORPD-specific theorem | Avoid broad first-ever benchmarking or fair-comparison priority claim; do not equate time and solver calls |
| Algorithm-specific failure/landscape maps are a new GAdapt selector theory | *Benchmarking Footprints of Continuous Black-Box Optimization Algorithms*, [Elsevier DOI:10.1016/j.swevo.2025.101895](https://doi.org/10.1016/j.swevo.2025.101895) | Publisher DOI landing reviewed | Problem-dependent footprints and algorithm complementarity are preexisting ideas; causal novelty is not demonstrated |

**Crossref caveat:** direct `https://api.crossref.org/works/<doi>` requests for six DOIs were attempted in this review; the web service returned unavailable/tool error. **Do not mark a Crossref-API validation PASS**. DOI metadata above was instead checked against named publisher, official-project or bibliographic sites. Where Crossref checks are a required institutional gate, leave that gate `NOT_VERIFIED` until a reviewer or a permitted environment can query the API.

## Specific mathematical discriminant and strongest adversarial comparison

Let `P_C` be the I65 proposed policy “after 20 completed GAdapt generations without significant improvement, pass remaining B to CMA”, versus fixed budget split `P_D` (historical E3), restart-only `P_B`, and existing population restart portfolio `P_E` (IPOP). The **switch event and acceptance predicate** do not, on available prior art, exhibit a formally new invariant or asymptotic bound versus established restart/portfolio principles. An implementation of the same switching rule under a strict cost ledger can make the experiment more honest **without changing the algorithmic novelty judgment**.

**Falsifiable, not-yet-implemented research question:** Can one *approved* bounded, pre-specified empirical study demonstrate an interaction between GAdapt mutation/constraint handling and problem families that existing CMA/DE portfolios cannot explain? That is **a future empirical hypothesis**, not a proven new method; current frozen negative and STOP results must be included.

**Strong comparisons:** original GAdapt-M, SciPy DE, CMA, IPOP, BIPOP, fixed historical E3 and all existing matched I64/ORPD controls. Report all negative results: DE wins 14/21 original final-median cells, CMA/IPOP/BIPOP beat GAdapt in extended aggregate ECDF, the ORPD fixed hybrid underperformed IPOP in the existing tested tail, and I59/I61/I63 calibration STOPs did not generate confirmatory studies. These are **repo-derived findings**, not re-estimated here.

## Decision

- **Technical prior-art result:** established prior art rules out any **unsupported** priority claim for restart, switch, ECDF, EAF, ordinary budget reservations or cross-solver repetition.
- **Proposed main contribution class:** **context-dependent empirical characterization and integrity-tool validity (potential; peer/supervisor review needed)**, not a new optimizer or theorem.
- **Gate M6/C1 remains OPEN.** Ask a human reviewer to identify the exact one-sentence contribution, strongest differentiating mathematical/empirical component, target venue and threshold for doctoral sufficiency.
- **NO-GO:** code a new candidate-C optimizer or publish general industrial reliability claims before a documented novelty/scope decision. **NO-FREEZE, held-out COCO NOT_RUN.**
