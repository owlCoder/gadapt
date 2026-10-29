"""POST HOC sensitivity analyses of I64-S0 computed only from the archive (Codex 085). Not part of the frozen primary analysis."""
import gzip, json, math, os
import numpy as np
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration64_s0")
load = lambda n: json.load(gzip.open(os.path.join(OUT, n + ".json.gz"), "rt"))
R, N = load("runs")["records"], load("normalizers")
CFG = ["gadapt", "pygad_random", "pygad_adaptive", "de"]; TAUS = (1e-2, 1e-4, 1e-6); BA = 12000
cells = sorted({(r["function"], r["d"]) for r in R}); nd = defaultdict(int)
for f, d in cells: nd[f] += 1
W = {(f, d): (1 / 9) / nd[f] for f, d in cells}
G = lambda r, f: max(0.0, (f - N[f"{r['function']}|{r['d']}"]["f_star"]) / N[f"{r['function']}|{r['d']}"]["s"])

def gap_at(r, B):
    best = math.inf
    for c, f, _ in r["events"]:
        if c <= B: best = f
    return G(r, best) if best < math.inf else math.inf

def area(r, mode):
    tot = 0.0
    for tau in TAUS:
        hit = None
        for c, f, ns in r["events"]:
            if G(r, f) <= tau:
                hit = c if mode == "all" else max(1, ns)  # search-only: initial manual evaluations count as search call 1
                break
        if hit is not None and hit <= BA: tot += (BA - hit + 1) / BA
    return tot / len(TAUS)

def by(cfg, f=None, seeds=None):
    return [r for r in R if r["config"] == cfg and (f is None or (r["function"], r["d"]) == f) and (seeds is None or r["s"] in seeds)]

out = []
w = out.append
w("\n## 6. Post hoc osetljivosti (samo iz arhive; Codex 085) — NISU deo zamrznute primarne analize\n")
w("### 6.1 Preciznost pri najviše B fizičkih poziva (jednak budžet; ranije završena pokretanja zadržavaju rezultat)\n")
w("| B | konfiguracija | M_B (ponderisan prosek ćelijskih medijana g) | CVaR₀,₉ (L) | P(g≤1e−2) | ćelije: GAdapt bolji / gori / jednak (medijana) |\n|---|---|---|---|---|---|")
for B in (3000, 12000):
    med = {c: {k: float(np.median([gap_at(r, B) for r in by(c, k)])) for k in cells} for c in CFG}
    for c in CFG:
        m = sum(W[k] * med[c][k] for k in cells)
        cv = sum(W[k] * (lambda L: float(np.mean(sorted(L)[-2:])))([x / (1 + x) for x in (gap_at(r, B) for r in by(c, k))]) for k in cells)
        pr = sum(W[k] * float(np.mean([gap_at(r, B) <= 1e-2 for r in by(c, k)])) for k in cells)
        if c == "gadapt": cmp_ = "—"
        else:
            b = sum(med["gadapt"][k] < med[c][k] for k in cells); g_ = sum(med["gadapt"][k] > med[c][k] for k in cells)
            cmp_ = f"{b} / {g_} / {len(cells) - b - g_}"
        w(f"| {B} | {c} | {m:.4g} | {cv:.4f} | {pr:.3f} | {cmp_} |")
w("\n### 6.2 ECDF površina: svi pozivi vs samo „search“ pozivi (ispravljeno: početna ručna evaluacija = search poziv 1)\n")
w("| konfiguracija | A (svi fizički pozivi) | A (samo search) |\n|---|---|---|")
for c in CFG:
    w(f"| {c} | {sum(W[k] * np.mean([area(r, 'all') for r in by(c, k)]) for k in cells):.4f} | {sum(W[k] * np.mean([area(r, 'search') for r in by(c, k)]) for k in cells):.4f} |")
