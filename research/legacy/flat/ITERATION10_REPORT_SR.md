# Iteracija 10 — dva stvarna AC proračuna pokazuju da slack ograničenja nisu opciona

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** uspešno završena preregistrovana kontrola, tačno **dva stvarna AC Newton–Raphson proračuna**. Nije pokrenut optimizator niti izmenjen originalni GAdapt paket.

Unapred registrovani eksperiment: [ITERATION10_PROTOCOL.md](ITERATION10_PROTOCOL.md), originalni MATPOWER generatori iz [iteracije 9](ITERATION9_REPORT_SR.md), testirana aktivna mreža pandapower. [Uspešan CI #39625839475](https://github.com/owlCoder/gadapt/actions/runs/39625839475). Model ostaje javni istraživački model koji nije za stvarni dispečing francuske/EU mreže.

## Rezultati — prava fizička AC evaluacija

| Pokazatelj | Originalna pandapower konverzija | Eksperimentalna promena slack sabirnice |
|---|---:|---:|
| Izvorni identitet BUS slack-a | 1268 | **1320** |
| Konvergentan NR solver? | Da | Da |
| Zbir naponskih povreda (p.u.) | 1,0917864473 | 1,1023620367 |
| Prekoračenja pozitivnih izv. RATE_A MVA | 0 | 0 |
| Ostvareni slack P (MW) | 55,005838 | 0,855064 |
| Ostvareni slack Q (MVAr) | 13,303711 | **1.384,477357** |
| Ext-grid-only P deficit prema njegovoj pandapower min granici (MW) | **32,994162** | 0 |
| Izmereni Q višak iznad sopstvenog prijavljenog Qmax (MVAr) | 0 | **1.383,477357** |
| Suma gubitaka (MW; nije izvodljiv optimum) | 990,915838 | 981,265064 |
| Broj fizičkih AC poziva | 1 | 1 |

**Kritično:** oba Newton–Raphson postupka konvergiraju, ali nijedna varijanta nije izvodljiv potpuni AC-OPF. Prva ima pandapower ext_grid-only P=55,005838 MW, što je 32,994162 MW manje od *njegovog* prijavljenog minimuma 88 MW; **ali to nije izvorni agregatni Pmin dva generatora na BUS1268**. Naknadna (jasno označena post-hoc) provera izvornog zbirnog bus P nalazi **99,505838 MW prema originalnom dozvoljenom intervalu [88, 90] MW**, dakle originalni agregatni **Pmax prekoračen je za 9,505838 MW**, uz naponska kršenja. Alternativna varijanta na originalnom izvoru BUS1320 mora da obezbedi **1.384,477 MVAr**, dok jedini originalni generator na tom bus-u (2019, red #298) ima izvorno zadat QMAX=**1 MVAr**; kršenje iznosi 1.383,477 MVAr. Ove dve formulacije imaju različit ext/grid uređaj i ne smeju se neposredno porediti kao dva validna, izvodljiva optimuma.

## Kako je scenario konstruisan

Pre bilo kakvog električnog rešavanja provereno je da MATPOWER 2019 ima jedan BUS_TYPE=3: originalni BUS1320 i generator #298 (PG=0, Pmin=0, Pmax=1000, Qmin=-1, Qmax=1, VG=1,0588). Originalni BUS1268 je BUS_TYPE=2 sa dva jednaka aktivna generatora po PG=44,5 MW.

U drugom scenariju, na **kopiji** konvertovane mreže, ext_grid je premesten na BUS1320 sa izvornim parametrom VG i P/Q limitima; na prethodnom BUS1268 dodat je jedan pandapower.gen sa izvornim PG/Q/P granicama, dok je već postojeći sgen od 44,5 MW ostavljen. Nijedna ostala grana, opterećenje, šant, tap ili prvi osam generatorskih kontrola nije promenjena. Po tom dizajnu eksperiment ne dokazuje potpunu ekvivalentnost izvorne MATPOWER v2 mreže, jer ostaju otvoreni drugi izvorni konverzioni detalji.

Realno korišćen evaluator SourceRatedRTEGrid meri **izvorne pozitivne termičke RATE_A MVA** (oba kraja grane) i naponske limite. Prethodni njegov indikator source-rated feasible **ne proverava dodatne slack P/Q granice**. Sada su P/Q slack izlazi prikazani kao zasebna i obavezna stavka fizičkog audita. Napredak u samom ograničenom indikatoru ne znači izvodljivo industrijsko rešenje.

## Dokazi

- [Sirovi CSV — oba stvarna AC poziva](results/rte1888_iteration10_source_slack_ac_20261021.csv)
- [Sirovi JSON — oba poziva, originalni identiteti, nova generator jedinica i dodatni limiti](results/rte1888_iteration10_source_slack_ac_20261021.json)
- [Kod](iteration10_slack_scenario.py) i [unit testovi](test_iteration10_slack_scenario.py)
- [Uspesan GitHub Actions CI i originalni logovi](https://github.com/owlCoder/gadapt/actions/runs/39625839475)
- [Pre-registracija](ITERATION10_PROTOCOL.md)

Ponoviti:

    python -m pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
    python -m unittest -v research.test_iteration10_slack_scenario research.test_iteration9_source_generators research.test_iteration7_source_physics
    python -m research.iteration10_slack_scenario --csv /tmp/i10.csv --json /tmp/i10.json

CI je uspešan i čuva rezultate čak i kod potencijalnog neuspeha solvera. Instalirana pip verzija pandapower je 2.14.11, interni reported __version__ je 2.14.10; eksplicitno prikazano.

## Nepristrasan naučni zaključak za mentora

Za disertaciju o **stvarnom GAdapt-u prilagođenom industrijski relevantnim problemima** potrebno je, pre bilo kakve tvrdnje o superiornosti, uvesti puna fizička P/Q ograničenja i proveriti originalnost/konverziju OPF modela. Numerički konvergentna AC simulacija nije dokaz fizičke izvodljivosti; obostrani pomak reference rešio je neke naponske povrede ali izazvao ogromno prekoračenje Q na originalnom slack generatoru. U originalnom konvertovanom slučaju eksterni uređaj samostalno odstupa od sopstvenog Pmin, ali za poređenje sa **izvornim MATPOWER agregatom dva generatora** relevantan je zbir sa preostalim sgen: taj zbir premašuje originalni Pmax za 9,505838 MW.

Samo na osnovu dva slučaja ne postoji dokaz da originalni MATPOWER AC-OPF nema rešenje — preraspodela aktivne/reaktivne snage, svi kontrolni resursi, sve konverzije i nezavisan OPF solver nisu istraženi. Nije pronađen originalan poboljšan GAdapt, ostvareni izvodljivi optimum, globalno optimalan režim, niti dokaz industrijske pouzdanosti.

## Dopuna — post-hoc ispravka interpretacije agregatnih P granica (bez novih AC poziva)

Nakon uvida u dva stvarna izlaza posebno je provereno da originalna MATPOWER sabirnica **1268** ima **dva** aktivna generatora, svaki PMIN=44 MW, PMAX=45 MW i početni PG=44,5 MW. Zato se **konvertovani ext_grid P ne sme sam porediti sa originalnom zbirnom Pmin=88 MW** bez preostalog generatora/sgen.

- Originalni konvertovani AC slučaj: ext_grid P=55,005838 + već postojeći sgen P=44,5 daje **99,505838 MW**; prema izvornom zbirnom opsegu **[88, 90] MW** to je **9,505838 MW iznad Pmax**. Prethodno navedeni deficit ext-grid-only prema njegovoj zasebnoj pandapower granici je tačan kao odit konverzije, ali nije pravilan izvorni agregatni test.
- Alternativni slučaj sa originalnom slack lokacijom: novi gen P=44,5 + zadržani sgen P=44,5 daje **89,0 MW**, unutar izvornog opsega BUS1268; istovremeno **slack BUS1320 Q=1.384,477 MVAr** i dalje krši izvorni QMAX=1 MVAr za 1.383,477 MVAr.

Ova dopuna je **post-hoc interpretativna korekcija, a ne preregistrovan treći eksperiment**. Zasnovana je isključivo na dva već arhivirana AC merenja, izvornom generator CSV-u i preflight-u aktivnog sgen od 44,5 MW: **0 dodatnih AC poziva**.

[Izvorni agregatni P JSON](results/rte1888_iteration10_posthoc_source_bus1268_p_20261021.json) · [Reproduktivni analizator](iteration10_posthoc_source_p.py) · [unit testovi](test_iteration10_posthoc_source_p.py) · [uspešan CI #39626732201](https://github.com/owlCoder/gadapt/actions/runs/39626732201).

I ovaj agregat je samo deo fizičkog modela; nisu proverene sve moguće naponske, Q, PV/PQ, konverzione i originalne jednačine. **Ni jedno stanje nije validirani puni izvodljivi AC-OPF.**
