# Iteracija 31 — kontrolisana ablacija: cenzurisani fitness nije isto što i ušteda AC simulacija

**21.10.2026. Završeno svih 48 unapred definisanih fizičkih run-ova.** Protokol [I31](ITERATION31_PROTOCOL.md) je sačuvan pre stvarnih I31 AC poziva. Model je **ISTA** originalna javna IEEE118 topologija i **ISTI I30** sintetički prostorno različiti source PD/QD režimi; ovo NIJE novi topološki, industrijski ili slepi scenario holdout. Šest prethodno kalibrisanih generator VG kontrola i granice nisu menjani. Originalni GAdapt default i I29 core scenario evaluator **nisu menjani**.

**Rezime:** ukupno **8.611 STVARNO izvršenih PYPOWER AC NR proračuna od najviše 8.640** (29 neiskorišćenih rezervisanih mesta pri ranim prekidima). **Nula numeričkih neuspeha**. Izvoz CSV-a u originalnom job-u imao je grešku zaglavlja zbog dodatnih kontrolnih polja; kompletni 48-row JSON i svi pojedinačni redovi bili su prethodno napisani. Originalni CI fizički job je stoga formalno FAILED na CSV koraku, a **ne na AC proračunima**. Eksperiment nije ponovo pokrenut: originalni JSON i ispravan CSV naknadno su sačuvani iz direktno parsiranog, auditabilnog `I31_TRUE_AC` stdout loga; exporter je popravljen, fizički workflow podešen za **isključivo ručni novi fizički rerun**.

## Glavni rezultati

Četiri varijante koriste isto 12 novih uparenih seedova **2080–2091**, najviše 180 stvarnih originalnih AC po metodi/semenu, identičnu GA konfiguraciju. `full_censored` je **posebna kontrola**, ne „nova AI/GA metoda“: troši sva tri stvarna AC po kandidatu, ali GA selekciji vraća isti cenzurisani score kao rani prekid po prvom fizički izmerenom kršenju, dok su numerički svi scenariji konvergentni.

| Varijanta GAdapt | Semena sa >=1 stvarno 3-scenario feasible x (od 12) | Ukupno stvarno feasible kandidata* | Potpuno izmerenih kandidata | Stvarnih AC | Najniža potpuno proverena originalna srednja ekonomska cena |
|---|---:|---:|---:|---:|---:|
| `full_true` — puni AC, pravi fitness | **9/12** | 127 | 720 | 2.160 | **131.195,943423** |
| `full_censored` — puni AC, cenzurisani selekcioni fitness | **7/12** | 149 | 720 | 2.160 | 131.196,169726 |
| **`stop_fixed` — prvi dokazan prekršaj prekida** | **11/12** | **375** | 375 | **2.148** | 131.195,951573 |
| `stop_adaptive` — empirijski redosled scenarija | **10/12** | 371 | 371 | **2.143** | 131.195,951573 |

*Broj izvodljivih kandidata meri trajektorije pretrage i može brojati povezana/ponovljena stanja; **nije** broj statistički nezavisnih eksperimenata. Svaki pozitivni kandidat u tabeli zaista je proverен u sva tri izvorna AC scenarija. Kod screening metoda dodatno je **908** (`stop_fixed`) odnosno **973** (`stop_adaptive`) kandidata fizički potvrđeno neizvodljivo pre kompletnog triple-batch-a. Za njihovi 1.701 odnosno 1.889 **neizvršenih** scenario-pokušaja ne postoje stvarno izmereni podaci niti je izmišljena originalna source mean cena. To su izbegnute evaluacije na **njihovim sopstvenim** pretražnim putanjama, ne empirijski meren cost difference na potpuno istim genome-ovima full GA.

## Upareni seed kontrasti — glavno značenje

| Kontrast | Oba uspešna | Uspešan samo prvi | Uspešan samo drugi | Nijedan | Oprezna interpretacija |
|---|---:|---:|---:|---:|---|
| `full_true` prema `full_censored` | 7 | 2 | 0 | 3 | Promeniti SAMO score na punom 3×AC evaluiranju **nije pomoglo** broju uspešnih seedova. |
| `full_censored` prema `stop_fixed` | 7 | 0 | **4** | 1 | Uz isti first-failure score i AC budget, rani prekid u ovom testu omogućava više uspešnih semena. |
| `stop_fixed` prema `stop_adaptive` | 10 | 1 | 0 | 1 | Empirijski redosled nije pomogao; jedno seme fixed je uspešno, adaptive nije. |
| `full_true` prema `stop_fixed` | 9 | 0 | 2 | 1 | Fixed je imao dva dodatna uspešna seed-a; ali najbolja potpuno verifikovana originalna cena ostaje minimalno niža u full_true. |

