# Iteracija 32 — transfer ranog fizičkog screeninga na nezavisnu IEEE14 topologiju

**Završeno 22. oktobra 2026, Srbija.** Protokol [I32](ITERATION32_PROTOCOL.md) komitovan **pre I32 fizičkih AC poziva**. Test obuhvata 6 varijanti × 12 potpuno novih uparenih semena **2104–2115**, najveći budžet 180 pravih originalnih AC NR solver poziva po pokretanju. Ukupno **72 pokretanja i 12.913 STVARNO izvršenih originalnih IEEE14 `pypower.runpf` poziva**, od zamrznutog maksimuma 12.960. **0 numeričkih neuspeha**. GitHub Actions originalni CI experiment **uspešan**, uključujući preflight, svih 72 run-ova i sačuvane ZIP artefakte.

## Zašto ova validacija jeste nezavisnija nego I29–I31, a šta nije

- I29–I31 su koristile **IEEE118**. I32 koristi **potpuno drugu fizičku topologiju IEEE14, originalni `pypower.case14()`** sa 14 BUS, 5 aktivnih GEN, 20 originalnih BRANCH i izvornim `gencost`. Time se smanjuje problem zaključka isključivo na istoj mreži.
- I32 nije *slepi, prvi put viđeni benchmark*, jer je IEEE14 iz ranijih iteracija I16/I17/I5 već bio korišćen kao izvorni model. I32 je **nova robusna tri-scenarijska formulacija**: originalni `nominal`, sintetički `odd_bus_plus1pct` (neparni BUS_I PD/QD ×1,01; parni ×0,99) i `even_bus_plus1pct` (obrnuto). Originalni izvorni branch/gen/bus parametri osim PD/QD i 9 kontrolisanih decision PG/VG ostaju isti.
- Ovo je **izvorni, 9-dimenzionalni PV-kontrolisani podskup**, ne potpuni slobodni ekonomski IEEE14 AC-OPF i ne stvarna industrijska mreža. P za 4 non-slack gen i V za 5 originalnih gen, isti originalni I17 dimenzioni box za sve metode. Za svako stvarno izmereno AC stanje nezavisno se proveravaju individualni originalni gen P/Q, BUS VMIN/VMAX, **pozitivni originalni RATE_A MVA na oba kraja** i kompleksni KCL; slack PG takođe može da krši originalnu granicu. Q se ne forsira u NR (`ENFORCE_Q_LIMS=0`), ali se individualno testira i povreda diskvalifikuje kandidata. Pozitivni verdict zahteva sva **3** realno izmerena i AC-konvergentna scenarija.
- **Nema dodatih pravih AC poziva u momentu arhiviranja**; 72 originalna JSON zapisa rekonstruisana su iz sirovih objavljenih `I32_REAL_SOURCE_AC` redova CI stdout-a i validirana u odnosu na isti originalni `I32_SUMMARY/I32_PAIRED/I32_METADATA`. Osim ovde obrađene PR fizičke serije, status drugih automatski pokrenutih job-ova može se proveriti u Actions istoriji i ne sme da se broji kao dodatna nezavisna seed potvrda bez posebnog protokola.

## Glavni rezultati: isti budžet stvarnih AC, šest metoda

| Optimizator i scenario evaluacija | Semena sa ≥1 zaista provereno robust-feasible kandidatom (od 12) | Broj kandidata provereno feasible na sva 3 AC* | Broj kompletnih kandidata | Stvarni originalni AC | Najniži u okviru metode **potpuno provereni mean source gencost** |
|---|---:|---:|---:|---:|---:|
| GAdapt **full_true** (puni AC, originalni score) | **8/12** | 47 | 720 | 2.160 | 8.818,596974 |
| GAdapt **full_censored** (puni AC, prvi-fail score) | **9/12** | 82 | 720 | 2.160 | 8.242,029219 |
| GAdapt **stop_fixed** | **12/12** | **404** | 404 | 2.149 | **8.240,999496** |
| GAdapt **stop_adaptive** | **12/12** | 403 | 403 | 2.146 | **8.240,999496** |
| SciPy DE **full_true** | **3/12** | 3 | 720 | 2.160 | 8.532,164931 |
| SciPy DE **stop_fixed** | **7/12** | 13 | 13 | 2.138 | 8.296,342025 |

