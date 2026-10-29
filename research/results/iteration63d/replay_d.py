"""Replay a stratified sample of I63-D tasks on the GATE-TIME gadapt tree (commit bc60030 extracted to /tmp/gt) and compare with archived records."""
import gzip, json, os, sys, random
os.environ["I61_LIBRARY"] = "/tmp/gt"
REPO = "/Users/danijel/Desktop/gadapt"
sys.path[:0] = [os.path.join(REPO, "research")]
import iteration63_replication as m
import gadapt
assert gadapt.__file__.startswith("/tmp/gt"), gadapt.__file__
K = int(sys.argv[1]); W = int(sys.argv[2])
recs = json.load(gzip.open(os.path.join(REPO, "research/results/iteration63d/run.json.gz"), "rt"))["records"]
rng = random.Random(20261029)
by = {}
for r in recs:
    t = r["task"]; by.setdefault((t["network"], t["j"]), {}).setdefault(t["seed"], []).append(r)
sel = []
for k, d in sorted(by.items()):
    for s in rng.sample(sorted(d), K):
        sel += d[s]
if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(W, maxtasksperchild=1) as pool:
        new = pool.map(m.run63, [r["task"] for r in sel], chunksize=1)
    bad = []
    for o, n in zip(sel, new):
        same = all(json.dumps(o[f], sort_keys=True) == json.dumps(n[f], sort_keys=True) for f in ("sequence", "best_feasible", "calls", "generations", "first_target", "T", "failures"))
        if not same: bad.append(o["task"])
    out = dict(sampled=len(sel), mismatches=len(bad), bad=bad, lib="bc60030 (gate-time tree)", seeds_per_cell=K)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_d_out.json"), "w"), indent=1)
    print(out)
