"""EXPLORATORY (not preregistered): Hamming distance of each evaluated vector to best-so-far."""
import random, numpy as np
from research.iteration43_budget_operator_diagnostic import build, Budgeted
from research.iteration44_mutation_mechanism import ValidatorFree
from research.iteration46_component_ablation import make_ga
from research.iteration45_generic_vs_specific import run_textbook_ga

class Probe(ValidatorFree):
    def __init__(self, f, n, skip):
        super().__init__(f, n); self.bestz=None; self.d=[]; self.imp=[]; self.seen=set(); self.dup=0
        if not skip: self.skipped = 2
    def __call__(self, values):
        if self.skipped < 2: return super().__call__(values)
        z=np.rint(np.asarray(values,float)).astype(int); key=z.tobytes()
        if key in self.seen: self.dup+=1
        self.seen.add(key)
        before=self.best; out=super().__call__(values)
        if self.bestz is not None: self.d.append(int(np.sum(z!=self.bestz)))
        self.imp.append(out < before)
        if out <= before: self.bestz=z
        return out

f=build("france"); n=f.n
for name in ("gadapt_A0","textbook"):
    random.seed(4600); np.random.seed(4600)
    p=Probe(f,n, name.startswith("gadapt")); p.budget=3000
    if name=="textbook": run_textbook_ga(p,n)
    else: make_ga(p,n,"A0").execute()
    d=np.array(p.d)
    for lo,hi in ((0,300),(300,1000),(1000,3000)):
        seg=d[lo:hi]; print(f"{name:11s} evals {lo}-{hi}: hamming median={np.median(seg):.0f} p10={np.percentile(seg,10):.0f} p90={np.percentile(seg,90):.0f}  improvements={sum(p.imp[lo:hi])}")
    print(name,'duplicates evaluated',p.dup,'final r',(p.best-f(np.zeros(n,int)))/f(np.zeros(n,int)))
