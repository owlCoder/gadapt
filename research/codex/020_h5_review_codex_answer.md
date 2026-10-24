**Verdict: REVISE before freezing the protocol.** H5 could support a PhD chapter, but the novelty claim is overstated and R1 is only partly resolved. No files were changed.

**1. Literature findings**

- **Mallipeddi et al. 2012:** Publisher §3 explicitly states “reactive power source installations are integer variables” and “tap positions of the tap changing transformers are discrete”; generator voltages are continuous. Thus discrete taps/shunts are confirmed prior art. Publisher snippets establish four individual CHTs plus their ensemble, with evaluation budgets varying by network. **I could not recover the complete paper** through publisher access, ResearchGate, KNU/NTU searches, author sites, or thesis searches. Consequently, adaptation/control-parameter factors and discretization sweeps remain **unverified**, not absent. [Publisher text](https://www.sciencedirect.com/science/article/pii/S2210650212000247).

- **Biswas et al. 2018:** Recovered the author full text. Table 2 fixes \(F=0.7,\ CR=0.9\); §4 describes a “pre-fixed crossover rate.” Population size was selected through preliminary trials, rather than crossed as an experimental factor. **No adaptation on/off factor.** Section 5.5 explicitly treats “both (shunt) capacitor banks and transformer taps” as discrete: capacitor steps **0.2 MVAr**, taps **0.02 p.u.**, range **0.90–1.10**. It compares this additional case with the continuous case, but does **not sweep discrete resolutions**. [Author manuscript, §§4–5.5, Tables 2/A.7](https://www.researchgate.net/publication/321211738_Optimal_power_flow_solutions_using_differential_evolution_algorithm_integrated_with_effective_constraint_handling_techniques).

- **Critical missing prior art:** Premkumar et al. **2023**, DOI **10.1049/gtd2.12738**, compares **SHADE-SFS, SHADE-SAP, DE-SFS, DE-SAP**, plus an ensemble, on IEEE30/118 with discrete taps/shunts. This already crosses adaptive versus conventional algorithm families with CHT. However, §3.1.4 describes adaptive \(F,CR\), while §4 says their values are **0.5 for all algorithms**. It is therefore an ambiguous, confounded predecessor—not a clean same-operator adaptation ablation. It materially weakens the broad novelty claim. [Full text](https://www.researchgate.net/publication/366903430_A_reliable_optimization_framework_using_ensembled_successive_history_adaptive_differential_evolutionary_algorithm_for_optimal_power_flow_problems).

The 2015 DEEPSO paper explicitly says “Parameter control is out of scope of this research work.” A **2026** QPSODM paper compares ε/SFS/SR and varies population/iteration settings, but supplies no adaptation on/off crossing. Neither closes H5’s narrower causal question. [2015 author copy](https://repositorio.inesctec.pt/server/api/core/bitstreams/800bcc3e-1f0b-4203-95be-f3fa366a1a82/content), [2026 paper](https://www.nature.com/articles/s41598-026-46233-2).

**2. Required design revisions**

**Matched fixed arm.** Split by **instances/operating scenarios**, not merely seeds. Estimate constants using development instances only, weighting runs equally over a fixed evaluation horizon. Freeze one parameter vector per CHT, pooled across resolutions; separately report any resolution-specific tuning. Freeze every adaptive component included in the estimand, including mutation scales. Trajectory medians are a descriptive match, not necessarily a competitive fixed configuration: add a fixed arm tuned on development data with a declared tuning budget.

**Adaptation signals.** Keep CHT selection separate from its scalar adaptation input. Let \(V\ge0\) be tolerance-adjusted, dimensionless aggregate violation; freeze its normalization. Define \(u(z)=\frac12+\arctan((z-a)/s)/\pi\), with development-only \(a,s>0\), and \(w(V)=V/(1+V)\).

Use positive merits:

- **Static/adaptive penalty:** \(m=1+u(P_t)\), where \(P_t\) is that CHT’s actual penalized objective.
- **Feasibility rules:** \(m=1+u(f)\) if feasible; otherwise \(m=2+w(V)\).
- **ε-constraint:** the same definition, replacing feasibility with \(V\le\epsilon(t)\); freeze the ε schedule.
- **Stochastic ranking:** \(m=1+\Pr(R\text{ beats }x)\), averaging its actual stochastic comparator against a **frozen reference distribution**, with half credit for ties. Freeze \(p_f\) and the reference distribution before evaluation.

Apply GAdapt’s survivor log-range normalization to \(m\); prescribe zero-initial-range and failed-PF behavior explicitly. **Current-population ranks are unsuitable:** their range can remain constant during convergence. Add a common-signal ablation; otherwise “CHT interaction” also includes your newly chosen scalarization.

**Device evidence.** Reading installed PYPOWER 5.1.19 gives:

| Case | Explicit tap entries | Nonzero bus \(B_s\) | Generator \(V_g\) entries |
|---|---:|---:|---:|
| 14 | 3 | 1 | 5 |
| 30 | **0** | 2 | 6 |
| 57 | 17 | 3 | 7 |
| 118 | 9 | 14 | 54 |

These are operating data, **not hardware step/range specifications or proof of controllability**. In case118, two shunts are reactors. Model \(B_s\) consistently with voltage-dependent injection. Generator-voltage quantization is an imposed control-resolution assumption. Cases14/57/118 use 9900-MVA branch ratings throughout, providing little thermal-constraint pressure. With fixed tap bounds 0.9–1.1, nested 9/17/33 grids imply steps **0.025/0.0125/0.00625**.

**PES2014:** The official page still links the test-bed ZIP; execution compatibility remains unchecked. It uses encrypted MATLAB/MATPOWER code, OLTC taps and switched shunts. Published budgets are **10k/50k/100k/300k function evaluations**, respectively WPP/57/118/300, **31 trials**. Those evaluations need not equal individual AC solves. Prefer it for external validation; changing its grids requires accessible device definitions. [Official downloads](https://www.uni-due.de/ieee-wgmho/competition2014), [budget/control specification](https://www.uni-due.de/imperia/md/content/ieee-wgmho/testbed.pdf).

**Power and target.** Fifteen paired seeds detect only a large standardized interaction: approximately **0.78 SD** at 80% power, two-sided α=.05, under a normal paired-contrast model. About **34** detect 0.5 SD before multiplicity. Simulate power for the actual censored attainment outcome; four networks do not identify a general “network-size effect.”

Freeze independently generated, feasible reference incumbents **per instance and grid**, with certified lower bounds where available. Call these best-known references unless optimality is proved. Avoid references derived from evaluation runs. Use an absolute-plus-relative target tolerance and report censoring.

**3. PhD value**

**Potentially enough for a chapter after revision; insufficient as currently framed.** Preregistration alone adds no substantive novelty. The valuable contribution would explain **when constraint-induced feedback helps or harms adaptation**, reproduce it across operating scenarios, and deliver a validated opt-in constraint interface, diagnostic traces, and actionable configuration guidance. Narrow the novelty claim accordingly; keep the 2012 gate open.