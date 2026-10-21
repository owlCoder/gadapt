# Iteracija 23 — prvi potpuno izvorno fizički izvodljivi IEEE118 kandidati u ograničenom PV/PG-fixed AC podskupu

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main, bez izmena upstream `bpzoran/gadapt`. **Status:** unapred registrovani, završeni **4 stvarna PYPOWER IEEE118 AC NR proračuna**, svi numerički konvergentni, **dva potpuno source-feasible** prema deklarisanim fizičkim kriterijumima. Nije korišćen GAdapt/DE/random optimizator i **ovo nije algoritamska novina**, globalni optimum ni dokaz rada u stvarnoj industrijskoj mreži.

## 1. Zašto je originalni IEEE118 sada prvi put izvodljiv u ovom užem testu

[Izvorni protokol I23](ITERATION23_PROTOCOL.md) je unapred arhiviran u commit-u `adb623a91729eaae4e0d7f90c6c7ab9303c34001`, pre svih 4 novih stvarnih AC PF pokušaja. Originalni IEEE118 `pypower.case118()`: 118 bus, 54 aktivna originalna generatora, 186 originalnih grana, originalni load/šant/tap, individualni generator P/Q limiti, sabirnički VMIN/VMAX i pozitivni izvorni RATE_A MVA obostrano. **Svih 54 generatorskih PG fiksno je na originalnim PG ulazima**, osim što se izvorni slack PG određuje fizičkim AC jednačinama. Nigde nije smanjivan load ili termički limit. Q se numerički ne nameće tokom PF, ali svaki izvorni QMIN/QMAX obavezno prolazi naknadnu fizičku proveru.

Postepeno *preregistrovano i naplaćeno pravim AC pozivima*:
- I19, tačno 10 originalnih AC: originalni PG/VG + 9 starih I18 vektora; utvrđeni konstantni Q prekršaji na BUS103 i BUS105;
- I20, 8 stvarnih AC: smanjenje BUS103 VG sa 1,01 na **0,99** uklanja Q prekršaje BUS103 i BUS105, ali ostaju četiri QMIN prekršaja;
- I21, 8 stvarnih AC: BUS32 VG sa 0,963 na **0,973** uklanja još jedan QMIN, a pregrubi `±0,01` koraci na tri preostala često pređu na QMAX;
- I22, 5 stvarnih AC: centralne konačne razlike iz I21 određuju male source-VG korekcije za BUS34, BUS92 i BUS19; zajednički **α=0,5** daje jedan QMIN prekršaj **BUS92, 2,464456 MVAr**; **α=1,0** daje jedan **drugi QMIN prekršaj BUS36, 3,642855 MVAr**. Nijedna od te dve prethodne AC tačke nije bila potpuno feasible.
- **I23, nova 4 stvarna AC:** unapred su izabrana sva četiri faktora **α=0,6, 0,7, 0,8, 0,9** *bez reakcije tokom rada*. Samo između arhiviranih, fizički stvarnih, suprotno neizvodljivih I22 tačaka; nisu ponavljane besplatne PF reference.

Fiksna source-VG formula iz prethodno izmerenih I21 osetljivosti:
- BUS103 originalni gen #46: **VG=0,990000**;
- BUS32 originalni gen #15: **VG=0,973000**;
- BUS34 gen #16: VG = **0,984 + α·0,004016033221868577**;
- BUS92 gen #43: VG = **0,990 + α·0,003533199035653122**;
- BUS19 gen #9: VG = **0,962 + α·0,004619105395208329**;
- preostalih **49** source generator VG ostaju na početnim izvornim setpointima.

## 2. Svih četiri realna rezultata bez selektivnog izostavljanja

