**REVISE pre zamrzavanja.** Ništa nisam menjao niti čitao I56 test rezultate. Pregledao sam [predlog I58](/Users/danijel/Desktop/gadapt/research/ITERATION58_PROPOSAL_SR.md), protokole, kod i patch v4.

1. **Blokirajuće greške i razjašnjenja**

- **Izbor tehnike:** unapred zamrznut izbor prema I56 testu ne kontaminira nezavisan I58 test. Međutim, I56 tada služi i za izbor konfiguracije; njena pobeda tamo nije nezavisna potvrda superiornosti. „Veze → FR“ nije potpuno pravilo ako su izjednačeni samo AP/EC. Najčistije je sada fiksirati FR.
- **Početna populacija:** pretpostavka da patch nužno menja inicijalizaciju nije tačna. Kod generiše populaciju pre CHT evaluacije; mala provera patch-a u memoriji dala je identične prve 32 evaluirane jedinke za G0/AP/FR/EC. Ipak, zahtevati aserciju u konačnom drajveru, sejati oba RNG-a i koristiti zasebne procese.
- **Biblioteka ≠ I56 konfiguracija:** [v4](/Users/danijel/Desktop/gadapt/research/patches/constraint_api.patch:358) koristi medijanu apsolutnih početnih ciljeva, arctan skalar, ograničenu AP težinu i odsecanje kaznenog skalara. Posebno, ε prati **generacije**, dok I56 prati potrošene evaluacije. Sa I56 postavkom `number_of_generations=10**9`, ε praktično neće opasti do nule. „Iste konstante“ zato nije dovoljan opis prenosa.
- **Instance:** `case24_ieee_rts` ima 33 generatora na **11 sabirnica**: postojećih 39 koordinata uključuje redundantne naponske komande. Jedna VG kontrola po sabirnici daje **17 kontrola**. `case300` ima 411 pozitivnih limita, ali svi su 9900 MVA; opravdano je samo opisna provera skale. R=17 ograničava tvrdnju na tu pretpostavljenu diskretizaciju.
- **Reference/provera:** „sve metode“ trenutno izostavlja random. Ponovni poziv iste evaluacione funkcije nije nezavisna implementaciona provera. Proveravati obe GAdapt grane, vraćena rešenja i rešenja koja određuju cilj/T.
- **Budžet:** 11,7 miliona + 2,88 miliona jeste tačno za napisanu šemu; 12 CPU-sati nije opravdano prenošenjem prosečne cene na case300. Petnaest semena ne garantuje dovoljnu snagu.

2. **Predloženi tekst za zamrzavanje**

> I58 proverava integrisani GAdapt v4 sa unapred fiksiranim `constraint_handling="feasibility_rules"` (G1), prema istom buildu sa `constraint_handling=None` i korisničkim skalarom f+1000V (G0). Izbor ne zavisi od I56/I57 ishoda. Ostala podešavanja su jednaka, sa podrazumevanom populacijom 32, bez sondiranja i imigracije. Arhiviraju se verzije, kompletna podešavanja i SHA-256 manifest.
>
> Primarni skup čine case30, case39 i case24_ieee_rts; case300 je opisni dodatak. R=17; scenariji su tačno (0,95;301), (1,00;302), (1,05;303), spread=0,1. Model nasleđuje I56, uz jednu VG kontrolu po generatorskoj sabirnici, primenjenu svim generatorima na njoj. OPF neuspeh znači izuzimanje bez zamene, pre optimizacionih pokretanja. Bez preostalog scenarija neke primarne mreže nema primarnog zaključivanja.
>
> Kontekst su CMAwM/FR, DE/FR i random, prema zamrznutim I57 podešavanjima. Formula semena je 10⁷p+10⁵i+10³R+100j+s: mreže navedenim redom i=0..3; scenariji j=0..2; test p=6,s=1..15; reference p=7,s=1,2. Seju se svi RNG-i; G0/G1 početne populacije moraju biti identične.
>
> Svaka metoda izvršava jednu putanju od 10.000 stvarnih PF poziva; prvih 3000 određuje primarni ishod. Broje se inicijalizacija, ponavljanja i neuspešni PF; nema prekida pri dostizanju cilja. Primene se I56 pravila grešaka, ponavljanja, potpunih jedinica i osetljivosti.
>
> Reference obuhvataju svih pet metoda, po 30.000 poziva i dva nezavisna semena. L* i cilj nasleđuju I56 formulu i fallback na izvodljivost. Reference se heširaju pre testiranja.
>
> T=min(prvi poziv dostizanja/3000,1), uz T=1 za nedostizanje. θ je prosek razlika T(G1)−T(G0), jednako po mrežama i preostalim scenarijima. Upareni vektori resampliraju se unutar mreža×scenario: 20.000 bootstrap uzoraka, seme 58, percentilni 95% interval. H58: θ<0; podržana ako je ceo interval ispod nule. Ostali ishodi su opisni.
>
> Nezavisno implementiran proverivač rekonstruiše kontrole, granice, gubitke i sve prekršaje. Drugi istraživač ponavlja zamrznuti paket u čistom okruženju. Planirani maksimum: 9 miliona testnih + 3,6 miliona referentnih PF poziva, bez provera i ponavljanja.

3. **Domet H58**

H58 podržava tvrdnju: **„Integrisana FR opcija smanjuje ograničeno vreme do evaluiranog izvodljivog cilja prema kazni 1000 na ovom skupu.“** To jeste dokaz poboljšanja pretrage stvarne biblioteke. Ne dokazuje opštu superiornost, industrijsku korist, novu metodu niti kvalitet vraćenog rešenja; poslednje zahteva zasebnu uspešnu proveru izlaza.