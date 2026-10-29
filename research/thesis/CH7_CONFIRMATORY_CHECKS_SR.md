# Poglavlje 7. Konfirmatorne provere ugrađenih tehnika za ograničenja

*Nacrt, 24. oktobar 2026, posle studija I58 i I60. Merodavni su zamrznuti protokoli i odgovarajući izveštaji, uključujući odstupanje D1 u I58. H58 = N i H60 = N. I59 je završen razvojnim NO-GO (nijedan dozvoljeni par budžeta i tolerancije nije zadovoljio 20–80% dostizanja na obe razvojne mreže; potvrda nije izvršena); izabrana je grana N/N/nedostupno.*

## 7.1 Zašto je posle opisnog nalaza potrebna konfirmatorna provera

Poglavlje 4 pokazalo je izraženu opisnu prednost ε-ograničenja na pojedinim blokovima mreže case14. Pri rezolucijama R = 17 i R = 33 srednje ograničeno vreme do cilja bilo je približno 0,28 i 0,39, prema 0,77 i 0,82 pod pravilima izvodljivosti. Taj nalaz nije bio predmet preregistrovane hipoteze. Izdvojen je posle pregleda rezultata i zato predstavlja razlog za novu proveru, sa unapred određenim kandidatom, poređenjem i pravilom odlučivanja.

Studije I58 i I60 ispituju praktičnu korist bibliotečke funkcionalnosti iz poglavlja 6. I58 proverava ugrađena Deb-ova pravila izvodljivosti, FR, prema korisničkoj kazni. Taj izbor zamrznut je pre ijednog I56 test rezultata i ostao je isti posle opisnog nalaza za ε. I60 zasebno proverava ugrađeno ε-ograničenje; njegov protokol zamrznut je pre ijednog I58 rezultata. Time se razdvajaju nastanak kandidata i procena njegove koristi.

Same tehnike imaju ustanovljene prethodnike. Deb-ova pravila potiču iz rada Deb-a (2000, DOI: 10.1016/S0045-7825(99)00389-8), a ε-pristup pripada postojećoj literaturi o ograničenoj evolutivnoj optimizaciji (Takahama i Sakai, 2010, DOI: 10.1109/CEC.2010.5586484). Mallipeddi i sar. već porede tehnike za ograničenja na ORPD-u sa diskretnim kontrolama (2012, DOI: 10.1016/j.swevo.2012.03.001). Postoje i samoadaptivni GA za ORPD i kombinacije adaptivne DE sa ε-ograničenjem (Subbaraj i Rajnarayanan, 2009, DOI: 10.1016/j.epsr.2008.07.008; Biswas i sar., 2019, DOI: 10.1016/j.asoc.2018.11.042).

Doprinos ovih provera zato je uzak: procena unapred određene bibliotečke opcije prema kazni 1000, na određenim instancama i pri jednakom broju stvarnih simulacija. One ne ustanovljavaju novu optimizacionu metodu niti rešavaju otvoreno pitanje prioriteta tačne faktorske studije iz I56.

## 7.2 Zajednički dizajn I58 i I60

Primarni skup čine case30, case39 i case24_ieee_rts. To su sveže mreže u okviru ovog projekta, odvojene od I56 skupa, ali već poznati javni slučajevi. Svaka kontrola ima R = 17 dozvoljenih vrednosti. Tri scenarija koriste faktore opterećenja 0,95, 1,00 i 1,05, semena 301–303 i dodatno odstupanje opterećenja po sabirnicama u opsegu ±10%.

Model nasleđuje diskretni ORPD iz poglavlja 3, uz jednu zadatu naponsku kontrolu po generatorskoj sabirnici, primenjenu na sve generatore na njoj. Primarne mreže proširuju proveru na slučajeve sa termičkim ograničenjima. case300 ostaje opisni dodatak, bez termičkih granica ispod 9900 MVA. Njegov treći scenario izuzet je zbog neuspelog pripremnog kontinualnog OPF-a, bez zamene.

Kontrolna grana G0 koristi isti bibliotečki build, `constraint_handling=None` i korisnički skalar

\[
P=f+1000V.
\]

