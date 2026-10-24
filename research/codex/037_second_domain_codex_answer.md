Recommend **modular telecommunications capacity planning with splittable multicommodity routing**. It gives GAdapt discrete installation decisions and a genuine optimization-based feasibility check. Keep this as a separate preregistered extension; leave frozen H58 unchanged.

**Formulation.** Use each archived TopoHub graph \(G=(N,E)\) and its stored positive static demands \(d_k\), \(k=(s_k,t_k)\). Preserve each demand entry exactly once; do not symmetrize or double triangular matrices.

For each edge, install \(x_e\in\{0,\ldots,16\}\) identical capacity modules. Define a reproducible module size: route every demand along its lexicographically first minimum-hop path, obtaining loads \(L_e^{SP}\), then set
\[
q=\max_e L_e^{SP}/8.
\]
Thus \(x_e^{SP}=\lceil L_e^{SP}/q\rceil\le8\) supplies a known feasible design. These are modules in the stored demand units; assigning them a physical Gbit/s interpretation would require a documented conversion.

Minimize installation cost
\[
C(x)=\sum_e c_ex_e,\qquad c_e=1+\mathrm{dist}_e/1000.
\]
The capacity grid and cost formula are **explicit synthetic planning assumptions**: the archived conversions supply neither native module menus nor native prices. See the local [provenance record](/Users/danijel/Desktop/gadapt/research/data/topohub_v1.5.1_sndlib/SOURCE.md).

Replace each undirected edge by two directed arcs. Feasibility means that nonnegative commodity flows \(y_{ka}\) exist satisfying
\[
By_k=d_k(\mathbf e_{s_k}-\mathbf e_{t_k}),\qquad
\sum_k(y_{k,ij}+y_{k,ji})\le qx_e.
\]
Capacities are shared between directions. This is failure-free, splittable routing.

**Deterministic evaluator.** For every candidate, solve an elastic routing LP: replace \(d_k\) by \(d_k-u_k\), constrain \(0\le u_k\le d_k\), and minimize
\[
V(x)=\frac{\sum_k u_k}{\sum_k d_k}.
\]
This LP always has a feasible solution and supplies a graded shortage signal. Use `scipy.optimize.linprog(method="highs-ds")`, HiGHS dual simplex, one thread, sorted indices, fixed options, and flows scaled by \(q\). Freeze tolerances: classify \(V\le10^{-8}\) as zero only after checking witness residuals within \(10^{-7}\) in scaled units. Solver errors are failed evaluations, never ordinary shortages. [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs-ds.html)

An in-memory smoke check here, using 20 random capacity vectors per graph, gave median LP times of **8.6 ms Polska, 23.1 ms Nobel-Germany, 19.7 ms Nobel-US**; GÉANT required 135.8 ms. These are preliminary timings, excluding GA overhead. Thousands of evaluations are practical.

**Instances.** Propose development on **Abilene** (12 nodes/15 edges/132 demands) and **PDH** (11/34/24); confirmation on **Polska** (12/18/66), **Nobel-Germany** (17/26/121), and **Nobel-US** (14/21/91). GÉANT (22/36/462) can be a descriptive scaling case. Counts come from the archived JSONs. These topologies have prior repository exposure; describe them as a new constraint-handling experiment, without claiming untouched datasets. Use only static matrices; the lost temporal TGZ remains outside scope.

**Closest prior art, with verified DOIs.**

- Khelifi, Saidi and Boudjit (2017), *Solving the Capacitated Network Design Problem in Two Steps*: especially close—GA topology selection plus LP capacity loading, using SNDlib Atlanta, France and Germany50. DOI **[10.25046/aj020339](https://www.astesj.com/v02/i03/p39/)**.
- Binh and Ngo (2014), *All capacities modular cost survivable network design problem using genetic algorithm with completely connection encoding*: modular-cost GA design on SNDlib topologies, with generated demand sets and protection requirements. DOI **[10.1186/s13673-014-0013-y](https://link.springer.com/article/10.1186/s13673-014-0013-y)**.
- Bauknecht (2021), *A Genetic Algorithm Approach to Virtual Topology Design for Multi-Layer Communication Networks*: evolutionary hardware-cost planning across packet/optical layers. DOI **10.1145/3449639.3459379**, verified in the [author-hosted paper](https://content.ikr.uni-stuttgart.de/Content/Publications/Archive/BauknechtUwe_GECCO2021_40786.pdf).

These establish substantial precedent; the contribution would be controlled validation of GAdapt’s integrated option.

**Strong baselines.** Solve the joint integer-capacity/continuous-flow formulation with `scipy.optimize.milp`/HiGHS. On small instances, seek certified optima; retain incumbent, dual bound and gap whenever certification fails. [SciPy MILP documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html) Also include continuous-relaxation rounding followed by deterministic feasible module deletion, multistart deletion, DE/FR, and random search. Report wall time alongside evaluator counts; MILP uses additional model structure.

**Falsifiable question and informative budgets.** Compare identical-build GAdapt G1/FR against G0/\(f+1000V\), with \(f=C/C(x^{SP})\), identical initial populations and H58’s execution controls. Target feasibility plus \(C\le(1+\epsilon)C^*\); uncertified references require a predeclared best-known-incumbent fallback, labelled accordingly.

On development instances only, choose a global \(B\in\{3000,10000,30000\}\) and \(\epsilon\in\{0.05,0.10,0.20\}\): smallest budget, then tightest target producing pooled 20–80% attainment in each development block. Confirm on separate development seeds; if none qualifies, report a development no-go. Freeze before confirmation.

Use \(T=\min(\text{first-hit}/B,1)\), equal topology weights, paired seeds and 20,000 stratified bootstrap resamples. **H: \(\theta=E[T_{FR}-T_{penalty}]<0\)**, supported only when the 95% interval lies below zero. Retain all-censored test blocks. Power simulations must preserve censoring: I56’s artificial shifts in all-\(T=1\) blocks overstated available information. More seeds cannot rescue universally unreachable targets.