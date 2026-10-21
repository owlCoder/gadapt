# Iteracija 19 — forenzički dokaz: IEEE118 9D pilot zaustavljaju pre svega Q granice, ne V ili RATE_A

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** završen unapred registrovani I19 fizički audit sa **tačno 10 novih stvarnih `runpf` AC proračuna** i **0 novih optimizatorskih pokretanja**. Originalni upstream nije menjan. [Uspešan CI #39652408164](https://github.com/owlCoder/gadapt/actions/runs/39652408164) sa testovima i neizmenjenim originalnim PYPOWER IEEE118 modelom.

## 1. Koja stanja smo proverili i zašto su unapred fiksirana

Prvo originalni IEEE118 PG/VG iz izvornog PYPOWER fajla, a zatim tačno 9 najboljih **penalizovanih**, nikad neizvodljivim proglašenih, stvarno evaluiranih vektora iz [raw iteracije 18](results/ieee118_iteration18_real_gadapt_de_random_20261021.json), raspoređenih `semena 2026–2028 × originalni GAdapt, SciPy DE, random`. Tačan izbor i protokol [ITERATION19_PROTOCOL.md](ITERATION19_PROTOCOL.md) iz commit-a `88008e33b58cce586aae9de989cef4901cf2b6a3` sačuvani su **pre** ovih 10 AC.

Sve je računato sa originalnim IEEE118, 118 bus/54 online generators/186 branches, originalni P/Q/V/`RATE_A`, NR `ENFORCE_Q_LIMS=0`. Q nije enforced tokom numeričkog PF, ali je kao **obavezna zasebna granica svakog generatora** proveravan *posle* PF. Zato nijedan Q-offender nije proglašen feasible. PG i VG od ostalih 49 generatora nisu menjani. Referentna slack BUS69.

## 2. Dosledni stvarno izmereni rezultati

| Stanje (10 real AC) | AC konvergira | Izvorni P-offenderi | Izvorni Q-offenderi | Ukupno Q prekor. (MVAr) | V-offenderi | Pozitivni `RATE_A` offenderi |
|---|---|---:|---:|---:|---:|---:|
| Originalni PG/VG, bez optimizacije | Da | 0 | 6 | **78,099195** | 0 | 0 |
| GAdapt 2026, najbolji kažnjeni vektor | Da | 0 | 7 | **88,794410** | 0 | 0 |
| DE 2026 | Da | 1 | 7 | **80,376554** | 0 | 0 |
| Random 2026 | Da | 1 | 8 | **94,002396** | 0 | 0 |
| GAdapt 2027 | Da | 0 | 7 | **85,372117** | 0 | 0 |
| DE 2027 | Da | 0 | 9 | **253,819653** | 0 | 0 |
| Random 2027 | Da | 0 | 11 | **282,083158** | 0 | 0 |
| GAdapt 2028 | Da | 0 | 6 | **144,665676** | 0 | 0 |
| DE 2028 | Da | 0 | 9 | **123,356029** | 0 | 0 |
| Random 2028 | Da | 1 | 7 | **167,829119** | 0 | 0 |

**Svih 10 AC konvergira, svih 10 neizvodljivo po originalnom Q**, svih 10 bez prekoračenja sabirničkih VMIN/VMAX ili originalnih pozitivnih RATE_A MVA na oba kraja aktivnih grana. Tri od devet I18 kontrolisanih best-penalized vektora dodatno imaju pojedinačnu P granicu prekoračenu (uglavnom slack PG blizu izvornog max); izvorni početni PG nema P-offendere. Svih 9 I18 prethodnih penalizovanih scores **ponovljeno tačno** (apsolutna razlika 0.0 uz isto pinovano okruženje). Ovo nije novo GA dostignuće niti 864 ponovo izvršena poziva; **samo 10 novih AC**.

## 3. Identitet upornih generatora

Dva originalna, **aktivna** generatora bila su izvan Q granica u **svih deset** nezavisno od promene devet kontrolnih varijabli:

- **Originalni gen red #46 (0-based 45), BUS103:** QG ≈ **+75,422363582 MVAr**, izvorni QMAX = **+40 MVAr**, originalni QMIN=-15, dakle **35,422364 MVAr iznad QMAX** u svih deset slučajeva. Izvorni PG=40 MW, izvorni VG=1.01 p.u.
- **Originalni gen red #48 (0-based 47), BUS105:** QG ≈ **-18,334525252 MVAr**, izvorni QMIN = **-8 MVAr**, QMAX=+23, dakle **10,334525 MVAr ispod QMIN** u svih deset slučajeva. Izvorni PG=0, izvorni VG=0.965 p.u.

Bus103 i BUS105 su **originalne PV (bus type 2) sabirnice**, sa aktivnim granama povezanim na okolinu; sami generatorski setpointi BUS103/BUS105 nisu bili nijedna od 9 kontrolnih varijabli u I18. Stoga je **hipoteza** da bi uključivanje njihovih VG kontrole moglo promeniti lokalne Q izlaze. Konstantnost pod prethodnim udaljenim kontrolama dokazuje samo nedovoljnu osetljivost unutar ovih deset stanja; **ne** dokazuje teorijsku nemogućnost, matematičku neizvodljivost originalnog IEEE118, niti garantuje da nova dva setpointa rešavaju *sve* Q probleme.

Dodatno originalni generatori BUS34 (red16) i BUS92 (red43) često krše QMIN/QMAX, ali njihov Q menja znak i intenzitet između različitih kandidata. To je korisna motivacija za preciznu domensku dijagnostiku Q/resursa pre predloga adaptacije unutar GAdapt-a.

## 4. Sledeći logičan eksperiment

**Ne menjati GA slepo.** Napraviti unapred registrovani mali jednofaktorski/simetrični screening samo **originalnih generatorskih VG na BUS103 i BUS105**, sa izvorno dopuštenim naponima, konstantnim svim ostalim PG/VG, originalnim load/tap/rating i tačnim brojanjem stvarnih `runpf` poziva. Cilj isključivo merljiva **Q osetljivost**, ne odmah GA prevlast. Ako ova dva VG menjaju uporne Q prekoračenja, naći smisleniji izbor kontrolnih resursa, pa razvijati i testirati ograničenjima svesnu adaptaciju u pravom GAdapt-u sa adekvatnim strong baselines.

Pravi full original IEEE118 AC-OPF u iteraciji16 bio je post-hoc provereno feasible, uz širi prostor. Ova dijagnostika je mali povratno provereni uzorak u *užem* 9D prostoru i ne može utvrditi postojanje izvodljivosti punog AC-OPF ili novog algoritamskog naučnog doprinosa.

## Dokazi

- [Preregistrovani protokol](ITERATION19_PROTOCOL.md)
- [Tačan program za 10 originalnih AC poziva i izvorna P/Q/V identitetna analiza](iteration19_ieee118_forensic_diagnostic.py)
- [Unit testovi bez AC poziva](test_iteration19_ieee118_forensic_diagnostic.py)
- [Raw CSV — sve komponente ograničenja za svih 10](results/ieee118_iteration19_forensic_10_real_ac_20261021.csv)
- [Raw JSON — top-12 izvornih offending BUS/GEN i svi fizički rezultati](results/ieee118_iteration19_forensic_10_real_ac_20261021.json)
- [Uspešan CI #39652408164](https://github.com/owlCoder/gadapt/actions/runs/39652408164)

Ponoviti (10 stvarnih AC):

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration19_ieee118_forensic_diagnostic
python -m research.iteration19_ieee118_forensic_diagnostic --json /tmp/i19.json --csv /tmp/i19.csv
```