I58 je poredi sa G1, `constraint_handling="feasibility_rules"`, a I60 sa G2, `constraint_handling="epsilon"`. Populacija ima 32 jedinke, elitizam zadržava polovinu, sondiranje funkcije troška i imigracija su isključeni. Početne populacije uparenih GAdapt grana moraju biti identične; asercije su prošle u obe studije. Svaki scenario koristi 15 semena, uz odvojene namene semena za I58 i I60.

I58 izvršava jednu putanju od 10.000 stvarnih proračuna toka snage po metodi; prvih 3000 određuje primarni ishod. Duži budžet i poređenja sa CMAwM/FR, DE/FR i nasumičnom pretragom služe opisnom kontekstu. I60 izvršava samo 3000 poziva. Broje se inicijalizacija, ponovljeni kandidati i neuspešni proračuni; dostizanje cilja ne prekida pretragu.

Za ε je unapred zadato `number_of_generations=188`. Početni nivo je 20. percentil prekršaja početne populacije, eksponent opadanja je 5, a ε postaje nula približno posle 1536 poziva. Ovo podešavanje pripada proveravanoj konfiguraciji; rezultat se ne prenosi automatski na drugi raspored ili budžet.

Reference su zajedničke. U I58 obuhvataju svih pet metoda, po dva zasebna semena i 30.000 poziva. Od 110 referentnih pokretanja završena su 104; šest CMAwM pokretanja ostalo je neuspešno posle dozvoljenog ponavljanja. Reference su heširane pre testiranja, a I60 preuzima iste reference i njihov manifest. Test rezultati ne menjaju referentne ciljeve.

## 7.3 Cilj, procena i zamrznuto pravilo odlučivanja

Cilj zahteva stvarnu izvodljivost i dovoljno mali gubitak:

\[
V=0,\qquad f\leq1,01L^*+0,01\ \mathrm{MW},
\]

gde je \(L^*\) najmanji izvodljiv gubitak iz uspešno završenih referentnih pokretanja. To je najbolje poznata vrednost, bez sertifikata optimalnosti. Kada reference ne nađu izvodljivo rešenje, cilj je sama izvodljivost.

Ako je \(\tau\) redni broj prvog poziva koji dostiže cilj, primarni ishod je

\[
T=\min(\tau/3000,1),
\]

uz \(T=1\) za nedostizanje. Procena \(\theta\) prosečava uparene razlike \(T(G1)-T(G0)\), odnosno \(T(G2)-T(G0)\), sa jednakim težinama mreža i scenarija unutar mreže.

Bootstrap uzorkuje cele uparene vektore unutar ćelija mreža × scenario. Obe analize koriste 20.000 ponavljanja i percentilni 95% interval, sa semenima 58 i 60. Hipoteza dobija podršku samo ako je ceo interval ispod nule.

T meri ograničen utrošak evaluacija do cilja. Povezuje ranije dostizanje i nedostizanje u jednu veličinu; ne predstavlja vreme izvršavanja na računaru. Dostizanje na poslednjem pozivu i nedostizanje imaju isti T, pa se uz njega prikazuju i brojevi dostizanja.

Nezavisni proverivač, bez korišćenja koda merila, rekonstruiše kontrole, granice, gubitke i prekršaje za relevantna rešenja. Manifesti povezuju proveru sa podacima, kodom i podešavanjima. Neuspešna provera sprečava prihvatanje zaključka.

## 7.4 Rezultati I58 i I60

I58 ima 134 potpune primarne jedinice od planiranih 135. Jedna cela jedinica izuzeta je zbog trajnog neuspeha CMAwM pokretanja, prema pravilu potpunih jedinica. Nije bilo praznih ćelija; stopa izuzimanja bila je ispod praga za aktiviranje analize osetljivosti. I60 ima svih 135 primarnih parova, bez ponavljanja i izuzimanja.

| Studija | Kontrast | Potpune primarne jedinice | Procena θ | 95% interval | Ishod |
|---|---|---:|---:|---|---|
| I58 | FR − kazna 1000 | 134 | −0,0143 | [−0,0345; +0,0061] | H58 = N |
| I60 | ε − kazna 1000 | 135 | −0,0114 | [−0,0350; +0,0117] | H60 = N |

Obe procene imaju povoljan znak za ugrađenu opciju, ali nijedan interval ne ispunjava zamrznuti uslov potvrde. Opisna prednost ε iz I56 zato nije potvrđena u I60. I60 proverava prenos koristi na nove projektne instance i ugrađenu implementaciju, uz promenjen raspored; nije direktno ponavljanje konfiguracije I56.

