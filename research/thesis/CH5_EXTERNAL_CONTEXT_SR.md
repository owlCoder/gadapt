# Poglavlje 5. Spoljni kontekst: GAdapt naspram CMA-ES sa marginom, DE i nasumične pretrage

*Nacrt, 24. oktobar 2026, posle studije I57 (protokol zamrznut pre ijednog I56 test rezultata; izveštaj ITERATION57_REPORT_SR.md; nezavisna ponovna analiza Codex 049). Studija je opisna i ne nosi konfirmatorne tvrdnje o superiornosti ili ekvivalenciji.*

## 5.1 Zašto je potrebno spoljašnje poređenje

Prethodno poglavlje ispituje odnos rukovanja ograničenjima i samoadaptacije unutar GAdapt-a. Takav eksperiment može pokazati da jedna politika mutacije radi drugačije pod različitim tehnikama za ograničenja, ali ne određuje praktičan položaj biblioteke prema drugim optimizatorima. Poboljšanje unutar jednog algoritma može ostati malo u odnosu na razliku između algoritama. Studija I57 zato odgovara na drugo istraživačko pitanje: gde se GAdapt nalazi na istom diskretnom ORPD-u kada se uporedi sa spoljnim metodama pri jednakom budžetu simulacija?

Ovo pitanje je posebno važno zbog ranije dijagnostike. U I47, na glatkom AC ekonomskom dispečingu, relativni jaz CMA-ES prema najboljem zabeleženom penalizovanom skoru bio je manji za tri do pet redova veličine na četiri od pet slučajeva. I53 je pokazao da konkretna intervencija sa oracle korakom mutacije bez uniformnog reseta zatvara samo 0–29% razlike na logaritamskoj skali jaza na četiri odlučujuća slučaja. Promena problema na diskretni ORPD zato sama po sebi ne opravdava očekivanje da je zaostatak uklonjen.

I57 daje spoljašnji kontekst za rezultate I56. Njegova svrha je da ograniči tvrdnje disertacije na ono što podaci podržavaju: proučavanje i unapređenje GAdapt-a ne predstavlja dokaz njegove konkurentnosti sa CMA-ES.

## 5.2 Instance, ciljevi i unapred određen obim

Preuzeti su model, ograničenja i test scenariji iz poglavlja 3: case14, case57 i case118, sa 9, 27 i 77 kontrola, i rezolucijama R ∈ {9, 17, 33}. Test scenariji imaju zajedničke faktore opterećenja 0,90, 1,00, 1,10 i 1,15, uz unapred sejano odstupanje po sabirnicama u opsegu ±10%. Dva scenarija case57, sa faktorima 1,10 i 1,15, ostaju izuzeta zbog neuspelog pripremnog kontinualnog OPF-a. Ukupno je ostalo 30 instanci i devet blokova mreža × R.

Cilj je nepromenjen u odnosu na I56:

\[
V=0,\qquad f\leq 1,01L^*+0,01\ \mathrm{MW},
\]

gde je \(f\) gubitak aktivne snage, a \(L^*\) najbolji izvodljiv gubitak iz zasebnih referentnih pokretanja. Reference potiču iz osam GAdapt AD-N pokretanja po instanci, po dva semena za svaku od četiri tehnike za ograničenja, sa po 30.000 poziva. One nisu dokazani optimumi. Na četiri instance × R bez izvodljive reference cilj je, prema unapred zadatom pravilu, samo izvodljivost.

Važna je razlika između predloga i zamrznutog protokola. Predlog je razmatrao izbor najbolje GAdapt grane prema I56 rezultatima. Konačni protokol to ne koristi: unapred su određene AD-N/SP i AD-N/FR. Nisu uključeni ε-ograničenje, fiksne politike mutacije, L-SHADE ni jDE. I57 zato opisuje sedam određenih putanja pretrage, bez naknadnog izbora konfiguracija prema test ishodima.

## 5.3 Metodi i podešavanja

Sve metode koriste iste sirove ishode evaluacije. Ukupan prekršaj je \(V=\sum_k\max(0,c_k-10^{-6})\), a izvodljivost zahteva \(V=0\). Statička kazna, SP, daje skalar

\[
P=f+1000V.
\]

Pravila izvodljivosti, FR, izražena su skalarom

\[
m=
\begin{cases}
1+f/(f+f_{\mathrm{ref}}), & V=0,\\
2+V/(1+V), & V>0,\\
3, & \text{neuspeo proračun}.
\end{cases}
\]

