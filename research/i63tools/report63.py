"""Renders ITERATION63_REPORT_SR.md from research/results/iteration63/*.json.gz (no hand-picked numbers). Run after `analyse` (or after a STOP)."""
import gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "results", "iteration63")
ex = lambda n: os.path.exists(os.path.join(OUT, n + ".json.gz"))
load = lambda n: json.load(gzip.open(os.path.join(OUT, n + ".json.gz"), "rt"))
L = []; w = L.append
w("# ITERATION63: replikacija H56a, kvalitet pri fiksnom budžetu — izveštaj (generisan iz arhive)\n")
w("Protokol: [ITERATION63_PROTOCOL.md](ITERATION63_PROTOCOL.md) (v2, zamrznut `7c1f698`); beleške: [ITERATION63_PRERUN_NOTES.md](ITERATION63_PRERUN_NOTES.md); driver `research/iteration63_replication.py`.\n")
if ex("STOP"):
    s = load("STOP"); w(f"## Ishod: KONAČAN STOP u fazi `{s['stage']}`\n\n{s['reason']}\n\nH63 NIJE ocenjena (STOP ne daje zaključak o H63; grana teze „I63 STOP“).")
stages = [x for x in ("gate", "normalizers", "fxt", "rehearsal", "power", "freeze", "test", "check", "analysis") if ex("manifest_" + x)]
w(f"\nPublikovane faze: {', '.join(stages)}.\n")
if ex("fxt"):
    f = load("fxt"); w(f"## FX-T kalibracija\nIzabrano: SP {f['chosen']['SP']}, FR {f['chosen']['FR']}; pokretanja {len(f['records'])}, ponavljanja {sum(1 for r in f['records'] if r.get('rerun'))}.\n")
if ex("rehearsal"):
    r = load("rehearsal"); w(f"## Razvojna proba: prošla = {r['passed']}\n")
    w("| mreža | kompletno j0/j1 | min izvodljivih po grani | ne-veze FR/SP | d≠0 | var(d) | prošla |\n|---|---|---|---|---|---|---|")
    for n, c in r["criteria"].items():
        w(f"| {n} | {c['complete']} | {min(c['feasible'].values())} | {c['non_tie']} | {c['nonzero']} | {c['variance']:.4f} | {c['passed']} |")
if ex("power"):
    p = load("power"); w(f"\n## Snaga\nizabrani n = {p.get('chosen_n')}, potvrda = {p.get('confirmation_ok')}, kalibracija = {p.get('calibration_ok')}, prošla = {p.get('passed')}.\n")
if ex("analysis"):
    a = load("analysis"); h = a["H63"]
    w("## Primarni rezultat\n")
    w(f"θ₆₃ = {h['estimate']:.4f}; 95% CI [{h['ci95'][0]:.4f}, {h['ci95'][1]:.4f}]; 90% CI [{h['ci90'][0]:.4f}, {h['ci90'][1]:.4f}].\n")
    w(f"- podržano (smer H56a, donja 95% granica > 0): **{h['positive']}**; suprotan smer (gornja < 0): **{h['negative']}**; praktična ekvivalencija (90% CI u (−0,05; 0,05), nijedna mreža degenerisana): **{h['equivalent']}**.")
    w(f"- srednje vrednosti po mreži: {a['network_means']}; izostavljanje jedne mreže: {a['leave_one_network_out']}; pravilo za proširenje tvrdnje teze (donja granica > 0,05, ≥ 2 mreže pozitivne, znak očuvan): **{a['expansion_rule_met']}**.\n")
    w("## Opisno po ćelijama\n\n| ćelija | n | srednje d | W(FR) | W(SP) | izv. FR AD-N | izv. FR FX-T | izv. SP AD-N | izv. SP FX-T |\n|---|---|---|---|---|---|---|---|---|")
    for k, v in sorted(a["descriptive"].items()):
        w(f"| {k} | {v['n']} | {v['d_mean']:.3f} | {v['W|FR']:.3f} | {v['W|SP']:.3f} | {v['FR|AD-N']['feasible']:.2f} | {v['FR|FX-T']['feasible']:.2f} | {v['SP|AD-N']['feasible']:.2f} | {v['SP|FX-T']['feasible']:.2f} |")
if ex("check"):
    c = load("check"); w(f"\n## Nezavisna provera: očekivano {c['expected']}, redova {c['rows']}, neuspeha {c['failures']}.")
w("\n## Ograničenja\nPonovno korišćene topologije; B = 12.000 izabran posle uvida u I61 razvojne medijane (pilot); kontrast uključuje zasebno podešavanje FX-T po CHT-u; estimand ≠ vreme dostizanja H56a; nema tvrdnje o novoj metodi.")
open(os.path.join(os.path.dirname(HERE), "ITERATION63_REPORT_SR.md"), "w").write("\n".join(L) + "\n"); print("written")
