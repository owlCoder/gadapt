**Prvo bih proveravao pravac 1, zatim 2. Nijednom trenutno nije ustanovljena originalnost.** Ispod su pet novih istraživačkih pitanja, rangiranih prema vezi sa GAdapt-om, mogućnosti formalizacije i riziku od prior art-a. GO znači nastavak provere literature i dokazivosti; ne odobrenje implementacije.

Pročitao sam tražene audite, prethodne odgovore i CH1, README/CLAUDE i relevantan kod. Važna korekcija premise: jedinstvenost nije stroga garancija. Posle 15 neuspelih pokušaja ukrštanje dodaje potomke bez provere ponavljanja; mutacija takođe ograničava pokušaje. Arhiva pamti i registrovane genotipove koji tek treba da prođu evaluaciju. To se vidi u [ukrštanju](/Users/danijel/Desktop/gadapt/gadapt/operations/crossover/base_crossover.py:18) i [populaciji](/Users/danijel/Desktop/gadapt/gadapt/ga_model/population.py:250).

Svi budžeti ispod odnose se na kasnije pilote i predstavljaju **plafone, ne izmerena trajanja**. Sada nisu pokretani eksperimenti niti menjani fajlovi.

**1. Zasićenje diskretnog prostora uz ograničeno izbegavanje ponavljanja — strukturna teorija**

**Pitanje:** kako ograničeni pokušaji popravke menjaju vreme dostizanja cilja kada arhiva zauzima sve veći deo prostora?