Ovde je \(f_{\mathrm{ref}}>0\) gubitak kontinualnog OPF-a scenarija, različit od reference \(L^*\) za cilj. FR daje prednost izvodljivosti, zatim manjem cilju među izvodljivim, odnosno manjem prekršaju među neizvodljivim rešenjima, prema Deb-ovim pravilima (Deb, 2000, DOI: 10.1016/S0045-7825(99)00389-8). Neuspeo proračun dobija \(f=2f_{\mathrm{ref}}\), \(V=10\) i nikada nije izvodljiv. Spoljni adapter eksplicitno računa FR; neposredni povratak evaluatora inače predstavlja SP.

**GAdapt** koristi granu AD-N: podrazumevanu adaptivnu politiku čiji signali čitaju skalar izabrane tehnike. Populacija ima 32 jedinke, elitizam zadržava 50%, roditelji se biraju ruletom po rangu, a blending ukrštanje ima verovatnoću 0,5. Ostaje podrazumevana kombinacija Gausove mutacije vođene kolonskom raznovrsnošću i uniformnog reseta, sa verovatnoćama 50:50 po mutiranoj koordinati. Granice standardne devijacije su 0,001 i 0,6, bez opadanja donje granice; mere raznovrsnosti su `log_relative`. Ostaju podrazumevana adaptivna pravila broja mutiranih jedinki i promenljivih, popravka duplikata i jedinstvenost diskretnih jedinki. Imigracija je isključena. Probni pozivi funkcije troška izostavljeni su opcijom `probe_cost_function=False`.

**CMA-ES sa marginom**, CMAwM, koristi paket `cmaes` 0.13.1 (Hamano i sar., 2022, DOI: 10.1145/3512290.3528827). Spoljni metodi rade nad indeksima \(k_j\in\{0,\ldots,R-1\}\), dekodiranim kao \(lo_j+k_j\,step_j\). CMAwM ima granice [0, R−1], jedinične korake, početnu sredinu (R−1)/2 na svakoj koordinati i početnu sigmu (R−1)/3. Ostala podešavanja su podrazumevana. Evaluira se `x_for_eval`, dok se `x_for_tell` predaje metodi `tell()` sa odgovarajućim skalarom. `should_stop()` se ne koristi.

**Diferencijalna evolucija**, SciPy 1.18.1, koristi `best1bin`, `popsize=15`, `mutation=(0.5, 1)`, `recombination=0.7`, `init="latinhypercube"`, `updating="immediate"`, `workers=1` i `vectorized=False`. Sve koordinate imaju `integrality=True`; `constraints=()`, jer ograničenja ulaze kroz SP ili FR. Poliranje je isključeno: `polish=False`. Podešavanja `maxiter=10**9`, `tol=0` i `atol=-1` prepuštaju prekid budžetskom omotaču.

**Nasumična pretraga** nezavisno i uniformno bira celobrojne koordinate sa vraćanjem. Pošto skalar ne utiče na izbor sledeće tačke, jedna putanja služi za oba poređenja sa GAdapt-om.

## 5.4 Jednaki budžeti i opisna analiza

Svako pokretanje izvršava tačno 3000 stvarnih `runpf` poziva. Uključeni su inicijalizacija, ponovljeni kandidati i neuspešni proračuni; ponovno računanje skalara iz sačuvanih sirovih ishoda ne dodaje pozive. Dostizanje cilja ne prekida pretragu. Budžet se odnosi na pretragu, dok pripremni OPF i ranije referentne studije predstavljaju zaseban trošak.

GAdapt koristi `exit_check="generations"`, nominalno \(10^9\) generacija, `timeout=10**6` i budžetski `exit_function`. CMAwM u poslednjoj generaciji evaluira samo preostale kandidate, bez delimičnog `tell()`. DE omotač podiže namenski izuzetak pre poziva 3001. Svi prijavljeni ishodi dolaze iz omotača stvarnih evaluacija.

Za svaku instancu korišćeno je deset novih semena, sa namenom 5 u I56 formuli:

\[
seed=5\cdot10^7+10^5i_{\mathrm{mreže}}+10^3R+
10^2i_{\mathrm{scenarija}}+s,\qquad s=1,\ldots,10.
\]

Generatori su eksplicitno sejani. Isto seme omogućava uparivanje konfiguracija, ali ne znači istu početnu populaciju različitih metoda. Izvedeno je 300 uparenih jedinica sa sedam putanja: 2100 pokretanja i 6,3 miliona proračuna. Nije bilo grešaka, ponavljanja, novih izuzimanja ni zabeleženih neuspešnih PF proračuna.

Ishod \(T\) je redni broj prvog poziva koji dostiže cilj, podeljen sa 3000; nedostizanje dobija \(T=1\). Šest kontrasta računa \(T(\mathrm{metod})-T(\mathrm{GAdapt})\) pod istom tehnikom. Blokovi imaju jednake težine, kao i preostali scenariji unutar bloka. Bootstrap uzorkuje cele uparene vektore unutar ćelija mreža × R × scenario: 20.000 ponavljanja, seme 57, tačkasti 95% percentilni intervali. Protokol ne dozvoljava p-vrednosti, proglašavanje značajnosti, superiornosti ili ekvivalencije.

