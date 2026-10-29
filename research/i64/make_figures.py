"""Thesis figures for CH8 from the archived analyses (no hand-typed numbers). Output: research/figures/i64/*.png and .csv (table view of every plotted value).
Colours: validated categorical slots 1-6 (blue, orange, aqua, yellow, magenta, violet; contrast WARN => every bar carries its value label and a CSV table exists)."""
import gzip, json, os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(os.path.dirname(HERE), "results"); OUT = os.path.join(os.path.dirname(HERE), "figures", "i64")
os.makedirs(OUT, exist_ok=True)
load = lambda p: json.load(gzip.open(os.path.join(R, p), "rt"))
E3 = load("iteration64_e3/analysis.json.gz")["aggregate_by_variant"]
E2 = load("iteration64_e2/analysis.json.gz")["aggregate_by_variant"]
CFG = [("gadapt", "GAdapt-M", "#2a78d6"), ("gadapt_hyb", "GAdapt→CMA", "#eb6834"), ("ipop", "IPOP-CMA", "#1baf7a"), ("cma", "CMA", "#eda100"), ("de", "SciPy DE", "#e87ba4")]
VAR = ("orig", "shift", "rot")
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b", "text.color": "#0b0b0b",
                     "xtick.color": "#52514e", "ytick.color": "#52514e", "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
rows = []
for metric, title, fname, fmt in (("cvar90", "Rep raspodele: prosek najgorih 10% (CVaR$_{0,9}$ od L), niže je bolje", "fig_cvar_by_variant.png", "{:.4f}"),
                                  ("A", "Efikasnost: ECDF-površina do 12.000 poziva, više je bolje", "fig_ecdf_by_variant.png", "{:.3f}")):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), sharey=True)
    for ax, var in zip(axes, VAR):
        vals = [E3[var][c][metric] if c in E3[var] else np.nan for c, _, _ in CFG]
        bars = ax.bar(range(len(CFG)), vals, color=[col for _, _, col in CFG], width=0.62, edgecolor="#fcfcfb", linewidth=2)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center", va="bottom", fontsize=7, color="#52514e")
        ax.set_xticks(range(len(CFG))); ax.set_xticklabels([n for _, n, _ in CFG], rotation=35, ha="right", fontsize=8)
        ax.set_title({"orig": "originalno", "shift": "pomereno", "rot": "pomereno + rotirano"}[var], fontsize=9, color="#52514e")
        ax.grid(axis="y", color="#e5e4df", linewidth=0.6); ax.set_axisbelow(True)
        for (c, n, _), v in zip(CFG, vals): rows.append([metric, var, c, v])
    axes[0].set_ylabel({"cvar90": "CVaR$_{0,9}$", "A": "ECDF-površina A"}[metric])
    fig.suptitle(title, fontsize=10, x=0.01, ha="left"); fig.tight_layout(); fig.savefig(os.path.join(OUT, fname), dpi=200); plt.close(fig)
# kappa vs outcome (E development, post hoc)
k = json.load(open(os.path.join(R, "iteration64_e", "kappa_vs_outcome.json")))["rows"]
kap = np.array([r[4] for r in k]); dA = np.array([r[5] for r in k]); var = [r[3] for r in k]
fig, ax = plt.subplots(figsize=(5.2, 3.6))
mk = {"orig": ("o", "#2a78d6"), "shift": ("s", "#1baf7a"), "rot": ("^", "#eb6834")}
for v in VAR:
    m = np.array([x == v for x in var])
    ax.scatter(kap[m], dA[m], marker=mk[v][0], color=mk[v][1], s=26, edgecolor="#fcfcfb", linewidth=1, label={"orig": "originalno", "shift": "pomereno", "rot": "rotirano"}[v])
ax.axhline(0, color="#52514e", linewidth=0.8)
ax.set_xlabel("indeks sprege $\\kappa$ (procena Hesijana)"); ax.set_ylabel("$A_{GAdapt} - A_{IPOP}$ (ECDF-površina)")
ax.set_title("POST HOC (razvoj, E arhiva): razlika u efikasnosti naspram $\\kappa$", fontsize=9, loc="left")
ax.legend(frameon=False, fontsize=8); ax.grid(color="#e5e4df", linewidth=0.6); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_kappa_vs_advantage.png"), dpi=200); plt.close(fig)
for kk, a, v in zip(kap, dA, var): rows.append(["kappa_vs_dA", v, f"{kk:.4f}", a])
with open(os.path.join(OUT, "figures_table.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "variant_or_group", "config_or_kappa", "value"]); w.writerows(rows)
print("figures written to", OUT)
