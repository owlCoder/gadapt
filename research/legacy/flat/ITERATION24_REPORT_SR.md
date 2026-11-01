# Iteracija 24 — prvi originalni GAdapt, DE, random i Powell na istih pet fizički relevantnih IEEE118 kontrola

**Datum:** 21.10.2026. **Repo:** `owlCoder/gadapt:main`. **Status:** preregistrovan, svih **12/12 optimizatorskih run-ova**, **1.152 stvarna PYPOWER Newton–Raphson AC PF** poziva, originalni GAdapt iz stvarnog `gadapt.ga.GA`, DE, random i bounded Powell, četiri metode × tri semena × 96 stvarnih AC. **Sva 12/12** pokretanja pronašla su bar jedan fizički izvodljiv kandidat; svi 1.152 PF su numerički konvergirali, ali pojedinačne neizvodljive tačke NISU proglašene validnim ekonomskim rešenjem. Svaka source physics provera obuhvatila je 54 individualnih PG/QG, 118 sabirničkih VMIN/VMAX, originalne pozitivne RATE_A oba kraja i kompleksni AC nodalni KCL.

**Kritično ograničenje:** ovo je **kalibracioni in-sample eksperiment**. Lokalni petodimenzionalni upravljački prostor i centar izabrani su **posle** I19–I23 pronalaženja fizički izvodljive oblasti. Nije nezavisna generalizacija na neviđene mrežne scenarije, nije dokaz nove GAdapt mehanike ili statističke superiornosti. Upstream `bpzoran/gadapt` nije menjan.

## 1. Unapred zamrznut fizički zadatak

[Preregistracija I24](ITERATION24_PROTOCOL.md) commit `3a24bb274b0148a4fb891c7c3bedb83af6fee76a` prethodila je svim I24 AC pozivima. Izvorni javni `pypower.case118()`: 118 originalnih bus, 54 online gen, 186 branch, izvorni originalni PG/QG Pmin/Pmax Qmin/Qmax, sabirnički VMIN/VMAX i source positive RATE_A termički apparent-MVA oba terminala, source polynomial gencost.

**PG svih 54 generatora na izvornim ulaznim vrednostima**, dok PG slack originalne BUS69 naravno određuje AC fizički model (mora naknadno zadovoljiti source PG limit). Pet podesivih originalnih generator naponskih setpointova `VG`: **BUS103, BUS32, BUS34, BUS92, BUS19**. Sve ostale originalne generatorske VG fiksirane, originalni load/tap/šant/topologija i generator PQ granice netaknuti.

Lokalni identični source-valid opseg svake metode: `center ±0.005 p.u.`. Centri postavljeni iz **prethodno plaćene** izvodljive I23 bracket oblasti, α=0.75 za BUS34/BUS92/BUS19, i poznati BUS103 VG=0.990, BUS32 VG=0.973. Originalne granice samih sabirnica su širine 0.94–1.06; suženi kalibracioni box je **informaciona prednost svih metoda**, ne algoritamska univerzalna pretraga. Ni jedna izvorna I23 fizička tačka nije ubačena kao besplatan optimiser incumbent niti ponovno besplatno evaluirana.

Fizička validacija svake konvergirane source tačke je stvarni `runpf`, `ENFORCE_Q_LIMS=0`, zatim obavezno samostalno poređenje individualnih originalnih QMIN/QMAX (nema pogrešne ideje `runpf.success==feasible`), individualnih PG/PMIN/PMAX, svih VMIN/VMAX, pozitivnih RATE_A MVA oba kraja i ponovni obračun kompleksnih AC reziduala istog PYPOWER izvornog modela. Izvorna originalna ekonomska `gencost` računa se iz izlaznih stvarnih PG **samo kao stvarno ostvarena cena ako su svi fizički uslovi ispunjeni**. Penalizovani score je originalna cena + `1e5*(sum V pu + sum P MW/100 + sum Q MVAr/100 + sum source terminal RATE_A excess MVA/100 + sum kompleksni KCL MVA/100)`, jednako za sve metode.

**Metode**: neizmenjeni legacy GAdapt `cost_diversity_metric=log_relative`, population16, postojeća adaptivna mutacija; originalni SciPy `differential_evolution`, bez `polish`; uniform random; lokalni *bounded Powell* sa `x0=center`, `xtol=1e-5`, `ftol=1e-7`, `maxfev=96`. Powell sam dobija determinističan informisani centar kao inicijalizaciju; ostali algoritmi stohastički uzorkuju istu kutiju, nisu podudarnih početnih populacija. Ovo je referentna **razlika metoda i inicializacije**, ne čista ablation efekta nekog GA operatora.

