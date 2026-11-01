# Posle I36 — metodološki GO/NO-GO, literaturna mapa i kandidat za nezavisni infrastrukturni test

**Datum 22.10.2026. Status: istraživački audit, NE preregistracija i NE novi eksperiment.** Svi brojevi ispod su iz postojećih arhiviranih I34–I36 izveštaja; eksterni radovi su provereni na navedenim izvornim stranicama. Tokom pisanja ovog dokumenta **nisu izvršene nove mrežne ili AC evaluacije**. Upstream `bpzoran/gadapt` je van opsega.

## 1. Falsifikacija trenutno najjače naučne tvrdnje

| Studie / stvarna funkcija | New core UCB >0 source / scenario-feasible semena | Legacy fixed | Primarni exact paired two-sided p | Dokazani pozivi |
|---|---:|---:|---:|---:|
| [I34 GÉANT](ITERATION34_REPORT_SR.md) — hipotetički izvorno NEPOSTOJEĆI cap po scenariju, odvojene recourse kupovine | 12/12 | 11/12 | **1** | **7.126** stvarnih domen routing evaluacija, 0 AC |
| [I35 IEEE118](ITERATION35_REPORT_SR.md) — originalni PYPOWER source AC, 3 sintetička scenarija | 10/12 | 10/12 | **1** | **8.587** stvarnih AC |
| [I36 IEEE14](ITERATION36_REPORT_SR.md) — originalni PYPOWER source AC, 3 sintetička scenarija | 12/12 | 12/12 | **1** | **8.585** stvarnih AC |

**Zaključak:** tri primarna testa sa istim first-failure selekcionim evaluatorom ne podržavaju tvrdnju o superiornosti I34 `censored_verified_per_cost`+UCB nad originalnim `legacy_fixed`. To nije dokaz njihove statističke ekvivalentnosti; male n=12 veličine, plafonski efekat IEEE14 i poznate mreže ograničavaju snagu generalizacije. Ne praviti pseudoreplikacije sabiranjem unutar-semenih kandidata ili automatskim pooling-om različitih domena.

**Mehanizam koji jeste dokazan kodom**: event validation proverava stvarni brojač, scenario labele, finite violation, konzistentan status; stvarno potpuno proverena 3-scenario feasibility daje credit 1/3, izmerena povreda daje 0, numerički unknown/nedostajuće merenje ne dobija lažno pozitivan signal. To je korisno data-integrity/inženjersko pravilo, **nije** do sada potvrđena nova metoda, niti adaptivno optimalna raspodela budžeta. U navedenom N=3 protokolu nagrada je za svaki potpuno uspešan kandidat ista 1/3; jeftina neuspešna odbacivanja imaju 0. Uspeh potom zavisi i od crossover-a, selekcije i roditeljskih kontrola — operator-level counterfactual nije identifikovan.

**Razdvojiti dva efekta**: (A) običan `first-fail screening` menja broj dostupnih kandidata i fitness rangiranje pri istom realnom budžetu; (B) izbor mutacionog operatora pomoću nove reward politike uz **isti** screening. Pozitivni full-vs-stop signali I31–I33 pripadaju efektu (A) ili njegovoj kombinaciji sa scoring razlikom; neutralni primarni I34–I36 direktno pobijaju dosadašnju pozitivnu tvrdnju za (B).

## 2. Verifikovana mapa prethodne naučne literature

