**C1 merits only a bounded theorem-feasibility attempt; C2 is NO-GO as presently stated.** Neither clears a methodological novelty gate. My subjective probabilities of a defensible new method-plus-theorem contribution are **10–15% for C1** and **3–5% for C2**. These replace the earlier, less-informed estimates. No files were changed or experiments run.

**1. Falsifiable mathematical specifications**

These are proposed analytical variants, not claims about unchanged GAdapt defaults.

Let \(P_t=\{x_t^1,\ldots,x_t^\mu\}\), \(\mu\ge2\), with \(\lambda=\mu\). Rank parents by increasing objective; independently select each parent with probability
\[
p_r=\frac{2(\mu-r+1)}{\mu(\mu+1)}.
\]
For each offspring, draw parents \(a_i,b_i\) and independent \(u_{ij}\sim U[0,1]\):
\[
q_{ij}=u_{ij}a_{ij}+(1-u_{ij})b_{ij}.
\]
Use independent Gaussian vectors \(z_i\sim N(0,I)\). Retain the best \(\mu\) members of \(P_t\cup\{y_i\}\), with fixed tie-breaking. Unmutated \(q_i\) are evaluated for feedback but are **not** survivor candidates.

For **C1**, define column variances and mutation:
\[
v_{tj}=\frac1{\mu-1}\sum_r(x_{tj}^r-\bar x_{tj})^2,\qquad
y_i=q_i+s_t\operatorname{diag}(\sqrt{v_t})z_i,
\]
\[
\widehat p_t=\lambda^{-1}\sum_i\mathbf1\{f(y_i)<f(q_i)\},\qquad
s_{t+1}=s_t\exp[(\widehat p_t-1/5)/d].
\]
Thus feedback measures mutation improvement **relative to its actual offspring centre**. Both evaluations count: \(2\lambda\) per generation.

Assume exact arithmetic, \(s_0>0\), every \(v_{0j}>0\), unconstrained noiseless sphere \(f(x)=\|x-x^\star\|^2\), no reset, rounding, clipping or positive variance floor.

**Contribution theorem to attempt:** writing \(R_t=\min_{x\in P_t}\|x-x^\star\|\) and \(T_\epsilon=\inf\{t:R_t\le\epsilon\}\), prove
\[
\limsup_{t\to\infty}t^{-1}\log(R_t/R_0)\le-c_\mu/d\quad\text{a.s.},
\]
\[
\mathbb E T_\epsilon\le A(P_0,s_0)+K_\mu d\log(R_0/\epsilon),
\]
with explicit finite constants and parameter restrictions. Crucially, **derive** variance stability; do not assume \(s_t\sqrt{v_{tj}}\asymp R_t/d\). Quadratics with bounded Hessian condition number are a subsequent extension.

For **C2**, let \(C_t\) be empirical population covariance, \(\tau=\operatorname{tr}(C_0)/d>0\), and fix \(0<\beta\le1\). One precise signal choice is
\[
D_{f,t}=\min\{1,\operatorname{sd}(f(P_t))/\operatorname{sd}(f(P_0))\},
\quad
D_{p,i,t}=\min\{1,\|a_i-b_i\|/\sqrt{2\operatorname{tr}C_0}\}.
\]
Require nonzero initial fitness spread. Set
\[
g_{it}=\beta(1-D_{f,t})(1-D_{p,i,t}),\quad
\Sigma_{it}=s_t^2[C_t+g_{it}(\tau I-C_t)_+],
\quad y_i=q_i+\Sigma_{it}^{1/2}z_i,
\]
using C1’s scale update and selection.

**Contribution theorem to attempt:** the preceding convergence/hitting-time bounds on positive-definite quadratics, additionally allowing rank-deficient initial covariance with positive trace. Prove recovery and scale stability despite gates that can vanish. Positive definiteness alone is insufficient. These signal definitions differ from GAdapt’s default logarithmic/coordinatewise signals; neither version inherits rotation invariance through coordinatewise crossover.

**2. Systematic prior-art findings and exact differences**

Searches covered the requested author families, plus/comma selection, recombination, drift, Gaussian EDAs, AVS/SDR, covariance repair and recent diversity mechanisms. The closest findings are:

- **Finite-population elitism already has a sphere runtime theorem.** Jägersküpper–Witt (2005), Theorem 3, proves distance halving in \(O(\mu d)\) mutation steps with overwhelming probability, assuming initially appropriately scaled individual mutation strengths. **C1 difference:** recombination, shared population-derived diagonal variance, and paired \(q_i\)-versus-\(y_i\) feedback; its required stability cannot be imported from that theorem. [Full paper](https://gpbib.cs.ucl.ac.uk/gecco2005/docs/p849.pdf).

- **Population plus recombination plus adaptive step size is already analysed.** Touré–Auger–Hansen (2023), DOI **10.1007/s10898-022-01249-6**, proves an asymptotic logarithmic rate for weighted-recombination ESs; its sign is determined numerically. **C1 difference:** persistent elitist population, coordinatewise crossover, endogenous empirical dispersion and discontinuous paired-success feedback. Proving a strictly negative rate would exceed merely establishing existence of a rate. [Paper](https://arxiv.org/html/2107.08847v3).

- **Linear convergence and expected hitting times on strongly convex functions already exist.** Akimoto–Auger–Glasmachers–Morinaga (2022), DOI **10.1137/20M1373815**, covers a \((1+1)\)-ES family with abstract covariance adaptation of bounded condition number. **Difference:** C1 must establish control of its potentially degenerating population variance rather than assume bounded shape. [Publisher](https://epubs.siam.org/doi/10.1137/20M1373815). Auger–Hansen’s normalized-chain framework and Akimoto–Auger–Hansen’s ODE framework supply existing proof machinery; using either is not itself novel. [Markov-chain framework](https://doi.org/10.1137/140984038), [ODE framework](https://arxiv.org/abs/1811.06703).

- **Progress calculations are weaker than the proposed theorem.** Beyer’s sphere/recombination analyses and Akimoto–Auger–Hansen’s quadratic quality-gain analysis already explain recombination and optimal scaling. They do not establish C1’s complete finite-population feedback dynamics. [Beyer tutorial](https://homepages.fhv.at/hgb/downloads/MA-ES-Principles-Tutorial.pdf), [quadratic analysis](https://doi.org/10.1016/j.tcs.2018.05.015).

- **Variance adaptation and generic convergence gates are crowded.** SDR/AMaLGaM already couple estimated covariance with progress-triggered scaling; Pošík identifies incompatible scaling demands on slopes and near optima. [SDR](https://homepages.cwi.nl/~bosman/publications/2007_sdrabetter.pdf), [Pošík](https://citeseerx.ist.psu.edu/document?doi=5ec31b8193c03155fcae47aab0b895e8dbac7846&repid=rep1&type=pdf). Chen–He (2021), DOI **10.1016/j.ins.2020.12.076**, supplies positive-adaptation convergence conditions. **Remaining work:** verify substantive conditions for C1, rather than restate conditional drift. [Paper](https://irep.ntu.ac.uk/id/eprint/42368/1/1408047_He.pdf).

A newly identified **2025 adaptive-elitist-EA linear-average-convergence paper** further narrows C1, DOI **10.1016/j.asoc.2025.113635**. Its complete mutation equations were unavailable; **equation-level equivalence remains UNVERIFIED**, preventing unconditional clearance. [Publisher](https://www.sciencedirect.com/science/article/abs/pii/S1568494625009469).

For **C2**, the closest mathematical operator is exactly
\[
C+g(\tau I-C)_+=(1-g)C+g\,\Pi_{\succeq\tau I}(C):
\]
a relaxed eigenvalue-floor projection. That projection is established matrix analysis. **The exact remaining difference is the offspring-specific joint gate \(g_{it}\), not spectral restoration itself.** [Higham](https://nhigham.com/2021/01/26/what-is-the-nearest-positive-semidefinite-matrix/).

Pycma also provides sampling-covariance condition repair. IPOP changes restart population size; sep-CMA restricts covariance; active CMA reduces variance using unsuccessful samples. None is the exact joint gate. [Repair](https://cma-es.github.io/apidocs-pycma/cma.sampler.GaussFullSampler.html), [CMA variants](https://cma-es.github.io/cmaes_sourcecode_page.html). DE-VCR (2026), DOI **10.1016/j.swevo.2026.102359**, combines PCA and diversity enhancement; exact equivalence remains **UNVERIFIED** beyond its abstract. [Publisher](https://www.sciencedirect.com/science/article/pii/S2210650226000799).

**3. Decision and minimal falsification**

**C1: conditional GO for a three-person-day feasibility screen only.** First resolve the 2025 equations. Reject proofs assuming normalized-scale stability, replacing the population by an infinite Gaussian, or silently reducing to incumbent mutation.

Synthetic screen: sphere, diagonal and rotated ellipsoids; \(d=10,30\); ordinary and tightly clustered off-optimum populations; 20 fresh seeds; 10,000 evaluations, checkpoint at 3,000. Eight arms: C1, incumbent-success ablation, fixed multiplier, AVS-style GA, one-fifth \((1+1)\)-ES, active full CMA-ES with budgeted restarts, sep-CMA, AMaLGaM. Total: **19.2 million cheap evaluations**. Log dispersion, scale and improvement probabilities. Persistent stalls undermine feasibility; measured slopes do not prove the theorem.

Only after synthetic survival and a credible proof outline: frozen I47/I53 dispatch evaluator, five cases, 12 fresh seeds, eight arms, exactly 3,000 `runpf` calls each: **1.44 million calls**. Preserve penalized score and feasibility separately; preregister paired contrasts and Holm correction.

**C2: NO-GO.** Its operator is known, joint-gate benefit is unestablished, and fixed \(\tau\) creates a rate obstacle unless scale adaptation compensates. No dispatch expenditure is justified.
---
**Lead verification (Claude, 2026-10-23 20:45):** DOIs checked on Crossref: 10.1007/s10898-022-01249-6 and
10.1137/20M1373815 (via search; direct lookup case-sensitive), 10.1016/j.tcs.2018.05.015, 10.1016/j.ins.2020.12.076,
10.1016/j.asoc.2025.113635. The 2025 paper (da Silva, Borges, Nepomuceno, Soler, Applied Soft Computing 183, 113635)
was resolved from the publisher page (highlights + abstract; full equations paywalled): it proposes a
positive-adaptive mutation for an elitist adaptive EA, proves a LINEAR average convergence rate with an explicit lower
bound in terms of the Lipschitz constant and dimension, applies it to GA, ES and DE, and validates on economic dispatch
with valve-point effects. The contribution TYPE targeted by C1 (adaptive mutation in an elitist GA + linear
convergence theorem + dispatch application) therefore already exists, in our domain. Remaining C1 differences
(population-derived diagonal variance, offspring-centred paired feedback) would be an incremental variant.
**Decision: C1 NO-GO** (novelty not established; CLAUDE.md: stop). C2 NO-GO as Codex concluded.