Najbliži prior art je NrGA: Yuen–Chow već koriste celu istoriju, mreže konačne rezolucije i adaptivnu mutaciju ([10.1109/TEVC.2008.2003008](https://hub.hku.hk/handle/10722/196704)). Pregled Lou–Yuen–Chen iz 2021. eksplicitno traži dublju teoriju nepovratnog pretraživanja i sistematsko proučavanje učestalosti ponavljanja ([10.1016/j.swevo.2020.100828](https://doi.org/10.1016/j.swevo.2020.100828)).

**Precizna kandidat-praznina:** oštre granice zajedničke raspodele broja predloga, stvarnih evaluacija i vremena dostizanja za *ograničenu* zabranu ponavljanja, sa adaptivnim predlozima na heterogenim mrežama. Nisam našao rezultat koji zatvara baš ovu tvrdnju; pregledni poziv na teoriju nije dokaz njenog prvenstva.

Formalizovati stanje kao populaciju, arhivu registrovanih tačaka \(H_t\), skup evaluiranih tačaka \(E_t\) i stanje kontrolera. Potrebna je teorema koja pokazuje kada ograničena popravka smanjuje evaluacije, ali pogoršava ukupno vreme do cilja. Formula za nezavisno uniformno uzorkovanje nije dovoljan doprinos.

**Falsifikacija:** iscrpno rešivi mali prostori; GAdapt, isti GA sa memoizacijom i ponavljanjem, strogi NrGA i uzorkovanje bez ponavljanja. Proveriti predviđene granice i promenu znaka koristi pri rastu cene simulatora.

**Budžet:** do 2 CPU-sata za sintetičku proveru; potom najviše 4 CPU-sata infrastrukturnog pilota. **GO za gate.** Zatvoriti ako rezultat ostane analiza odsečenog geometrijskog uzorkovanja ili nova politika mutacije svesna jedinstvenosti.

**2. Statistički zaključak koji važi uprkos nepoznatom referentnom optimumu — metodologija**

**Pitanje:** može li alat potvrditi prednost algoritma za svaki optimum saglasan raspoloživim donjim i gornjim granicama?

Najbliži radovi već obrađuju izbor ciljeva i vreme dostizanja ([Hansen i sar., 10.1109/TEVC.2022.3210897](https://doi.org/10.1109/TEVC.2022.3210897)), kao i prikaz performansi bez unapred definisanih ciljeva kroz EAF i IOHanalyzer ([López-Ibáñez i sar., 10.1109/TEVC.2024.3462758](https://doi.org/10.1109/TEVC.2024.3462758)). Zato nova kriva ili analiza osetljivosti nije dovoljna.

**Kandidat-tvrdnja:** za nezavisno dobijeno \(f^\star\in[L,U]\), konstruisati istovremeni interval za
\[
\Delta(r)=\mathbb E[\min(T_A(r+\varepsilon),B)-\min(T_B(r+\varepsilon),B)]
\]
koji važi za sve \(r\in[L,U]\), uz veze i administrativnu cenzuru na budžetu \(B\).

Alat bi prijavljivao prednost samo kada ona opstaje preko celog intervala reference. Predložena dokaziva osobina jeste kontrola verovatnoće bilo kog lažnog zaključka preko tog intervala. Tačno nabrajanje prelomnih tačaka rešava empirijski deo; samo po sebi je elementarno. Novina inferencijalnog dela **nije ustanovljena**.

**Falsifikacija/validacija:** mali problemi sa poznatim optimumom, namerno proširene referentne granice, ukrštene putanje i potpuna cenzura; nezavisna implementacija proverava rezultat alata. Poređenje sa jednom referencom, EAF prikazom i standardnim intervalima.

**Budžet:** do 1 CPU-sata za arhivirane tragove i 2 za proveru pokrivenosti. **Uslovni GO za gate.** Posebno proveriti postojeću literaturu o simultanim funkcionalnim intervalima; ovo mora prevazići njihovu neposrednu primenu.

**3. Granica praćenja promenljivog optimuma zbog zakašnjenja signala raznovrsnosti — dinamička teorija**

**Pitanje:** koliko star signal raznovrsnosti sme da bude pre nego što adaptivna mutacija izgubi sposobnost praćenja promenljivih infrastrukturnih uslova?

Jansen–Schellbach već analiziraju praćenje na rešetki ([10.1145/1068009.1068152](https://www.cs.york.ac.uk/rts/docs/GECCO_2005/docs/p841.pdf)). Lehre–Qin dokazuju prednost genotipski kodirane samoadaptacije na dinamičkom problemu DSM ([10.1145/3583131.3590494](https://research.birmingham.ac.uk/en/publications/self-adaptation-can-help-evolutionary-algorithms-track-dynamic-op/)). Opšta tvrdnja da samoadaptacija pomaže dinamici već je zauzeta.

**Uža praznina:** praćenje uz mutaciju određenu endogenom raznovrsnošću populacije i eksplicitnom starošću povratne informacije. Cilj je granica verovatnoće izlaska iz prihvatljive udaljenosti od optimuma, zavisna od perioda promene \(K\), kašnjenja \(\ell\), kardinalnosti mreža i veličine populacije.

To je novo pitanje u odnosu na odbačeni statički K6 i topli start, ali **prvenstvo ove formulacije nisam potvrdio**. GAdapt trenutno nema ugovor za evaluacije nad promenljivim okruženjem; on mora biti deo modela.

**Falsifikacija:** dinamički separabilni problemi sa poznatim optimumom; ista politika sa različitim kašnjenjima, podešene fiksne stope i pravovremeno osvežavanje kao kontrola. Dokaz mora predvideti oblast uspešnog praćenja na neviđenim parametrima.

**Budžet:** do 2 CPU-sata sintetike; bez infrastrukturnih simulacija pre dokaza. **Uslovni GO za gate**, visok rizik. Opšta donja granica zbog kašnjenja nije dovoljan doprinos.

**4. Vodovod: vrednost optimizacije neposredno na izvršivim komandama — novi domen**

Pregled Brás i sar. identifikuje nedovoljno proučene formulacije sa promenljivom brzinom pumpi ([10.1016/j.ejor.2024.07.039](https://doi.org/10.1016/j.ejor.2024.07.039)). Dandy i sar. nalaze slabu zastupljenost nesigurnosti u optimizacionim ciljevima ([10.3390/w15010136](https://digital.library.adelaide.edu.au/dspace/handle/2440/137373)). Međutim, robusno upravljanje već postoji, uključujući prilagodljive odluke ([10.1029/2023WR035508](https://doi.org/10.1029/2023WR035508)); uključivanje nesigurnosti nije novina.

**Precizna empirijska hipoteza:** zajednički uticaj diskretnih brzina, minimalnog trajanja rada i nesigurnosti hrapavosti menja ostvarivu cenu i pouzdanost toliko da optimizacija na izvršivom skupu komandi daje bolji rezultat od kontinualne optimizacije praćene diskretizacijom.

GAdapt odgovara reprezentaciji, ali korist njegove adaptacije mora se posebno dokazati. Za mali sistem može se tražiti sertifikovan jaz između kontinualnog i izvršivog optimuma. Nisam proverio da li je upravo ova zajednička analiza već objavljena.

**Falsifikacija:** dve javne EPANET mreže; GAdapt, podešeni fiksni GA, kontinualni solver sa diskretizacijom i jak diskretni/robusni solver. Isti izvršivi skup i nezavisni hidraulički proverivač; scenariji procene odvojeni od razvoja.

**Budžet:** pilot do 12 CPU-sati; prvo kalibrisati cenu evaluacije. **Uslovni GO za domenski gate; NO-GO za tvrdnju da sama primena GAdapt-a predstavlja novu metodu.**

**5. Deljenje prefiksa simulacije između različitih rasporeda — ekonomika evaluacija**

Za determinističku dinamiku \(s_{t+1}=F(s_t,u_t,\xi_t)\), različiti genotipovi mogu deliti isti početni niz komandi. Keširanje kompletnog stanja omogućava ponovno korišćenje prefiksa uz iste konačne troškove i iste adaptivne signale.

**Problem novine:** Santos–Santos već analiziraju keširanje delimičnih proračuna, uključujući prefikse, i daju teoriju troška ([izvorni rad iz 2000.](https://cdn.aaai.org/FLAIRS/2000/FLAIRS00-021.pdf)). Prošireni rad navodi DOI **10.1142/S0218213001000520**; pronašao sam ga u bibliografskim zapisima, ali izdavačev zapis nisam uspeo nezavisno otvoriti.

Preostala moguća tvrdnja zahtevala bi novu granicu troška pod ograničenom memorijom i adaptivno generisanim rasporedima. Jednakost putanje uz tačan keš nije dovoljna.

**Falsifikacija:** porediti punu simulaciju, keš celih genotipova i keš prefiksa; zahtevati identične tragove odluka, pa meriti broj prelaza stanja i memoriju.

**Budžet:** do 4 CPU-sata pilota. **NO-GO u sadašnjem obliku:** koristan inženjerski pravac, suština već postoji.

Za narednih 25 sati prioritet bih dao punom tekstu teorije NrSS i formalnoj lemi za pravac 1. Pravac 2 ostaje rezervni kandidat sa najjeftinijom kasnijom validacijom.