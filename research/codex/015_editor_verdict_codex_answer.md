**My desk decision: reject at TELO; reject at EMSE/TOSEM/JSS in its present form.** There is publishable work here, but the manuscript currently reads as a conscientious investigation report whose scientific argument remains unfinished.

I read :codex-file-citation{path="/Users/danijel/Desktop/gadapt/research/paper_integrity_audit/manuscript.md" purpose="source"} and inspected the compiled presentation in :codex-file-citation{path="/Users/danijel/Desktop/gadapt/research/paper_integrity_audit/tex/main.pdf" purpose="source"}. I did not recheck numbers or modify files.

The five main reasons, ranked:

1. **The central contribution is insufficiently resolved.** The paper alternates between prevalence study, testing method, bug catalogue, reproducibility study and practitioner tool. Seven contributions enumerate outputs rather than establish one important advance. TELO needs a stronger implication for optimization research; an SE journal needs transferable knowledge about testing scientific software.

2. **“Integrity” combines different kinds of observations.** Contract violations, documented behavior, adapter choices, computational inefficiency and unmet user expectations share an umbrella. The qualifications are honest, but the organizing concept remains unstable. Returning something other than the best evaluated point is not universally incorrect; neither are boundary visits or repeated evaluations.

3. **The design supports existence and mechanism better than prevalence or generality.** One algorithm/configuration per library, different budgets, purposive and compatibility-filtered selection, and one application family support bounded case findings. They do not characterize libraries generally. More seeds cannot repair that mismatch. Agreement that includes many negative/negative cases is also weaker evidence of transfer than its headline suggests.

4. **Validation establishes basic operation, not comparative scientific value.** Planted faults demonstrate that several intended predicates fire. They do not establish robust discrimination between defects and legitimate behavior, complete detector coverage, or added effectiveness over existing logging/testing approaches. Known Study 1 findings can support replication, but do not independently establish novelty.

5. **The manuscript follows the investigation’s chronology instead of developing an argument.** Corrections, reruns, protocol identifiers and disclosure status repeatedly interrupt the research story. Preregistration strengthens procedural transparency; it cannot supply an interesting question or validate a weak construct.

**On form:** the PDF looks recognizably academic, but typesetting does not solve the problem. The abstract is an overloaded miniature report: too many outcomes, corrections, issue discoveries and archive-reproduction details. Reduce it to problem, approach, principal insight and bounded evidence.

Bullets are appropriate for predicates, configurations and a checklist. Related work, interpretation and discussion need connected prose that compares alternatives and derives conclusions. The present discussion largely repeats findings. Add a conclusion that answers the research questions.

The tables are useful inventories, but the findings table sprawls across pages with narrow columns and awkward code wrapping. Keep a compact synthesis table; develop two or three mechanisms in prose. Reduce the contributions list to three defensible claims.

Move I49–I55 mappings, filenames, launcher commands, deviation codes and disclosure chronology into an artifact appendix. Keep a concise account of material corrections and their consequences in the paper. Appendix A is a predicate specification, not substantial formal analysis; its implementation details should not be presented as theoretical depth.

**On substance:** “How often do libraries behave unexpectedly?” has an empirical answer, but the current sample makes that answer narrow. “Bugs exist and seeds are insufficient” is familiar. A stronger question is: **Which observable properties distinguish an optimizer’s execution from its advertised evaluation contract, and where does black-box observation fail?**

A referee could identify a worthwhile insight: recording objective calls is insufficient unless those calls are related to returned results, declared obligations and process/environment controls. The SMAC, Nevergrad and SciPy mechanisms make that concrete. Corner detection provides the complementary lesson that observing geometry does not establish purpose. This becomes research through synthesis and explicit limits; merely integrating prior components remains primarily engineering.

A defensible thesis from the same evidence would be:

> Optimization comparisons depend on an execution contract covering objective calls, reported results and reproducibility conditions. We operationalize selected obligations as trace-based checks and investigate them in 21 specified library configurations. Mechanistic diagnoses show how reporting transformations, nested randomness and result-acceptance policies can undermine common comparison assumptions. Other observations reveal legitimate design choices that resemble defects. The resulting contribution is a bounded account of what black-box auditing can establish, what requires contract interpretation, and what remains unobservable.

Use this section sequence: problem and research questions; related work and gap; contract model and observability limits; audit and validation; empirical design; results organized by mechanism; implications and limitations; conclusion.

A useful formal element would define a trace, result, environment and explicit contract, with applicability conditions for each check. Add a modest indistinguishability proposition: identical observed traces cannot distinguish a legitimate boundary evaluation from a hidden validation probe without additional information about purpose. That explains the C1 failure and constrains the method’s claims. More notation alone adds nothing.

New evidence is needed for broad prevalence, comparative detection effectiveness, configuration robustness or claims that auditing changes benchmark rankings. A narrowly framed diagnostic paper can use the existing evidence.

**My recommendation: pursue a focused short research/tool paper first.** JSS is my best journal-fit judgment, conditional on deriving general SE knowledge—an explicit requirement in its [scope](https://shop.elsevier.com/journals/journal-of-systems-and-software/0164-1212). A journal rewrite is worth attempting only around the contract-and-observability thesis. The current material exceeds “thesis chapter only,” but I would not invest in polishing this journal narrative without fundamentally rebuilding it.