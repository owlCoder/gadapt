# Iteracija 25 — prvih 10 pravih IEEE118 AC holdout provera na veštački izmenjenim opterećenjima ±2%

**Datum:** 21.10.2026. **Repo:** owlCoder/gadapt:main. **Status:** pre-registrirano, uspešno izvršeno **tačno 10 NOVIH stvarnih native PYPOWER IEEE118 AC NR proračuna**, sve konvergencije ispravne, **0/5 source-feasible prethodnih odluka na 98% load**, **2/5 na 102% load**. Protokol i originalna istorija prethodnih I23/I24 5 source-feasible kandidata zamrznuti su **pre** novih AC poziva. **Nije pokrenut niti promenjen originalni GAdapt ili drugi optimizator**. Nema statističkog zaključka o robustnoj superiornosti bilo kog algoritma.

## 1. Test koji razlikuje izvorno kalibrisani uspeh od robusnosti

[Preregistrovani protokol I25](ITERATION25_PROTOCOL.md), commit `efcd2b7fc8b5ea9897b341757d6429b53256f94f`, prethodio je novim fizičkim evaluacijama. Prehodni I24 je za **1.152 realna AC** pomoću stvarnog originalnog GAdapt-a, DE, random i bounded Powell-a u kalibrisanom petodimenzionalnom IEEE118 PV podskupu pronašao izvorno source-izvodljive tačke (sva četiri metoda 3/3). Izbor VG upravljačkih resursa i lokalnog centra baziran je na izvornim I19–I23 AC merenjima — zato taj raniji rezultat **nije nezavisna generalizacija**.

Da proverimo zadržavaju li source-feasible odluke fizičke limite kada se **opterećenje malo promeni**, preuzeto je bez ponovnog AC:
- jedna prethodna deterministička izvorno feasible tačka **I23 α=0,8**, originalni cost 131.198,797575;
- po **jedan prethodno fizički feasible kandidat najniže ekonomske cene** iz 3 seed run-a za GAdapt 131.195,131546 (seed 2026), DE 131.194,777680 (seed 2027), random 131.196,562290 (seed 2028), bounded Powell 131.193,636506 (seed 2026). Ovo pravilo je fiksirano u protokolu **pre** stres testova; izbor najboljeg već je optimizovan na **izvornom load 100%** i nije originalno nezavisan.

Svaka od tih pet originalnih source-feasible fiksnih 5-VG kontrolnih odluka ponovo je stvarno simulirana za **dva izvorno različita VEŠTAČKA load režima**:
- originalni `case118` PD i QD *svih 118 sabirnica* pomnoženi sa **0,98**;
- isti izvorni PD i QD pomnoženi sa **1,02**.

Ispitani modeli su zato **stres-varijante originalnog javnog IEEE118**, ne originalni IEEE118 i ne realni SCADA radni podaci. Svi generatori originalnog modela drže prethodni originalni PG (osim neophodnog fizičkog slack PG), sve granice generator P/Q, izvorni rated RATE_A oba kraja, bus VMIN/VMAX, topologija, šant i originalni troškovi ostali su neizmenjeni. Svaki kandidatski setpoint potpuno **fiksan** — nijednom nije dozvoljeno podešavanje za stres scenario. Standardni `runpf`, AC Newton–Raphson, `ENFORCE_Q_LIMS=0`, sa naknadnim obaveznim pojedinačnim proverama PG/QG/VM/rated apparent-MVA/KCL na svakom novom stres modelu, uključujući sve originalne izvorne reference granica.

## 2. SVA realna fizička stanja, bez filtriranja