w("\n### 6.3 Doprinos funkcija agregatnom ΔM prema DE (pri izvornom zaustavljanju) i izostavljanje po jedne funkcije\n")
med_orig = {c: {k: float(np.median([G(r, r["best_f"]) for r in by(c, k)])) for k in cells} for c in CFG}
funcs = sorted({f for f, _ in cells})
tot = {c: sum(W[k] * (med_orig[c][k] - med_orig["gadapt"][k]) for k in cells) for c in CFG[1:]}
w("| funkcija | doprinos ΔM(DE) | ΔM(DE) bez te funkcije (renormalizovano) |\n|---|---|---|")
for f in funcs:
    contrib = sum(W[k] * (med_orig["de"][k] - med_orig["gadapt"][k]) for k in cells if k[0] == f)
    rest = [k for k in cells if k[0] != f]; ws = sum(W[k] for k in rest)
    w(f"| {f} | {contrib:.4g} | {sum(W[k] * (med_orig['de'][k] - med_orig['gadapt'][k]) for k in rest) / ws:.4g} |")
w(f"\nUkupno ΔM(DE) = {tot['de']:.4g}; ΔM(PyGAD random) = {tot['pygad_random']:.4g}; ΔM(PyGAD adaptive) = {tot['pygad_adaptive']:.4g}.\n")
w("### 6.4 Bez semena 1–3 (viđena u probi pre glavnog pokretanja): ΔA i ΔM tačkaste procene na semenima 4–20\n")
seeds = set(range(4, 21))
for c in CFG[1:]:
    dA = sum(W[k] * (np.mean([area(r, "all") for r in by("gadapt", k, seeds)]) - np.mean([area(r, "all") for r in by(c, k, seeds)])) for k in cells)
    dM = sum(W[k] * (np.median([G(r, r["best_f"]) for r in by(c, k, seeds)]) - np.median([G(r, r["best_f"]) for r in by("gadapt", k, seeds)])) for k in cells)
    w(f"- {c}: ΔA = {dA:.4f}, ΔM = {dM:.4g}")
w("\n## 7. Odstupanja i napomene (Codex 085)\n")
w("- Primarna analiza sprovedena po protokolu; nema odstupanja u primarnim računskim koracima (nezavisno reprodukovano, t* = 3,2138).")
w("- Provenijencija S0: manifest hešira drajver i protokol, ne i sve tranzitivne izvore (mentorov klon pinovan je komitom; razrešena podešavanja su u drajveru); normalizator arhivira s, f*, minimum uzorka, ne i uzorke; seme normalizatora (64001) je u drajveru.")
w("- Semena u kodu: `c` = indeks u listi `FUNCS` (ne `3i+v`), uparivanje konfiguracija očuvano; PyGAD dobija globalno postavljena semena, bez `random_seed`.")
w("- Styblinski–Tang f* računat u dvostrukoj preciznosti. Faza svakog događaja nije sačuvana (samo indeks pretraživačkih poziva). CVaR za n = 20: prosek dva najlošija ishoda.")
w("- Pomoćna kolona „A (samo search)“ u tabeli 2 koristi neispravan nulti indeks za PyGAD (početna ručna evaluacija); ispravljena vrednost je u 6.2.")
w("\n## 8. Šta S0 sme da tvrdi (formulacija; ćelijska brojanja su POST HOC, opisna)\n")
w("S0 podržava operacionalizovanu H64a: među četiri ispitane konfiguracije GAdapt ima veći ponderisani prosečni ECDF A do 12.000 fizičkih poziva od sva tri konkurenta, prema simultanim bootstrap intervalima sa nominalnim porodičnim α = 0,01 (prolaz grane „svi ΔA pozitivni“; „izuzetak“ nije potreban). Završna preciznost je **manji ponderisani prosek ćelijskih medijana pri izvornom zaustavljanju**, ne pri jednakom budžetu, i veliki deo agregata dolazi iz dve ćelije (Rastrigin-20, Griewank-7). Po ćelijama SciPy DE ima manju medijanu u 14 od 21 ćelije, GAdapt veći A u 17 od 21. S0 NE tvrdi opštu veću preciznost, prednost u većini ćelija, industrijsku pouzdanost, korist preseta ni uzročnu ulogu mutacionog operatora; funkcije nisu pomerene ni rotirane. Prethodni uvid u semena 1–3 obelodanjen je.")
path = os.path.join(os.path.dirname(HERE), "ITERATION64_S0_REPORT_SR.md")
body = open(path).read().split("\n## 6. Post hoc")[0]
open(path, "w").write(body.rstrip("\n") + "\n" + "\n".join(out) + "\n")
print("appended")
