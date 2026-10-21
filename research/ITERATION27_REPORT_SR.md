# Iteracija 27 — prvi stvarni IEEE118 AC test novog in-core GAdapt scenario-feasibility operator credit mehanizma

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Rezultat:** stvarno izvršeno **3.240 PYPOWER IEEE118 Newton–Raphson AC PF poziva**, tačno 18 optimizatorskih pokretanja `6 metoda × 3 prethodno zamrznuta semena × 180 AC`, od kojih svako ima **60 kompletno naplaćenih 3-scenarijskih kandidata**. Tačno **jedan kompletno source-feasible kandidat u SVA TRI load režima**, pronađen u jednom pokretanju novog experimental `gadapt_ucb_scenario_feasibility` mehanizma, naspram nula takvih kandidata u ostalim 17 pokretanja. Ovo je **samo pilot**, nikako dokaz superiornosti, statističkog efekta, uzročnosti mutation-credit nagrade ili naučne originalnosti.

## 1. Zašto je I27 DRUGAČIJA od prethodnih iteracija

Prvi put je promenjena **stvarna core implementacija GAdapt-a**. Pre toga su I19–I25 uglavnom dijagnostikovali fizički sistem i učinak originalnog legacy GAdapt-a, ali nisu razvili novi operator/credit. U [I26 kodu i izveštaju](ITERATION26_REPORT_SR.md) opt-in `mutation_operator_credit='scenario_feasibility'` prošao je testove Python 3.10, 3.11, 3.12; kredit uči iz *celog N-vektora source fizičkih povreda*, a ne samo penalizovanog score ili scalar worst-case source povrede.

[Preregistracija I27](ITERATION27_PROTOCOL.md), commit `532c4457b274e28a706b1beef763a21672135111`, zamrznula je **pre novih stvarnih AC**: istu izvornu mrežu `pypower.case118()`, iste source P/Q/V/positive RATE_A MVA oba kraja i kompleksni AC KCL uslove, sa tri **namerno veštačka PD+QD load režima 0,98 / 1,00 / 1,02**. Svaki genetski kandidat je **isti šestodimenzionalni originalni generator VG vektor** u sva tri scenarija, potpuno bez adaptacije specifične za scenario; **PG svih 54 gen fiksiran na izvorni ulaz**, osim stvarnog AC redispečinga originalnog slack BUS69 koji mora zadovoljavati source P bounds. Originalni generator `gencost` source polynomial se računa iz stvarnog PG izlaza svakog kompletnog AC.

Šest izvornih PV generatora **BUS103, BUS32, BUS34, BUS92, BUS19, BUS74**: prvih pet zajedno sa prethodno kalibrisanim I23/I24 centar ±0,005 p.u.; BUS74 originalni generator red#34, izvorni VG=0,958 sa dodatnim bound ±0,010. Izbor BUS74 je **direktno informisan** I25 98%-load Q-offenderom i predstavlja prethodno plaćeno domensko znanje. Sve metode imaju **identičan 6D izvorni decision-space i jednake granice**, ali to i dalje NIJE nezavisna out-of-sample generalizacija. Ni jedan prethodni I23/24/25 solver output nije besplatna nova GA tačka.

## 2. Fiksirana zajednička fizička cena i pravi broj poziva

**Jedan fitness kandidat = tačno TRI stvarna AC simulator poziva** u redosledu `factor=0.98,1.00,1.02`. Izvršeno po metodi/seme **180 pravih AC** = **60 trostruko simuliranih kandidata**. Originalni NR solver v5.1.19, PF_ALG=1, PF_DC=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8, PF_MAX_IT=40. Za svaku konvergentnu AC fizičku tačku obavezno potpuno post-hoc source PG/QG svih 54 aktivna generatora, originalni bus VM svih 118, terminal apparent-rate MVA source pozitivnih RATE_A i kompleksni KCL. Kriterijumi isti I18–I26: P/Q/RATE_A=1e-3 (MW/MVAr/MVA), V=1e-5 p.u., KCL=1e-3 MVA. Q nije nasilno clamp-ovan tokom NR već pojedinačno naknadno proveravan.

Fitness identičan za svih 6 metoda: **aritmetička sredina tri originalna source ekonomska troška + 100000 × zbir tri source normalizovane fizičke povrede**. Zapis violation svakog režima je **0 samo ako je stvarno sve source-feasible** (ne kada je `runpf.success=True` bez Q provere). `robust_feasible=True` zahteva da **svaki** od tri stvarno plaćena AC scenarija zadovolji sve izvorne limite. Unapred je zabranjeno računanje partial 1/3 ili 2/3 scenario batch-a. Posle trošenja 180 AC objective može dati sentinel `1e12` kao nefizičku završnu poruku, nikako novo stvarno mrežno stanje ili UCB nagradu. Svaki realni simulator ulaz, čak i failure, broji se na `runpf` granici; **0 od 3240 realnih source AC poziva numerički je fail**, ali mnogi konvergentni kandidati nisu potpuno fizički izvodljivi.

