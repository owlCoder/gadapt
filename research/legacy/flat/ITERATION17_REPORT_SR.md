# Iteracija 17 — stvarni GAdapt na originalnom IEEE14, 864 AC proračuna

**Datum:** 21.10.2026. **Fork:** owlCoder/gadapt:main, originalni upstream bpzoran/gadapt nije menjan. **Status:** unapred registrovan pilot, pravi Python `gadapt.ga.GA`, dva konkurentska metoda, svih **864 izvornih IEEE14 AC Newton–Raphson poziva stvarno izvršeno**, 9/9 optimizer postupaka završeno; source fizička izvodljivost nezavisno pregledana u svakoj AC evaluaciji.

## 1. Zašto je ovaj experiment bolji od prethodnih

[Preregistrovani protokol](ITERATION17_PROTOCOL.md), commit `8cf704d4ac225242ab623c2b2730964af0507dcb` nastao je pre prvog stvarnog PF poziva ove iteracije. Izvorna public PYPOWER IEEE14 mreža sa **14 sabirnica, 5 aktivnih generatora, 20 source RATE_A grana** i originalnom kvadratnom generatorskom ekonomskom cenom. Stvarna GA kandidatska jedinka ima **9 varijabli**: 4 PG generatora van slack sabirnice i svih 5 generator VG setpointova, u izvornim pojedinačnim P/V granicama. Svaki zahtevan kandidat se fizički evaluira originalnim PYPOWER `runpf`, AC `PF_ALG=1`, originalnom mrežom i bez promene loads ili ratings.

**Bitna ograničenja:** ovo je **PV-kontrolisani podskup** punog nelinearnog AC-OPF: runpf sa `ENFORCE_Q_LIMS=0` rešava AC fizičke jednačine, a **svako** stvarno kršenje izvornog generator QMIN/QMAX ispituje se posle rešavanja i može potpuno isključiti kandidata iz izvodljivih. Puno optimizaciono rešavanje sa nezavisnim P/Q setpointovima, PQ prelazima i svim Q saturacijama **nije isto kao ovaj pilot**, čak iako originalna izvorna cena i fizička ograničenja dolaze iz istog slučaja. Kandidati ne mogu biti proglašeni fizički izvodljivim ako krše individualne PG/QG, sve bus VMIN/VMAX, originalne source RATE_A MVA oba kraja ili kompletan kompleksni AC nodalni balans. Tolerancije: 1e-5 p.u. V, 1e-3 MW/MVAr PG/QG, 1e-3 MVA thermal i KCL; penalizovana funkcija nije indikator izvodljivosti.

Stvarni **originalni `from gadapt.ga import GA`**, `cost_diversity_metric=log_relative` legacy režim, 16 kandidata; pravi SciPy diferencijalna evolucija bez `polish` i obična uniformna slučajna pretraga. Identični izvorni 9D bounds, jedna penalizovana ciljna funkcija (originalna ekonomska cena + unapred fiksirana kazna), uparena random semena 2026, 2027, 2028. Fiksni **96 real AC poziva po metodi i semenu**; ukupno 9 pokretanja = **864**. `runpf` poziv se broji **na stvarnoj fizičkoj solver granici**, a pozivi optimizatora posle limita vraćaju penalni sentinel koji nije AC rezultat.

## 2. Izmerene fizičke evaluacije

