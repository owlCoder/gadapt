**Verdikt: FREEZE AFTER FIXES.** W estimand je koherentan i implementabilan; nacrt još nije dovoljno jednoznačan za zamrzavanje. Pregled je read-only: ništa nije menjano niti pokretano od optimizacionih eksperimenata.

**1. Blokirajući nedostaci i tačne zamene**

**ESS za tri varijante nije jednoznačan.** U [nacrtu, redovi 61–63](/Users/danijel/Desktop/gadapt/research/ITERATION63_PROTOCOL.md:61), „≥20 od40“ može biti primenjeno i na jednoscenarijske pool-ove od20 jedinica. Tada ESS≥20 dopušta samo uniformne težine: sva tri cilja θ=0,±0,05 ne mogu proći.

Zameniti zahtev za ESS tekstom:

> „Za svaku varijantu prenosa v i mrežu i, N_iv je broj redova njenog izvornog pool-a: 40 za objedinjeni pool, odnosno20 za j=0 ili j=1. Zahteva se ESS_iv=1/Σ_u w_ivu² ≥ N_iv/2, dakle20 odnosno10. Naginjanje se rešava zasebno za svaku kombinaciju varijante i ciljnog θ.“

**Potpuni slučajevi menjaju estimand i razdvajaju planiranu snagu od analize.** [Redovi 77–79](/Users/danijel/Desktop/gadapt/research/ITERATION63_PROTOCOL.md:77) dopuštaju selekciju prema tehničkom uspehu, bez pretpostavke o mehanizmu nedostajanja. Neuspeh može zavisiti od grane i ishoda. To odstupa i od strožeg pravila dizajna077.

Zameniti:

> „Svaka tehnički neuspešna grana ponavlja se jednom, istim zadatkom i semenom, u novom procesu. Ponovljen neuspeh bilo koje planirane grane znači konačan STOP bez potvrdnog zaključka. Svi pokušaji ostaju arhivirani. Tehnički neuspeh ne kodira se kao algoritamska neizvodljivost. Neuspeo PF koji instrument pravilno evidentira ostaje algoritamski ishod i troši poziv.“

**Lanac zamrzavanja nije dovoljno konkretan.** „I61 obrazac“ u [redovima 28–29](/Users/danijel/Desktop/gadapt/research/ITERATION63_PROTOCOL.md:28) i heš samo FX-T/n nisu potpuna specifikacija.

Dodati:

> „Posle zamrzavanja protokola, a pre prvog izvršavanja I63, zamrzavaju se drajver, analiza, simulacija, proverivač, svi tranzitivno korišćeni izvori, biblioteka, zavisnosti i razrešena GA podešavanja. Svaka faza proverava provenijenciju pre i posle izvršavanja i objavljuje heševe ulaznih i izlaznih artefakata. Pre potvrde dodatno se vezuju roster scenarija, OPF normalizatori i scenarijski podaci, svi razvojni rezultati, izabrani FX-T i n. Faze su create-once za jedinstveni I63 identitet; novi direktorijum ne dozvoljava ponovno odlučivanje posle STOP-a.“

Dopuniti OPF pravilo:

> „Samo eksplicitni neuspeh OPF-a dopušta unapred propisano izuzimanje scenarija. Ostale greške ili nekonačan/nepozitivan r_ij znače STOP. Svako kasnije konstruisanje scenarija mora odgovarati zamrznutom scenariju i normalizatoru.“

Dopuniti semena:

> „Redosled mreža je case30, case39, case24_ieee_rts. Opsezi s su1..3,1..20 i1..n za p=1,2,3. Jedinstvenost se proverava nad različitim jedinicama, uz namerno deljenje semena među njihovim granama/konfiguracijama. Zahtevaju se identične generisane početne populacije svih uparenih pokretanja.“

**§6 ostavlja izbor implementacije simulacije i kriterijuma.** Zameniti operativni deo postupkom iz tačke2; posebno, simulirana ekvivalencija mora uključivati isti uslov nedegenerisanosti kao završna analiza.

**2. W i tačan algoritam snage**

**W sa pragom0,001 jeste koherentan.** Izvodljivost ima prvenstvo; oba neizvodljiva ishoda daju½. Za oba izvodljiva računati
\[
\Delta=(f_{AD}-f_{FX})/r_{ij};
\]
W=1 ako Δ>0,001, W=0 ako Δ<−0,001, inače½. Time se izbegava aritmetika ∞−∞. Veze nisu tranzitivne, ali to ne sprečava definisani skor pobede. Prag označava0,1% normalizatora, a ne relativno poboljšanje prema AD-N.

Sledeći tekst može neposredno zameniti operativni deo §6:

> „Za svaku mrežu formiraju se tri pool-a: svih40 razvojnih jedinica,20 jedinica j=0 i20 jedinica j=1. Svaki red čuva ceo upareni četvorovektor normalizovanih ishoda, oznake izvodljivosti i njegov d. Prenosi se raspodela ovih normalizovanih ishoda; ne preračunavaju se prema normalizatoru potvrdnog scenarija. Ponovljeni jednaki redovi zadržavaju multiplicitet.
>
> Za svaku varijantu v i cilj t∈{0,+0,05,−0,05} određuje se zajednički λ_vt za tri mreže:
> \[
> w_{iu}=\frac{\exp(\lambda d_{iu})}{\sum_h\exp(\lambda d_{ih})},
> \qquad \frac13\sum_i\sum_u w_{iu}d_{iu}=t.
> \]
> Težine se računaju stabilnim softmax-om. Stroga dostižnost znači
> \[
> \frac13\sum_i\min_u d_{iu}<t<
> \frac13\sum_i\max_u d_{iu}.
> \]
> Proveravaju se greška≤10⁻⁸ i ESS prema veličini odgovarajućeg pool-a; objavljuju se λ, težine i ESS.
>
> U svakom simuliranom eksperimentu, za svaku stvarno podobnu potvrdnu ćeliju(i,j), nezavisno se uzorkuje n celih četvorovektora sa vraćanjem iz pool-a mreže i, sa verovatnoćama w_i. Sve potvrdne ćelije iste mreže koriste istu izvornu raspodelu, ali nezavisna izvlačenja.
>
> Ekvivalentno, C_ij∼Multinomial(n,w_i). Unutrašnji bootstrap zatim nezavisno po ćelijama uzorkuje C*_{ijb}∼Multinomial(n,C_ij/n). Bootstrap raspodela ne koristi ponovo naginjane težine.“

