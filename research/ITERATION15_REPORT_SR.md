# Iteracija 15 — RTE1888 originalni AC-OPF sa step-controlled PIPS 565: vremenski ograničen neuspeh

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** unapred registrovana druga strategija, svi testovi prošli, oba stvarna AC-OPF poziva izvršena i arhivirana, veliki izvorni RTE1888 ostao **bez potvrđenog izvodljivog rešenja**. Nije testiran niti menjan algoritam GAdapt, originalni bpzoran/gadapt nije menjan.

## 1. Šta je fiksirano pre novih poziva

Preregistrovan [ITERATION15_PROTOCOL.md](ITERATION15_PROTOCOL.md), commit `eee5fba88d8c8d94c9a18fcdddf9581d71c612c5`, posle negativnog originalnog rezultata iz iteracije 14 (PYPOWER 560 `success=False` za 5,1993 s). Sada je korišćen **PYPOWER 5.1.19, `OPF_ALG=565` step-controlled PIPS**, sa originalnom neizmenjenom MATPOWER 2019 mrežom i generatorima, ukupno 1888 sabirnica, 298 originalnih generatora, 2531 grana i 298 originalnih linearnih generatorskih cena. `PF_DC=False`, apparent RATE_A oba kraja, originalni P/Q i V bounds, max 100 iteracija, one-thread BLAS, SciPy 1.13.1, Python 3.12.

Javni originalni izvor je MATPOWER/matpower commit `80b6e16f760f58721ad31221c7287c28259cd4ad`, CC BY 4.0, Josz et al. Testni RTE podaci izričito **nisu za operativno upravljanje ili planiranje realne francuske/EU mreže**.

## 2. Dva stvarna solver pokušaja i dokazni status

[Uspešan GitHub Actions CI #39641058963](https://github.com/owlCoder/gadapt/actions/runs/39641058963) znači da su testovi i procedura evidencije prošli. **Ne znači** da je veliki OPF numerički uspeo.

| AC-OPF poziv | Solver rezultat | Wall time |
|---|---|---:|
| PYPOWER case9, `OPF_ALG=565`, prethodno fiksirani mali kontrolni primer | **success=True**, 12 iteracija | **0,55296 s** |
| **Originalni RTE1888** ekonomski AC-OPF, `OPF_ALG=565` | **`TimeoutError`: limit unapred fiksiran na 780 s** | **780,07039 s** |

Na kontrolnom primeru dijagnostika navodi `raw.info=1`, `message=Converged`, poslednja normalizovana `feascond=4,32e-7`, `gradcond=1,51e-7`, `compcond=7,95e-7`. Prijavljeni izvorni trošak kontrolnog standardnog case9 565 iznosi 5296,68778547, ne treba direktno porediti sa numeričkom kontrolom algoritma 560 iz iteracije 14 kao statističku prednost. Bez dodatne nezavisne verifikacije u ovim kontrolama `case9` iz njih se ne izvode posebne teorijske tvrdnje.

**Veliki originalni RTE1888 proračun nije dao nijedan verifikovan PG/QG, naponski vektor, termičko stanje, ekonomsku cenu niti optimum.** U sirovom JSON-u njegove fizičke metrike su eksplicitno `null`; ukupno računamo **dva stvarna AC-OPF pokušaja**, uključujući onaj koji je istekao. Pošto timeout prekida solver pre povratnog rezultata, `raw.info`, `raw.output` i iteraciona istorija **nisu raspoloživi** za veliki poziv; ne sme se izmišljati da je bio blizu konvergencije ili da nije imao fizički izvodljivih rešenja.

## 3. Značenje i naredni smer

Originalni IEEE14 i IEEE118 AC-OPF iz **iteracije 16** potvrdili su uspeh istog native PYPOWER solvera 560 na manjim javnim mrežama uz nezavisnu post-hoc proveru source pojedinačnih P/Q/V, MVA na oba kraja i kompleksnog AC nodalnog balansa. Time postoji makar jedan rigorozan poligon za budući GA pre nego što originalni 1888-bus OPF bude rešen.

RTE1888 rezultati 14 (brzi `success=False` sa 560) i 15 (timeout sa 565) **ne dokazuju matematičku neizvodljivost originalnog AC-OPF niti da je GAdapt bolji ili gori**. Sledeći smislen korak za originalni RTE1888 je nezavisan pouzdan nelinearni solver ili relevantno inicijalizovanje uz novi unapred registrovan protokol, i stroga post-hoc fizička provera pre prijave svakog rezultata.

Za doktorski rad sada je prioritet osloniti se na već **verifikovane IEEE14 i IEEE118 izvorne AC-OPF slučajeve** i napraviti strogo budžetiran *stvarni* GAdapt baseline uz zajedničku fizičku ciljnu funkciju i bez lažnih izvodljivih rezultata. Tek zatim predložiti literaturom potkrepljen originalni mehanizam adaptacije.

## 4. Reprodukcija

- [Protokol](ITERATION15_PROTOCOL.md)
- [Implementacija](iteration15_source_opf_solver_diagnostics.py)
- [Unit testovi](test_iteration15_source_opf_solver_diagnostics.py)
- [Sirovi CSV sa oba native AC-OPF poziva](results/rte1888_iteration15_source_acopf_solver_565_20261021.csv)
- [Sirovi JSON sa stvarnim PIPS statusom i timeout razlogom](results/rte1888_iteration15_source_acopf_solver_565_20261021.json)
- [CI i originalni log](https://github.com/owlCoder/gadapt/actions/runs/39641058963)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration15_source_opf_solver_diagnostics research.test_iteration14_original_acopf
python -m research.iteration15_source_opf_solver_diagnostics --json /tmp/i15.json --csv /tmp/i15.csv
```

**Naučni zaključak:** uspešan kontrolni solver, neokončan veliki izvorni nelinearni OPF pod ograničenim budžetom. Izvedena negativna dijagnostika je verodostojna, ali nije naučni doprinos o novom GAdapt-u, lokalnom/globalnom optimalnom RTE dispečingu ili stvarnoj industrijskoj primeni.