Svaka metoda po semenu dobija **96 stvarnih poziva AC PF**, sa semenom 2026, 2027, 2028. Svim metodama pošteno je zajednički maksimalni i ostvareni AC budget, ali broj **internih objective zahteva posle budžeta** kod DE/GA nije stvarno fizičko evaluiranje. Powella seed ne menja: tri ponovljena ista deterministična toka **nisu tri nezavisne stohastičke replikacije**.

## 2. Kompletni izmereni rezultati

[GitHub Actions CI #39659382865](https://github.com/owlCoder/gadapt/actions/runs/39659382865): prošli izvorni unit testovi bez AC i sva 12 stvarna fizička optimizer run-a. Prvo workflow pod istim protokolom imao je YAML sintaksu neispravnog opisa koraka, pa **nije izvršio nijedan AC**; ispravljena je isključivo navodnicima obavijena YAML rečenica, a protokol/kod/seed nisu menjani.

| Metod | Seed | Stvarni AC | Source-feasible kandidata | Prvi pravi feasible AC # | Najbolja source-feasible ekonomska cena |
|---|---:|---:|---:|---:|---:|
| **GAdapt legacy** | 2026 | 96 | **23** | 57 | **131.195,131546** |
| DE bez polish | 2026 | 96 | 1 | 41 | 131.199,138078 |
| Uniform random | 2026 | 96 | 2 | 11 | 131.199,142494 |
| **Bounded Powell** | 2026 | 96 | **67** | 1 | **131.193,636506** |
| **GAdapt legacy** | 2027 | 96 | **52** | 5 | **131.196,733578** |
| DE bez polish | 2027 | 96 | 7 | 61 | 131.194,777680 |
| Uniform random | 2027 | 96 | 1 | 42 | 131.198,808587 |
| **Bounded Powell** | 2027 | 96 | **67** | 1 | **131.193,636506** |
| **GAdapt legacy** | 2028 | 96 | **31** | 50 | **131.197,245167** |
| DE bez polish | 2028 | 96 | 10 | 1 | 131.195,123634 |
| Uniform random | 2028 | 96 | 4 | 25 | 131.196,562290 |
| **Bounded Powell** | 2028 | 96 | **67** | 1 | **131.193,636506** |

**Svi prikazani najbolji kandidati zadovoljili su** source individualne P/Q, svih V i izvorni pozitivni RATE_A MVA (nula prekoračenja), sa maksimalnim kompleksnim AC balans rezidualom oko 1,6·10⁻¹⁰ MVA. Dakle, tabelarni cost zaista pripada source-feasible kandidatu u ovom **fiksno-P, pet-VG** podskupu, a ne samo penalizovanom score-u.

Sa 288 stvarnih AC poziva po metodi:
- **GAdapt legacy:** ukupno **106 fizički izvodljivih** kandidata; sve **3/3** stohastičke putanje imaju bar jedno feasible rešenje; najbolji feasible cost **131.195,131546**, medijana tri run best cost **131.196,733578**.
- **DE:** ukupno **18** source-feasible, 3/3 uspešnih seedova; najbolji cost **131.194,777680**, medijana **131.195,123634**.
- **Random:** ukupno **7** source-feasible, 3/3 seedova; najbolji cost **131.196,562290**, medijana **131.198,808587**.
- **Powell:** ukupno **201 source-feasible pokušaj** ako se doslovno saberu tri **identične determinističke 96-evaluacione putanje** (realno fizički izvršene triput, ne 201 nezavisna stohastička kandidata). Svako pokretanje 67 source-feasible; lokalna putanja dostigla najbolji feasible cost **131.193,636506**. Powell počinje u centru, fizički izvodljivoj tački, i zato pronalazi feasible već na **AC pozivu 1**; ostali ne dobijaju tu identičnu `x0` kao prvog kandidata. Numerička statusna zastavica Powell je **`success=False` — maksimalnih 96 funkcijskih evaluacija je potrošeno pre algoritamskog formalnog završetka**. To **ne menja** činjenicu da je 67 realnih AC kandidata prošlo source fizičku proveru; fizičku izvodljivost ne treba mešati sa SciPy `OptimizeResult.success`.

Sva 12 ran-a potrošila su tačno **96 realnih AC**; `optimizer_reported_success` je 3/3 GA, 3/3 DE, 3/3 random, 0/3 Powell zbog `maxfev` termina. Ni jedan stvarni AC nije numerički neuspeo. GAdapt ima po 98 objective zahteva (**2 posle budžeta**, sentineli), DE po 175 (**79 posle budžeta**, sentineli), a random i Powell 96 zahteva (**nula sentinel poziva**). Nisu izmišljeni dodatni AC, a senzitivno je to što interne DE završne iteracije primaju penalni sentinel i njihov status nije ekvivalent naučno relevantnom budžetu; naučno poređenje koristi **samo memoriju monitora stvarno izvršenih** kandidata.

## 3. Šta ova studija još NIJE dokazala

1. **Nije dokaz da je GAdapt bolji:** u po tri stohastičke putanje, GAdapt ima više source-feasible kandidata od DE i random, ali **DE i Powell daju niži minimum originalne ekonomske cene**, a Powell i veću učestalost fizički izvodljivih pokušaja. Nema p-vrednosti ni statističke zaključke iz samo tri slučajna semena. Powell tri puta ponavlja istu determinističku inicijalizaciju, dakle nije nezavisno replicitiran eksperiment.
2. **Nije dokaz adaptivne novine:** stvarna GA implementacija NIJE menjana. Razlika između ranijeg I18 bez feasible i sadašnjeg I24 sa feasible dominantno odražava **drugu reprezentaciju kontrolnih PV resursa i suženu in-sample pretragu** (prethodni I18 koristio je četiri PG i pet uglavnom drugih VG generatora i 49 PG/VG ostalih fiksnih). Ona NIJE GAdapt algoritamska superiornost.
3. **Nije dokaz prenosivosti:** relevantni PV izvori i centar određeni su analizom ranijih IEEE118 stvarnih AC proba I19–I23, uključujući pronalaženje feasible α=0.7/0.8. Takav in-sample benefit je **kalibracija**, ne predikcija nepoznatih elektroenergetskih mrežnih režima.
4. **Nije puni AC-OPF niti globalna optimalnost:** slobodni P dispečing cele 54-generator mreže u I16 izvornom `runopf` dao je originalni ekonomski objective **129.660,686390** uz drugi, širi problem i potpuno drugačiji interni AC-OPF solver. Najbolji I24 lokalni Powell cost **131.193,636506** nije pobeda nad punim I16 OPF. History I23 najbolji deterministički PG-fixed PV cost **131.198,797575** nije besplatno inicijalizovano GA rešenje; I24 ga malo lokalno poboljšava unutar posebnog informed box-a, ali oba su različiti nastanci, te direktna stopa poziva nije poštena.

## 4. Zašto je ovo korisno za doktorat i sledeći eksperiment

Za disertaciju sada ima smisla zamrznuti *odvojeno* tri domena istraživanja:
- **reprezentacija fizički korisnih izvora** (koji originalni generatori, koliko PV setpointova i kako zadržati PG/Q/V/source thermal poštenim);
- **efikasnost realne GA pretrage** uz snažnu lokalnu kontrolu (Powell) i DE, a ne samo random;
- **eventualni originalan constraint-feasibility-aware operator/adaptation** sa eksplicitnim ablation i ekonomskom cenom *svake* dodatne AC probe, preživljavanje Q zasićenja, široki i novi slučajevi, statistički upareni testovi i pregled postojeće adaptive operator selection/sensitivity repair literature.

Pre *nove* GAdapt modifikacije najvažnije je da sledeći eksperiment bude **out-of-sample**: izvorni drugačiji IEEE118 load/šant/P/Q režimi sa identičnim prioritetnim PV resursima, ali bez selekcije novog centra na osnovu test rezultata; svi source AC kandidati i fizika plaćeni jednako. Mogu se razmotriti zasnovane **dve suprotne nulte hipoteze** (npr. da bilo kakva korist dolazi samo od ručno odabrane reprezentacije, ne od adaptacije operatora), a tek potom predstaviti mehanizam koji to nadmašuje.

## 5. Dokazi, kod i ponavljanje

- [Pre-registracija I24](ITERATION24_PROTOCOL.md)
- [Prava GA, DE, random i bounded-Powell pet-VG source IEEE118 evaluacija](iteration24_ieee118_fivepv_real_gadapt.py)
- [Statički/unit testovi izvornog kontrolnog 5D prostora i budžeta](test_iteration24_ieee118_fivepv_real_gadapt.py)
- [Sirovi CSV svih 12 metoda-seme pokušaja](results/ieee118_iteration24_legacy_gadapt_de_random_powell_20261021.csv)
- [Sirovi JSON, 12 kompletnih source fizičkih proveravanja i realna brojila](results/ieee118_iteration24_legacy_gadapt_de_random_powell_20261021.json)
- [Uspešan I24 GitHub Actions #39659382865](https://github.com/owlCoder/gadapt/actions/runs/39659382865)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration24_ieee118_fivepv_real_gadapt
python -m research.iteration24_ieee118_fivepv_real_gadapt --seeds 2026 2027 2028 --budget 96 --population 16 --json /tmp/i24.json --csv /tmp/i24.csv
```

**Naučna odluka:** veliki napredak u pouzdanom objektivnom benchu stvarnog GAdapt-a sa originalnom AC fizikom i snažnim lokalnim baseline-om, ali ne i demonstriran doktoratski algoritamski doprinos. Javni IEEE case ne može biti podloga za industrijski operativni rad bez zasebne validacije.
