**The strongest lead is constraint handling × adaptation on genuinely discrete power controls.** The literature supports investigating that interaction; it does not yet establish an original GAdapt method.

Read-only review completed. All DOIs below were verified against publisher or institutional records; titles are shortened. **U** = no closure found in targeted 2024–2026 searches; **P** = partly addressed; **C** = addressed sufficiently to reject the broad novelty claim. These are search findings, not proofs of absence. Fit and proposed questions are my assessments.

1. **OPF: constraint handling and parameter settings.** Ulrich et al. (2025), *Optimal Power Flow Formulations for Coordinating Controllable Loads…*, §5. [10.3390/electricity6020031](https://doi.org/10.3390/electricity6020031).
   
   > “However, only a few articles research the effect of different constraint handling techniques or hyper parameter settings on the performance of the metaheuristic solver.”
   
   **U; high fit:** grids and adaptation provide directly ablatable components. **Question:** Does diversity adaptation improve feasible-target attainment across tap/shunt resolutions, independently of constraint handling?

2. **Mixed-integer plateaus: understanding search behaviour.** Tanabe (GECCO 2024), *Benchmarking Parameter Control Methods in Differential Evolution for Mixed-Integer Black-Box Optimization*, conclusion. [10.1145/3638529.3654019](https://doi.org/10.1145/3638529.3654019).
   
   > “Fitness landscape analysis on the bbob-mixint suite is necessary for a better understanding of the behavior of DE algorithms.”
   
   **P; high fit:** mixed-variable ELA subsequently advanced, but that does not settle adaptation on physical device grids. **Question:** Do grid cardinality and plateau occupancy predict when GAdapt adaptation beats fixed mutation on held-out networks?

3. **Dynamic reconfiguration coordinated with controllable resources.** Behbahani et al. (2024), *Comprehensive Review on Static and Dynamic Distribution Network Reconfiguration Methodologies*, §VI. [10.1109/ACCESS.2024.3350207](https://doi.org/10.1109/ACCESS.2024.3350207).
   
   > “Moreover, future research can be conducted for intelligent coordination strategies to optimize the utilization of these resources alongside dynamic reconfiguration.”
   
   **P; high conditional fit:** binary switches and device grids fit; radiality requires a decoder/repair. [2025 coordination work](https://doi.org/10.1016/j.ijepes.2025.111407) prevents claiming coordination itself. **Question:** Does immigration improve deadline-feasible recovery after unseen load changes as network size increases?

4. **Reconfiguration with demand response.** Yang et al. (2024), *A Critical Review of Active Distribution Network Reconfiguration…*, §5. [10.32604/ee.2024.054662](https://doi.org/10.32604/ee.2024.054662).
   
   > “Unfortunately, DRs are usually ignored in ADNR, which contradicts reality and application.”
   
   **C for “add DR”; medium fit.** [2025 work](https://doi.org/10.1016/j.compeleceng.2025.110227) and [2026 work](https://doi.org/10.3390/pr14020241) explicitly coordinate DR and reconfiguration. **Question:** Does joint search outperform sequential DR–topology optimisation under identical models and budgets? Useful experiment; weak novelty.

5. **Unbalanced, reconfigurable networks with EVs.** Gholami et al. (2022), *State-of-the-art technologies for volt-var control…*, §4. [10.1016/j.egyr.2022.06.080](https://doi.org/10.1016/j.egyr.2022.06.080).
   
   > “Therefore, voltage control of unbalanced reconfigurable networks which are under high penetration of electric vehicles and other RESs could be another open topic.”
   
   **P; high encoding fit.** [2025 distributed planning](https://doi.org/10.1016/j.apenergy.2024.124449) already combines unbalance, EV charging and reconfiguration. **Question:** Does adaptation improve out-of-sample voltage feasibility under uncertain EV allocation? The remaining contribution must exceed combining these ingredients.

6. **SCOPF/UC: computational scalability under uncertainty.** Roald et al. (2023), *Power systems optimization under uncertainty…*, §15.0.4. [10.1016/j.epsr.2022.108725](https://doi.org/10.1016/j.epsr.2022.108725).
   
   > “Across all applications and methods, one of the principal challenges is computational scalability.”
   
   **U broadly; low–medium fit:** populations multiply scenario evaluations; GAdapt supplies no decomposition or bound. **Question:** Can grid-based search beat decomposition in independently AC-validated feasible cost before a fixed deadline as contingency counts grow?

7. **UC/planning: insufficient AC-network fidelity.** Motta et al. (2024), *Survey of optimization models…with demand response*, conclusion. [10.1016/j.ejor.2023.01.019](https://doi.org/10.1016/j.ejor.2023.01.019).
   
   > “An ACOPF model is seldom employed in either operation or expansion planning models.”
   
   **P; medium fit:** commitment bits fit naturally, continuous dispatch less strongly. [2025 robust SCUC](https://doi.org/10.1016/j.egyr.2025.04.069) advances smart-device coordination using MILP. **Question:** Does full AC validation reverse the apparent ranking of GA and approximate mathematical schedules?

8. **Expensive, high-dimensional mixed-variable optimisation.** Talbi (2024), *Metaheuristics for variable-size mixed optimization problems…*, conclusion. [10.1016/j.swevo.2024.101642](https://doi.org/10.1016/j.swevo.2024.101642).
   
   > “Very few works try to solve (V)MVOPs that involve both expensive objective functions and high number of mixed variables.”
   
   **P; medium fit:** native grids help representation, not sample efficiency or variable-length genomes. [PWAS, 2025](https://doi.org/10.1007/s10957-024-02596-y) addresses medium-sized mixed problems. **Question:** At what evaluation budget does GAdapt overtake surrogate search on constrained network simulators?

9. **Telecom: joint IT–optical resource optimisation.** Miyamura and Misawa (2024), *Recent Progress in Optical Network Design and Control…*, abstract. [10.1587/transcom.2023PNI0001](https://doi.org/10.1587/transcom.2023PNI0001).
   
   > “One of the important open challenges lies in multilayer resource optimization including IT and optical network resources.”
   
   **C as a generic proposal:** this same paper supplies adaptive joint MILP optimisation. **Medium fit:** placement/capacity catalogues fit grids. **Question:** Can GAdapt improve deadline primal solutions under nonlinear simulation? Requires a narrower gap and additional optical data.

10. **Transport: demonstrate the value of modelling uncertainty.** *Network design, line planning and timetabling…with uncertain parameters* (2026), abstract. [10.1016/j.ejtl.2026.100174](https://doi.org/10.1016/j.ejtl.2026.100174).
    
    > “The value of including uncertainty in the optimisation is often not quantified, and real-life applications that can estimate its benefits are scarce.”
    
    **U; medium fit:** route-pool selections and integer frequencies fit. **Question:** Does scenario-based GA planning reduce held-out passenger delay versus deterministic planning at equal fleet cost? Public topologies alone lack passenger-demand evidence.

11. **Real-world MOEA adaptability.** Zatarain Salazar et al. (online 2024), *Diagnostic benchmarking…real-world problems*, abstract. [10.1080/0305215X.2024.2381818](https://doi.org/10.1080/0305215X.2024.2381818).
    
    > “Further, the results highlight the need to improve the adaptability and ease-of-use of MOEAs given the often ill-defined nature of real-world problem-solving.”
    
    **P; low current fit:** Borg already provides strong adaptive performance; scalar elitism is insufficient for Pareto coverage. **Question:** With identical archiving, does immigration improve coverage of disconnected feasible alternatives over matched multistart?

12. **Benchmarking: extract useful problem characteristics.** Bartz-Beielstein et al. (2020), *Benchmarking in Optimization: Best Practice and Open Issues*, §6.5. [10.48550/arXiv.2007.03488](https://doi.org/10.48550/arXiv.2007.03488) — **preprint DOI**.
    
    > “How can one (automatically) extract its most relevant information?”
    
    **P; medium diagnostic fit:** [mixed-variable ELA, 2024](https://doi.org/10.1109/TEVC.2024.3399560) already enables algorithm selection. **Question:** Do inexpensive probes predict GAdapt’s relative performance on unseen physical networks better than dimension and variable-type counts alone?

**Top three to pursue** — ordinal scores, 1–5; products express priorities, not probabilities:

| Rank | Narrow question | Open × fit × public data | Decisive baseline |
|---|---|---:|---|
| **1** | Constraint handling × adaptation on discrete OPF controls (#1) | 4 × 5 × 5 = **100** | Mixed-integer DE with simple parameter control; matched fixed-parameter GA isolates adaptation. |
| **2** | When grid plateaus help or defeat adaptation (#2) | 3 × 5 × 5 = **75** | Tanabe’s strong DE configurations, plus CMA-ES with Margin. |
| **3** | Dynamic reconfiguration under deadlines at increasing scale (#3) | 2 × 4 × 5 = **40** | Graph-aware branch exchange with AC evaluation; MISOCP plus AC validation anchors solution quality. |

For #1–2, use MATPOWER/PYPOWER cases and [pandapower networks](https://pandapower.readthedocs.io/en/v3.5.0/networks.html), with explicitly documented device grids. For #3, use pandapower/SimBench profiles and publish every added tie-switch assumption. Telecom experiments can use [TopoHub’s preserved SNDlib topologies and original static demands](https://topohub.readthedocs.io/en/latest/web.html), without the lost temporal TGZ.

**Discrete variables do not disqualify modern CMA-ES or BO variants.** GAdapt’s plausible advantage is native grid exploration under combinatorial constraints; feasibility repair, failure handling and retention of diverse alternatives still require explicit design and testing.