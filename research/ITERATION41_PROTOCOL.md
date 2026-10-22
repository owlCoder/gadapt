# I41: exact route-aware temporal constraint domination — METHOD preregistration

**Frozen 2026-10-22 BEFORE any I41 benchmark of the approach.** Upstream `bpzoran/gadapt` MUST NOT change. The original I39 288-SNDlib dataset remains unavailable at the known content-addressed SHA256; DO NOT synthesize a replacement, rerun I39/I40, fabricate holdout outcomes or treat toy data as original DFN.

## Scientific problem, result, and novelty boundary

I39's actual 272-pair, two-route static modular capacity MILP has **26×192 = 4,992 edge-time capacity rows** even though some are redundant for *every* route vector, and ran for ~169 s to a 1%-target gap. Test one independently justified exact **route-aware constraint implication certificate**, NOT another GA/UCB credit tweak, by proving when an edge-time inequality can be omitted without changing the feasible set or objective of the original linear integer MILP. The generic idea of scenario elimination, presolving and dominance is ALREADY established (e.g. Goerigk and Khosravi 2023, https://doi.org/10.1016/j.ejor.2023.03.019; Chen and Wu 2026, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428860; robust network design local reduction https://doi.org/10.1002/rnc.7038). This route-specific formulation is a *candidate implementation/theorem*, not a proven original doctoral breakthrough. Real-world utility is undecided until independently held-out benchmarks.

## Exact algebraic certificate

Let `q[t,d]>=0` be the traffic for original demand d in frame t, `a[e,d,0]` or `a[e,d,1]` equal 1 iff candidate unsplittable route j uses physical edge e; and `z[d] ∈ {0,1}` independent over demands. Fixed route load:
`L[e,t](z)=Σ_d q[t,d]*a[e,d,z[d]]`.
For any pair of original *time frames* s,t and one physical edge e define
`M[e;s,t] = Σ_d min((q[s,d]-q[t,d])*a[e,d,0], (q[s,d]-q[t,d])*a[e,d,1])`.
Because route choice is separable across demands, **M is EXACTLY min_z (L[e,s](z)−L[e,t](z))**. If `M>=0` in exact real arithmetic, `L[e,s](z)>=L[e,t](z)` for every route vector z. Hence an installed capacity constraint `L[e,s](z)<=C_e(y)` IMPLIES `L[e,t](z)<=C_e(y)` for all binary z and all allowable source modular installation decisions y. Removing the (e,t) row is exact. For floating source inputs require a roundoff-aware strictly positive M margin; identical traffic-on-edge expressions may be matched bitwise to remove equality rows. No permissive negative tolerance.

Retain a directed witness map from each removed edge-time row to a retained dominating representative; re-evaluate every original row against its final representative **directly** (NO merely assumed tolerance-transitivity). Return explicit certificate with counts and per-row lower-bound margins. If any certificate fails, reject compression; no optimization using unverified rows. The original 272-route binary feasibility set, all 20/40 module costs and objective remain unchanged.

## Experimental stage within this turn

1. Commit protocol BEFORE algorithm file.
2. Implement reusable stand-alone `certified_route_aware_rows(problem)` for full `JointCapacityProblem`/I39 `ModularCommonPlan` incidence and exact source frame matrices. Add optional `certified_rows` arg to existing original `exact_modular_milp`; default `None` MUST preserve I39 behavior bit-for-bit.
3. Synthetic domain-only cases: (a) strictly nested 128 frames with known removable rows; (b) same total demand but opposite physical-link loads MUST not be confused as dominance; (c) numeric adversarial nearly tied demands; (d) enumerate every route combination of a small network (2^D), assert all full/reduced inequalities and minimal modular capacity plan/cost exactly equal; (e) unmodified MILP versus certified-reduced MILP same incumbent objective and dual bound for a tiny modeled network. No SNDlib download/official solver evaluation.
4. One GitHub CI synthetic theorem regression, no branch/PR automatic physical-domain run. Revisit source only when original bytes are provably recovered. No claims of empirical speedup or original science from toy reductions.

## What this can contribute to a dissertation

A precisely stated, falsifiable safe screening theorem and an actual integrated MILP presolver; a benchmark quality metric (fraction removed vs certificate cost, MILP CPU/gap at identical source data) when valid independent datasets are accessible. Significant performance and novelty are NOT established by current baseline. A true PhD contribution requires distinguishing exact new mechanism from prior dominance/presolve and prospective many-instance validation, not merely this theorem.
