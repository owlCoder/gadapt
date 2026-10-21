# Iteracija 16 — izvorni standardni AC-OPF kontrolni reperi IEEE14 i IEEE118

**Registrovano:** 21.10.2026 pre novih AC-OPF poziva iteracije 16. Ne menja osnovni GAdapt niti upstream. Ovo je zasebna kontrolna lestvica dok veliki izvorni MATPOWER RTE1888 ekonomski AC-OPF još nije nezavisno potvrđen (iteracija 14 failed, iteracija 15 je zaseban solver test).

## Fiksni domenski zadaci

PYPOWER v5.1.19 *nemodifikovani ugrađeni* case14 i case118, sa izvornim originalnim ekonomskim polinomnim `gencost` po generatoru, originalnim sabirnicama, P/Q, V, tap, šant i RATE_A. Javni istorijski IEEE *testni modeli* nisu stvarni industrijski dispečing. Posebno nije dozvoljeno tvrditi da rezultat na IEEE14/118 validira francusku mrežu RTE1888.

## Stvarni ograničeni budžet

Tačno po jedan izvorni native AC-OPF pokušaj na case14 i case118, **najviše 2 stvarna AC-OPF solver poziva**. Uvek izvesti oba, čak i ako prvi ne uspe (različiti javni zadaci). Solver PYPOWER `runopf` `OPF_ALG=560`, `OPF_FLOW_LIM=0` MVA na oba kraja, `PF_DC=0`, `OPF_IGNORE_ANG_LIM=False`, `OPF_VIOLATION=5e-6`, `PDIPM_MAX_IT=100`, `VERBOSE=0, OUT_ALL=0`; jednonitni BLAS, Python 3.12, PYPOWER 5.1.19, SciPy 1.13.1, pandas2.2.3, pandapower2.14.11. Timeout po pozivu 120 s (IEEE14) / 300 s (IEEE118).

## Independent post-hoc standard proverljivosti

Samo ako native OPF prijavi `success=True`, posebno ponovo izračunati:
1. Individualne P/Q izvorne granice aktivnih generatora, izvorne sabirničke VMIN/VMAX, oba kraja svih pozitivnih originalnih RATE_A MVA grana; RATE_A=0 NE znači limit.
2. Kompleksni AC nodalni KCL `V*conj(Ybus V) = (PG+jQG-PD-jQD-shunts)/baseMVA` preko standardnih PYPOWER matričnih rutina `makeYbus/makeSbus`, ali **ne predstavljati kao električki nezavisnu implementaciju** — to je nezavisan naknadni rezidual istog modela, a ne drugi solver.
3. Originalni kvadratni generatorski trošak `sum(c2*PG**2+c1*PG+c0)` nad aktivnim generatorima, odvojen od gubitaka u MW, uporediti sa `result['f']`. Ne koristiti rezultate gde source gen/gencost row ID nisu poravnati.
4. Numeričke pragove definisati unapred: V <=1e-5 p.u.; generator P/Q max prekoračenje <=1e-3 MW/MVAr, RATE_A terminal MVA max excess <=1e-3 MVA, max kompleksni KCL <=1e-3 MVA i ekonomskog f <=max(1e-3, 1e-7*abs(f)). Nije dovoljan `success=True`, mora i sve da prođe.
5. Ako solver ne uspe ili exception, **nema validnih fizičkih PG/Q/V/MVA, objective ili gubitaka**, čuvati null + grešku. Ako solver tvrdi uspeh a nezavisne provere padnu, čuvati sirove rezultate ali označiti `posthoc_validated=False` (ne optimizovati GA na nevalidnom benchmarku).
6. Statički testovi za oba polinomna gencost izvora, sintetički MVA oba kraja i KCL sa reaktivnom greškom, neuspeh kada ima individualnog P ili Q prekoračenja i neuspeh na pogrešnom broju elemenata. Sačuvati CSV/JSON i CI, srpski izveštaj, bez p-vrednosti, bez tvrdnji o globalnom optimumu i dokaza GAdapt superiornosti.

## Razlog

Ako su ove manje, originalno dobro definisane instances direktno provereno izvodljive, one pružaju metodološki korektan *kontrolni skup* za naredno poređenje stvarnog GAdapt-a sa domenskim solverom i poznatim algoritmima. Ako nisu, negativni rezultat treba pošteno objaviti; veliki RTE1888 se ne sme prošvercovati kao izvodljiv samo zato što se na njemu neki PF solver zaustavio.
