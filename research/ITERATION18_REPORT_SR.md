# Iteracija 18 — stvarni GAdapt na IEEE118 pokazuje granicu prenosa uskog devetodimenzionalnog pristupa

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** preregistrovan originalni IEEE118 transfer pilot, uspešni unit testovi i CI, 9 optimizatorskih pokretanja, ukupno **864/864 stvarnih AC PF proračuna**; svi konvergentni, ali **nula fizički izvodljivih kandidata** u deklarisanom ograničenom kontrolnom prostoru. Nije dokaz bilo kakve algoritamske superiornosti ili matematičke neizvodljivosti punog AC-OPF-a.

## 1. Tačno koji problem je testiran

Po [pre-registraciji](ITERATION18_PROTOCOL.md) (commit `54772ca3ad20c38fd9d6bbc758e7e900ab20b22e` pre IEEE118 AC proračuna), originalni `pypower.case118()` model: 118 bus, 54 generatora, 186 grana, originalni P/Q, VMIN/VMAX, RATE_A i izvorni polinomni generatorski ekonomski trošak. Izvorni slack BUS69, generator red #30 (0-based 29). **Samo četiri najveća PG originalna generatora van slack-a** mogu da menjaju PG: originalni gen redovi 0-based **39 BUS89, 36 BUS80, 4 BUS10, 28 BUS66**, sa originalnim početnim PG **607, 477, 450, 392 MW**. Pet njihovih i slack BUS69 VG setpointova je podešavano. **Preostalih 49 aktivnih generatora imaju fiksirani originalni PG i VG.**

Sve originalne individualne PG/QG granice **svih 54**, svaka bus V granica, izvorni RATE_A MVA na oba kraja svake ocenjene grane i složeni kompleksni AC KCL bili su fizikalni *feasible* kriterijumi, a nikada samo penalizovana ekonomska funkcija. `pypower.runpf`, NR sa `ENFORCE_Q_LIMS=0`; generator Q se naknadno proverava i prekoračenje isključuje kandidata. Dakle, ovo je samo fizički izvodljiv **podskup** originalnog 54-generator AC-OPF, ne puni AC-OPF.

Originalni veliki cilj i originalna ekonomija NISU menjani za pogodniji rezultat. Model je javni referentni testni skup, ne realno upravljanje industrijskim sistemom.

## 2. Stvarno izmereni rezultati