*Unutar iste evolutivne trajektorije ponovljeni ili srodni kandidati nisu nezavisni statistički uzorci. **Glavna jedinica zaključivanja je seme (12) a ne 404 fizička kandidata.** Broj svih objective requests uključuje i neplaćene post-budžetske sentinel zahteve; jedino `actual_native_AC_calls` i `actual_AC_per_scenario` predstavljaju realan fizički trošak. Pritom originalni robust mean source `gencost` postoji isključivo za potvrđeno izvodljive celovite trojke. Nije legitimno cenu cenzurisanog scoring-a porediti kao originalni ekonomski trošak.

**Fizički tačno prekinuti kandidati:** GAdapt `stop_fixed` i `stop_adaptive` po **911** konvergentno izmerenih ranih fizičkih neuspeha; njihovih po **1.796** nedostajućih scenarija **NISU izvršeni niti su predstavljeni kao izvodljivi**. DE `stop_fixed`: **2.099** fizički izmerenih ranih neuspeha i **4.198** neizvršenih scenarija. Zbir stvarno započetih kandidata za GA stop_fixed 404+911=**1.315** naspram 720 kod `full_censored`, uz skoro isti broj stvarnih AC (2.149 prema 2.160). Zato broj GA fizički probanih kandidata znatno raste, ali su mnogi ocenjeni samo po 1–2 scenarija i nisu robust-feasible.

## Zamrznuti upareni kontrasti 12 novih semena

| Kontrast uspešnog semena | Obe uspešne | Uspešna samo prva | Uspešna samo druga | Nijedna | **Egzaktna dvostrana p, NEkorigovana** |
|---|---:|---:|---:|---:|---:|
| GA `full_true` : GA `full_censored` | 7 | 1 | 2 | 2 | **1,000000** |
| GA `full_censored` : GA `stop_fixed` | 9 | 0 | 3 | 0 | **0,250000** |
| GA `stop_fixed` : GA `stop_adaptive` | 12 | 0 | 0 | 0 | **1,000000** |
| GA `stop_fixed` : DE `stop_fixed` | 7 | 5 | 0 | 0 | **0,062500** |
| GA `full_true` : DE `full_true` | 1 | 7 | 2 | 2 | **0,179688** |

Ovo su dvostrani egzaktni binomni testovi za uparene diskordantne seedove, **bez korekcije pet planiranih poređenja**. Najmanji p=0,0625, pa **nijedan kontrast nije statistički značajan na nivou 0,05 čak ni pre korekcije**. Ovo ne dokazuje statističku jednakost metoda. Kod GA `stop_fixed` prema GA `stop_adaptive` oba uspevaju u svih 12 semena, zato seed success uopšte ne razlikuje metode.

## Tumačenje bez preterivanja

