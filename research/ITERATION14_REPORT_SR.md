# Iteracija 14 — prvi originalni MATPOWER RTE1888 ekonomski AC-OPF pokušaj

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main, originalni upstream nije menjan. **Status:** kompletan protokol, implementacija, unit testovi, GitHub Actions, 2 stvarna AC-OPF solver poziva sa originalnim izvornim troškovima; originalni veliki solver završio je sa success=False. **Nema prihvaćenog fizički izvodljivog AC-OPF rešenja i nema poređenja GAdapt algoritama.**

## 1. Polazna formulacija

[Protokol iteracije 14](ITERATION14_PROTOCOL.md), commit `fb023e31726a88c79a16b75774b9c12fd970e86a`, prethodio je pozivima solvera. Direktni, **nekonvertovani** MATPOWER RTE1888 source [2019](https://github.com/MATPOWER/matpower/blob/80b6e16f760f58721ad31221c7287c28259cd4ad/data/case1888rte.m) sadrži originalnu BUS1320 slack referencu, 1888 sabirnica, 298 generatora (291 online), 2531 granu (455 nedefinisanih RATE_A termičkih limita). Posebno smo izvukli [svih 298 izvornih gencost redova](results/rte1888_iteration14_original_matpower_gencost_full7_2019.csv); **svaka jedinica ima originalnu linearnu cost funkciju**, sa koeficijentima samo iz skupa {1, 2, 10}, bez kvadratnog člana. Ovo je **ekonomski AC-OPF**, ne ranije optimizovani MW gubici — nije dozvoljeno direktno porediti te različite ciljane funkcije.

Native PYPOWER 5.1.19, `runopf` / primal-dual interior-point `OPF_ALG=560`, `PF_DC=0`, apparent MVA oba kraja source-positive RATE_A, originalna individualna PG/QG i V ograničenja, izvorno fiksirana mreža. `PDIPM_MAX_IT=100`; originalni originalni brojevi nisu promenjeni. Zasebni **post-hoc** validator proverava source P/Q/V i positive-rated oba kraja MVA, kompleksni AC nodalni bilans i ponovno izračunatu ekonomsku cenu. Kod je spreman za proveru ako solver prijavi uspeh, ali **za originalni slučaj ovde nije bilo validnog rezultata koji bi mogao da se proveri**.

## 2. Stvarno izmereni budžet i ishodi

[GitHub Actions CI #39640202591](https://github.com/owlCoder/gadapt/actions/runs/39640202591) je uspešno izvršio sve testove i oba preregistrovana poziva:

| Stvarni AC-OPF poziv | PYPOWER local solver status | Trajanje |
|---|---|---:|
| Mali izvorni kontrolni `case9` (isti OPF solver) | **success=True** | 0,15238 s |
| Veliki originalni `case1888rte` (298 izvornih gencost redova) | **success=False** | 5,1993 s |

Na malom `case9` prijavljena solver-ekonomska cena je 5296,68652363, isključivo kao dijagnostički signal da instalirani solver radi na poznatom manjem slučaju. Ona nije nezavisno proverena kao fizički izvodljiv optimum u ovoj iteraciji. Na velikom izvornom RTE1888 proračunu **nema prihvaćene ekonomske vrednosti, snaga, dispečinga ili ukupno izvodljivog rezultata**, a sve odgovarajuće post-hoc metrike su zapisane kao JSON `null`.

**Ovo nije dokaz da puni originalni nonlinear AC-OPF nema rešenje.** To je konkretnim pretpostavkama i solverom ograničen negativni pokušaj. Razlog numeričke terminacije `success=False` još nije izmeren na odgovarajućoj dijagnostičkoj dubini; zasebna pre-registracija mora prethoditi sledećem pokušaju.

## 3. Arhiva i ponavljanje

- [Izvorna numerička gencost 298x7 CSV](results/rte1888_iteration14_original_matpower_gencost_full7_2019.csv)
- [Originalni 1888 BUS, 298 GEN, 2531 BRANCH i P/Q/V/termalni validator](iteration14_original_acopf.py)
- [Originalni gencost, sintetički kompleksni KCL i negativni acceptance testovi](test_iteration14_original_acopf.py)
- [Sirovi CSV oba solver poziva](results/rte1888_iteration14_original_acopf_20261021.csv)
- [Sirovi JSON oba solver poziva](results/rte1888_iteration14_original_acopf_20261021.json)
- [Uspešan CI sa izvornim logovima](https://github.com/owlCoder/gadapt/actions/runs/39640202591)

Instalacija: Python 3.12.15, `pypower==5.1.19`, `scipy==1.13.1`, `pandas==2.2.3`, `pandapower==2.14.11`; jednonitni BLAS/OMP. Podaci su istraživački, licencirani CC BY 4.0 i **nisu za realno operativno upravljanje niti planiranje francuske ili evropske mreže**.

## 4. Zašto je ovo ipak korak napred

Prvi put su postavljeni i arhivirani originalni gencost, potpuni originalni P-dispečing prostor i nezavisni fizički validacioni kriterijumi za budući lokalni izvorni AC-OPF reference solver. Nije više opravdano porediti GA score na naponskom screen-u sa ekonomskom AC-OPF cenom, ili tvrditi da je fizička AC konvergencija sama po sebi optimum.

**Sledeće:** jasno ograničena dijagnostika PYPOWER `raw.info` i `raw.output` statusa / broja iteracija na originalnom problemu, uz nezavisni pokušaj prikladnije postavljenog solvera i jednaka izvorna ograničenja. Tek zatim pristupiti algoritamskoj modifikaciji GAdapt-a i verifikovanom infrastrukturnom benchmarku. GAdapt originalnost i superiornost nisu potvrđene.
