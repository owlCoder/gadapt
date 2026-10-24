**Partly established overall; the exact claim remains open in the literature located.** Empirical constraint-handler comparisons already exist on **discrete ORPD**, and epsilon handling has already been combined with adaptive DE. I found no study establishing that epsilon reduces a prespecified, capped time-to-feasible-target relative to both penalty and feasibility rules under the same self-adaptive GA. This is a bounded search conclusion, not proof of absence.

The closest precedent is **Mallipeddi et al. (2012)**: DE with superiority of feasible solutions (SF, corresponding to feasibility rules), self-adaptive penalty, epsilon constraint, stochastic ranking, and their ensemble, tested on IEEE 30/57/118. Transformer taps are explicitly discrete and reactive-source installations integer; budgets are 6,000/12,000/30,000 evaluations. Thus, “comparing constraint handlers on discrete ORPD” is already established prior art. The accessible sections do not justify declaring epsilon the universal winner. [Publisher record and methods/results excerpts](https://www.sciencedirect.com/science/article/pii/S2210650212000247).

Two further precedents narrow the novelty. **Subbaraj and Rajnarayanan (2009)** already apply a self-adaptive real-coded GA to ORPD with continuous voltages, discrete taps, and binary VAR sources; **Biswas et al. (2019)** integrate epsilon handling with SHADE for deterministic and stochastic ORPD. Neither accessible account establishes the exact controlled GA comparison and target-attainment endpoint proposed here. [SARGA study](https://www.sciencedirect.com/science/article/abs/pii/S0378779608002046), [SHADE-EC study](https://www.sciencedirect.com/science/article/abs/pii/S1568494618306744).

A particularly relevant recent comparison is **Naidji et al. (2026)**: within one QPSO-with-differential-mutation framework, epsilon outperforms or statistically matches SF in most OPF cases, while stochastic ranking generally performs worse. However, **taps are explicitly modeled continuously**, and the study reports final performance, convergence, and execution time rather than H60’s common-target hitting-time statistic. It supports conditional advantages, not the precise discrete-ORPD claim. [Full paper](https://www.nature.com/articles/s41598-026-46233-2).

**Schedule and anytime interpretation.** The familiar schedule
\[
\epsilon(g)=\epsilon_0(1-g/T_c)^{c_p},\quad g<T_c;\qquad \epsilon(g)=0,\quad g\ge T_c
\]
is longstanding. Mallipeddi and Suganthan report recommended ranges \(c_p\in[2,10]\) and \(T_c/T_{\max}\in[0.1,0.8]\); H60’s \(c_p=5,\ T_c/T_{\max}=0.5\) lies inside them. These ranges do **not** establish an optimal schedule for ORPD or short budgets. Once epsilon reaches zero, its comparison reduces to feasibility rules. [Original ECHT paper](https://www.researchgate.net/publication/220381210_Ensemble_of_Constraint_Handling_Techniques).

From [H60’s protocol](/Users/danijel/Desktop/gadapt/research/ITERATION60_PROTOCOL.md), the cutoff is approximately 1,536 actual PF calls. Its \(T=\min(\tau/3000,1)\) measures **capped evaluation effort**, combining attainment speed and failure to attain; it is neither wall-clock time nor unrestricted expected runtime. Final losses and convergence plots cannot establish superiority on this endpoint.

**What the experiments can add, one sentence each:**

- **H60:** A preregistered, paired test of whether GAdapt’s fixed epsilon schedule reduces mean capped PF evaluations to an independently verified feasible reference-relative target versus \(f+1000V\), on the specified project-held-out ORPD instances and budget.
- **H58:** A preregistered, paired test of whether GAdapt’s integrated Deb feasibility rules reduce that same capped target-attainment measure versus \(f+1000V\), under the frozen configuration and instances.

Neither tests superiority over penalties generally, schedule optimality, or the benefit of self-adaptation itself; **H60 does not directly test epsilon versus FR**, and separate H58/H60 outcomes cannot supply that missing comparison. “Fresh networks” should mean held out within this project: IEEE case30 is already extensively studied.

The following **eight references belong in chapters 2/6**. DOI checks were attempted live; resolution verification must be distinguished from publisher-supported bibliographic identification.

**DOI resolution verified:**

1. **Takahama & Sakai (2010), “Constrained optimization by the epsilon constrained differential evolution with an archive and gradient-based mutation.”** Foundational epsilon-DE precedent; its combined algorithm must not be treated as an isolated handler ablation. [DOI](https://doi.org/10.1109/CEC.2010.5586484) resolved to the matching IEEE document number; full text encountered a robot check.
2. **Naidji et al. (2026), “Comparative analysis of advanced constraint-handling in quantum PSO with differential mutation for optimal power flow.”** Current controlled OPF comparison, with the continuous-tap limitation. [DOI](https://doi.org/10.1038/s41598-026-46233-2) resolved to the matching full paper.

**DOIs unverified through doi.org/Crossref in this session**—reported by publisher records or paper text, not guessed; resolver/API access failed:

3. **Deb (2000), “An efficient constraint handling method for genetic algorithms.”** FR foundation and empirical GA evidence. [DOI](https://doi.org/10.1016/S0045-7825(99)00389-8).
4. **Runarsson & Yao (2000), “Stochastic ranking for constrained evolutionary optimization.”** SR foundation; experiments use evolution strategies. [DOI](https://doi.org/10.1109/4235.873238).
5. **Mallipeddi & Suganthan (2010), “Ensemble of Constraint Handling Techniques.”** Direct SF/penalty/epsilon/SR comparisons and ensemble evidence. [DOI](https://doi.org/10.1109/TEVC.2009.2033582).
6. **Mallipeddi et al. (2012), “Efficient constraint handling for optimal reactive power dispatch problems.”** Closest discrete-ORPD precedent. [DOI](https://doi.org/10.1016/j.swevo.2012.03.001).
7. **Subbaraj & Rajnarayanan (2009), “Optimal reactive power dispatch using self-adaptive real coded genetic algorithm.”** Essential boundary on self-adaptive-GA novelty. [DOI](https://doi.org/10.1016/j.epsr.2008.07.008).
8. **Biswas et al. (2019), “Optimal reactive power dispatch with uncertainties in load demand and renewable energy sources adopting scenario-based approach.”** Adaptive-DE plus epsilon ORPD precedent. [DOI](https://doi.org/10.1016/j.asoc.2018.11.042).