1. **Transfer mogućeg benefit-a screeninga, ali ne i dokaz generalne superiornosti.** Za IEEE14 kontrolu sa **istom cenzurisanom ocenom** i svim stvarno plaćenim scenarijima, GA `full_censored` je uspeo 9/12, dok GA `stop_fixed` sa ranim izbacivanjem fizički dokazanih neizvodljivih kandidata uspeva **12/12** uz 11 manje AC; test ima samo 3 diskordantna semena (p=0,25). Raniji I31 IEEE118 kontrolni kontrast bio je 7/12 prema 11/12 uz p=0,125. **Smer nalaza se ponavlja na drugoj topologiji**, ali rezultati ne dokazuju statističku generalizaciju i ne identifikuju jedinstven kauzalni efekat zbog različitih evolutivnih putanja.
2. **Selekcioni skor menja zaključak i ne prenosi se isto kao na IEEE118.** IEEE14 `full_true` 8/12 prema `full_censored` 9/12. U I31 IEEE118 je bilo 9/12 prema 7/12. Dakle ne postoji konzistentan znak efekta samo promene fitness-a.
3. **Adaptivni redosled opet nije pokazao korist.** `stop_fixed` i `stop_adaptive` imaju 12/12, 404 vs 403 potvrđeno izvodljiva kandidata i identičnu najbolju zaista proverenu mean cenu **8.240,999496**. Jedno ili dva dodatna obrađena scenarija nisu dokaz nove adaptive politike.
4. **Snažniji optimizator DE je fer fizička kontrola, ali ni on nema statistički definisan poraz.** DE `full_true` 3/12, DE `stop_fixed` 7/12, uz isti stvarni AC plafon. Različit raspored kandidata i optimizerska početna populacija su deo metoda. GA `stop_fixed` 12/12 vs DE `stop_fixed` 7/12 daje p=0,0625, nedovoljno za 0,05 i pogotovo nakon multiplicitet korekcije.
5. **Ne porediti ove `gencost` sa I16 nominalnim puni IEEE14 `runopf` minimumom od oko 8.081,526** kao ekvivalentne optimizacije: ovde su tri odvojena opterećenja, drugački 9D PV-kontrolisan prostor i robust potvrda.

## Evidencija i reproduktivnost

- **[Preregistracija PRE svakog novog I32 AC](ITERATION32_PROTOCOL.md)** · [I32 izvorni kod](iteration32_ieee14_topology_transfer.py) · [I32 zero-AC fizička/pseudofizička proveravanja](test_iteration32_ieee14_topology_transfer.py).
- **[Stvarni CI run: 39686171613, svi poslovi SUCCESS](https://github.com/owlCoder/gadapt/actions/runs/39686171613)** · [originalni Actions artefakt sa JSON + CSV](https://github.com/owlCoder/gadapt/actions/runs/39686171613/artifacts/12386702402), ZIP SHA256 `c2a84c57571841737c7a9f006091a4a97097fe6843d42265ef3ccbd84937f782`. Originalni job pravih AC: `119520891494`.
- **[Kompletni 72 raw source zapisa u repozitorijumu](results/ieee14_iteration32_12seed_6arms_12913_real_AC_20261022.json)** · [72 CSV redova](results/ieee14_iteration32_12seed_6arms_12913_real_AC_20261022.csv); arhivska razrada nastala iz **72 stvarna zapisa**, nikakav novi solver poziv, metapodaci, sekundarne summary metrike i svi unapred definisani upareni kontrasti provereni.
- **Pokriće testova:** osnovne 9D originalne source granice, jedino PD/QD perturbovani, originalni branch i `gencost` očuvani; 3-scenario kompletna rezervacija, prva izmerena source povreda, stvarni counters, numeric unknown ne predstavlja matematičku fizičku neizvodljivost. Specijalno **sintetički unit testovi nisu računati u 12.913 AC**.
- Softver CI Python 3.11.17, NumPy 1.26.4, SciPy 1.13.1, pandas 2.2.3, PYPOWER 5.1.19. Core `gadapt.ga.GA`, I29 originalni evaluator i upstream projekat nisu menjani.

**Zaključak za disertaciju:** Ostvaren je metodološki jači *cross-topology* potvrdni signal za poznatu tehniku *first-failure / sequential scenario screening*, uz fizički pošteno računanje i DE baznu kontrolu. **Nije dokazana originalna naučna novina, statistički značajna superiornost, pravi puni AC-OPF optimum, bezbednost mreže ili generalizacija na telekomunikacionu industriju.** Sledeći korak: odvojena unapred registrovana provera iste ideje na GÉANT plansko-kapacitetnom telekom domenu sa **stvarnim evaluacijama mrežnog kapaciteta, ne AC simulacijama**, ili većom nezavisnom strujnom topologijom, uz literaturu o scenario racing i cenovnim adaptivnim operatorima. Rezultati I32 ne smeju da se koriste da bi se retroaktivno menjali I32 parametri.
