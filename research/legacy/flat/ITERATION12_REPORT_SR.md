# Iteracija 12 — kontrolisani pokušaj PYPOWER Q-limit ispravke nije rešio sve softverske greške

**Datum:** 21.10.2026. **Status:** dva stvarna native original-MATPOWER AC poziva u uspešnom CI postupku; kontrolna grana fizički identična originalnom referentnom pozivu, Q-limit grana ponovo završila sa `IndexError`. **Nema dodatnog validnog Q-enforced fizičkog stanja.** Ovo je potpuno reproduciran *negativni softverski rezultat*.

Pre-registracija [ITERATION12_PROTOCOL.md](ITERATION12_PROTOCOL.md), fiksirana u commit-u `b4f74bcd27479760f7b9e612f4fbe5096152a291` pre AC. [Uspešan CI #39630468071](https://github.com/owlCoder/gadapt/actions/runs/39630468071), kompletan raw [JSON](results/rte1888_iteration12_native_q_repair_20261021.json) i [CSV](results/rte1888_iteration12_native_q_repair_20261021.csv).

PYPOWER 5.1.19 je korišćen sa jasno pripisanom lokalnom BSD kopijom iz `rwl/PYPOWER` commita `c7f1cf50bedd34012b92fae4f092ec55617546a8`; popravljena su tri unapred definisana dela grananja Q-enforcement: konverzija float sabirničkog indeksa u integer u PV/REF proveri, ispravno grupisanje uslova i upoređivanje samo jednakih dužina, plus drugi float indeks u proveri više REF sabirnica. Ni jedna numerička metoda, izvorni ulaz ili agregatni limiti nisu menjani. Kontrola bez Q-enforcementa pokazala je:
- izvorna slack sabirnica 1320;
- 45 povreda donjeg napona, zbir 0,05400669747 p.u.;
- 10 originalnih aktivnih PG ispod PMIN, zbir 54,95 MW; ove povrede su **već u izvornom ulaznom dispečingu**, pre AC solvera;
- 12 QMIN i četiri QMAX prekoračenja, ukupno 31,4391 + 6,9424 MVAr;
- 0 prekoračenja originalnih pozitivnih RATE_A MVA granica;
- identitet kontrolne iteracije 11 provereno poklapanjem svih suma, brojeva i izvornog slack PG/QG u apsolutnoj toleranciji 1e-5.

Drugi stvarni AC pokušaj sa Q enforcement ponovo je prijavio `IndexError: only integers, slices (...) and integer or boolean arrays are valid indices`. Sačuvani su null fizički rezultati, bez nagađanja o voltima/MW/MVAr ili nezavisnoj izvodljivosti.

Naknadnim pregledom lokalnog PYPOWER koda uočena su moguća **dodatna** mesta: vraćanje gen injekcije koristi `bi = gen[limited[i], GEN_BUS]` kao float indeks; preusmeravanje slack-a koristi `bus[pv, BUS_TYPE] = pv` gde treba konstanta `PV` a ne niz bus indeksa. **Ove dve promene nisu bile deo fiksiranog eksperimenta iteracije 12**. Moraju dobiti zaseban protokol i novu proveru, a ne retroaktivnu promenu istih rezultata.

**Status za disertaciju:** direktna originalna AC referenca bez nametanja Q uspešno proverena; puna izvodljivost nije ostvarena niti je pokušaj softverske ispravke Q enforcementa uspeo. Ništa ovde ne potvrđuje originalni mehanizam GAdapt-a, statističku prednost, potpuno OPF rešenje ili industrijsku spremnost.