[Uspesan GitHub Actions CI #39645834755](https://github.com/owlCoder/gadapt/actions/runs/39645834755). Brojevi su očitani iz arhiviranog JSON i potvrđeni iz stvarnih logova.

| Izvorni metod | Seed | Pravi AC pozivi | Fizički izvodljivi pojedinačni kandidati | Najbolja stvarno izvodljiva izvorna ekonomska cena |
|---|---:|---:|---:|---:|
| **Originalni GAdapt legacy** | 2026 | 96 | **11** | **9.575,672226** |
| SciPy differential evolution | 2026 | 96 | 0 | **nema** |
| Uniform random search | 2026 | 96 | 0 | **nema** |
| **Originalni GAdapt legacy** | 2027 | 96 | **1** | **11.212,108431** |
| SciPy differential evolution | 2027 | 96 | 0 | **nema** |
| Uniform random search | 2027 | 96 | **2** | **10.936,112421** |
| **Originalni GAdapt legacy** | 2028 | 96 | 0 | **nema** |
| SciPy differential evolution | 2028 | 96 | **1** | **8.892,350877** |
| Uniform random search | 2028 | 96 | 0 | **nema** |

Svi uspešni fizički kandidati imaju `max_voltage_excess=0`, `max_generator_P_excess=0`, `max_generator_Q_excess=0` i `max_original_RATE_A_MVA_excess=0`, a maksimalni kompleksni nodalni KCL rezidual njihovih sačuvanih najboljih kandidata je reda 1e-9 MVA ili manje. **Nula od 864 fizička PF pokušaja završila se neuspešnom konvergencijom**, ali mnogi konvergentni kandidati nisu fizički izvodljivi — ovo se rigorozno razlikuje u JSON i CSV. Nijedan numerički neizvodljiv kandidat nije u tabeli dobio izmišljenu ekonomsku cenu kao izvodljivo rešenje.

### Bez statističkog zaključka iz samo tri semena

- **GAdapt legacy:** bar jedan fizički izvodljiv kandidat u **2/3** pokretanja, najbolja cena po semenu 9.575,672226 / 11.212,108431 / null. Ukupno **12** realno izvodljivih kandidata i 288 AC poziva; medijana samo preko dva uspešna starta **10.393,890329** (ovo nije medijana svih pokretanja).
- **Differential evolution:** bar jedan izvodljiv u **1/3**, najbolji 8.892,350877, ukupno 1 feasible kandidat i 288 AC poziva.
- **Random:** bar jedan izvodljiv u **1/3**, najbolji 10.936,112421, ukupno 2 feasible kandidata i 288 AC poziva.

**Iz ovoga se ne može dokazati superiornost GAdapt-a.** GAdapt ima više uspešnih početnih semena, ali DE ostvaruje najbolju stvarnu cenu među ovim pilot metodama. Moguće je da slučajni brojevi i drugačija raspodela kandidata objasne sve. Tri uparena semena nisu osnova za p-vrednosti, statističke testove, rad u industriji ili novu doktorsku novinu. Pilot samo dokazuje da pravi GAdapt može da proizvodi **stvarna PF-konvergentna, po originalnim ograničenjima fizički izvodljiva** rešenja na maloj izvornoj IEEE14 mreži.

### Razlika od punog AC-OPF domenskog referentnog solve-a

U iteraciji 16 standardni pun `runopf` PIPS solver je na originalnoj IEEE14 mreži postigao source-economy **8.081,526393** sa post-hoc potvrđenim P/Q/V/RATE_A i kompletnim KCL bilansom. Nijedan pilot GA, DE ili random realno izvodljiv kandidat sa ukupno 96 AC evaluacija po pokretanju nije bolji od te vrednosti. **To NIJE statistički fer performans benchmark**, jer PIPS ima drugačiji interni rad, globalno ekonomično rešava drugačiji, širi kontinuirani optimizacioni prostor i njegov rad nije izražen kao isti broj AC PF poziva. Nije dokazano da je PIPS globalno optimalan.

### Pošteno o request sentinelima

GAdapt tri puta ima po **98** objective zahteva, od kojih su dva po pokretanju *posle* stroge granice, pa nema dodatnih fizičkih AC poziva. DE tri puta ima po **270** objective zahteva, od kojih čak **174** po pokretanju su *posle* realne granice (završetak programa izvršava brojne interne evaluacije koje vraćaju sentinel) — ovo nije 270 fizičkih simulacija i ne sme tako biti predstavljeno. Random svaki put ima 96 objective zahteva i isto toliko stvarnih AC proračuna. Ovo stanje pravi dodatni metodološki rizik: dozvoljeni sentinel može uticati na internu optimizatorovu završnu logiku, ali **ne** na arhiviran fizički najbolji primer, koji se ažurira samo stvarno završenim AC proračunom. Sledeći ozbiljan benchmark treba koristiti kontrolisan način zaustavljanja i poređenje sa jednakim stvarnim budžetom i brojem pravih pokušaja.

## 3. Reproduktivnost

- [Originalni protokol preregistracije](ITERATION17_PROTOCOL.md)
- [Originalni GAdapt, DE i random nad fizički AC validiranim izvorom](iteration17_ieee14_gadapt_economic_pf.py)
- [Testovi brojanja isključivo stvarnog PF i individualne fizičke izvodljivosti](test_iteration17_ieee14_gadapt_economic_pf.py)
- [Sirovi CSV svih 9 stvarnih optimizatorskih pokretanja](results/ieee14_iteration17_real_gadapt_de_random_20261021.csv)
- [Sirovi JSON sa najboljem source-feasible tačkama i svim dijagnostikama](results/ieee14_iteration17_real_gadapt_de_random_20261021.json)
- [GitHub Actions workflow — uspešno izvršenje #39645834755](https://github.com/owlCoder/gadapt/actions/runs/39645834755)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration17_ieee14_gadapt_economic_pf
python -m research.iteration17_ieee14_gadapt_economic_pf --seeds 2026 2027 2028 --budget 96 --population 16 --json /tmp/i17.json --csv /tmp/i17.csv
```

## 4. Odnos prema mentorskoj tezi

Ovo je **prvi po ovom novom izvornom ekonomskom kontrolnom problemu** realno budžetirani GAdapt pilot koji može da se ponovi nezavisno od ranijeg pandapower tumačenja. Originalna fizička granica je jednostavna ali precizna, a izvorni IEEE14 termički limiti su **veoma labavi**, tako da rezultat nije dokaz algoritamske robusnosti u industrijski ozbiljnom termičkom stresu.

**Naredni koraci:** (1) po posebnoj preregistraciji pokušati istu ograničenjima svesnu fizičku evaluaciju na IEEE118, uz pažljivo označen pilot podskup izvornog punog AC-OPF; (2) razviti korektno i troškovno efikasno upravljanje fizičkim constraints i solver fail-om u *stvarnom* GAdapt-u; (3) snažnije metode i više uparenih semena u više električnih scenarija i telco benchmarku. Ne nazivati postojeći feasibility operator ili AOS literaturu svojim novim otkrićem. **Originalan mehanizam i statistički potvrđena prednost još nisu pokazani.**
