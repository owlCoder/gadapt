"""I39 source SNDlib MODULAR-capacity common-plan model and HiGHS MILP.

PREREG: research/ITERATION39_PROTOCOL.md committed before all I39 solvers.
The reduction from full native (20..800) options to unlimited (20,40) modules
is used ONLY if every original menu is independently audited to be EXACTLY
equivalent at the same source price. No hypothetical cost cap or recourse.
"""
import math
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix
from research.iteration38_joint_capacity_model import JointCapacityProblem


NETWORK_SHA="35e58a3799d78d2ebfd2a557be2ba4a221ca17fc704cfdd13df56bb90c12a796"
ARCHIVE_SHA="2c3ca706a8d5c9601eb4d144651816dfd956257c20f60111a8aceb5f07ab0100"


def verify_exact_source_module_equivalence(links):
    """A formal cost/isomorphism gate. Fail before solver if any edge violates."""
    prices=[]
    for link in links:
        if any(abs(v)>1e-8 for v in
               (link.base,link.base_cost,link.setup_cost,link.routing_cost)):
            raise ValueError("I39 requires exact source zero base/routing/setup terms")
        menu=dict(link.options)
        if len(menu)!=40 or set(menu)!={float(20*k) for k in range(1,41)}:
            raise ValueError("I39 original source must list capacities 20,40,...,800")
        c20,c40=menu[20.],menu[40.]
        if not all(math.isfinite(v) and v>0 for v in (c20,c40)):
            raise ValueError("Nonfinite native source module price")
        if not (c20<=c40<=2*c20):
            raise ValueError("I39 O(1) exact module-cost reduction condition failed")
        for k in range(1,41):
            expected=(k//2)*c40+(k%2)*c20
            if abs(menu[float(20*k)]-expected)>1e-6:
                raise ValueError("A listed source module breaks 20/40-price equivalence")
        prices.append((float(c20),float(c40)))
    return tuple(prices)


class ModularCommonPlan(JointCapacityProblem):
    def __init__(self,nodes,links,pairs,traffic):
        self.module_prices=verify_exact_source_module_equivalence(links)
        super().__init__(nodes,links,pairs,traffic)

    def evaluate(self,choices):
        z=np.asarray(choices,dtype=float)
        if z.shape!=(self.n,) or not np.all(np.isfinite(z)):
            raise ValueError("Wrong number of static route choices")
        if not np.all((abs(z)<1e-7)|(abs(z-1.)<1e-7)):
            raise ValueError("Route choice must be integer in {0,1}")
        z=np.rint(z).astype(int)
        load=self.base+self.q @ (self.delta * z[:,None])
        peak=np.max(load,axis=0)
        # At every edge: source module capacities 20,40; source costs c20,c40.
        # With c20<=c40<=2c20, the cheapest cover of R>=0 is exactly
        # floor(ceil(R/20)/2) x40 plus (ceil(R/20)%2) x20 modules.
        needed=np.maximum(0.,peak-self.base_cap)
        quanta=np.maximum(0,np.ceil(needed/20. - 1e-10)).astype(int)
        n40=quanta//2
        n20=quanta%2
        cap=self.base_cap+20*n20+40*n40
        prices=np.asarray(self.module_prices,dtype=float)
        cost=float(np.sum(n20*prices[:,0]+n40*prices[:,1]))
        return dict(feasible=True,cost=cost,
                    modules_20=[int(v) for v in n20],
                    modules_40=[int(v) for v in n40],
                    installed_capacity=[float(v) for v in cap],
                    max_required_capacity=[float(v) for v in peak],
                    worst_excess=float(np.max(np.maximum(0.,peak-cap))),
                    training_snapshots_violated=int(np.sum(np.any(load>cap[None,:]+1e-7,axis=1))))


def exact_modular_milp(problem,seconds=180.):
    if not isinstance(problem,ModularCommonPlan):
        raise TypeError("I39 MILP requires EXACT same original modular planning model")
    d,e,t=problem.n,len(problem.links),len(problem.q)
    num=d+2*e
    obj=np.zeros(num)
    for i,(c20,c40) in enumerate(problem.module_prices):
        obj[d+2*i]=c20
        obj[d+2*i+1]=c40
    rr,cc,vv=[],[],[]
    rhs=np.empty(e*t)
    for edge in range(e):
        touched=np.flatnonzero(problem.delta[:,edge])
        for ti in range(t):
            row=edge*t+ti
            rhs[row]=problem.base_cap[edge]-problem.base[ti,edge]
            for demand in touched:
                coefficient=problem.q[ti,demand]*problem.delta[demand,edge]
                if coefficient!=0:
                    rr.append(row);cc.append(int(demand));vv.append(float(coefficient))
            rr.extend((row,row));cc.extend((d+2*edge,d+2*edge+1))
            vv.extend((-20.,-40.))
    A=coo_matrix((vv,(rr,cc)),shape=(e*t,num)).tocsr()
    lb=np.zeros(num)
    ub=np.full(num,np.inf)
    ub[:d]=1
    out=milp(c=obj,integrality=np.ones(num,dtype=int),bounds=Bounds(lb,ub),
             constraints=LinearConstraint(A,-np.inf,rhs),
             options=dict(time_limit=float(seconds),mip_rel_gap=.01,presolve=True))
    def finite_float(value):
        return float(value) if value is not None and math.isfinite(value) else None
    result=dict(status=int(out.status),message=str(out.message),
                solver_objective=finite_float(out.fun),
                dual_bound=finite_float(getattr(out,"mip_dual_bound",None)),
                mip_gap=finite_float(getattr(out,"mip_gap",None)),
                mip_variables=num,source_capacity_constraints=e*t,
                incumbent=None)
    if out.x is not None:
        z=[int(round(v)) for v in out.x[:d]]
        verified=problem.evaluate(z)
        if not verified["feasible"] or verified["worst_excess"]>1e-6:
            raise RuntimeError("MILP chose an invalid common source capacity plan")
        if (result["solver_objective"] is not None and
                verified["cost"]>result["solver_objective"]+1e-4):
            raise RuntimeError("Independent minimum source module cost exceeds MIP incumbent")
        result["incumbent"]=dict(choices=z,**verified)
    if result["dual_bound"] is not None and result["incumbent"] is not None:
        if result["dual_bound"]>result["incumbent"]["cost"]+1e-5:
            raise RuntimeError("HiGHS purported valid lower bound greater than incumbent")
    return result
