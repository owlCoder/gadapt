# Iteracija 13 — nativni originalni MATPOWER AC sa Q enforcement konačno konvergira, ali nije izvodljiv OPF

**Datum:** 21.10.2026. **Fork:** owlCoder/gadapt:main, bez izmena upstream bpzoran/gadapt. **Status:** uspešan CI, svi testovi prošli, **tačno jedan stvarni originalni native AC proračun**; matematički neizvodljivo stanje prema proveravanim izvorno zadatim P/V ograničenjima. **Nije AC-OPF** i nije optimizacija GAdapt-om.

## Kontekst i predregistracija

U iteraciji 11 direktno originalni 2019 MATPOWER `case1888rte.m` (MATPOWER commit `80b6e16f760f58721ad31221c7287c28259cd4ad`) konvergirao je samo kada nisu nametnute Q granice, uz 45 povreda donjeg napona, 10 povreda generator PMIN i 16 Q povreda. Aktivni PG/PMIN konflikt u svih deset generatora **postoji već u originalnom ulaznom dispečingu**. Q enforcement preko neizmenjenog PYPOWER 5.1.19 koda i dalje je bacao `IndexError`.

Iteracija 12 testirala je prvu transparentnu BSD-pripisanu PYPOWER Q-limit ispravku: originalni kontrolni no-Q AC se poklopio u fizičkim pokazateljima u toleranciji 1e-5 sa iteracijom 11, ali Q-enforcement je opet bacio `IndexError`. Te negativne pokušaje **nismo brisali**.

[ITERATION13_PROTOCOL.md](ITERATION13_PROTOCOL.md) unapred je zamrznuo **još samo jednu pravu AC evaluaciju**; commit [35b294149b4dcd6e0965fe788fb2dac5c2bf9253](https://github.com/owlCoder/gadapt/commit/35b294149b4dcd6e0965fe788fb2dac5c2bf9253). U novu lokalnu kopiju PYPOWER `runpf` izvorne BSD implementacije (rwl/PYPOWER commit `c7f1cf50bedd34012b92fae4f092ec55617546a8`) dodata su samo još dva popravka: pretvaranje BUS ID-ja u integer pri vraćanju Q-limit injekcije i upis odgovarajuće konstante `PV` umesto niza PV indeksâ u `BUS_TYPE`. Originalna numerička matrica 1888 BUS x 13, 298 GEN x 21 i 2531 BRANCH x 13 ostala je neizmenjena. Nije menjana nijedna GAdapt strategija.

## Provereni stvarni AC rezultati

[Uspešno izvršenje CI #39631108812](https://github.com/owlCoder/gadapt/actions/runs/39631108812) pokazuje numeričku konvergenciju sa `ENFORCE_Q_LIMS=1`, Newton-Raphson, maksimalno 40 iteracija, tolerancija 1e-8, uključene izvorne Q granice za svih 291 aktivnih generatora.

| Pokazatelj | Native PF bez Q enforcement (iteracija 11) | Native PF sa ispravljenim Q enforcement (iteracija 13) |
|---|---:|---:|
| Numerička AC konvergencija | Da | **Da** |
| Finalna referentna/slack sabirnica | 1320 | **89** |
| Originalna BUS1320 postaje tip | REF (3) | **PQ (1)** |
| Sabirnice ispod VMIN | 45 | **41** |
| Zbir manjka napona (p.u.) | 0,0540066975 | **0,0523731909** |
| Aktivni generatori ispod PMIN | 10 | **10** |
| Zbir manjka aktivne snage (MW) | 54,95 | **54,95** |
| Aktivni generatori van QMIN/QMAX | 16 | **0** (tolerancija 1e-7) |
| Pozitivno rated originalne RATE_A MVA grane preopterećene | 0 / 2076 | **0 / 2076** |
| Originalni generator #298 (BUS1320) QG | -2,086913 MVAr | **-1,0 MVAr**, tačno na QMIN |
| Ocenjeni gubici u granama (MW; nisu izvodljiv optimum) | 980,73314 | **980,55866** |
| Sva proveravana fizička ograničenja zadovoljena? | Ne | **Ne** |

**Važna promena interpretacije:** originalni MATPOWER 2019 početni REF je BUS1320, ali nakon Q-limit enforcementa on menja tip u PQ, a solver bira BUS89 za novu referencu. To je rezultat solver algoritma koji reaguje na zasićenje Q originalnog slack generatora, **ne povratak potpuno istom fiksiranom izvornom referentnom problemu**. Originalni slack generator #298 sada je na QMIN=-1 MVAr, njegova pozicija ne postaje pravilo validnog dispečinga.

Iako su Q prekoračenja uklonjena do male numeričke tolerancije i dobili smo konvergentan originalni nativni proračun, **41 preniska naponska sabirnica i 10 generatora sa ukupno 54,95 MW ispod P minimuma ostaju**. Ovo nije AC-OPF izvodljivo rešenje, a kamoli optimum. Q-limit enforcement nije ni predviđen da automatski optimizuje P dispečing.

## Šta je za disertaciju dokazano, a šta nije

**Dokazano u kodu i CI:** originalni MATPOWER nativni model i njegov tip REF/PV/PQ, lokalni PYPOWER softverski problem i transparentno dokumentovana korekcija, konvergencija jednog Q-limit PF, zaostala jasna fizička P/V kršenja, izvorna pozitivna MVA ograničenja bez prekoračenja na ovom proveravanom stanju.

**Nije dokazano:** puno izvodljiv AC-OPF na originalnom RTE1888, optimalan P redispečing, kapacitet/prenosivost GAdapt-a, originalnost adaptivne metode, prednost nad domenskim solverom, rad u realnoj industriji. Podaci su javni MATPOWER testni slučaj i izričito **nisu** za operativno upravljanje ili planiranje stvarne francuske/EU mreže.

## Trajni dokazi

- [Raw CSV — jedan direktni AC poziv](results/rte1888_iteration13_original_q_limited_20261021.csv)
- [Raw JSON — konvergencija, svih 1888 bus V statusa agregatno, 291 izvorni generator i originalni RATE_A](results/rte1888_iteration13_original_q_limited_20261021.json)
- [Pre-registracija](ITERATION13_PROTOCOL.md)
- [Program za jedan native AC poziv](iteration13_native_q_diagnostic.py)
- [Lokalna BSD PYPOWER kopija sa pet eksplicitno praćenih tehničkih korekcija](iteration13_local_pypower_qlim_patch.py)
- [Testovi minimalnog diff-a u odnosu na iteraciju 12](test_iteration13_native_q_diagnostic.py)
- [GitHub Actions CI #39631108812](https://github.com/owlCoder/gadapt/actions/runs/39631108812)

Reprodukcija:

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration13_native_q_diagnostic research.test_iteration12_native_q_repair
python -m research.iteration13_native_q_diagnostic --csv /tmp/i13.csv --json /tmp/i13.json
```

**Sledeći naučni zadatak:** odvojeno zamrznut pravi **izvorni AC-OPF** sa slobodnim P dispečingom, originalnim P/Q/V/MVA granicama i ozbiljnim nezavisnim domenskim solverom. Uspostaviti fizički izvodljivu baznu tačku (ako postoji i solver je pronađe) *pre* testiranja ograničenjima svesne adaptacije stvarnog GAdapt-a. Izvorna formulacija i oba neuspešna Q patch pokušaja ostaju u historiji radi transparentnosti.