[Zelen GitHub Actions CI #39660714312](https://github.com/owlCoder/gadapt/actions/runs/39660714312): prošli svi unit testovi i svih 10 realnih AC. **0/10 fizičkih AC numeričkih neuspeha**, svi KCL ponovo izračunati; puna izvodljivost proverena nezavisno od uspeha solvera.

| Zamrznuta kontrolna odluka (prethodno svi feasible @100%) | Izvorni 100% source-feasible cost | Load 98%: originalni Q offenderi / ukupno excess MVAr | Load 102%: originalni Q offenderi / excess MVAr | Load 102% source-feasible economic cost samo ako source-feasible |
|---|---:|---|---|---:|
| I23 α=0,8 deterministic | 131.198,797575 | 2 / **2,284055** (BUS74, BUS36) | **0 / 0,000000** | **134.993,698462** |
| Originalni GAdapt I24 najbolji | 131.195,131546 | 3 / **2,446491** (BUS74, BUS105, BUS36) | 1 / **0,221845** (BUS92) | **null** |
| DE I24 najbolji | 131.194,777680 | 2 / **2,092576** (BUS74, BUS105) | 1 / **0,761144** (BUS92) | **null** |
| Uniform random I24 najbolji | 131.196,562290 | 1 / **1,551683** (BUS74) | **0 / 0,000000** | **134.991,355175** |
| Bounded Powell I24 najbolji | 131.193,636506 | 3 / **4,538300** (BUS15, BUS74, BUS105) | 1 / **0,947433** (BUS92) | **null** |

**Puna source-feasibility: 0/5 pri 98% opterećenju, 2/5 pri 102%.** U svim deset numerički konvergentnih scenarija **0 originalnih PG prekoračenja, 0 bus V prekoračenja i 0 pozitivno originalno rated RATE_A prekoračenih grana**. Izvori neizvodljivosti su **pojedinačni QMIN/QMAX generatora** — fizički Q-limit se ne nameće u numeričkom PF, te njegovim prekršajem kandidat jasno postaje *infeasible*, iako PF konvergira. Source ekonomska cena na stresiranom load-u prijavljena je kao fizički prihvatljiva **samo** za dve uspešne 102%-load odluke; za ostalih osam originalni feasiblity-cost je eksplicitno JSON `null`. Nijednom od ostalih numerički konvergentnih kandidata nije pridodat izmišljeni izvodljiv trošak.

**BUS74 je uporan pri -2% opterećenju:** u svih pet testova ima individualno izvorno Q prekoračenje približno **1,552 MVAr**, nepoznato u užoj prethodnoj kalibrisanoj kontrolnoj reprezentaciji. Pri +2% glavni neuspeh GAdapt/DE/Powell prethodno najboljih setpointova je **BUS92** sa 0,222 / 0,761 / 0,947 MVAr Q exced. Jedan raniji random kandidat i stari I23 α0,8 zadržali su sve izvorne P/Q/V/rated-thermal/KCL zahteve i pri +2%, što pokazuje da **najniži izvorni economic cost na originalnom 100%-load nije nužno najrobusnija odluka**.

## 3. Šta ovaj nalaz sme i ne sme da znači za doktorat

**Dozvoljeni zaključak:** uski izvorno PG-fiksni, pet-VG PV podskup prethodno source-feasible odluka može biti vrlo osetljiv na male zajedničke promene **PD/QD ±2%**. Prva stvarna predefinisana **promena režima** identifikovala je BUS74 Q ograničenje koje nijedan od najnižih ekonomskih kandidata nije mogao da zadovolji na 98% load, bez novih reaktivnih kontrola i scenario-aware repair.

**Nedozvoljeni zaključci:**
- Nije dokazano da **puni originalni IEEE118 AC-OPF** postaje neizvodljiv pod stresom. Izvodljivost drugih VG/PG/Q kontrola na veštački stres modelu nije istražena. Nije dokazano da lokalna promena BUS74 VG rešava problem.
- Nije robustni eksperiment nad 3+ mnogo nepristrasnih scenarija, niti metodološki fer poređenje **GAdapt vs random pri stres load-u**. Samo **po jedan, unapred izabran prethodni najbolji source-vektor** testiran je bez nove optimizacije. Činjenica da prethodni random source vektor preživi +2%, a prethodni najbolji GAdapt ne, nije statistička metoda superiornost.
- Originalni GAdapt NIJE unapređen, nijedan novi operator nije implementiran, i nije utvrđena originalnost adaptation methoda. Robust AC-OPF, sensitivity-guided repair i operator adaptation su postojeće oblasti literature koje treba proveriti pre hipoteze o doktoratskoj inovaciji.
- Nije dokazano da je izvorni puni OPF I16 ispod jednog ili oba izmenjena scenarija feasible niti je izvršen puni `runopf` na stres mreži — samo 10 pravih PF, 0 dodatnih AC OPF poziva.

## 4. Šta je sledeći razuman korak

Za informisan naučni originalni GAdapt mehanizam treba testirati **scenario-aware feasibility** na zamrznutom skupu nezavisnih mrežnih scenarija i faktorisati evaluator sa **računanjem realnih AC poziva po svakom scenariju**: na primer, jedan kandidatski VG vektor u 3 source load režima `0,98, 1,00, 1,02` je **3 stvarna AC poziva**, ne “1” niti besplatna dodatna provera. Zatim definisati fer, preregistrovani benchmark nad istim originalnim generator PG/Q, bus V i RATE_A uslovima, posebno porediti originalni GAdapt i strong local/DE baselines; tek nakon pregleda literature predlagati pravi adaptivni mechanism sa ablation.

Ako budući pokusi promene broj kontrolnih PV generatora (npr. uključenje BUS74), takva promena mora biti dodeljena SVIM metodama ili tretirana kao odvojeno preregistrovano poređenje reprezentacija, jer je I24 već pokazao da izbor resursa može biti važniji od samog GA algoritma.

## 5. Dokazi i ponavljanje

- [Pre-registracija I25](ITERATION25_PROTOCOL.md)
- [Deterministička desetostruka IEEE118 load±2% source AC analiza](iteration25_ieee118_stress_holdout.py)
- [Preflight autentičnih prethodnih source-feasible vektora bez AC](test_iteration25_ieee118_stress_holdout.py)
- [Sirovi CSV svih 10 native AC proračuna](results/ieee118_iteration25_5_prior_feasible_PV_2percent_stress_10_AC_20261021.csv)
- [Sirovi JSON sa svih 10 P/Q/V/thermal/KCL i source fizičkih dijagnostika](results/ieee118_iteration25_5_prior_feasible_PV_2percent_stress_10_AC_20261021.json)
- [Zelen CI #39660714312](https://github.com/owlCoder/gadapt/actions/runs/39660714312)

```bash
python -m pip install -e . 'pypower==5.1.19' 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
python -m unittest -v research.test_iteration25_ieee118_stress_holdout
python -m research.iteration25_ieee118_stress_holdout --json /tmp/i25.json --csv /tmp/i25.csv
```

**Upozorenje:** ovo su javne IEEE118 simulacije sa namerno **veštački skaliranim opterećenjima**, ne merenja, verifikacija, sertifikacija ili dobijeni pogonski recept za stvarne mreže.