## 5.5 Rezultati: vreme do cilja, dostizanje i izvodljivost

Primarni opisni kontrasti iznose:

| Metod − GAdapt | Tehnika | Procena | 95% interval |
|---|---|---:|---|
| CMAwM | SP | −0,101 | [−0,117; −0,084] |
| CMAwM | FR | −0,105 | [−0,124; −0,086] |
| DE | SP | +0,012 | [−0,005; +0,029] |
| DE | FR | +0,008 | [−0,009; +0,026] |
| Nasumična pretraga | SP | +0,060 | [+0,045; +0,075] |
| Nasumična pretraga | FR | +0,057 | [+0,042; +0,073] |

CMAwM ima niže opaženo srednje ograničeno vreme pod obe tehnike. Tačkaste razlike DE prema GAdapt-u su male, a intervali obuhvataju nulu; to ne uspostavlja ekvivalenciju. Nasumična pretraga ima više opaženo vreme. Sličnost kontrasta pod SP i FR opisuje ove konfiguracije, bez potvrde da izbor tehnike nema efekat.

Sledeća tabela razdvaja vreme i nalaženje izvodljivosti. Svaka ćelija prikazuje **srednji T / broj pokretanja sa bar jednim izvodljivim rešenjem**. Imenilac je 40 za case14 i case118, a 20 za case57.

| Blok | GAdapt SP | GAdapt FR | CMAwM SP | CMAwM FR | DE SP | DE FR | Nasumična |
|---|---|---|---|---|---|---|---|
| case14, R=9 | 0,980 / 6 | 0,962 / 10 | 1,000 / 3 | 1,000 / 4 | 1,000 / 7 | 1,000 / 6 | 1,000 / 1 |
| case14, R=17 | 0,714 / 40 | 0,725 / 40 | 0,231 / 39 | 0,233 / 39 | 0,688 / 40 | 0,697 / 40 | 1,000 / 34 |
| case14, R=33 | 0,762 / 40 | 0,811 / 40 | 0,316 / 40 | 0,302 / 40 | 0,872 / 40 | 0,855 / 40 | 0,992 / 36 |
| case57, R=9 | 1,000 / 20 | 1,000 / 20 | 1,000 / 14 | 1,000 / 9 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case57, R=17 | 1,000 / 20 | 1,000 / 20 | 1,000 / 17 | 0,993 / 20 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case57, R=33 | 1,000 / 20 | 0,979 / 20 | 1,000 / 15 | 1,000 / 16 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case118, R=9 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case118, R=17 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case118, R=33 | 1,000 / 1 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |

Glavnina negativnog kontrasta CMAwM dolazi sa case14 pri R=17 i R=33. Tamo cilj dostiže u 92,5–95% pokretanja, prema 47,5–60% za GAdapt. Odnos srednjih ograničenih vremena iznosi približno 2,4–3,1 u korist CMAwM. To je odnos ishoda koji uključuje nedostizanja, a ne odnos vremena izvršavanja ili vremena samo uspešnih pokretanja. Pri R=9 slika se menja: GAdapt povremeno dostiže cilj, CMAwM nijednom.

DE pokazuje zašto dostizanje i T treba prijavljivati odvojeno. Na case14/R=17 cilj dostiže u 87,5% i 92,5% pokretanja, ali su srednji T oko 0,69. Veća učestalost dostizanja zato ne znači srazmerno niže ograničeno vreme.

Na case57 GAdapt nalazi izvodljivo rešenje u svakom pokretanju pod obe tehnike. CMAwM nalazi izvodljivost u 9–20 od 20 pokretanja po bloku i tehnici, dok DE i nasumična pretraga nijednom. Ipak, kroz sve konfiguracije i rezolucije cilj je dostignut samo dvaput. Na case118 nijedna konfiguracija ne dostiže cilj; jedino izvodljivo rešenje nalazi jedno GAdapt/SP pokretanje pri R=33.

Zbirni brojevi, bez težinskog uprosečavanja, dodatno pokazuju razliku između ishoda:

| Konfiguracija | Cilj dostignut, od 300 | Izvodljivost nađena, od 300 |
|---|---:|---:|
| GAdapt/SP | 46 | 147 |
| GAdapt/FR | 43 | 150 |
| CMAwM/SP | 75 | 128 |
| CMAwM/FR | 76 | 128 |
| DE/SP | 55 | 87 |
| DE/FR | 62 | 86 |
| Nasumična pretraga | 1 | 71 |

