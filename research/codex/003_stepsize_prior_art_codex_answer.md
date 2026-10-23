**Prior-art gate: the generic formula \(\sigma=s_t\,\mathrm{spread}(P_t)\), with success-adapted \(s_t\), is already covered.** AMBOA (2004) is particularly close. No files were edited.

The strongest verified precedents follow; EDAs, GA hybrids, and conventional GAs are distinguished explicitly.

1. **Očenášek, J.; Kern, S.; Hansen, N.; Koumoutsakos, P. (2004).** [“A Mixed Bayesian Optimization Algorithm with Variance Adaptation.”](https://jiri.ocenasek.com/papers/ppsn356.pdf) *PPSN VIII*, LNCS 3242, 352–361. DOI: **10.1007/978-3-540-30217-9_36**.  
   **Closest formula:** Gaussian kernel width equals population range divided by a factor, multiplied by \(\eta_t\); replacement successes increase \(\eta_t\), failures decrease it, targeting a configurable success rate. This is an EDA.

2. **Shapiro, J. L. (2005).** [“Drift and Scaling in Estimation of Distribution Algorithms.”](https://research.manchester.ac.uk/en/publications/drift-and-scaling-in-estimation-of-distribution-algorithms/) *Evolutionary Computation* 13(1), 99–123. DOI: **10.1162/1063656053583414**.  
   Establishes finite-population drift toward degenerate probability models; its principal examples are discrete UMDAs, so it is not specifically a Gaussian-mutation nonconvergence theorem.

3. **Grahl, J.; Bosman, P. A. N.; Rothlauf, F. (2006).** [“The Correlation-Triggered Adaptive Variance Scaling IDEA.”](https://ir.cwi.nl/pub/14432/) *GECCO*, 397–404. DOI: **10.1145/1143997.1144071**.  
   Introduces adaptive multiplication of estimated Gaussian covariance to prevent premature convergence, with a correlation-based trigger.

4. **Bosman, P. A. N.; Grahl, J.; Rothlauf, F. (2007).** [“SDR: A Better Trigger for Adaptive Variance Scaling in Normal EDAs.”](https://homepages.cwi.nl/~bosman/publications/2007_sdrabetter.pdf) *GECCO*, 492–499. DOI: **10.1145/1276958.1277066**.  
   Uses \(C_{\mathrm{sample}}=c_t\widehat C_t\), adjusting \(c_t\) from improvements and their distance from the mean measured in standard deviations.

5. **Bosman, P. A. N.; Thierens, D. (2007).** [“Adaptive Variance Scaling in Continuous Multi-Objective Estimation-of-Distribution Algorithms.”](https://homepages.cwi.nl/~bosman/publications/2007_adaptivevariancescaling.pdf) *GECCO*, 500–507. DOI: **10.1145/1276958.1277067**.  
   Extends AVS/SDR to Gaussian mixtures with separate cluster multipliers; documents premature convergence and unnecessary scaling slowing convergence.

6. **Cai, Y.; Sun, X.; Xu, H.; Jia, P. (2007).** [“Cross Entropy and Adaptive Variance Scaling in Continuous EDA.”](https://www.cs.york.ac.uk/rts/docs/GECCO_2007/docs/p609.pdf) *GECCO*, 609–616. DOI: **10.1145/1276958.1277081**.  
   Explicitly analyzes the interaction between population-estimated covariance and success-controlled scaling: failures caused by incorrect model shape can misleadingly shrink the multiplier; proposes cross-entropy correction.

7. **Bouter, A.; Alderliesten, T.; Witteveen, C.; Bosman, P. A. N. (2017).** [“Exploiting Linkage Information in Real-Valued Optimization with the Real-Valued Gene-Pool Optimal Mixing Evolutionary Algorithm.”](https://ir.cwi.nl/pub/26553/GECC1115.pdf) *GECCO*, 705–712. DOI: **10.1145/3071178.3071272**.  
   RV-GOMEA combines population-estimated Gaussian distributions, linkage subsets, and progress-controlled AVS/SDR multipliers during partial variation of existing individuals.

8. **Hinterding, R.; Michalewicz, Z.; Peachey, T. C. (1996).** [“Self-Adaptive Genetic Algorithm for Numeric Functions.”](https://link.springer.com/chapter/10.1007/3-540-61723-X_1006) *PPSN IV*, LNCS 1141, 420–429. DOI: **10.1007/3-540-61723-X_1006**.  
   Evolves Gaussian mutation strength alongside solutions and adapts population size; establishes numeric-GA self-adaptation, rather than the proposed explicit spread multiplier.

9. **Ursem, R. K. (2002).** [“Diversity-Guided Evolutionary Algorithms.”](https://link.springer.com/chapter/10.1007/3-540-45712-7_45) *PPSN VII*, LNCS 2439, 462–471. DOI: **10.1007/3-540-45712-7_45**.  
   DGEA uses distance-to-centroid diversity thresholds to alternate exploration through mutation and exploitation through recombination/selection.

10. **Güneş, İ.; Çataltepe, Z.; Gündüz Öğüdücü, Ş. (2011).** [“GA-TVRC: A Novel Relational Time Varying Classifier to Extract Temporal Information Using Genetic Algorithms.”](https://web.itu.edu.tr/~cataltepe/pdf/2011_mldm_GATVRC.pdf) *MLDM*, LNCS 6871, 568–583. DOI: **10.1007/978-3-642-23199-5_42**.  
    Explicit real-valued GA with crossover and Gaussian mutation using the **1/5 success rule**; no explicit measured-diversity feedback.

11. **Hansen, N.; Atamna, A.; Auger, A. (2014).** [“How to Assess Step-Size Adaptation Mechanisms in Randomised Search.”](https://link.springer.com/chapter/10.1007/978-3-319-10762-2_6) *PPSN XIII*, LNCS 8672, 60–69. DOI: **10.1007/978-3-319-10762-2_6**.  
    Compares self-adaptation, CSA, and two-point adaptation as diversity control in ESs; sphere-only assessments can mislead.

12. **Auger, A.; Hansen, N. (2016).** [“Linear Convergence of Comparison-based Step-size Adaptive Randomized Search via Stability of Markov Chains.”](https://epubs.siam.org/doi/abs/10.1137/140984038) *SIAM Journal on Optimization* 26(3), 1589–1624. DOI: **10.1137/140984038**.  
    Gives sufficient normalized-Markov-chain stability conditions for global linear convergence on scaling-invariant objectives; no automatic guarantee for a particular GA.

13. **Pošík, P. (2008).** [“Truncation Selection and Gaussian EDA: Bounds for Sustainable Progress in High-Dimensional Spaces.”](https://link.springer.com/chapter/10.1007/978-3-540-78761-7_58) *Applications of Evolutionary Computing*, LNCS 4974, 525–534. DOI: **10.1007/978-3-540-78761-7_58**.  
    Studies constant multiplication of estimated spread; demonstrates that slope traversal and contraction near an optimum can require incompatible constants.

I did **not verify** an earlier conventional RCGA with precisely GAdapt’s additive columnwise-spread mutation, or CSA/TPA combined with explicit diversity feedback inside such a GA. Those remain search gaps, not novelty evidence.

**Sphere qualification:** spread-proportional scale can support linear convergence. Mathematical inference: in an idealized Gaussian model centered at the sphere optimum, fixed-fraction truncation gives \(\sigma_{t+1}=q\sigma_t\), \(0<q<1\), hence geometric contraction of RMS radius. This does not establish finite-population GAdapt convergence; centering, selection, and its positive floor matter.

**Verdict:** constant spread scaling, success-adapted spread multipliers, covariance multipliers, and improvement-distance triggers are clearly prior art. A coordinatewise GA port is insufficient novelty by itself. My subjective probability that the **generic candidate formula** remains novel is **<1%**. A specifically defined offspring-centered controller with a new convergence result plausibly remains open—approximately **25%**, pending a search against its exact equations and assumptions.
---
**Lead verification (Claude, 2026-10-23 20:05):** all 11 DOIs above checked on Crossref (title, year, authors match);
10.1137/140984038 confirmed via Crossref search after a transient direct-lookup failure. Gate verdict accepted:
the generic "spread × success-adapted multiplier" step control is PRIOR ART (AMBOA 2004, AVS 2006, SDR 2007,
RV-GOMEA 2017); NO-GO as a PhD method. Only an exactly specified offspring-centred controller with a new
convergence result might remain open (Codex estimate ~25%), not pursued without a separate gate.