Sledeća tabela prikazuje srednje razlike pri 3000 poziva i dostizanja u odgovarajućim potpunim primarnim jedinicama. I58 i I60 koriste različita semena.

| Ćelija | I58: FR − G0 | I58: dostizanja G0 / FR | I60: ε − G0 | I60: dostizanja G0 / ε |
|---|---:|---:|---:|---:|
| case30, j=0 | 0,000 | 0 / 0 | 0,000 | 0 / 0 |
| case30, j=1 | +0,016 | 6 / 5 | +0,114 | 12 / 11 |
| case30, j=2 | 0,000 | 0 / 0 | 0,000 | 0 / 0 |
| case39, j=0 | −0,099 | 5 / 7 | −0,049 | 3 / 5 |
| case39, j=1 | −0,004 | 1 / 1 | −0,059 | 2 / 3 |
| case39, j=2 | −0,023 | 5 / 2 | −0,038 | 6 / 6 |
| case24_ieee_rts, j=0 | 0,000 | 0 / 0 | −0,048 | 1 / 3 |
| case24_ieee_rts, j=1 | −0,018 | 1 / 1 | −0,022 | 0 / 1 |
| case24_ieee_rts, j=2 | 0,000 | 0 / 0 | 0,000 | 0 / 0 |

Imenilac je 15, osim prve I58 ćelije, gde je 14. Veći opisni pomak FR potiče sa case39/j=0. Kod ε pet ćelija ima negativnu razliku, dok jedina case30 ćelija sa dostizanjima ima pozitivnu razliku. Broj dostizanja i T ne moraju imati isti smer: nekoliko ranih dostizanja može dati niži srednji T od većeg broja kasnih dostizanja.

Duži I58 budžet ostaje opisni. Na case39 srednji T pri 10.000 poziva iznosi 0,611 za G0 i 0,595 za FR, a na case24_ieee_rts 0,864 i 0,851. Ti brojevi ne zamenjuju primarni ishod. Na case300 nijedna metoda nije našla izvodljivo rešenje.

## 7.5 Odstupanje D1 i provera izlaza

Originalna I58 provera odbila je 67 od 374 vraćena GAdapt izlaza: 33 iz G0 i 34 iz G1, sve na opisnoj mreži case300. Kontrole su bile validne, ali proračuni toka snage nisu konvergirali. Instrument i nezavisni proverivač bili su saglasni o nekonvergenciji; pravilu prihvatanja nedostajala je grana za konvencionalno evidentiranje takvog neuspeha.

D1 prihvata izlaz samo kada proverivač nezavisno potvrdi nekonvergenciju i tačne konvencionalne vrednosti. G0 mora vratiti \(2f_{\mathrm{ref}}+1000\cdot10\), a G1 cilj \(2f_{\mathrm{ref}}\), prekršaj 10 i oznaku `feasible=False`. Ovde \(f_{\mathrm{ref}}\) označava gubitak pripremnog kontinualnog OPF-a; razlikuje se od bibliotečke skale za FR skalar.

Dopuna je promenila tačno 67 redova, uz zaštitu koja dozvoljava samo odgovarajući prelaz neuspelog vraćenog izlaza u prihvaćen zapis neuspeha. Originalna provera sačuvana je kao `i58_check_v1.json.gz`, a dopunjena beleži heševe i izmene. Konačna provera ima 1008 redova i nijedan neuspeh.

D1 je naknadna promena kriterijuma prihvatanja provere. Originalno pravilo blokiralo je analizu, a dopuna ju je omogućila. Podaci, ciljevi, izuzimanja i formula H58 nisu promenjeni; case300 ne ulazi u primarni kontrast. Izveštaj navodi da je dopuna napravljena pre analize i uvida u H58 ishode. Istorija komitova potvrđuje redosled dopune i analize, ali sama ne može dokazati odsustvo ranijeg uvida.

Ista grana ugrađena je u I60 proverivač pre njegovih pokretanja. Tamo su prošla sva 562 reda, uključujući 44 vraćena izlaza sa nezavisno potvrđenom nekonvergencijom. Prolaz te grane potvrđuje pravilno evidentiranje neuspeha. Ne potvrđuje izvodljivost vraćenog rešenja.