[Uspešan GitHub Actions #39646983369](https://github.com/owlCoder/gadapt/actions/runs/39646983369). Tri semena **2026, 2027, 2028**, GAdapt legacy, DE bez poliranja, uniform random, pop16 za GA, budžet **96 pravih runpf poziva po pokretanju**.

| Metod | AC 2026 / feasible | AC 2027 / feasible | AC 2028 / feasible | Ukupno stvarnih AC | Bar jedno feasible u koliko semena? |
|---|---|---|---|---:|---:|
| **Stvarni GAdapt legacy** | 96 / **0** | 96 / **0** | 96 / **0** | **288** | **0/3** |
| SciPy differential evolution | 96 / **0** | 96 / **0** | 96 / **0** | **288** | **0/3** |
| Uniform random | 96 / **0** | 96 / **0** | 96 / **0** | **288** | **0/3** |
| **Ukupno** | 288 / 0 | 288 / 0 | 288 / 0 | **864** | 0/9 |

Svaki od 864 stvarnih originalnih AC NR pokušaja je konvergirao numerički (`solver_failed_calls=0`), ali **ne postoji izvorno fizički izvodljiv kandidat**. JSON beleži `best_feasible_economic_cost=null` i `best_feasible_vector=null` za svih 9 pokretanja, bez lažnih MW i polinomnih ekonomskih “ostvarenja”. Prikazani `best_penalized_ac_score` od 216.781 do 414.325 je samo **izvorni economic cost + unapred definisana fizička kazna** za neizvodljive kandidate — nikako stvarna izvodljiva ekonomija.

Kao i u iteraciji 17, GAdapt ima po 98 objective zahteva (2 sentinel posle 96 real AC), DE po 270 (174 sentinel), a random 96. To nisu dodatni AC pozivi i nikakva statistika o algoritmu ne sme prebrojavati sentinele kao fizičke evaluacije.

## 3. Zašto ovo nije dokaz da IEEE118 nema rešenje

U [iteraciji 16](ITERATION16_REPORT_SR.md) **puni originalni IEEE118 AC-OPF** sa slobodnijim P/Q/V optimizacionim promenljivama dao je solver `success=True`, a rešenje je prošlo sve naknadne PG/QG, VMIN/VMAX, pozitivno izvorne RATE_A MVA oba kraja i složene AC KCL provere. Tadašnja originalna polinomna referentna ekonomska cena iznosi **129.660,686390**. Ona nije postavljena kao početna GA tačka, jer bi to dalo nezasluženu prednost i prikrilo pitanje samostalnog nalaženja izvodljivosti.

Sadašnji devetodimenzionalni prostor drži **49 izvornih PG/VG fiksnim**, što u velikoj mreži može blokirati redispečing i ravnotežu reaktivne snage. Ni odsustvo izvodljivih kandidata, ni veliki kazneni scores ne pokazuju da puni IEEE118 problem nema rešenje. Svi kandidati imaju dobro definisan PF, ali izbor kontrola je preuzak / budžet prenizak za ovaj *pilot*, i još ne postoji dokaz kako deluju odvojene fizičke Q, V, P komponente među najboljim neizvodljivim tačkama. Sledeća pravovremena dijagnostika tih komponenti zahteva posebno brojane nove AC provere.

## 4. Mentorski zaključak o stvarnom GAdapt-u

IEEE14 pilot ([I17 izveštaj](ITERATION17_REPORT_SR.md)) pokazao je da **neizmenjeni stvarni GAdapt** može samostalno pronaći izvorno feasible IEEE14 PF-kandidate u **2/3** pokretanja, naspram 1/3 za DE i random, ali DE ima najbolji pojedinačni feasible ekonomski cost. Sada IEEE118 (I18) pokazuje da uska devetodimenzionalna reprezentacija **ne prenosi automatski izvodljivost na veći sistem**. Ovaj razlaz (14 vs 118) je potencijalno važna istraživačka motivacija za ograničenjima svesnu adaptaciju, *ali još nije dokaz* da nov mehanizam treba da bude bolji, ni da je problem u GAdapt algoritmu: korisni kontrolni resursi mogu biti sasvim drugi.

Za narednu naučno poštenu fazu predlaže se pre svega selektovati izvorno fizički smislen broj generatorskih P/V kontrola, proveriti Q saturation i PG redispečing, ili uvesti domenski OPF **feasibility repair** koji se merljivo plaća fizičkim AC pozivima; zatim odvojeno uporediti originalni i eventualno novi GAdapt pod zajedničkom fizikom i budgetom. Pretrage operatora i AOS, UCB i feasibility credit postoje u literaturi i ne smeju se nazvati našom novinom.

**Nema statističkog dokaza**, samo 3 uparena semena. Originalni upstream nije menjan, nema rada na stvarnoj operativnoj mreži.

## 5. Dokazi i ponavljanje

- [Preregistrovani postupak](ITERATION18_PROTOCOL.md)
- [Originalni IEEE118 GAdapt/DE/random AC evaluator](iteration18_ieee118_gadapt_transfer.py)
- [Testovi source slack BUS69, četiri PG kontrole i fizičkog budžeta](test_iteration18_ieee118_gadapt_transfer.py)
- [Raw CSV svih 9 nezavisnih pokretanja](results/ieee118_iteration18_real_gadapt_de_random_20261021.csv)
- [Raw JSON svih 9 pokretanja](results/ieee118_iteration18_real_gadapt_de_random_20261021.json)
- [GitHub Actions #39646983369](https://github.com/owlCoder/gadapt/actions/runs/39646983369)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration18_ieee118_gadapt_transfer
python -m research.iteration18_ieee118_gadapt_transfer --seeds 2026 2027 2028 --budget 96 --population 16 --json /tmp/i18.json --csv /tmp/i18.csv
```
