**NO-GO for K1 as an original algorithmic contribution.** My subjective probability of substantial methodological novelty is **2–5%**. The exactness claim is defensible, but the underlying pruning principle and population-informed evaluation ordering have close precedents.

1. **Closest prior art actually found**

   - **Rosete-Suárez, Ochoa Rodríguez & Sebag (1999), “Evolving objective function for saving computational effort.”** The closest conceptual match: truncation selection; stop evaluating an individual when a bound proves exclusion from the best \(L\); order components using previous-generation statistics. Their worked objective is additive. **No DOI verified.** [Author-uploaded paper](https://www.researchgate.net/publication/302025818_Evolving_objective_function_for_saving_computational_effort_a_case_study).
   - **Bongard & Hornby (2010), “Guarding Against Premature Convergence while Accelerating Evolutionary Search.”** Guaranteed early termination when monotone partial fitness proves a candidate cannot reproduce; demonstrated through dominance pruning in a population method. DOI **[10.1145/1830483.1830504](https://doi.org/10.1145/1830483.1830504)**; [full paper](https://meclab.w3.uvm.edu/papers/2010_GECCO_Bongard_2.pdf).
   - **Heidrich-Meisner & Igel (2009), “Hoeffding and Bernstein Races…”** Explicit best-\(\mu\)-of-\(\lambda\) selection racing. Its guarantee is probabilistic and concerns mean performance, unlike K1’s deterministic finite maximum. DOI **[10.1145/1553374.1553426](https://doi.org/10.1145/1553374.1553426)**; [full paper](https://icml.cc/2009/papers/229.pdf).
   - **Branke & Rosenbusch (2008), “New Approaches to Coevolutionary Worst-Case Optimization.”** Learns adverse scenarios alongside candidate solutions. Relevant scenario prioritization precedent, but its abstract establishes no lossless finite-suite selection guarantee. DOI **[10.1007/978-3-540-87700-4_15](https://link.springer.com/chapter/10.1007/978-3-540-87700-4_15)**.
   - **“Feasibility-ratio based sequencing…” (2021).** Population-based constraint sequencing and partial evaluation: directly relevant to “lazy constraint” evaluation, although its lexicographic treatment does not establish equivalence to K1’s penalized objective. DOI **[10.1016/j.swevo.2021.100850](https://www.sciencedirect.com/science/article/pii/S2210650221000110)**.
   - **Capitanescu et al. (2007), “Contingency Filtering Techniques…”** SCOPF filtering through comparisons of post-contingency violations. DOI **[10.1109/TPWRS.2007.907528](https://ieeexplore.ieee.org/document/4349062/)**.
   - **Li & Li (2020), “Security-Constrained Multi-Objective Optimal Power Flow…with Lasso-based Contingency Filtering.”** Already combines an evolutionary optimizer and learned contingency screening. This establishes application overlap, not K1’s exactness. DOI **[10.1109/ACCESS.2019.2963372](https://arxiv.org/abs/2001.01579)**.

2. **What mathematical difference remains?**

For \(P>0\), after evaluating scenario subset \(S\),

\[
L_S(x)=c(x)+P\max_{k\in S}v_k(x)\le F(x).
\]

Maintain \(q=\texttt{keep_number}\) fully evaluated candidates from the current comparison pool; let \(\tau\) be their worst cost. If \(L_S(x)>\tau\), discard \(x\). Those \(q\) candidates already beat it, regardless of unobserved scenarios. Handle equality using the original stable tie order; fully evaluate final survivors.

**My assessment:** this is a standard bound-based rejection lemma, with \(q=1\) equivalent to pruning a depth-two minimax tree. Alpha-beta correctness long predates K1: Knuth & Moore, DOI **[10.1016/0004-3702(75)90019-3](https://www.sciencedirect.com/science/article/pii/0004370275900193)**. Replacing additive partial bounds with partial maxima is a straightforward specialization. AC contingencies and a particular ordering heuristic remain application details.

3. **GAdapt exactness: the rank-roulette objection needs correction**

[ElitismCostFinder](/Users/danijel/Desktop/gadapt/gadapt/operations/cost_finding/elitism_cost_finder.py:64) truncates first. [GAExecutor](/Users/danijel/Desktop/gadapt/gadapt/execution/ga_executor.py:97) then updates statistics; subsequent parent selection uses survivors.

Consequently, **no selection or statistics redesign is required**: preserve the ordered survivor list and its exact costs. Rejected candidates need neither exact costs nor mutual ranks. A population-aware cost finder must manage bounds; censored values must never reach retained-cost statistics.

Changing to tournaments or altering diversity statistics would change behavior unnecessarily. Trajectory equivalence additionally requires deterministic scenario outputs, matching RNG use and ties, and generation-based comparison: the default wall-clock timeout can produce different stopping generations. Optional credit controllers consuming rejected evaluations need separate treatment.

The existing first-fail wrapper proves infeasibility but returns surrogate costs; it does not supply this guarantee.

**Strongest killing baseline:** ordinary exact top-\(q\) bound pruning with fixed contingency order, then the same pruning with the 1999 population-informed ordering. Compare identical seeded generation trajectories and AC counts. If K1 only beats full evaluation, the central novelty claim fails. No single source found establishes the identical AC/GAdapt combination; the methodological overlap is nevertheless decisive.