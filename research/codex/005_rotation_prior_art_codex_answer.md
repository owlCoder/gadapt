**Gate verdict: the broad contribution is already prior art.** Rotation-independent variation, explicit covariance learning, and diversity control must be distinguished. I53 establishes none as the cause of GAdapt’s deficit.

1. **UNDX:** Ono, I.; Kobayashi, S. (1997). [“A Real-coded Genetic Algorithm for Function Optimization Using Unimodal Normal Distribution Crossover.”](https://web.db.tokushima-u.ac.jp/cgi-bin/edb_browse?EID=17891) *Proceedings, 7th International Conference on Genetic Algorithms*, 246–253. **DOI: UNVERIFIED.** Three-parent Gaussian crossover uses parent geometry to generate coordinate-independent, correlated offspring; no persistent covariance estimator is required.

2. **SPX:** Tsutsui, S.; Yamamura, M.; Higuchi, T. (1999). [“Multi-parent Recombination with Simplex Crossover in Real Coded Genetic Algorithms.”](https://gpbib.pmacs.upenn.edu/gecco1999/Tsutsui_icga99.pdf) *GECCO*, 657–664. **DOI: UNVERIFIED.** Uniform sampling within an expanded parental simplex provides coordinate-independent GA recombination.

3. **PCX/G3:** Deb, K.; Anand, A.; Joshi, D. (2002). “A Computationally Efficient Evolutionary Algorithm for Real-Parameter Optimization.” *Evolutionary Computation* **10**(4), 371–395. **DOI: [10.1162/106365602760972767](https://doi.org/10.1162/106365602760972767).** Parent-centric directional sampling is combined with the elitist G3 population model; parental spread determines offspring spread.

4. **Rotation-invariant DE:** Takahama, T.; Sakai, S. (2010). “Solving Nonlinear Optimization Problems by Differential Evolution with a Rotation-Invariant Crossover Operation Using Gram-Schmidt Process.” *NaBIC*, 526–533. **DOI: [10.1109/NABIC.2010.5716327](https://doi.org/10.1109/NABIC.2010.5716327).** Builds an orthogonal crossover basis from population differences.

5. **Eigenvector DE:** Guo, S.-M.; Yang, C.-C. (2015). “Enhancing Differential Evolution Utilizing Eigenvector-Based Crossover Operator.” *IEEE Transactions on Evolutionary Computation* **19**(1), 31–49. **DOI: [10.1109/TEVC.2013.2297160](https://doi.org/10.1109/TEVC.2013.2297160).** Applies crossover after projection into population-covariance eigenvectors.

6. **CoBiDE:** Wang, Y.; Li, H.-X.; Huang, T.; Li, L. (2014). “Differential Evolution Based on Covariance Matrix Learning and Bimodal Distribution Parameter Setting.” *Applied Soft Computing* **18**, 232–247. **DOI: [10.1016/j.asoc.2014.01.038](https://doi.org/10.1016/j.asoc.2014.01.038).** Combines learned-coordinate crossover, adaptive parameters and original-coordinate mixing; the complete mixture is not strictly rotation invariant.

7. **Covariance-guided GA mutation:** Kramer, O. (2017). “Machine Learning,” §8.2, in *Genetic Algorithm Essentials*, Springer, 65–72. **DOI: [10.1007/978-3-319-52156-5_8](https://doi.org/10.1007/978-3-319-52156-5_8).** Algorithm 10 explicitly places covariance-guided mutation after GA crossover and updates covariance from selected parents.

8. **RV-GOMEA:** Bouter, A.; Witteveen, C.; Alderliesten, T.; Bosman, P.A.N. (2017). “Exploiting Linkage Information in Real-Valued Optimization with the Real-Valued Gene-pool Optimal Mixing Evolutionary Algorithm.” *GECCO*, 705–712. **DOI: [10.1145/3071178.3071272](https://doi.org/10.1145/3071178.3071272).** Combines linkage subsets, Gaussian models and acceptance-tested partial variation; linkage exploitation does not imply arbitrary rotation invariance.

9. **CMA-based variation inside GOMEA:** Bouter, A.; Alderliesten, T.; Bosman, P.A.N. (2021). “Achieving Highly Scalable Evolutionary Real-Valued Optimization by Exploiting Partial Evaluations.” *Evolutionary Computation* **29**(1), 129–155. **DOI: [10.1162/evco_a_00275](https://doi.org/10.1162/evco_a_00275).** Embeds separately adapted CMA-ES sampling models within RV-GOMEA—direct overlap with importing CMA-based variation into a GA-family method.

10. **AREX:** Akimoto, Y.; Nagata, Y.; Sakuma, J.; Ono, I.; Kobayashi, S. (2009). “Proposal and Evaluation of Adaptive Real-coded Crossover AREX.” *Transactions of the Japanese Society for Artificial Intelligence* **24**(6), 446–458. **DOI: [10.1527/tjsai.24.446](https://doi.org/10.1527/tjsai.24.446).** Covariance-preserving ensemble crossover adapts its expansion and mean movement to prevent premature diversity loss.

11. **AMaLGaM:** Bosman, P.A.N.; Grahl, J.; Thierens, D. (2013). “Benchmarking Parameter-Free AMaLGaM on Functions With and Without Noise.” *Evolutionary Computation* **21**(3), 445–469. **DOI: [10.1162/EVCO_a_00094](https://doi.org/10.1162/EVCO_a_00094).** Gaussian covariance learning is coupled to adaptive variance scaling and standardized-improvement feedback; this is adjacent EDA prior art.

12. **Recent diversity/spectral overlap:** Zhao, L.; Sun, L.; Song, Z.; Zhang, Q.; Matsveichuk, N.; Sotskov, Y. (2026). “Differential Evolution with a Variance Contribution Ratio-Based Diversity Enhancement Mechanism for Numerical Optimization.” *Swarm and Evolutionary Computation* **104**, 102359. **DOI: [10.1016/j.swevo.2026.102359](https://doi.org/10.1016/j.swevo.2026.102359).** The publisher abstract explicitly combines PCA, variance-based diversity enhancement and parameter adaptation; detailed equivalence remains unchecked.

**Clearly prior art:** substituting UNDX/SPX/PCX, adding Gaussian covariance mutation, importing CMA updates, crossing in eigen-coordinates, learning linkage, or generally coupling correlation-aware variation with diversity preservation.

**Possibly open:** a specifically different GAdapt feedback law. One concrete candidate to investigate—not established novelty—is offspring-specific spectral restoration:
\[
\Sigma_{i,t}=\sigma_t^2\!\left[C_t+\beta(1-D_{f,t})(1-D_{p,i,t})(\tau I-C_t)_+\right].
\]
Here \(D_f,D_p\in[0,1]\) measure fitness and parental diversity, \(\tau=\operatorname{tr}(C_0)/d\), and \((\cdot)_+\) clips negative eigenvalues. The difference would be **joint fitness/parent feedback restoring depleted eigendirections**, beyond scalar rescaling or simply changing basis. Its distinctness from AREX, AMaLGaM and spectral-restoration DE must be demonstrated. Rotation invariance additionally requires invariant diversity measures, crossover, initialization and boundary handling.

My subjective probability of a defensible methodological contribution from such a narrow variant: **~15%**; from merely “adding correlation learning to GAdapt”: **<1%**.
---
**Lead verification (Claude, 2026-10-23 20:25):** 9 DOIs checked on Crossref (title, year, authors match):
10.1162/106365602760972767, 10.1109/NABIC.2010.5716327, 10.1109/TEVC.2013.2297160, 10.1016/j.asoc.2014.01.038,
10.1007/978-3-319-52156-5_8, 10.1162/evco_a_00275, 10.1527/tjsai.24.446, 10.1162/EVCO_a_00094,
10.1016/j.swevo.2026.102359 (+ 10.1145/3071178.3071272 verified in 003). UNDX and SPX remain UNVERIFIED (no DOI).
Gate verdict accepted: adding correlation learning / rotation-invariant variation to GAdapt = PRIOR ART, NO-GO.
The narrow "spectral restoration driven by GAdapt's diversity signals" variant (~15%) is not pursued without a separate gate.