Za svako ponavljanje:
\[
\hat\theta_b^*=
\frac13\sum_i\frac1{m_i}\sum_j
\frac1n\sum_u C^*_{ijbu}d_{iu}.
\]
Procena koristi C umesto C*. Ne resampluju se mreže ili scenariji. CI95 su linearni percentili2,5/97,5; CI90 su5/95 **istih izvlačenja**.

Dodati:

> „Pozitivan zaključak zahteva L95>0, negativan U95<0. Ekvivalencija zahteva L90>−0,05 i U90<0,05, uz najmanje jedan opaženi d≠0 u svakoj mreži simuliranog eksperimenta. Ista funkcija odlučivanja koristi se u simulaciji i završnoj analizi.“

Preliminarno, najmanji n mora zadovoljiti oba kriterijuma snage u **sve tri** varijante. Nezavisna potvrda proverava oba kriterijuma ponovo. Kalibracija proverava oba smera pri θ=0 i ekvivalenciju na obe granice, u sve tri varijante. Nema povećanja n posle neuspele potvrde.

RNG nejasnoću zameniti:

> „Simulirana uzorkovanja i njihov bootstrap koriste jedan `numpy.random.default_rng` po seriji, sa semenom63023,63024 odnosno63025, bez resetovanja između eksperimenata. Redosled je rastući n, zatim objedinjeni/j=0/j=1 pool, ciljevi +0,05/0/−0,05 kada su potrebni, pa sortirane ćelije. Završni bootstrap koristi zaseban `default_rng(63)`.“

Za1000 eksperimenata Wilsonovi uslovi znače najmanje825 uspeha, odnosno najviše36 grešaka. Poslednji uslov je izrazito konzervativan: pri stvarnoj grešci5% prolazi približno2,1% serija. Nije nemoguć, ali taj rizik STOP-a treba prihvatiti unapred; granice se ne smeju naknadno ublažavati. Provera svakog smera zasebno ne potvrđuje ukupnu grešku „bilo koji smer“≤5%.

**3. Tačna FX-T statistika**

Da: [§4 već zahteva isto seme/scenario](/Users/danijel/Desktop/gadapt/research/ITERATION63_PROTOCOL.md:48). Za konfiguraciju k, CHT c:
\[
Q_{kc}=\frac1{3\cdot2\cdot3\cdot26}
\sum_{i=0}^{2}\sum_{j=0}^{1}\sum_{s=1}^{3}
\sum_{\ell\ne k}S_{ijsc}(k,\ell),
\]
gde je S skor **konfiguracije k protiv ℓ**, prema navedenom W pravilu. Ne porede se različita semena niti sva međusobna ukrštanja pokretanja.

Dodati:

> „Bira se k sa najvećim Q_kc; pri tačno jednakom skoru bira se najmanji indeks `FXT_GRID`. Poređenje se obavlja preko celobrojnog zbira 2S, bez numeričke tolerancije za izjednačenje.“

**4. Dostupnost estimanda i dodaci drajvera**

**Dostupan je bez izmene zamrznutih modula.**

- [I56:132–151](/Users/danijel/Desktop/gadapt/research/iteration56_cht_study.py:132): posle B nema evaluacije; svaki raniji poziv izvršava PF, čuva raw ishod i ažurira `best_feasible`. Keš ovde ne preskače ponovljene PF evaluacije.
- [I56:490–499](/Users/danijel/Desktop/gadapt/research/iteration56_cht_study.py:490): rezultat se već zapisuje iz evaluatora.
- [I61:277–288](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:277): iz keša se izvlači `best_feasible_x`, uz gubitak i heš sekvence.
- [I58:399–438](/Users/danijel/Desktop/gadapt/research/iteration58_validation.py:399): nezavisna provera vektora, R-mreže, PF-a, gubitka i izvodljivosti.

I63 drajver mora dodati sopstveni raspored scenarija/semena, puni B bez ciljnog prekida, zapis r/G/svedoka, W kalibraciju, tri pool-a, opisanu snagu i provenijenciju. Proverivač mora dobiti **I63 scenarije**; direktan I58 poziv koristi njegove stare scenarije. Zamrznuti izvori ostaju neizmenjeni.

Pri ponovnoj upotrebi [I61 bootstrap-a](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:903), ključevi moraju biti `(i,i,j)` ili se grupisanje mora prilagoditi: funkcija grupiše preko `k[:2]`. Ključevi `(i,j)` pogrešno bi ponderisali mreže kada imaju različite m_i.

**5. Konačna odluka**

**FREEZE AFTER FIXES:** zadržati B, W, prag i tri pretpostavke prenosa; pre zamrzavanja uneti navedene zamene. Redizajn estimanda nije potreban.