Kvalitet izvodljivih rešenja takođe zavisi od mreže. Na case14/R=17 medijane najboljeg izvodljivog gubitka su 9,512 i 9,533 MW za GAdapt, prema 9,475 MW za oba CMAwM kraka. Na case57/R=17 pod SP odgovarajuće medijane su 15,408 i 17,077 MW. Na nivou scenario × R × tehnika GAdapt ima nižu medijanu od CMAwM u devet od dvanaest case57 ćelija. Ove medijane su uslovne na pronađenu izvodljivost i porede različite podskupove pokretanja.

Nezavisna analiza Codex 049 potvrdila je svih šest tačkastih procena, rekonstrukciju ishoda i svih 30 referenci. Najveće odstupanje kraja nezavisno izračunatog intervala bilo je 0,000281 T, uz drugačiji redosled bootstrap izvlačenja.

## 5.6 Kako I57 ograničava tvrdnje disertacije

I57 ne daje osnov da se GAdapt predstavi kao konkurentan CMA-ES. Na case14 pri dve finije rezolucije, gde ciljevi dovoljno često bivaju dostignuti, CMAwM ima znatno niže opaženo ograničeno vreme i češće dostizanje. Nalaz je saglasan sa ranijom dijagnostikom glatkog AC dispečinga, ali ne prenosi njene numeričke odnose na ORPD.

Ograda iz I47 i I53 ostaje obavezna: na case14–case57 tamo nijedna metoda nije našla izvodljivo rešenje, pa se velika razlika odnosila na penalizovani skor. Ni oracle eksperiment nije utvrdio učenje korelacija kao uzrok preostalog jaza. I57 takođe ne izoluje taj mehanizam; poredi cele algoritme.

I48 pokazuje zavisnost odnosa od problema. Na multimodalnom valve-point dispečingu IPOP-CMA-ES bio je značajno bolji na dve od tri instance, uz odnos medijana jaza približno 1,3–1,5, dok je GAdapt nadmašio SciPy DE na dve instance. To poređenje koristi drugi problem, varijantu CMA-ES i budžet od 50.000 evaluacija. Manji jaz nije dokaz da GAdapt-ova raznovrsnost uzrokuje korist, niti rezultat I57.

Nalaz izvodljivosti na case57 ostaje kandidat za buduću preregistrovanu proveru. On opravdava posebno pitanje o verovatnoći nalaženja izvodljivog rešenja pri fiksnom budžetu, ali ne menja opisni status studije. Doprinos disertacije ostaje kontrolisano znanje o biblioteci i proverljiva inženjerska funkcionalnost, bez tvrdnje o novoj optimizacionoj metodi.

## 5.7 Pretnje validnosti

Prvo, ciljevi potiču iz GAdapt referentnih pokretanja. Mogu biti povoljniji za obrasce pretrage slične GAdapt-ovim, ali smer i veličina te pristrasnosti nisu izmereni. Reference su najbolje poznata rešenja, a četiri cilja mere samo izvodljivost.

Drugo, cenzura ograničava razlikovanje metoda. U četiri bloka svako pokretanje ima T=1; oni zadržavaju protokolarne težine. U još tri bloka dostizanje je retko. Jednako T zato može prikriti razlike u prekršajima i izvodljivim gubicima, a ne predstavlja dokaz jednake efikasnosti.

Treće, konfiguracije su ograničene budžetom i nisu prilagođavane problemu. SciPy `popsize=15` znači populacije od 135, 405 i 1155 jedinki. Posle inicijalizacije, case57 i case118 dopuštaju samo mali broj generacija pre potrošnje 3000 poziva. Opaženi rezultat zato ne opisuje DE sa manjom populacijom, većim budžetom ili adaptivnim varijantama. Jednaki PF budžeti ne znače jednako vreme rada ni jednak trud podešavanja.

Najzad, tri mreže i pretpostavljene mreže vrednosti uređaja ne predstavljaju industrijsku validaciju. Termičke granice na ovom skupu praktično ne deluju. Deset semena po instanci i bootstrap opisuju promenljivost pod zamrznutim scenarijima i referencama; intervali nisu istovremeni za šest kontrasta i ne opravdavaju generalizaciju na druge mreže.

## 5.8 Prelaz ka bibliotečkoj funkcionalnosti

Spoljašnji kontekst određuje domet narednog koraka. Ugradnja standardnih tehnika za rukovanje ograničenjima može korisniku olakšati modelovanje i pravilno izveštavanje izvodljivog rešenja, ali sama po sebi ne uklanja opaženi zaostatak prema CMAwM. Poglavlje 6 zato opisuje interfejs, redosled ocenjivanja i proveru ispravnosti opt-in funkcije. I58/I60 nisu potvrdile ubrzanje; H59 je nedostupna posle razvojnog NO-GO.