Po uparenim seedovima, za ključni kontrast `full_censored` naspram `stop_fixed` ima samo **4 diskordantna** para, sva 4 u korist fixed: dvostrani **egzaktni McNemar/binomni p = 0,125**. To **ne opravdava** tvrdnju o statistički dokazanoj superiornosti na standardnom 0,05 nivou. Kod `full_true` naspram `stop_fixed` samo dva različita seeda (p=0,5). Ni drugi kontrasti nisu statistički odlučujući. Dodatni seedovi i nezavisni domeni neophodni su pre naučne tvrdnje.

### Mehanistički zaključak

1. **Promena ocene sama po sebi može da škodi:** pri identična 2.160 AC i 720 potpuno izmerenih kandidata, cenzurisana kontrola je uspela u 7/12 naspram 9/12 u originalnoj verziji, iako ima 149 prema 127 potpuno izvodljivih kandidata unutar uspešnih GA putanja. To jasno pokazuje da **broj kandida­ta nije ekvivalentan uspešnosti semena**.
2. **Ušteda AC pri istom selekcionom pravilu jeste povezana sa više obrađenih kandidata i 11/12 prema 7/12 uspeha** u ovom konkretnom problemu: stop_fixed je imao 1.314 objective requests naspram 744 u full_censored, sa 2.148 prema 2.160 originalnih AC. Ovaj kontrast je bliži izdvojenom efektu budžeta nego raniji I29/I30, ali evolutivne putanje nisu iste i ovi brojevi nisu matematički identifikovan pojedinačni uzročni efekat.
3. **Adaptacija nije donela dodatan benefit:** 10/12 umesto 11/12 i potpuno isti najbolji provereni source trošak; dodatni scenario redosled se ne sme predstavljati kao naučni doprinos.
4. **Najbolja prava ekonomska cena je praktično izjednačena**, sa minimalnom prednošću `full_true`; stoga ni potvrđeni benefit u broju seed uspeha ne implicira globalno bolju ekonomsku optimizaciju.

## Verifikacija i granice

- [Originalni I31 workflow run #39681669407](https://github.com/owlCoder/gadapt/actions/runs/39681669407) — **20/20 zero-AC testova uspešno**, fizički 48 run-ova završeni, CSV export korak neuspešan zbog različitih kolona; ne prikazivati originalni job kao potpuno zelen.
- [Originalni CI artifact sa punim pre-CSV-failure JSON](https://github.com/owlCoder/gadapt/actions/runs/39681669407/artifacts/12383827867). Isti sirovi 48 individualna `I31_TRUE_AC` reda imaju javni job log.
- [Potpuno arhiviran JSON od 48 run-ova, rekonstruisan bez AC rerun-a](results/ieee118_iteration31_12seeds_4arms_8611_real_AC_20261021.json) · [CSV sa unijom svih kolona](results/ieee118_iteration31_12seeds_4arms_8611_real_AC_20261021.csv).
- [Izvorni I31 kontrolni benchmark](iteration31_fitness_budget_ablation.py) · [Sintetički I31 no-AC testovi](test_iteration31_fitness_budget_ablation.py) · [I31 preregistracija](ITERATION31_PROTOCOL.md).

**Glavno ograničenje:** 12 semena, kontrolne promenljive i uže granice preuzete iz ranijih radova, isti IEEE118, tri veštačka prostorna režima, jedan PYPOWER solver, nikakav nezavisan inženjerski solver/field telco validation i nije puni AC-OPF. Bez navedene dodatne validacije ovo predstavlja **metodološki i inženjerski rezultat**, ne originalno dokazan novi optimizacioni algoritam.

**Preporučeni sledeći samostalni zadatak:** definisati nezavisnu IEEE14/drukčiju topologiju sa novim source ograničenjima i scenarijima, novim semенima i fer potpuno plaćenim baseline-ovima; kasnije pravi telekom/infrastrukturni domen. Zatim literaturno uporediti metod za upravljanje budžetom sa scenario racing/surrogate radovima. Ne podešavati više ni adaptivni redosled ni censored score samo prema pozitivnom rezultatu.