## 7.6 Značenje oznake N i granice dokaza

Prema unapred napisanoj mapi ishoda, N znači validno završenu studiju bez ispunjenog uslova potvrde. H58 i H60 zato ne podržavaju tvrdnju o ubrzanju prema kazni 1000 u ispitanim uslovima. N ne uspostavlja jednakost metoda, praktičnu ekvivalenciju ili odsustvo koristi. Intervali dopuštaju i smanjenje i povećanje srednjeg ograničenog vremena.

Informativnost ograničava degeneracija ćelija. U I58 četiri od devet primarnih ćelija imaju T=1 za obe GAdapt grane u svim jedinicama; u I60 takve su tri. One ostaju u analizi, nose odgovarajuću težinu i daju nultu bootstrap varijansu. To opisuje ponašanje pri budžetu od 3000 poziva. Ne pokazuje da bi putanje bile jednake pri većem budžetu. Na dve case30 ćelije ni reference nisu našle izvodljivost, pa je cilj samo izvodljivost; neuspeh pretrage ne dokazuje neizvodljivost problema.

Reference dodatno ograničavaju zaključak. Šest referentnih pokretanja nije završeno, a test pretrage su na tri ćelije našle gubitak bolji od zamrznutog \(L^*\). Bootstrap je uslovan na te reference, mreže i scenarije i ne obuhvata njihovu neizvesnost.

Kazna 1000 nije razvojno podešena. Kontrasti zato ne opisuju prednost prema kaznenim metodama uopšte. I58 i I60 dele mreže i reference, pa nisu dve nezavisne replikacije prenosa na nove topologije. Takođe ne daju direktno poređenje FR–ε niti identifikuju mehanizam efekta: opcije menjaju i poredak i skalarne signale adaptacije.

Nezavisne ponovne analize reprodukovale su primarne procene i tabele. Ipak, proverivač koristi isti PYPOWER solver, a drugi istraživač nije ponovio ceo paket u čistom okruženju. Udeo pokretanja sa nađenom izvodljivošću u tabelama znači da je izvodljivo rešenje ikada evaluirano; ne garantuje da je ono vraćeno korisniku.

## 7.7 I59: razvojni NO-GO

I59 proverava FR prema istoj kazni u modularnom planiranju kapaciteta telekom mreže. Razvoj koristi Abilene i PDH, a potvrda
Polska, Nobel-Germany i Nobel-US. Model ima statičke zahteve, deljive tokove i zajednički kapacitet oba smera; moduli i cene
su sintetičke pretpostavke. Budžet \(B\) i tolerancija cilja \(\varepsilon\) biraju se zamrznutim razvojnim pravilom
(zbirno G0/G1 dostizanje 20–80% na svakoj razvojnoj mreži), bez ponovnog izbora posle neuspeha.

Obe razvojne MILP reference su sertifikovane (gap 0) i nezavisno proverene. Zbirno dostizanje (20 putanja po mreži):

| B | Abilene ε = 0,05 / 0,10 / 0,20 | PDH ε = 0,05 / 0,10 / 0,20 |
|---|---|---|
| 3000 | 0,75 / 1,00 / 1,00 | 0,00 / 0,00 / 0,50 |
| 10.000 | 1,00 / 1,00 / 1,00 | 0,10 / 0,80 / 1,00 |
| 30.000 | 1,00 / 1,00 / 1,00 | 0,95 / 1,00 / 1,00 |

Nijedan dozvoljeni par nije zadovoljio razvojni uslov; H59 zaključak je nedostupan, bez ponovnog izbora. Abilene je pri svim
parovima osim (3000; 0,05) iznad 80%, a pri tom paru PDH ima 0%: dve razvojne mreže vrlo različite težine čine pravilo teško
ispunjivim, što je svojstvo unapred zadatog dizajna. Nedostupan zaključak ostaje različit od N; uz H58/H60 = N/N izabrana je
grana **N/N/nedostupno**. Nova telekom provera zahtevala bi nov protokol (npr. budžet po mreži, kao u I61).

## 7.8 Posledice za biblioteku i README

