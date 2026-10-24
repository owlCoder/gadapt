The defensible thesis is an empirical investigation of constraint handling and diversity-driven adaptation, coupled with a validated improvement to GAdapt. **I56 alone cannot establish practical improvement or a new optimization method.** The statements below are conditional drafts; the record describes I56/I57 as ongoing and the API patch as awaiting integration.

**1. Dissertation outline**

Working title: *Constraint Handling and Diversity-Driven Adaptation in GAdapt for Discrete Infrastructure Optimization.*

| Chapter | Contribution and supporting iterations |
|---|---|
| **1. Problem, research questions, and related work** | Define the infrastructure requirement: feasible solutions under limited simulation budgets. Distinguish established CHT methods, GAdapt engineering, and the empirical question. Use the direction decision, rejected-candidate audits, and H5. Avoid “first” while Mallipeddi 2012 remains incompletely checked. |
| **2. Evaluation foundations and diagnostic evidence** | Establish trustworthy evaluation accounting and summarize GAdapt’s observed limitations. I43–I46 support the routing diagnosis; I47–I48 establish contrasting dispatch results; I53 tests one specific oracle intervention. Retain only relevant lessons from I49–I52/I55. This chapter motivates the investigation rather than carrying its originality claim. |
| **3. Discrete ORPD model and experimental design** | Specify controls, assumed grids, violations, scenarios, references, exclusions, development/test separation, and budgets. Explain why the factorial intervention isolates the whole adaptive mutation policy. Supported by the I56 benchmark, protocol, and clarifications. Contribution: an inspectable experimental foundation. |
| **4. Constraint handling × adaptive mutation policy** | Present I56’s primary FR-versus-SP interaction against development-tuned fixed mutation, then corrected secondary contrasts and signal interventions. Report resolution patterns descriptively. Contribution: the central empirical finding, including uncertainty and scope. |
| **5. External performance context** | Present I57’s GAdapt, CMAwM, DE, and random-search results for attainment, feasibility, and feasible loss. Contribution: practical context. Preserve its descriptive status and disclose GAdapt-derived targets. |
| **6. Constraint handling in the actual library** | Document the opt-in API, dynamic rescoring, adaptation signals, result semantics, compatibility, and examples. Support with the reviewed patch, integration checks, and the proposed validation below. Contribution: usable software, with performance claims requiring direct evidence. |
| **7. Synthesis and limits of applicability** | State which configurations help, where evidence remains inconclusive, and what transfers beyond the tested settings. Separate empirical knowledge, engineering achievements, and unresolved questions. |

The [I56 protocol](/Users/danijel/Desktop/gadapt/research/ITERATION56_PROTOCOL.md) supports a primary CHT × policy contrast; it does **not** provide confirmatory evidence of a three-way interaction with resolution or a general network-size effect.

**2. Conditional contribution statements**

**If interaction is detected:**  
“This dissertation establishes, within the studied discrete ORPD scenarios and evaluation budget, that the performance effect of GAdapt’s diversity-driven adaptive mutation policy depends on constraint handling. A preregistered comparison using the same variation operators estimates the difference in adaptive-versus-tuned-fixed performance under feasibility rules and static penalties. Secondary signal interventions assess whether changing the scalar values consumed by adaptation affects performance; resolution patterns delimit the observed result. The work also delivers an opt-in constraint-handling implementation in GAdapt and evaluates its practical behavior against the original configuration and external optimizers. The contribution comprises specific empirical knowledge and validated software; broader superiority and general applicability remain outside the evidence.”

**If interaction is not detected:**  
“This dissertation evaluates whether GAdapt’s adaptive mutation policy responds differently to feasibility rules and static penalties on discrete ORPD and reports the estimated interaction with its uncertainty. The preregistered primary contrast does not detect an interaction under the studied scenarios, references, fixed-policy tuning, and budget. This finding does not establish independence, equivalence, or the absence of effects within individual settings. Secondary analyses, external comparisons, and an opt-in constraint-handling implementation document the consequences for GAdapt users. The contribution comprises a reproducible empirical assessment and software capability; any claim of practical improvement requires separate observed gains.”

A wide interval makes the second outcome **inconclusive**. A null result plus an API is not automatically a sufficient doctoral contribution.

**3. Biggest remaining gap and cheapest credible closure**

The committee’s strongest attack is: **“You measured a library-specific interaction, but where is the original, reproducible improvement to infrastructure optimization?”** Statistical interaction can occur while every configuration performs poorly. Moreover, the [API design](/Users/danijel/Desktop/gadapt/research/GADAPT_CONSTRAINT_API_DESIGN_SR.md) leaves adaptation scaling open because the library lacks I56’s OPF-derived reference scale.

My recommended next-weeks closure is a small, preregistered validation of the **integrated library**, on fresh public ORPD cases/scenarios with justified device steps and meaningful constraints:

- Freeze one recommended configuration before validation.
- Compare original GAdapt, the integrated configuration, CMAwM, and DE at two simulation budgets; report feasibility, feasible loss, attainment, and runtime.
- Independently check returned solutions and have another researcher execute the frozen package.

This directly tests the product claim with limited new infrastructure. A second domain would strengthen breadth but add modeling work; a theorem would need a distinct, substantive result. Close the [Mallipeddi literature gap](/Users/danijel/Desktop/gadapt/research/H5_PROPOSAL_SR.md) before asserting originality. If improvement remains absent, narrow the thesis claim and acknowledge that the mentor’s improvement requirement remains unmet.

**4. Material to remove or demote**

- Remove the integrity-audit manuscript as a central contribution; retain a short methods section and appendix.
- Move I42 and the twelve rejected candidates to a concise research-selection appendix.
- Exclude withdrawn I54 as evidence.
- Exclude unavailable I39 data from quantitative support.
- Remove claims that I53 establishes geometry as the cause, that I48 proves diversity caused the smaller gap, or that I47 demonstrates feasible-dispatch superiority.
- Replace iteration-by-iteration chronology with research questions and evidence.