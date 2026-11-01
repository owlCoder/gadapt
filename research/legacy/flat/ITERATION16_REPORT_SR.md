# Iteracija 16 — potpuno proverene lokalne AC-OPF referentne tačke IEEE14 i IEEE118

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** registrovani protokol, kod, testovi, uspešan CI i sirovi CSV/JSON. Ukupno **2 stvarna AC-OPF poziva**, dva solver uspeha i dve pozitivne post-hoc fizičke provere. **Ovo nisu GAdapt rezultati ni industrijski verifikovana postrojenja.**

## Istraživačka motivacija

Izvorno MATPOWER RTE1888 ima modelnu neusaglašenost sa ranijom pandapower konverzijom i, do iteracije 14, originalni PYPOWER ekonomični AC-OPF nije konvergirao. Da se doktorski rad ne zadrži beskonačno na softverskoj ispravci velikog slučaja, pre većih GAdapt eksperimenata zamrzli smo [ITERATION16_PROTOCOL.md](ITERATION16_PROTOCOL.md), sa ograničenim nezavisnim javnim IEEE kontrolnim problemima. Nisu promenjene originalne PYPOWER `case14` i `case118` matrice ili originalni kvadratni generatorski troškovi.

Native PYPOWER 5.1.19 `runopf`, standardni PIPS `OPF_ALG=560`, AC `PF_DC=0`, source-rated apparent MVA `OPF_FLOW_LIM=0`, `OPF_IGNORE_ANG_LIM=False`, max 100 iteracija; Python 3.12, scipy1.13.1, pandas2.2.3, jednonitni BLAS. Izvorne javne IEEE mreže su **testne mreže**, ne podaci stvarnog operativnog sistema.

## Stvarni rezultati i fizička post-hoc provera

[Uspešan CI #39642073586](https://github.com/owlCoder/gadapt/actions/runs/39642073586): svi regression testovi i oba originalna AC-OPF proračuna prošli.

| Pokazatelj | IEEE14 | IEEE118 |
|---|---:|---:|
| Broj sabirnica / aktivnih generatora / grana | 14 / 5 / 20 | 118 / 54 / 186 |
| Native AC-OPF `success=True` | **Da** | **Da** |
| **Naknadno svi provereni source uslovi zadovoljeni** | **Da** | **Da** |
| Izvorni polinomni ekonomski objective | **8.081,526393** | **129.660,686390** |
| Individualna P/Q prekoračenja | 0 / 0 | 0 / 0 |
| Naponske VMIN/VMAX povrede | 0 | 0 |
| Izvorne RATE_A MVA prekoračene grane | 0 / 20 | 0 / 186 |
| Najveće source-rated opterećenje | 1,3114% | 4,1823% |
| Maksimalni kompleksni nodalni KCL rezidual | 3,61e-8 MVA | 6,59e-5 MVA |
| Ekonomski cilj ponovo izračunat iz PG i gencost? | **Tačno se poklapa** | **Tačno se poklapa** |
| Gubici u MW, *ne cilj optimizacije* | 9,2872 | 77,4010 |
| Broj pravih native AC-OPF poziva | 1 | 1 |

**Ključna granica:** prikazani izlazi su lokalni numerički **rešeni AC-OPF kandidati** sa proverom originalnih pojedinačnih P/Q, svih VMIN/VMAX, pozitivno definisanih RATE_A (oba kraja), kompleksnog AC nodalnog bilansa i izvornog polinomnog troška. `makeYbus` i `makeSbus` koriste istu PYPOWER biblioteku koja predstavlja solver; to je *nezavisno ponovno izračunata vrednost reziduala*, **ne drugi nezavisan električni model ili formalni dokaz globalne optimalnosti**.

Dodatno, source-rated granice su na ova dva originalna mala modela **veoma labave** (najveća iskorišćenost 1,31% i 4,18%). Ne smemo tvrditi da je dokazano pametno postupanje optimizatora u termički tesnoj mreži, kao ni da se rezultati mogu preneti na stvaran veliki nacionalni sistem. Potrebni su unapred definisani stres režimi na istim modelima, sa korektnim izvorom novih limitâ i jasnom razlikom između originalne i izmenjene formulacije.

## Preregistracija i trajni dokazi

- [Pre-registracija](ITERATION16_PROTOCOL.md)
- [Izvorni PYPOWER IEEE14/IEEE118 AC-OPF i fizički validator](iteration16_ieee_original_acopf.py)
- [Testovi prvobitnih izvora i realne/nereaktivne/generatorske logike](test_iteration16_ieee_original_acopf.py)
- [Sirovi JSON sa svim fizičkim metrima](results/ieee14_ieee118_iteration16_native_acopf_20261021.json)
- [Sirovi CSV, jedan red po stvarnom solver pozivu](results/ieee14_ieee118_iteration16_native_acopf_20261021.csv)
- [GitHub Actions #39642073586](https://github.com/owlCoder/gadapt/actions/runs/39642073586)

Ponoviti:

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration16_ieee_original_acopf research.test_iteration14_original_acopf
python -m research.iteration16_ieee_original_acopf --json /tmp/ieee.json --csv /tmp/ieee.csv
```

## Naučni zaključak i veze sa budućim GAdapt testovima

**Prvi put imamo dva lokalno rešena i kompletno post-hoc proverena source IEEE AC-OPF kontrolna zadatka**, što je kvalitetna osnova za ozbiljnije eksperimentalno poređenje GAdapt-a sa domenskim solverom — **ali optimizaciona formulacija GA mora biti identična**. Sama činjenica da poznati interior-point solver radi na originalnim malim slučajevima nije nov doktorski doprinos.

Sledeće: napraviti ograničeni GAdapt evaluator sa stvarnim AC tokovima snaga i nedvosmislenom fizičkom izvodljivošću, povezati sve selekcije i vrednosti sa brojem pravih AC solver poziva, i uporediti originalni GAdapt sa odgovarajućim jednostavnim referentnim metodama na istom zadatku. Dok se ne napravi i verifikuje isti task space, **ne upoređivati direktno ekonomsku vrednost interior-point AC-OPF i raniji GAdapt gubitak u MW**. RTE1888 ostaje zaseban veliki istraživački problem.

**Status originalnosti:** nema dokaza algoritamske superiornosti, nema novog dovoljno opravdanog operatora, nema validacije industrijske eksploatacije i nema prava na tvrdnje o globalnom optimumu.