`constraint_handling` ostaje opt-in. I58 i I60 ne daju osnov za preporuku FR ili ε zasnovanu na brzini u ispitanom elektroenergetskom zadatku. Inženjerska vrednost ostaje: korisnik može odvojeno zadati cilj i prekršaj, primeniti standardnu tehniku i proveriti izvodljivost prijavljenog rešenja. Ispravna implementacija i empirijska korist predstavljaju odvojene tvrdnje.

Odgovarajuća formulacija za README glasi:

> GAdapt podržava opcione standardne tehnike za rukovanje ograničenjima. Na ispitanim ORPD instancama, pri 3000 stvarnih proračuna toka snage, nije potvrđeno da ugrađena pravila izvodljivosti ili ε-ograničenje smanjuju srednje ograničeno vreme do izvodljivog referentnog cilja prema korisničkoj kazni \(f+1000V\). Rezultati zavise od konfiguracije, budžeta i definicije prekršaja; za ε je korišćeno `number_of_generations=188`.

Dokumentacija treba da objasni izbor tehnike, raspored ε i značenje izlaznih polja. Telekom korist ostaje neproverena; nova provera zahteva novi protokol.

## 7.9 I61, I63 i I62

Praktične provere ne zamenjuju replikaciju centralnog nalaza o interakciji. I61 je zato trebalo da ponovi kontrast adaptivna naspram podešene fiksne politike, ukršten sa FR i statičkom kaznom, na topologijama odvojenim od I56 (iste kao I58, uz druge scenarije i reference). Zamrznuti protokol je zahtevao razvojni izbor informativnog budžeta. **I61 je stao na tom pravilu (§5):** nijedna mreža nije imala budžet B ∈ {3000, 6000, 12000} za koji su sve četiri razvojne medijane vremena dostizanja u [0,3; 0,8]; faze posle izbora budžeta nisu izvršene, a test scenariji nisu otvoreni. H61 nije ocenjena, što nije negativan rezultat za H56a. Opisni uzrok je cilj f ≤ 1,01·L* + 0,01 MW, koji u razvojnim pokretanjima nije dostignut u 12.000 poziva na nekim scenarijima (case30, scenario 0: 0/10), dok se na drugima dostiže pri vrlo različitim budžetima; to ne dokazuje da je cilj nedostižan niti isključuje uticaj većeg budžeta (T = h/B opada sa B, pa veći budžet ne bi nužno popravio zamrznuti kriterijum).

Zbog toga je zamrznut tačno jedan naslednik, I63, sa drugim procenjivačem (kvalitet najboljeg izvodljivog rešenja pri fiksnom budžetu od 12.000 poziva, uparena „pobeda“ FX-T nad AD-N sa pragom 0,1% kontinualnog OPF normalizatora) i sa obelodanjivanjem da su I61 razvojni podaci služili kao pilot za izbor procenjivača i budžeta. I63 ne tvrdi novu metodu: fiksni budžet i ECDF su deo COCO prakse, a poređenje tehnika za ograničenja na ORPD-u postoji kod Mallipeddi i sar. (2012). **I63 je stao na konačnom STOP-u u fazi snage (23:06, 28. oktobra):** razvojna proba, izbor n = 160, potvrda snage i kalibracija nule su prošli, ali kalibracija lažne ekvivalencije na granicama ±0,05 nije (stopa 4,9–5,8% pri zahtevu da gornja Wilsonova granica ne prelazi 5%). I63 nije zadovoljio zamrznuti kriterijum kalibracije; zahtev za gornju Wilsonovu granicu stope greške ≤ 0,05 je zahtevan pri nominalnoj veličini testa od 5% (sa 1000 simulacija se očekuje da retko prolazi), što je osobina zamrznutog pravila, a ne podatak o H56a. Test faza nije izvršena. H56a ostaje lokalni nalaz bez konfirmatorne replikacije; I63-D ima isključivo deskriptivan status.

I62 je za sada predlog za jači spoljni kontekst. Predviđa validirane L-SHADE i jDE implementacije, zadržavanje CMAwM poređenja i razvojno podešenu kaznu. Time treba proveriti koliko zaključci zavise od jednog nepodešenog kaznenog koeficijenta i skupa konkurenata. Predlog nije zamrznut i nema rezultate.

I63 je završen STOP-om; I62 ostaje nezamrznut predlog bez rezultata. H58 = N i H60 = N ostaju deo glavnog dokaza i određuju granicu sadašnje tvrdnje o korisnosti ugrađenih opcija.