[GitHub Actions CI #39656195300](https://github.com/owlCoder/gadapt/actions/runs/39656195300) zelen, svi unit testovi i četiri stvarne originalne AC evaluacije. Neuspešni fizički kandidati nisu dobili izmišljeni feasible objective.

| Unapred fiksiran faktor α | Numerička AC konvergencija | Source generatorski Q-offenderi | Ukupno Q excess (MVAr) | P/V/positive RATE_A prekršaji | SVA proveravana fizička ograničenja? | Izvorna ekonomska cena samo ako feasible |
|---|---|---:|---:|---:|---|---:|
| 0,6 | Da | 1 — BUS92 | 0,761637 | 0 / 0 / 0 | **Ne** | **null** |
| **0,7** | Da | **0** | **0** | 0 / 0 / 0 | **DA** | **131.199,623157** |
| **0,8** | Da | **0** | **0** | 0 / 0 / 0 | **DA** | **131.198,797575** |
| 0,9 | Da | 1 — BUS36 | 1,706599 | 0 / 0 / 0 | **Ne** | **null** |

Kompleksni AC KCL maksimalni reziduali sva četiri su samo ≈ **1,60·10⁻¹⁰ MVA**. Po istim I18–I22 unapred definisanim pragovima: generator P/Q 1e-3 MW/MVAr, V 1e-5 p.u., izvorna termička RATE_A MVA 1e-3 MVA, originalni AC nodalni KCL 1e-3 MVA — **α=0,7 i α=0,8 zadovoljavaju sve proveravane izvorne fizičke uslove**. Ovo je validna, lokalna matematičko-fizička činjenica o navedenom javnom testnom modelu, ne certificikacija rada u pravoj elektroenergetskoj mreži. KCL je ponovo izračunat `makeYbus/makeSbus` iz **iste PYPOWER biblioteke** koja predstavlja izvorni PF, pa ne tvrdimo da postoji druga nezavisna električna implementacija.

Najbolji među ova dva fizički uspešna deterministička kandidata je **α=0,8**, izvorni originalni generatorski ekonomski cost **131.198,797575**. Rešeni IEEE118 puni originalni `runopf` iz iteracije 16 imao je verifikovan lokalni economic cost **129.660,686390** uz širi prostor kontrola; ovo je deskriptivno **oko 1,19% veća cena**, a **nije budžetski fer poređenje** (potpuni AC-OPF koristi drugačiji interni solver i slobodniji PG/Q/V dispečing). Nijedan rezultat nije dokaz globalnog minimuma.

## 3. Šta je zaista dokazano o GAdapt-u

Prethodni I18 imao je **864 pravih IEEE118 AC NR simulacija** kroz stvarni originalni GAdapt, DE i random na **drugom, devetodimenzionalnom skupu kontrola**, bez ijednog fizički izvodljivog kandidata. I19–I23 zajedno imaju **10 + 8 + 8 + 5 + 4 = 35 NOVIH realnih AC poziva** koji su transparentno dijagnostikovali i fizički razrešili ključne Q prekršaje kroz **domenski izabrane kontrole** i male Q/VG korake. Ovo **nije fer eksperiment “35 protiv 864”** za algoritamsku superiornost: I19–I23 koriste *posle analize prethodnih rezultata* izabrane nove kontrolne varijable, novi skup korekcija i već izmerene reaktivne osetljivosti. Nijedan novi GAdapt operator nije implementiran, pa *GA superiornost nije dokazana*. Korisno je pokazano da **reprezentacija fizičkih upravljačkih resursa, održavanje Q granica i veličina koraka** mogu biti ključniji od pukog povećanja populacije ili slučajnih mutacija.

### Sledeći disertacijski eksperiment (još nije sproveden)

Na istoj originalnoj IEEE118 fizici treba unapred fiksirati zajednički **relevantan petodimenzionalni originalni PV skup** (BUS103, BUS32, BUS34, BUS92, BUS19), puna jednaka originalna P/Q/V/RATE_A/KCL evaluacija, i strog fizički budžet za **legacy GAdapt, GAdapt+nezavisno plaćen sensitivity-aware repair, DE, uniform random i barem jednu jaku lokalnu fizikalnu bazu**; zahtevi za finite-difference credit i potvrdu feasibility moraju potrošiti isti real AC budžet. Potreban pregled prethodnih radova jer adaptive operator selection, feasibility ranking i sensitivity-guided repair već postoje. Pravi doktorski doprinos će postojati tek ako nova (literaturom odbranjiva) mehanika daje robustne potvrđene statističke koristi na više pre-registriranih elektroenergetskih scenarija i telco instancama.

## 4. Trajni izvori i ponavljanje

- [Preregistrovani protokol I23](ITERATION23_PROTOCOL.md)
- [Program `iteration23_ieee118_qbracket.py` za 4 stvarne izvorne IEEE118 AC PF](iteration23_ieee118_qbracket.py)
- [Strukturni/unit testovi, bez AC](test_iteration23_ieee118_qbracket.py)
- [Raw CSV — sva četiri rezultata, null za dva neizvodljiva](results/ieee118_iteration23_qbracket_4_real_ac_20261021.csv)
- [Raw JSON — sve originalne fizičke provere i tačan generator VG vektor](results/ieee118_iteration23_qbracket_4_real_ac_20261021.json)
- [Uspešan CI #39656195300](https://github.com/owlCoder/gadapt/actions/runs/39656195300)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration23_ieee118_qbracket
python -m research.iteration23_ieee118_qbracket --json /tmp/i23.json --csv /tmp/i23.csv
```

**Strogo:** izvorni IEEE118 je javni akademski testni slučaj, ne stvarni industrijski operativni model; dokumentovani direktni AC kandidati nisu globalni OPF, nisu statistički verifikovani doprinos GAdapt-u i nisu proizvodno sertifikovani.