## 3. Izmerena kompletna tabela bez cherry-pick-a

[Uspešan GitHub Actions CI #39663741753](https://github.com/owlCoder/gadapt/actions/runs/39663741753): unit testovi novog i starog GA credit-a + svih 18 realnih source PF eksperimenata. Svaka metoda i seed izvršili su tačno 180 pravih AC.

| Metod (isti source 6D PV box) | Seed 2026: robusno source-feasible od 60 | Seed 2027 | Seed 2028 | Ukupno robust-feasible od 180 trostrukih kandidata | Najbolja **samo ako all-three-feasible** srednja source cena |
|---|---:|---:|---:|---:|---:|
| GAdapt **legacy original** | 0 | 0 | 0 | 0 | **null** |
| GAdapt UCB + već postojeći objective credit | 0 | 0 | 0 | 0 | **null** |
| GAdapt UCB + već postojeći scalar source feasibility credit (worst scenario) | 0 | 0 | 0 | 0 | **null** |
| **GAdapt UCB + NOVI scenario-feasibility credit** | 0 | 0 | **1** | **1** | **131.314,640348** |
| SciPy differential evolution bez polish | 0 | 0 | 0 | 0 | **null** |
| Bounded Powell (jednaki 3 deterministička centrirana 60-batch pokušaja) | 0 | 0 | 0 | 0 | **null** |

**Jedini all-three source-feasible, genetski generisan kandidat** pronađen je u novom GAdapt reward modu **seed=2028, pri stvarnom AC pozivu #177** (59. trostruki source batch). Njegov stvarno evaluiran 6D generator VG setpoint:
`[BUS103 0.9898506009, BUS32 0.9700322306, BUS34 0.9865841207, BUS92 0.9944308972, BUS19 0.9643283682, BUS74 0.9601205052]` p.u.

Tačno tri source ekonomskih cost-a za fizikalno all-scenario-feasible vektor:
- **98% load:** `127755.89159703799`;
- **100% load:** `131196.63081166210`;
- **102% load:** `134991.39863551230`;
- **mean tri:** `131314.6403480708`.

Sva tri izvorna scenario Q individualna max prekoračenja su **0 MVAr**, source PG/V/positive RATE_A takođe zadovoljeno (iz samog `physics_118`), realni KCL maksimum po tri scenarija iznosi `2.02e-10 / 1.58e-10 / 1.57e-10 MVA`. Ne tvrditi globalni optimum niti da ovaj vektor rešava neizmerene drugačije mrežne promene!

**Sekundarni prvorazredni dokaz jakog ograničenja:** 98%-load režim je uporan: novi mehanizam **jedini** ima samo **1/180** source-feasible pojedinačni 98%-load kandidat, svih ostalih 5 metoda **0/180**. Na 100%-load, originalni legacy GAdapt 18/180, UCB objective 10/180, scalar feasibility 6/180, novi scenario 8/180, DE 1/180, bounded Powell **162/180**. Na 102%-load: legacy 68/180, UCB objective 65/180, scalar 64/180, novi 65/180, DE 2/180, Powell **156/180**. To ističe da **Powell može biti odličan na svakom pojedinačnom režimu, ali ti različiti feasible dizajni nisu bili ISTI fiksni VG vektor za sva 3 opterećenja**. Pri proveri scenario robusnosti ne sme se brojati suma po režimima kao 180 potpuno robusnih kandidata.

Statusi SciPy DE/Powell `success=False` su zbog dosezanja preregistrovanog maksimalnog budžeta/iteracija, NE dokaz fizičkog neuspeha njihovih pojedinačnih simulator poziva. Svaki metod ima jednako naplaćenih 540 stvarnih AC po 3 semena, ukupno 6×540 = **3240**. Post-budget objective requestovi: legacy i UCB GA po 2 po semenu, SciPy DE po 120 po semenu, Powell 0 — **nisu** fizički solver pozivi. Nema naknadnog punjenja budžeta novim slučajnim ishodima.

## 4. Zašto NE tvrdimo da je napravljen doktoratski dokaz

- **Samo jedan uspešan robust-feasible kandidat** u ukupno 180 novi-mode trostrukih fitness pokušaja i **1/3 stohastička semena**, svih drugih metoda 0/3. Ovo nije dovoljno za statističku ili robusnu algoritamsku tvrdnju; slučajnost mutacije, selekcija, razlika u putanjama RNG i činjenica da samo neki offspring dobijaju operator credit mogu u potpunosti uticati na rezultat. **Nije dokazano da je baš novi reward uzročno stvorio taj kandidat.** Vreme do prvog potpuno source-feasible u poslednjem uspešnom run-u (AC #177) takođe znači da je event vrlo redak.
- **Uski, prethodno informisani source problem:** fizikalni PV kontrolni skup i 6D granice su izabrani nakon ranijih stvarnih I19–I25 merenja, uključujući fizikalnu feasible tačku u I23, a BUS74 eksplicitno po I25 Q stres dijagnostici. Nije direktan transfer na nekog drugog infrastruktura/domen, niti field validacija.
- **Ovo je mutator-credit, ne nova constraint selection:** `cost_function`, stari elitizam i turnirska/roulette selekcija nisu promenjeni za scenario feasibility. Reward utiče samo na izbor jednog od postojećih decision-variable mutatora, a izvorna physics i score su zajednički za sve.
- **Naučna originalnost nepoznata:** UCB/bandit AOS, feasibility-first, operator credit, reward preko više constraint kršenja su dobro poznate klase literature, uključujući Duboka RL rešenja. Bibliografija [I26](ITERATION26_REPORT_SR.md). Ne tvrditi da je nova kombinacija automatski publikabilna. Nema nezavisnog elektrotehničkog `Ybus` implementacionog solvera, iako je source AC KCL rezidual ponovo izračunat.
- **Nema formalne garancije scenario robusnosti:** scenario faktori su samo tri unapred izabrana veštačka fiksna skalarna množioca PD+QD. Ne dokazuje se AC ograničenje za bilo koje nepoznato opterećenje, mrežni kvar, stvarni industrijski sistem, niti preostali termički stres. Globalni puni IEEE118 AC-OPF sa slobodnim dispatch-om je **drugi problem**.

## 5. Reproduktivnost i naredna direktna GAdapt studija

- [I27 pre-registracija](ITERATION27_PROTOCOL.md)
- [I26 izmena stvarnog algoritma, protokol i literatura](ITERATION26_REPORT_SR.md)
- [Kod IEEE118 6D source / 3 realna scenarija × pravi GAdapt, UCB, DE, Powell](iteration27_real_scenario_credit_benchmark.py)
- [Jedinični testovi pravog triple-AC budgeta i šest originalnih PG/VG identiteta](test_iteration27_real_scenario_credit_benchmark.py)
- [Core GA scenario-feasibility regresioni testovi](../tests/test_scenario_feasibility_credit.py)
- [Sirovi CSV svih 18 fizikalno naplaćenih eksperimenta](results/ieee118_iteration27_3load_scenario_GAdapt_ablation_20261021.csv)
- [Sirovi JSON sa 18 realnih run-ova, nagradama operatora i punim robust-feasible best source evidence](results/ieee118_iteration27_3load_scenario_GAdapt_ablation_20261021.json)
- [CI 3240 stvarnih originalnih AC #39663741753](https://github.com/owlCoder/gadapt/actions/runs/39663741753)
- [I26 3-Python testovi core GA #39662796544](https://github.com/owlCoder/gadapt/actions/runs/39662796544)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v tests.test_scenario_feasibility_credit research.test_iteration27_real_scenario_credit_benchmark
python -m research.iteration27_real_scenario_credit_benchmark --seeds 2026 2027 2028 --budget 180 --population 12 --json /tmp/i27.json --csv /tmp/i27.csv
```

### Sledeći korak koji ZAISTA testira mogući doktoratski doprinos

Pre dodatnih realnih AC, **zamrznuti više različitih fizičkih mrežnih scenarija** (izmenjene lokalne Q/potrošnje, ne samo iste uniformne load faktore), i izvesti veću, uparenu studiju **legacy GAdapt vs objective-UCB vs scalar-UCB vs scenario-UCB uz istu domensku fizičku kontrolnu reprezentaciju** plus lokalni Powell i DE. Pre p-vrednosti verifikovati da za neki deo tih referentnih problema zaista postoji source-feasible **zajednička** 3-scenario tačka. Zatim ablation (coverage vs max vs mean Q, N=3/N=5, ukloniti 6. kontrolu), bukvalno po istom pravom AC budžetu, sa neutralnim rezultatom ako novi credit ne radi. Paralelno sistematski proveriti literaturu za preciznu originalnost. Do tada **postoji kod i prva stvarna pozitivna naznaka**, ali **NEMA dokaza naučnog doprinosa koji je spreman za disertaciju**.
