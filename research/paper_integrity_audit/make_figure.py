"""Figure 1 of the manuscript: runs with each finding class, per library, from the raw I49/I50/I51 outputs.

Run with an interpreter that has matplotlib (e.g. the I49 environment from research/h4_requirements_lock.txt).
"""
import ast
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "results")
CLASSES = ["C3", "C4", "C5", "R1", "R2", "R3", "D3", "D3x"]
NAMES = {"scipy_de": "SciPy DE", "geneticalgorithm": "geneticalgorithm", "gfo": "GFO", "scikit_opt": "scikit-opt",
         "bayes_opt": "bayes_opt", "evolopy": "EvoloPy", "niapy": "NiaPy", "smac": "SMAC", "cma": "cma",
         "pymoo": "pymoo", "deap": "DEAP", "pygad": "PyGAD", "nevergrad": "Nevergrad", "optuna": "Optuna",
         "pyswarms": "PySwarms", "cmaes": "cmaes", "emukit": "emukit", "baybe": "baybe", "bofire": "bofire",
         "evotorch": "evotorch", "evox": "evox"}
CONTRADICTS = {("cma", "C4"), ("nevergrad", "D3"), ("nevergrad", "D3x"), ("gfo", "R2"), ("gfo", "R3"),
               ("smac", "D3x")}