| Tema i provereni izvor | Šta je već poznato (ne smemo prisvajati) | Naša moguća razlika / preostali dug |
|---|---|---|
| Deb, *An efficient constraint handling method for genetic algorithms* (2000), DOI [10.1016/S0045-7825(99)00389-8](https://doi.org/10.1016/S0045-7825(99)00389-8) | GA feasibility-first / constraint handling ima dugu literaturu | Naše eksplicitno fizičko flagovanje/validacija događaja je implementacija, ne otkriće prioriteta izvodljivosti |
| Li, Fialho, Kwong, Zhang, *Adaptive operator selection with bandits for a multiobjective evolutionary algorithm based on decomposition* (2014; online 2013), DOI [10.1109/TEVC.2013.2239648](https://doi.org/10.1109/TEVC.2013.2239648) | Bandit/UCB-like izbor operatora po zabeleženoj performance već postoji | Naš UCB bez ozbiljnog causal/strong-bandit baselina nema dokazanu konceptualnu novinu |
| Sankary & Ostfeld, *Stochastic Scenario Evaluation in Evolutionary Algorithms Used for Robust Scenario-Based Optimization* (2018), DOI [10.1002/2017WR022068](https://doi.org/10.1002/2017WR022068) | Upravljanje brojem scenario simulacija i tradeoff evaluacionog budžeta u infrastrukturi već su razvijani | I29 deterministički first-failure nije isti njihov stohastički resampling, ali nije dovoljno razlikovanje samo „ne raditi sve scenarije” |
| Guo i saradnici, *DRL-AEOSF: A deep reinforcement learning-assisted evolutionary operator selection framework for constrained optimization problems* (2026), DOI [10.1016/j.swevo.2026.102453](https://doi.org/10.1016/j.swevo.2026.102453) | AOS state-action-reward koji uključuje feasibility stanje eksplicitno postoji | Naš jednostavniji UCB treba formalno i empirijski uporediti sa constraint-aware AOS klasom, ne sugerisati prvenstvo |
| Bachoc i saradnici, *Online Budget Allocation with Censored Semi-Bandit Feedback* (arXiv preprint 2025, verzija 2), [arXiv:2508.05844](https://arxiv.org/abs/2508.05844) | Cenzurisana observabilnost nagrada i cost/budget-aware učenje iz nepotpunih povratnih informacija već su predmet formalne teorije | Njihov model nije isto što i our deterministic first-fail fizički verifier; potrebno egzaktno definisati identifiability i missing-not-at-random mehanizam pre originalne tvrdnje |

**Opseg ove mape je preliminaran**: potvrđeni bibliografski identiteti i sažeci/odabrani otvoreni delovi, **ne sistematska, iscrpna full-text pretraga** niti prior-art garancija. Sledeće je čitanje punih dokaza/koda, bibliometrijska pretraga IEEE/ACM/Scopus i algoritamski „istovetno/različito” pseudokod.

## 3. GO/NO-GO nakon 3 empirijske provere

- **NO-GO:** tvrditi da je `censored_verified_per_cost` nova superiorna AOS naučna metoda ili ponavljati hiperparametarske probe na istim poznatim mrežama do prvog pozitivnog rezultata.
- **GO (inženjerski dokaz):** sačuvati opt-in core sa proverom naplaćenih poziva, trima scenarijima, fail-closed feedback-om i surovim negativnim rezultatima. To je realan software research artefakt.
- **CONDITIONAL GO (nauka):** definisati jednu originalniju, falsifikabilnu tvrdnju o *certified partial-feedback sequential robust evaluation* ili operator-level counterfactual attribution **samo ako** literaturni test pokaže stvaran gap, uz jake baseline-ove, formalnu tvrdnju i nezavisan eksperiment.
- **STOP pravilo:** ako izvorni fizički model nije dobro definisan, ako jake metode već daju isti rezultat, ili ako nema proverljive razlike prema literaturi, rezultate objaviti kao evaluacioni/negativni rad, a ne kao potvrdu disertacijske metodske novine.

## 4. Konkretan kandidat nezavisne mreže: SNDlib `nobel-germany`

**Izvorno provereno na https://sndlib.put.poznan.pl/nobel-germany.overview.action**: originalno javni SNDlib opis sa **17 čvorova, 26 linkova, 121 default demand**. Moguće je preuzeti izvorni native [topology/demand model](https://sndlib.put.poznan.pl/download/sndlib-networks-native/nobel-germany.txt) i **288 petominutnih matrica (jedan dan)**, **28 dnevnih matrica (mesec)** i **14 mesečnih matrica (godina)**. [Izvorni Readme](https://sndlib.put.poznan.pl/download/nobel-germany-rm.txt) navodi da su saobraćajne vrednosti izvedene iz **DFN accounting podataka 2004–2005**, agregiranih radi poverljivosti i pretvorenih u Mbit/s, da su matrice **usmerene** i da podaci mogu sadržati greške. To nije savremeni live operativni sistem, niti garancija industrijske validacije.

Izvorna native mreža eksplicitno sadrži za svaki link pre-installed capacity/cost, routing/setup cost i parove **source module_capacity/module_cost**. Stoga možemo umesto GÉANT izmišljenog 145.000 cap-a ispitati **jedan zajednički trajni modularni kapacitetni plan** kroz više stvarno izvornih vremenskih matrica, pod verifikovanim source kapacitetima/cenama. Buduća odluka da se dodatno uvedu OSPF-like weight, routing model i eksterni investment cap **bila bi NAŠE modelovanje, ne automatski source SNDlib default zadatak**; svako odstupanje mora biti eksplicitno označeno.

**Predlog odvojivog modela za naučnu proveru (još NE zamrznut):** jedno statičko `y_e` (izvorna opcija module capacity) po linku, a ne nova kupovina za svaki scenario; routing odluka `x` specificirana nezavisno od opservacija; zahtev iz odabranog vremenskog koraka `t` prolazi samo ako source-flow/capacity i definisani domenski QoS uslovi važe. Minimizovati ukupnu jedinstvenu source investicionu cenu, prikazati source fail-ove odvojeno od solver-unknown-a. Ako se `y_e` računa adaptivno iz posmatranih vremena, eksplicitno isključiti bilo kakav *per-scenario recourse* i dokazati da early-failure sertifikat za delimična merenja ostaje logički validan. Routing/capacity model neće se predstavljati kao izvorni SNDlib MIP bez posebne provere.

### I37 pripremni „data/model gate” — bez izvršavanja optimizatora

1. Preuzeti originalni SNDlib native opis i arhivu petominutnih usmerenih demand matrica, zabeležiti URL, SHA256, vreme arhive i licencu. Potvrditi parsiranjem 17/26, source link cost/capacity, ispravnost jedinica i broj originalnih 288 vremenskih matrica; prijaviti nedostajuće/negativne/duplikat zahteve i nepodudaranja pre modelovanja.
2. Pre gledanja **rezultata algoritama** unapred odrediti blokovski split vremenskih intervala (ne slučajno mešanje korelisanih petominutnih koraka), nemogućnost optimizacije na holdout-u i identičnu finalnu proveru svih metoda. Precizno definisati smisao nezavisnosti: nova topologija i izvorna vremenska saobraćajna serija, ali arhivski i agregiran history dataset.
3. Modelovati **jedan zajednički kapacitetni plan**, bez hipotetičkog cap-a izabranog posthoc. Odlučiti da li je optimizator promenljive `(x,y)` ili je minimalni legalni source `y` određen iz `x` i svih trening matrica. Sva `source/modified` odstupanja dokumentovati. Dodati mali reproduktibilni ručni primer za dokaz logičke bezbednosti sequential failure certifikata.
4. Dizajnirati jake kontrole: (a) originalni GAdapt fixed-screen, (b) novi UCB i uniform istog reward-a, (c) jasan greedy shortest-path+source-capacity baseline, (d) constraint-aware/cost-aware AOS baseline, (e) exact MIP ili dostupna jaka optimizaciona referenca kad model dozvoljava. Isti fair domain-cost budget, nezavisna računarska semena, counter stvarnih izvršenih network/routing poziva i bez posthoc besplatne dopune.
5. **Tek zatim** pripremiti i komitovati I37 puni PREREGISTERED PROTOCOL (n seedova, primarni continuous/binary ishod, korekcija svih testova, budget, failure handling, datumski split, zaustavljanje). Novu solver seriju pokrenuti jednom nakon zelenog zero-domain preflight-a; arhivirati kompletan stdout i JSON/CSV na `main`, bez repeat-until-positive.

**Naučno upozorenje:** odvojene prednosti jednostavnog screeninga i nove AOS selekcije moraju ostati dva nezavisna unapred određena kontrasta. Ako je cilj izvorni min-cost robust trajni plan, binarni "našli smo makar jedan ispod proizvoljne cene" više ne sme biti primarni ishod bez izvornog, unapred nezavisno opravdanog budžetskog kriterijuma.

## 5. Kratka beleška za mentora

„Pravi GAdapt core dobio je strogu obradu stvarno izmerenog parcijalnog scenario-feedback-a i reproduktibilna fizička i telekom testiranja. Na tri preregistrovane studije sa istim first-failure evaluatorom nov UCB signal **nije** nadmašio legacy na primarnom egzaktno uparenom kriterijumu (I34/I35/I36 p=1). Ovo je naučno važan neutralan/negativan nalaz i radi istraživačkog integriteta neću ga prikazati kao originalnu metodu. Predlažem odluku: formalizovati novost u verified sequential robust evaluation uz dokaz/strong baselines, ili napraviti nezavisnu source SNDlib nobel-germany rekonstrukciju zajedničkog kapacitetnog plana sa pravim vremenskim matricama; tek nakon toga novi preregistrovani eksperiment.” 
