**The prior art substantially weakens this candidate.** Search conducted 23 October 2026 across all requested topic families, using keyword/title variants and citation chaining. No files changed.

1. **Z. Wang and F.L. Alvarado (1992).** [“Interval Arithmetic in Power Flow Analysis.”](https://minds.wisconsin.edu/handle/1793/9734) *IEEE Transactions on Power Systems* 7(3), 1341–1349. DOI: **10.1109/59.207353**.  
   Interval power-flow solution enclosures under uncertain nodal data.

2. **E.A. Martínez, B. Barán and T.A. Diverio (2002).** [“Solving Electrical Power Load Flow Problems Using Intervals.”](https://www.reliable-computing.org/interval.02/mart.pdf) *SIAM Workshop on Validated Computing*, Toronto, extended abstract. DOI: **UNVERIFIED**.  
   Interval Newton/generalized bisection seeks every solution within a bounded domain.

3. **L.E.S. Pereira, V.M. da Costa and A.L.S. Rosa (2012).** [“Interval Arithmetic in Current Injection Power Flow Analysis.”](https://www.sciencedirect.com/science/article/abs/pii/S0142061512002244) *International Journal of Electrical Power & Energy Systems* 43(1), 1106–1113. DOI: **10.1016/j.ijepes.2012.05.034**.  
   Krawczyk interval power flow, including IEEE systems.

4. **J.B. van den Berg, J.-P. Lessard and K. Mischaikow (2010).** [“Global Smooth Solution Curves Using Rigorous Branch Following.”](https://www.math.vu.nl/~janbouwe/pub/branch_following.pdf) *Mathematics of Computation* 79(271), 1565–1584. DOI: **10.1090/S0025-5718-10-02325-2**.  
   General rigorous parameter/pseudo-arclength continuation; not power-flow-specific.

5. **L. Jaulin and E. Walter (1993).** [“Set Inversion via Interval Analysis for Nonlinear Bounded-Error Estimation.”](https://doi.org/10.1016/0005-1098(93)90106-4) *Automatica* 29(4), 1053–1064. DOI: **10.1016/0005-1098(93)90106-4**.  
   SIVIA already constructs inner/outer unions of boxes enclosing feasible parameter sets.

6. **S. Bolognani and S. Zampieri (2016).** [“On the Existence and Linear Approximation of the Power Flow Solution in Power Distribution Networks.”](https://www.research-collection.ethz.ch/entities/publication/59d5d34d-56a7-4d77-b4bd-b5169dc40b04) *IEEE Transactions on Power Systems* 31(1), 163–172. DOI: **10.1109/TPWRS.2015.2395452**.  
   Fixed-point solvability certificates; operational inequalities require additional checking.

7. **S. Yu (2017).** [*Simple Certificate for Power Distribution Network Security Assessment.*](https://dspace.mit.edu/entities/publication/e5ebf14f-349f-42e4-bc95-ee7b36482cf6) S.M. thesis, Massachusetts Institute of Technology. DOI: **UNVERIFIED**.  
   Banach/Kantorovich certificates, solvability margins and certificate-based continuation applications.

8. **K. Dvijotham, H. Nguyen and K. Turitsyn (2018).** [“Solvability Regions of Affinely Parameterized Quadratic Equations.”](https://www.mit.edu/~turitsyn/assets/pubs/Dvijotham2017dg.pdf) *IEEE Control Systems Letters* 2(1), 25–30. DOI: **10.1109/LCSYS.2017.2721380**.  
   Explicit certified parameter regions around nonsingular solutions, applied to power systems.

9. **H.D. Nguyen, K. Dvijotham and K. Turitsyn (2019).** [“Constructing Convex Inner Approximations of Steady-State Security Regions.”](https://dspace.mit.edu/entities/publication/4be1e1b0-9aab-4ec6-9ec0-cca3d20ff1a5) *IEEE Transactions on Power Systems* 34(1), 257–267. DOI: **10.1109/TPWRS.2018.2868752**.  
   Brouwer-based certified security polytopes.

10. **D. Lee, H.D. Nguyen, K. Dvijotham and K. Turitsyn (2019).** [“Convex Restriction of Power Flow Feasibility Sets.”](https://arxiv.org/abs/1803.00818) *IEEE Transactions on Control of Network Systems* 6(3), 1235–1245. DOI: **10.1109/TCNS.2019.2930896**.  
    Convex sufficient conditions jointly enforce solution existence and operational constraints.

11. **D. Lee, K. Turitsyn, D.K. Molzahn and L.A. Roald (2020).** [“Feasible Path Identification in Optimal Power Flow With Sequential Convex Restriction.”](https://molzahn.github.io/pubs/lee_turitsyn_molzahn_roald-feasible_path.pdf) *IEEE Transactions on Power Systems* 35(5), 3648–3659. DOI: **10.1109/TPWRS.2020.2975554**.  
    Certified linear transitions inside restrictions and piecewise-linear paths; not complete prescribed-chord enumeration.

12. **D.K. Molzahn (2017).** [“Computing the Feasible Spaces of Optimal Power Flow Problems.”](https://arxiv.org/abs/1608.00598) *IEEE Transactions on Power Systems* 32(6), 4752–4763. DOI: **10.1109/TPWRS.2017.2682058**.  
    Entire small-OPF feasible spaces to discretization tolerance using polynomial homotopy and relaxation pruning.

13. **Z. Michalewicz and G. Nazhiyath (1995).** [“Genocop III: A Co-evolutionary Algorithm for Numerical Optimization Problems With Nonlinear Constraints.”](https://doi.org/10.1109/ICEC.1995.487460) *IEEE International Conference on Evolutionary Computation* 2, 647–651. DOI: **10.1109/ICEC.1995.487460**.  
    Generic evolutionary feasibility-repair precedent.

14. **M.S. Osman, M.A. Abo-Sinna and A.A. Mousa (2004).** [“A Solution to the Optimal Power Flow Using Genetic Algorithm.”](https://www.sciencedirect.com/science/article/abs/pii/S0096300303007859) *Applied Mathematics and Computation* 155(2), 391–405. DOI: **10.1016/S0096-3003(03)00785-9**.  
    OPF coevolution and offspring repair to numerical feasibility tolerances.

15. **C. Zhang, H. Chen, H. Ngan, Z. Liang, M. Guo and D. Hua (2017).** [“Solution of Reactive Power Optimisation Including Interval Uncertainty Using Genetic Algorithm.”](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-gtd.2016.1195) *IET Generation, Transmission & Distribution* 11(15), 3657–3664. DOI: **10.1049/iet-gtd.2016.1195**.  
    GA with affine/interval feasibility assessment; no chord-coverage distribution guarantee.

16. **T. Joswig-Jones, K. Baker and A.S. Zamzam (2022).** [“OPF-Learn: An Open-Source Framework for Creating Representative AC Optimal Power Flow Datasets.”](https://par.nsf.gov/servlets/purl/10388977) *IEEE PES Innovative Smart Grid Technologies Conference*, 1–6. DOI: **10.1109/ISGT50606.2022.9817509**.  
    Hit-and-run sampling of an outer polytope refined using infeasibility certificates.

17. **M.R. Narimani, J.A. Madrigal, K.R. Davis and D.K. Molzahn (2026).** [“Exploring OPF Feasible Spaces Using Nonlinear Programming and Continuation Methods.”](https://molzahn.github.io/pubs/narimani_madrigal_davis_molzahn-nlp_cpf.pdf) *10th Texas Power and Energy Conference*. DOI: **UNVERIFIED**.  
    Continuation between feasible-point pairs followed by constraint filtering; no complete interval certificate.

**Gate: NO-GO as presently specified.** I found no exact duplicate, but my inference is that rigorous branch following plus one-dimensional SIVIA supplies the proposed construction under the original nonsingularity/simple-crossing assumptions. Summing unresolved interval lengths supplies the ε stopping rule. Length-weighted interval sampling supplies uniformity on \(A^-\); its total-variation error is simply \(1-|A^-|/|A|\le\varepsilon/|A|\). Measure coverage does not ensure detection of every tiny component.

Reopening requires a new mathematical contribution: for example, a proved amortized certification-complexity improvement or rigorous branch-consistent PV/PQ event handling. Neither is currently specified.

**Effort, one researcher:** 2–4 weeks for a numerical prototype; 3–6 months for rigorous fixed-mode IEEE 9/14/30/57/118 certification and validation; 6–12 months total including switching, stressed/disconnected examples and repeated-seed comparisons against rejection, repair, generic SIVIA and convex restriction. [PYPOWER supplies nominal numerical routines](https://rwl.github.io/PYPOWER/api/pypower.newtonpf-module.html); outward-rounded interval machinery remains additional work.

**Subjective probability of passing the originality-and-usefulness gate as stated: 5%**, down from 10%.
---
**Lead verification (Claude, 2026-10-23 20:30):** 14 DOIs checked on Crossref (title, year, authors match), incl.
10.1090/S0025-5718-10-02325-2 (found via search; direct lookup is case-sensitive). Martínez 2002, Yu 2017 and
Narimani 2026 remain UNVERIFIED (no DOI). Gate verdict accepted: NO-GO as specified.
