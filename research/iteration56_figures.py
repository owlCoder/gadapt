"""Figures of the I56 report, from results/iteration56/{test,analysis}.json.gz (written before any test result).

Run with an interpreter that has matplotlib 3.11.2 (research/h4_requirements_lock.txt):
  python research/iteration56_figures.py [results_dir] [output_dir]
"""
import gzip
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE = "#2a78d6"
SERIES = {("FR", "AD-N"): ("#2a78d6", "-"), ("FR", "FX-T"): ("#eb6834", "-"),
          ("SP", "AD-N"): ("#1baf7a", "--"), ("SP", "FX-T"): ("#eda100", "--")}
NETWORKS, RESOLUTIONS = ("case14", "case57", "case118"), (9, 17, 33)


def load(directory, name):
    with gzip.open(os.path.join(directory, name + ".gz"), "rt") as f:
        return json.load(f)


def units(records):
    table = {}
    for r in records:
        t = r["task"]
        table.setdefault((t["network"], t["resolution"], t["scenario_index"], t["seed"]), {})[(t["cht"], t["arm"])] = r
    return table


def style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def figure_interaction(table, analysis, out):
    """Points: descriptive, unweighted within-block mean d; bars: 95% percentile intervals from 5000 simple within-block
    bootstrap resamples (scenarios pooled). Line/band: protocol θ_a and its 95% cell-stratified interval (20,000
    resamples, equal scenario/block weights). No blockwise hypothesis tests."""
    import iteration56_cht_study as st
    fig, ax = plt.subplots(figsize=(7.2, 3.4), facecolor=SURFACE)
    style(ax)
    labels, x = [], 0
    rng = np.random.RandomState(56)
    for n in NETWORKS:
        for R in RESOLUTIONS:
            ds = np.array([st.d_a(u) for (nn, RR, j, s), u in table.items() if nn == n and RR == R
                           and len(u) == len(st.TEST_ARMS) and all(r["ok"] for r in u.values())])
            if len(ds):
                boots = ds[rng.randint(0, len(ds), (5000, len(ds)))].mean(axis=1)
                lo, hi = np.percentile(boots, [2.5, 97.5])
                ax.plot([x, x], [lo, hi], color=BLUE, lw=2, solid_capstyle="round")
                ax.plot(x, ds.mean(), "o", ms=8, color=BLUE, mec=SURFACE, mew=2)
            labels.append(f"{n}\nR={R}")
            x += 1
        x += 0.5
    h = analysis["results"]["H56a"] if analysis.get("results") else None
    if h:
        ax.axhspan(h["ci"][0], h["ci"][1], color=BLUE, alpha=0.12, lw=0)
        ax.axhline(h["estimate"], color=BLUE, lw=1)
        ax.text(x - 0.4, h["estimate"], f" θa = {h['estimate']:+.3f}", va="center", fontsize=8, color=INK)
    ax.axhline(0, color=MUTED, lw=0.8)
    ticks = [i + 0.5 * (i // 3) for i in range(9)]
    ax.set_xticks(ticks, labels, fontsize=7.5)
    ax.set_ylabel("interaction d (time-to-target units)", fontsize=8.5, color=INK)
    ax.set_title("H56a: does the effect of adaptation depend on the constraint handling? (FR vs SP)",
                 fontsize=9, color=INK, loc="left")
    fig.text(0.01, 0.01, "Points/bars: descriptive within-block means and simple bootstrap intervals (no blockwise tests).\n"
             "Line/band: protocol estimate θa with its cell-stratified 95% interval.", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"fig56_interaction.{ext}"), dpi=200, facecolor=SURFACE)


def figure_heatmap(table, out):
    """Mean T per arm (rows) and block (columns); one sequential blue ramp."""
    import iteration56_cht_study as st
    from matplotlib.colors import LinearSegmentedColormap
    ramp = LinearSegmentedColormap.from_list("blue", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    arms = st.TEST_ARMS
    cols = [(n, R) for n in NETWORKS for R in RESOLUTIONS]
    grid = np.full((len(arms), len(cols)), np.nan)
    for i, arm in enumerate(arms):
        for k, (n, R) in enumerate(cols):
            ts = [u[arm]["T"] for (nn, RR, j, s), u in table.items() if nn == n and RR == R and arm in u and u[arm]["ok"]]
            if ts:
                grid[i, k] = np.mean(ts)
    fig, ax = plt.subplots(figsize=(7.2, 5.2), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    image = ax.imshow(grid, cmap=ramp, vmin=0, vmax=1, aspect="auto")
    for i in range(len(arms)):
        for k in range(len(cols)):
            if np.isfinite(grid[i, k]):
                ax.text(k, i, f"{grid[i, k]:.2f}", ha="center", va="center", fontsize=6.5,
                        color=SURFACE if grid[i, k] > 0.4 else INK)
    ax.set_xticks(range(len(cols)), [f"{n}\nR={R}" for n, R in cols], fontsize=7)
    ax.set_yticks(range(len(arms)), [f"{c} · {a}" for c, a in arms], fontsize=7)
    for side in ax.spines.values():
        side.set_visible(False)
    bar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    bar.set_label("mean T (T = 1: target unreached or first reached at call 3000)", fontsize=7.5, color=INK)
    bar.ax.tick_params(labelsize=7, colors=MUTED)
    ax.set_title("Descriptive mean restricted normalized time to target by arm and block (lower is better)",
                 fontsize=9, color=INK, loc="left")
    fig.text(0.01, 0.005, "Unweighted average over successful runs within each block; scenarios pooled;\n"
             "includes successful runs of incomplete units.", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"fig56_mean_T.{ext}"), dpi=200, facecolor=SURFACE)


def figure_attainment(table, out):
    """Share of runs that reached the target by each number of power flows, pooled over all blocks."""
    fig, ax = plt.subplots(figsize=(7.2, 3.6), facecolor=SURFACE)
    style(ax)
    calls = np.arange(1, 3001)
    ends = []
    for arm, (colour, dash) in SERIES.items():
        firsts = np.array([u[arm]["first_target"] or np.inf for u in table.values() if arm in u and u[arm]["ok"]], float)
        if not len(firsts):
            continue
        share = (firsts[None, :] <= calls[:, None]).mean(axis=1)
        ax.plot(calls, share, color=colour, ls=dash, lw=2, label=f"{arm[0]} · {arm[1]}")
        ends.append([share[-1], f"{arm[0]} · {arm[1]}"])
    ends.sort()
    for i in range(1, len(ends)):  # direct labels, nudged apart so they never collide
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 0.045)
    for y, text in ends:
        ax.text(3010, y, f" {text}", va="center", fontsize=7.5, color=INK)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)
    ax.set_xlim(0, 3400)
    ax.set_ylim(0, 1)
    ax.set_xlabel("power flows (calls)", fontsize=8.5, color=INK)
    ax.set_ylabel("share of runs at target", fontsize=8.5, color=INK)
    ax.set_title("Target attainment (solid: feasibility rules, dashed: static penalty)", fontsize=9, color=INK,
                 loc="left")
    counts = {f"{a[0]}·{a[1]}": sum(1 for u in table.values() if a in u and u[a]["ok"]) for a in SERIES}
    fig.text(0.01, 0.01, "Descriptive cumulative attainment among successful runs, pooled across blocks, each run equal weight\n"
             "(case57 blocks contribute half as many runs). n = " + ", ".join(f"{k} {v}" for k, v in counts.items()),
             fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"fig56_attainment.{ext}"), dpi=200, facecolor=SURFACE)


def main():
    results = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "results", "iteration56")
    out = sys.argv[2] if len(sys.argv) > 2 else results
    table = units(load(results, "test.json")["records"])
    analysis = load(results, "analysis.json")
    figure_interaction(table, analysis, out)
    figure_heatmap(table, out)
    figure_attainment(table, out)


if __name__ == "__main__":
    main()
