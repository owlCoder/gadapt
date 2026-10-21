# Iteracija 29 — stvarno izvršen cost-aware IEEE118 scenario-screening: više izvodljivih odluka po istom AC budžetu, ali early-reject NIJE nova teorija

**Datum:** 21.10.2026. **Repo:** `owlCoder/gadapt:main`, upstream `bpzoran/gadapt` nije menjan. **Status:** pre-registrirano, svih **20 stvarnih GA/DE run-ova** kroz originalnu IEEE118 izvornu P/Q/V/rated thermal/KCL fiziku, **ukupno 3.583 ZAISTA izvršena AC PF** od 3.600 maksimalno dozvoljenih, 0 numeričkih neuspeha. **Testovi opt-in core GAdapt evaluatora uspešni na Python 3.10 / 3.11 / 3.12**, sve proveravano pre pravog AC benchmarka. [Zeleni GitHub Actions #39669410103](https://github.com/owlCoder/gadapt/actions/runs/39669410103). Nema lažnog fizički izvodljivog ili besplatno izmerenog nepotpunog scenario kandidata.

## 1. Šta je zapravo novi KOD i šta nije nova naučna ideja

[Preregistracija I29](ITERATION29_PROTOCOL.md), commit `c5477eb24f86046780959617bd1fe969faf4cce7`, sačuvana pre novih AC poziva i izborа novih random seedova. Umesto podešavanja UCB operator-credit reward koji **nije pokazao prednost u I28 (6/12 vs 8/12 legacy)**, implementiran je opciono pozivljiv evaluator **unutar GAdapt package**: [`gadapt/operations/cost_finding/sequential_scenario_budget_cost.py`](../gadapt/operations/cost_finding/sequential_scenario_budget_cost.py). GA koristi evaluator kao obični `cost_function`; default `GA()` niti UCB formula iz I26 nisu menjani.

- `full`: jedan originalni generator setpoint x STVARNO se proverava u **sva tri** originalna source load režima `0.98/1.00/1.02`, uvek tačno 3 prava `pypower.runpf`, i tek tada ima potpun izvorni `mean(source polynomial gencost)+1e5*sum(real normalized violation)`.
- `stop_fixed`: najpre stvarni 98%-load NR + sva originalna pojedinačna source P/Q/V/rated RATE_A/KCL provera. Ako je **konvergentan i fizički neizvodljiv**, odmah se prekida scenario niz: time je matematički poznato da all-3 conjunction za TAJ x nije ispunjen, ali originalni 100%/102%-load AC **NISU** izmereni, njihova fizika i ekonomski cost **OSTAJU nepoznati**. GA dobija `censored heuristic score=1e9+1e5*measured_violation`, **ne** lažnu punu ekonomsku cenu.
- `stop_adaptive`: isti stop, ali redosled novih evaluacija vodi samo prethodna `(observed source-limit fail+1)/(actually observed AC+2)` po režimu, bez ikakvog "feedback" sa neizvršenih režima.
- Ako originalni AC numerički ne konvergira, status je **numerically unknown, ne dokazana fizička neizvodljivost**. `full` i dalje broji sva tri stvarna AC; `stop` može stati, ali nikad ne objavljuje validnu all-3 feasible cenu. Svaki stvarni callback koji ne poveća brojač za tačno +1 FAIL CLOSED. Ostatak budžeta manji od 3 znači nijedan novi simulator pokušaj, pa može ostati 1–2 neiskorišćena AC i ne beleži se kao postignuti optimum.

**Izvorna javna IEEE118 fizika:** 118 bus, 54 online gen (originalni PG osim fizičkog slack), 186 branch; originalni individualni PG/QG limits, bus V limits, originalni pozitivni RATE_A MVA oba kraja, kompleksni KCL; generator control VG isti originalni šest BUS103/32/34/92/19/74 i isti prethodno IEEE118-informisani lokalni 6D box za svih pet metoda. Sva tri PD+QD sinteticka globalna load množioca fiksna. Fizički source cost je stvaran i validan za pobednički x **samo ako sva TRI fizička scenarija STVARNO konvergiraju i prođu source limits**. Ovo je uski originalno-P-fixed, šest-setpoint model, **nije globalni AC-OPF ni stvarna industrijska mreža**.

Detaljan [pregled prior art](ITERATION29_PRIOR_ART_SR.md) priznaje Sankary et al. (2018), [doi:10.1002/2017WR022068](https://doi.org/10.1002/2017WR022068), scenario sampling in EAs, kao i early stopping/scenario racing. **Prikazivati rani prekid kao novu doktorsku algoritamsku ideju bilo bi neodbranjivo.** Naš kod je ipak direktno merljivo unapređenje *upravljanja realnim evaluacijama GAdapt-a* u konkretnom problemu, sa zaštitom od fiktivnog feasibility.

## 2. Pre-registrirani fer protokol stvarnih AC

Pet načina rada, potpuno isti originalni 6D model i sama GA ili DE metoda u odgovarajućim parovima:
- `gadapt_full`,
- `gadapt_stop_fixed`,
- `gadapt_stop_adaptive`,
- `scipy_de_full`,
- `scipy_de_stop_fixed`.

**4 NOVA i unapred odabrana seeds 2060–2063** za svaku metodu (20 run-ova). Svaka ima **limit do 180 STVARNIH AC**, ne jednak broj generisanih kandidata; metod sa ranim prekidom sme obraditi više pojedinačnih candidate vektora jer se mnogi physically falsifikuju već posle 1 stvarnog AC. Isti GAdapt legacy operatori, cost-diversity log-relative, pop12 i potpuno jednaki originalni izvorni 6D box; DE SciPy `polish=False`, popsize=5. Proračuni i optimizer statusi numeričke konvergencije nisu isto što i source physics izvodljivost. Sve stvarne 3-scenario cene uračunavaju se **samo među zaista potpuno izmerenim all-three-feasible kandidatima**.

## 3. Kompletni ukupni rezultati iz pravog CI, uključujući negativne

| Metod | Izvodljiv uspeh po seed (od 4) | Potpuno source all-3 feasible kandidata | Broj source kandidata potpuno izmerenih kroz sva 3 AC | Fizički odbačeni već posle <3 AC (nepotpuni) | Izvršenih STVARNIH AC | Najbolja stvarna all-3-feasible mean original cost |
|---|---:|---:|---:|---:|---:|---:|
| **GAdapt full** | **1/4** | **1** | 240 | 0 | **720** | 131.315,435665 |
| **GAdapt stop-fixed** | **4/4** | **118** | 118 | **355** | **715** | **131.312,095132** |
| GAdapt stop-adaptive | **4/4** | **118** | 118 | **355** | **715** | **131.312,095132** |
| SciPy DE full | **0/4** | 0 | 240 | 0 | **720** | **null** |
| SciPy DE stop-fixed | **4/4** | **9** | 9 | **680** | **713** | **131.311,760046** |

**Bitna interpretacija:** za GAdapt stop-fixed je ukupno **473 stvarno započeta candidate vektora** (118 potpuno izmerenih po 3 AC + 355 physically rejected pre 3 AC) naspram **240** u punom GAdapt evaluatoru. To je za **715 stvarnih AC**, ne besplatnih 1.419 koji bi bili potrebni kada bi se svih 473 vektora naivno proverilo po 3 source scenario PF. Razlika od **704** su **preskočeni, NIKADA NEIZMERENI** originalni source-scenario AC, a ne stvarno validirana ušteda u istoj putanji full evaluatora (njegovi x kandidati nisu ista evolutivna putanja!). To je accounting kontrafaktual broj za **baš tu screen-putanju**, ne fizički izvršene simulacije. Pozitivnih 118 su sve realno **3× plaćene** proverene tačke i uključuju ponovljena source-vektorska stanja/related GA potomke unutar samo 4 putanje, dakle nije 118 nezavisnih statističkih eksperimenata.

**Adaptivni redosled nije dodao ništa fiksnoj kontroli**: sva 4 GAdapt metoda po semenu imaju numerički identične stop-fixed vs stop-adaptive real physical counts, best feasible cost, i stop source-scenario puts. Originalni **98%-load** je skoro uvek dominantan izvorni Q-limit failure u ovom prethodno kalibrisanom prostoru, pa posterior fail-rate ordering nije pružio stvarno novu informaciju niti dodatnu uštedu. Nova adaptivna komponenta kao zaseban doprinos **nije demonstrirana**.

**DE**: izmereno 713 stvarnih AC u stop-fixed, ali originalni SciPy zatražio je znatno više *neizvršenih objective poziva nakon iscrpljivanja budžeta*, koje nisu bile označene kao simulator AC. Zbog maksimalnog `maxiter` SciPy `OptimizeResult.success=False` ne negira fizičku izvodljivost 9 stvarno punih 3-scenario provera. DE full nema nijedan all-three feasible u 240 potpuno izmerenih candidate vektora u četiri 180-AC run-a. Različit senzorni fitness `censored heuristic=1e9+` naspram punog `mean+penalty` menja GA/DE selekciju — rezultat NIJE čista izolacija benefita redosleda, već *evaluacioni režim + score landscape* zajedno.

**Broj stvarno nepotrošenih fizičkih poziva = 17** od maksimalnih 3.600 jer za broj starih upita ostaje 1–2 AC, ali novi kandidat sme da započne samo sa rezervacijom sva tri. Nije korektno tvrditi tačno 3.600 AC; rezultat je **3.583 originalnih real AC PF**.

## 4. Koliko je svaki scenario stvarno proveravan

- GAdapt **full**: 240 pravih AC po svakom od `0.98/1.0/1.02`.
- GAdapt **stop-fixed i stop-adaptive**: po **473 stvarnih 98%-load**, **123 stvarnih 100%-load**, **119 stvarnih 102%-load** AC; unobserved **704** 100/102 load proba nisu izvršene, njihovu source fiziku ne izmišljamo.
- DE **full**: po 240 realnih AC po režimu.
- DE **stop-fixed**: po 689 / 14 / 10 realnih AC na load `0.98/1.00/1.02`, sa **1.354 neizvršenih, ali dijagnostički mogućih drugih proba** u njegovoj vlastitoj candidate putanji.

**Svi realni `runpf` pozivi numerički konvergentni**; 0 nepoznatih numeričkih stanja, 0 lažno declared robust feasible. Pojedinačno 3-AC source-feasible kandidati imaju nula originalnih individualnih generator P/Q, bus V i positive rated RATE_A prekoračenja i proverene kompleksne AC bilanse kroz `physics_118` istu PYPOWER implementaciju. Nema nezavisnog drugog fizičkog solvera.

## 5. Naučna granica i preporuka

Ovo je **pozitivan stvarni softversko-inženjerski rezultat**: opcioni budžetski evaluator efikasnije otkriva za ovaj kalibrisani problem robustno izvodljive kontrolne odluke pod ograničenim brojem native AC solves. Međutim **rano otkrivanje makar jednog kršenja je logički trivijalna osobina AND-feasibility, poznata evolutivna early-screening/racing ideja**; sama fiksna screen varijanta koja daje skoro sav benefit **nije nova naučna metoda**.

Za disertaciju je imperativ **pre sledećeg reward tuninga** unapred odabrati *nezavisne različite source load/topološke slučajeve* (npr. različite prostorne PD/QD perturbacije ili IEEE14, i telco), gde 98%-load nije gotovo uvek najteži. Onda videti da li **stvarno adaptivni izbor redosleda** ili nov teorijski dobro utemeljen mehanizam daje nešto preko vrlo jednostavnog stop-fixed. Potrebna dodatna analiza source OPF availability i benchmark jaka baseline solvers na istim AC budgetima; 4 semena su pilot i ne dokazuju statistički superiornost ili operativni deployment.

**Ako se pokaže da običan fiksni first-failure check ostaje najbolji, rezultat doktorata može biti metodološka analiza, ali nije dovoljan originalan algoritamski doprinos bez nove teorijske i praktično potvrđene komponente.**

## 6. Proverljivi dokazi

- [I29 protokol (zamrznut pre 3.583 source AC)](ITERATION29_PROTOCOL.md)
- [I29 evaluator — novi opt-in cost_function u stvarnom GAdapt source code-u](../gadapt/operations/cost_finding/sequential_scenario_budget_cost.py)
- [I29 source IEEE118 GA/DE stvarni `runpf` benchmark](iteration29_real_scenario_earlystop_benchmark.py)
- [I29 sintetički regression testovi koji NE pokreću AC](../tests/test_sequential_scenario_budget_cost.py)
- [I29 proverа originalnih generatora/source budgeta bez AC](test_iteration29_earlystop_protocol.py)
- [I29 literal prior art/novelty audit](ITERATION29_PRIOR_ART_SR.md)
- [Sirovi JSON svih 20 metoda-seed stvarnih source AC rezultata](results/ieee118_iteration29_scenario_earlyreject_20runs_trueAC_20261021.json)
- [Sirovi CSV svih 20 runova](results/ieee118_iteration29_scenario_earlyreject_20runs_trueAC_20261021.csv)
- [Uspešan GitHub Actions #39669410103, 3 Python matrix i 3583 stvarnih AC](https://github.com/owlCoder/gadapt/actions/runs/39669410103)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v tests.test_sequential_scenario_budget_cost research.test_iteration29_earlystop_protocol
python -m research.iteration29_real_scenario_earlystop_benchmark --json /tmp/i29.json --csv /tmp/i29.csv
```

**Strogo:** sve ovo je akademski javni IEEE118 sa veštačkim opterećenjima, originalni PG-fiksni podskup i delimično fizikalno data-informed decision bounds. Nije opservacija stvarne industrije, nije puni ekonomski AC-OPF i nema garancije robusnosti izvan tri konkretna scenarija, ni dokaza algoritamske doktoratske novine.
