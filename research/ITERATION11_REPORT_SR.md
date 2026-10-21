# Iteracija 11 — direktni originalni MATPOWER v2 AC proračun: konvergencija, ali P/Q i naponska kršenja

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main; originalni bpzoran/gadapt nije menjan. **Status:** završen unapred fiksiran protokol, pravi AC proračun na **originalnim numeričkim MATPOWER podacima**, originalna slack sabirnica BUS1320, dva izbrojana pokušaja. Nije korišćena pandapower električna konverzija niti GAdapt optimizator.

[Unapred registrovani protokol](ITERATION11_PROTOCOL.md) je sačuvan u commit-u `202630c2f69102b10c93f72d26a817219a5aa8ec` **pre novih AC proračuna**. [Uspešan GitHub Actions CI #39629480835](https://github.com/owlCoder/gadapt/actions/runs/39629480835) sadrži završene unit testove, originalni solver log i arhivirana dva pokušaja. Uspeh CI znači da je eksperimentski postupak uredno evidentirao i neuspehe, **ne** da su oba numerička rešavanja konvergirala.

## Originalni podaci, nezavisnost od pandapower i budžet

Originalni izvor [MATPOWER case1888rte.m — 2019](https://github.com/MATPOWER/matpower/blob/80b6e16f760f58721ad31221c7287c28259cd4ad/data/case1888rte.m), fiksni commit `80b6e16f760f58721ad31221c7287c28259cd4ad` (blob SHA `820bd317167381baf819d67eab7d886013e8b05a`), CC BY 4.0, Josz et al. (2016), sadrži 1888 sabirnica, 298 generatorskih redova (291 aktivan) i 2531 granu (2076 sa pozitivnim RATE_A, 455 sa RATE_A=0). Originalna jedina referentna BUS_TYPE=3 sabirnica je **1320**, a poslednji izvorni generator #298 na njoj ima izvorni QMIN=-1 i QMAX=1 MVAr. Podaci **nisu za realno operativno upravljanje ili planiranje francuske/EU mreže**.

U ovoj iteraciji sirovi celokupni originalni `mpc.bus` (13 kolona), `mpc.gen` (21), `mpc.branch` (13) prosleđeni su direktno kroz **PYPOWER 5.1.19** `runpf`, bez prevođenja u pandapower elemente. Newton–Raphson, PF_TOL=1e-8, PF_MAX_IT=40, originalni fiksni P i V podaci. Probna dva pristupa od početka poznata: A sa `ENFORCE_Q_LIMS=0`; B sa `ENFORCE_Q_LIMS=1`. Izvršena su **tačno dva originalna native AC PF pokušaja**; oba se broje, čak i kad solver izbaci Python izuzetak. Nije rađen AC-OPF ili optimizacija, nijedna statistička hipoteza nije testirana.

## Prvi originalni native AC: zaista konvergentan, ali neizvodljiv

| Nezavisno provereni kriterijum | Direktni MATPOWER source bez Q enforce |
|---|---:|
| Numerička konvergencija AC NR | **Da** |
| Referentna sabirnica | **1320** (ostala REF) |
| Sabirnice ispod VMIN | **45** |
| Ukupan nedostatak napona ispod VMIN | 0,0540066975 p.u. |
| Sabirnice iznad VMAX | **0** |
| Izvorni generatori ispod PMIN | **10** |
| Ukupan deficit aktivne snage ispod PMIN | **54,95 MW** |
| Izvorni generatori iznad PMAX | **0** |
| Generator QG ispod QMIN | **12** |
| Generator QG iznad QMAX | **4** |
| Ukupni QMIN deficit / QMAX višak | **31,4391 / 6,9424 MVAr** |
| Originalne pozitivne RATE_A MVA preopterećene grane | **0 od 2076** |
| Najveće izvorno rated opterećenje | 83,6521% |
| Izvorni slack generator #298 PG / QG | **0,32314 MW / -2,08691 MVAr** |
| Izvorni slack QMIN / QMAX | **-1 / +1 MVAr** |
| Rezultat potpuno izvodljiv uz proverene fizičke granice? | **Ne** |
| Izmereni gubici (nisu izvodljiv optimum) | 980,73314 MW |

Generator na originalnoj slack sabirnici 1320 zato **krši svoj QMIN za približno 1,086913 MVAr**. Q granice nisu nametnute u ovom solver režimu, ali su nezavisno *izmerene* kao deo izvorne fizičke dijagnostike. Poput svih ostalih pomenutih generatora, broji se svaka originalna online jedinica, ne samo konvertovani `net.gen`.

**Važno:** mali zbir naponskih prekoračenja u originalnom native slučaju (0,0540 p.u.) ne predstavlja poboljšanje GAdapt-a naspram pandapower rezultata iz iteracije 10 (1,0918 p.u.). To su **različiti električni modeli, u različitim solver režimima**, sa različitim reference/slack i razdvajanjem generatora. Prvo treba proveriti elekričnu i modelnu ekvivalenciju, pa tek onda porediti algoritme.

## Drugi pokušaj: softverska greška, bez fizičkih rezultata

Originalna mreža pokrenuta je sa `ENFORCE_Q_LIMS=1`. PYPOWER je bacio `IndexError: arrays used as indices must be of integer (or boolean) type`. Po zamrznutom protokolu, **nije** proglašen numerički konvergiranim, nisu tumačene parcijalne/nekonzistentne snage ni naponi, a svi metrički ishodi su sačuvani kao JSON `null`. **Ova greška nije dokaz matematičke neizvodljivosti originalnog MATPOWER AC-OPF problema**. Za ponavljanje treba izvorno verifikovan solver ili zasebna, jasno označena tehnička korekcija PYPOWER implementacije.

## Reprodukcija i sirovi dokazi

- [CSV sa oba pokušaja](results/rte1888_iteration11_original_native_ac_20261021.csv)
- [JSON sa originalnom slack P/Q, naponskim i MVA prekršajima i stvarnom greškom PYPOWER](results/rte1888_iteration11_original_native_ac_20261021.json)
- [Originalna matrica svih 298 gen x 21 kolona](results/rte1888_iteration11_original_matpower_gen_full21_2019.csv)
- [Originalna matrica svih 2531 grana x 13 kolona](results/rte1888_iteration11_original_matpower_branch_full13_2019.csv)
- [Originalne 1888 sabirnice x 13 kolona](results/rte1888_iteration9_original_matpower_bus_rows_2019.csv)
- [Reproduktivni direktni PYPOWER source evaluator](iteration11_original_matpower_native_pf.py)
- [Strukturni testovi](test_iteration11_native_pf.py)
- [GitHub Actions — originalna evidencija oba poziva](https://github.com/owlCoder/gadapt/actions/runs/39629480835)

```bash
python -m pip install -e . 'pandapower==2.14.11' 'pypower==5.1.19' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration11_native_pf research.test_iteration9_source_generators
python -m research.iteration11_original_matpower_native_pf --json /tmp/i11.json --csv /tmp/i11.csv
```

CI izveštava Python 3.12.15, SciPy 1.13.1, pandas 2.2.3, izvorni runtime PYPOWER 5.1.19 preko pip-a (Python biblioteka interno ne izlaže `__version__`). Jednonitni BLAS i deterministički source redosled.

## ImplIkacija za mentorski doktorat

Sada postoji dokazni native original izvorni RTE1888 PF, koji **nije zavisan od pandapower konverzije** i koji otkriva konkretne nedozvoljene P/Q i naponske vrednosti, umesto nagađanja. Sledeće: izolovati PYPOWER Q-enforce indeksnu grešku bez menjanja naučnih pretpostavki; nezavisno proveriti validnost native source OPF ograničenja, zatim odvojeno zamrznuti i testirati novi, potencijalno originalni mehanizam GAdapt adaptacije pod zajedničkim budžetima. Ova iteracija **ne dokazuje novost, izvodljiv optimum, upotrebljivost u stvarnoj industriji niti superiornost GAdapt-a**.