# checks whose input the adapter never returns: C4 needs a documented maximum, R1 a returned x, R2/R3 also a returned f
NEEDS = {"C4": "documented_max", "R1": "x", "R2": "f", "R3": "f"}
# Nevergrad returns f only when the recommendation carries a loss, which was not archived per run
UNKNOWN = {("nevergrad", "R2"), ("nevergrad", "R3")}
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"
BLUES = LinearSegmentedColormap.from_list("blue", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
NA_GREY = "#e4e3df"


def returned_fields(script):
    """Adapter name -> result fields it returns (not None), read from the top-level return of each run_* function."""
    out = {}
    for fn in ast.parse(open(os.path.join(os.path.dirname(HERE), script)).read()).body:
        if not (isinstance(fn, ast.FunctionDef) and fn.name.startswith("run_")):
            continue
        call = next(n.value for n in fn.body if isinstance(n, ast.Return))
        fields = dict(zip(["x", "f", "reported_evals", "documented_max"], call.args))
        fields.update({k.arg: k.value for k in call.keywords})
        out[fn.name[4:]] = {k for k, v in fields.items() if not (isinstance(v, ast.Constant) and v.value is None)}
    return out


def applicability(lib, fields, cls):
    """'yes', 'n/a' (the adapter cannot produce the check's input) or '?' (applicability not archived)."""
    if (lib, cls) in UNKNOWN:
        return "?"
    return "n/a" if cls in NEEDS and NEEDS[cls] not in fields else "yes"


def rows():
    i49 = json.load(open(os.path.join(RES, "iteration49", "integrity_audit.json")))["per_library"]
    i51 = json.load(open(os.path.join(RES, "iteration51", "d3x.json")))["per_library"]
    i50 = json.load(open(os.path.join(RES, "iteration50", "integrity_audit.json")))["per_library"]
    f49, f50 = returned_fields("iteration49_integrity_audit.py"), returned_fields("iteration50_integrity_audit.py")
    out = []
    for lib, r in i49.items():
        if lib == "gadapt":
            continue
        counts = dict(r["runs_with_class"], D3x=i51[lib]["d3x_runs"])
        out.append(("Study 1", lib, counts, r["runs"] - r["errors"], r["median_duplicate_fraction"], f49[lib]))
    for lib, r in sorted(i50.items()):
        fields = f50[lib] - ({"x", "f"} if not r["r_applicable"] else set())
        out.append(("Study 2", lib, r["runs_with_class"], r["runs"] - r["errors"], r["median_duplicate_fraction"],
                    fields))
    return out


def main():
    data = rows()
    cols = CLASSES + ["C1"]
    fig, ax = plt.subplots(figsize=(7.4, 8.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, (study, lib, counts, completed, dup, fields) in enumerate(data):
        for j, cls in enumerate(cols):
            n = counts.get(cls) or 0
            x = j + (0.4 if cls == "C1" else 0)
            status = applicability(lib, fields, cls)
            if status == "n/a":
                assert n == 0, (lib, cls)
                ax.add_patch(Rectangle((x + 0.04, i + 0.04), 0.92, 0.92, facecolor=NA_GREY, edgecolor=MUTED,
                                       hatch="////", lw=0))
                ax.text(x + 0.5, i + 0.52, "n/a", ha="center", va="center", fontsize=6.5, color=INK,
                        bbox=dict(boxstyle="square,pad=0.05", facecolor=NA_GREY, edgecolor="none"))
            elif status == "?" and not n:
                ax.text(x + 0.5, i + 0.52, "?", ha="center", va="center", fontsize=8, color=MUTED)
            elif not n:
                ax.text(x + 0.5, i + 0.52, "0", ha="center", va="center", fontsize=7, color="#b4b2ad")
            if n:
                colour = BLUES(n / completed) if cls != "C1" else "#d9d8d4"
                ax.add_patch(Rectangle((x + 0.04, i + 0.04), 0.92, 0.92, facecolor=colour, edgecolor="none"))
                light = cls != "C1" and n / completed > 0.45
                ax.text(x + 0.5, i + 0.52, str(n), ha="center", va="center", fontsize=8,
                        color=SURFACE if light else INK)
            if (lib, cls) in CONTRADICTS:
                ax.add_patch(Rectangle((x + 0.04, i + 0.04), 0.92, 0.92, facecolor="none", edgecolor=INK, lw=1.8))
        label = f"{dup * 100:.1f}%" if dup and dup >= 0.0005 else "0"
        ax.text(len(cols) + 0.75, i + 0.52, label, ha="left", va="center", fontsize=8, color=MUTED)
        suffix = f"  ({completed})" if completed < 30 else ""
        ax.text(-0.15, i + 0.52, NAMES.get(lib, lib) + suffix, ha="right", va="center", fontsize=8.5, color=INK)
    split = sum(1 for d in data if d[0] == "Study 1")
    ax.axhline(split, color=MUTED, lw=0.8)
    ax.text(len(cols) + 2.6, split / 2, "Study 1\n(chosen)", ha="center", va="center", fontsize=8, color=MUTED)
    ax.text(len(cols) + 2.6, split + (len(data) - split) / 2, "Study 2\n(external\nrule)", ha="center", va="center",
            fontsize=8, color=MUTED)
    for j, cls in enumerate(cols):
        x = j + (0.4 if cls == "C1" else 0)
        ax.text(x + 0.5, -0.35, cls, ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="bold")
    ax.text(len(cols) + 0.75, -0.35, "repeated", ha="left", va="bottom", fontsize=8.5, color=INK, fontweight="bold")
    ax.text(8.9, -1.25, "info", ha="center", va="bottom", fontsize=7.5, color=MUTED)
    ax.text(4.0, -1.25, "integrity classes", ha="center", va="bottom", fontsize=7.5, color=MUTED)
    ax.set_xlim(-0.2, len(cols) + 3.4)
    ax.set_ylim(len(data) + 0.2, -1.6)
    ax.axis("off")
    fig.text(0.02, 0.035, "Cell: runs (of 30 per library; fewer completed in parentheses) in which the class occurred; "
             "shade = share of completed runs.\nDark outline: behaviour that contradicts the library's documentation "
             "(rule pre-specified in Study 2, applied post hoc\nin Study 1). Study 1 D3x comes from Study 3. C1 (corner "
             "evaluations) is shown apart because it proved non-specific.\n\"repeated\": median share of re-evaluated "
             "points. \"0\": checked, not found. Hatched \"n/a\": the adapter does not return the check's\ninput (C4: no "
             "documented maximum; R1: no returned point; R2/R3: no returned value). \"?\": applicability not\narchived "
             "per run.", fontsize=7.2, color=MUTED, va="bottom")
    fig.subplots_adjust(left=0.24, right=0.99, top=0.97, bottom=0.15)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"fig_integrity_matrix.{ext}"), dpi=200, facecolor=SURFACE)


if __name__ == "__main__":
    main()
