**Prvo bih ispitao kompenzacionu mutaciju, zatim izbor celih kombinacija operatora; nasumične rotacije stavio bih poslednje.** Nijedan kandidat trenutno nema dokazanu metodološku novinu. Ovde **GO znači samo opravdanost detaljnijeg prior-art audita**, bez odobrenja implementacije ili tvrdnje o doprinosu.

Pročitao sam E/E2/E3, poslednje zapise napretka, obe IDEATION liste, H3–H8 i raniji audit rotacionih operatora. Predlozi ispod predstavljaju konkretne, dosad neispitane zahvate u GAdapt-u. Generičko „dodaj kovarijansu“, spektralnu restauraciju i postojeći UCB ne vraćam kao nove ideje.

**1. Kompenzaciona mutacija koja čuva lokalne veze — prvi izbor**

**Mehanizam.** Posle standardnog mutacionog pomaka \(\delta_i\), dodati pomak najviše jednoj povezanoj koordinati:

\[
\delta_j=\operatorname{clip}\!\left(
\frac{\widehat C_{ji}}{\widehat C_{ii}+\varepsilon},-2,2
\right)\delta_i .
\]

Kovarijansa se procenjuje iz trenutnih elitnih jedinki, u koordinatama normalizovanim opsezima. Partner \(j\) prihvata se samo ako dve deterministički razdvojene polovine elite daju isti znak korelacije i obe imaju \(|\rho_{ij}|\ge0,5\). Parovi su disjunktni; broj promenjenih koordinata ima eksplicitan limit. Procena se obnavlja svake generacije. Nema dodatnih evaluacija cilja.

Hipoteza: standardna mutacija razbija korisne zavisnosti; kompenzacija omogućava pomeranje duž njih. Elitna korelacija ipak može nastati selekcijom ili mešanjem basena, pa je pouzdanost procene sastavni deo kandidata.

**Najbliži prior art.** Andreadis, Alderliesten i Bosman, *Fitness-based Linkage Learning and Maximum-Clique Conditional Linkage Modelling…* (2024), DOI **[10.1145/3638529.3654103](https://ir.cwi.nl/pub/34532/34532.pdf)**. Rad koristi uslovne modele, zajedničku varijaciju povezanih promenljivih i korake koji mogu obnoviti narušene veze. Širi prethodnik, kovarijansom vođena mutacija posle GA krosovera, već je identifikovan u lokalnom auditu.

**Tačna razlika za proveru.** Očuvanje izvornog GAdapt pomaka i dodavanje ograničene determinističke kompenzacije, dozvoljene samo kroz proveru saglasnosti dve procene. RV-GOMEA uzorkuje vrednosti iz uslovnih raspodela i koristi GOM prihvatanje; ovde ostaju GAdapt populaciona selekcija i mutacioni signali. To može biti samo restriktivna varijanta poznatog uslovnog uzorkovanja — taj rizik je velik.

**Dvodnevna falsifikacija.** Dan 1: izolovana implementacija i zamrzavanje navedenih konstanti. Dan 2: zajednički test ispod, sa kontrolama: standardni GAdapt; kompenzacija bez provere saglasnosti; pomaci istih dužina i istog broja koordinata sa nasumično permutovanim partnerima. Ako permutovana kontrola daje istu korist, hipoteza o iskorišćavanju veza nije podržana.

**Gate: uslovni GO**, isključivo za audit ove kompenzacione zakonitosti. Ako se svodi na postojeći conditional-GOM/regresioni operator sa pragom pouzdanosti, **NO-GO kao nova metoda**. Praktična vrednost može ostati.

**2. Bandit bira celu kombinaciju krosovera i mutacije — drugi izbor**

**Mehanizam.** Jedna odluka po potomku bira jednu od četiri kombinacije:

- koordinatni blending ili aritmetički krosover sa jednim zajedničkim \(\alpha\) za ceo vektor;
- postojeća mutacija ili kompenzaciona mutacija iz kandidata 1.

Svaka kombinacija dobija jednu Bernulijevu nagradu: evaluirani potomak strogo poboljšava boljeg roditelja. Klizni prozor sadrži poslednjih 64 evaluirana potomka; svaki krak ima minimalnu verovatnoću izbora 0,1. Neevaluirani predlozi ne dobijaju nagradu. Pripisuje se uspeh kombinaciji, bez tvrdnje o izolovanom uzročnom efektu mutacije.

**Najbliži prior art.** Fialho i saradnici, *Analyzing bandit-based adaptive operator selection mechanisms* (2010), DOI **[10.1007/s10472-010-9213-y](https://link.springer.com/article/10.1007/s10472-010-9213-y)**, već obrađuju dinamički UCB i klizne prozore. Noviji primer je Bajpai i saradnici (2024), *Dynamic Mutation Strategy Selection…*, DOI **[10.1007/s42979-024-03062-2](https://link.springer.com/article/10.1007/s42979-024-03062-2)**.

**Tačna razlika.** Postojeći GAdapt kontroler bira skalarni mutator pri promeni pojedinačne promenljive. Predlog bira celu putanju varijacije potomka i može naučiti kompatibilnost krosovera i korelisane mutacije. Postojeći `paired` režim već evaluira nemutiranog potomka; takvu kontrolu ne predstavljam kao novinu.

**Dvodnevna falsifikacija.** Dan 1: povezivanje četiri kraka i trag njihovih izbora. Dan 2: zajednički test, uz uniformni izbor iste četiri kombinacije, postojeći UCB i sve četiri fiksne kombinacije. Adaptivnost mora nadmašiti uniformni izbor po \(A_{\rm rot}\), uz očuvan rep. Ako pomaže samo jedan fiksni krak, poboljšanje pripada operatoru; razlog za bandit slabi.

**Gate: NO-GO za novi metodološki audit u ovom obliku.** Atomski krakovi koji predstavljaju kombinacije operatora spadaju u poznati AOS okvir. Inženjerski je smislen, naročito posle eventualnog uspeha kandidata 1, ali promena granularnosti odluke nije dovoljan diferencijator.

**3. Nasumična baza po restartu — treći izbor**

**Mehanizam.** Četiri unapred raspoređena GAdapt restarta po 3.000 evaluacija. Svaki dobija nezavisnu Haar-ortogonalnu bazu; krosover, mutacija i statistike koordinata rade u toj bazi. Fenotip i evaluacija ostaju u izvornom domenu. Dozvoljeni skup u novim koordinatama jeste rotirani poliedar: ograničeno ponovno uzorkovanje mora proveravati izvorne granice. Aproksimacija tog skupa običnom kutijom promenila bi problem.

**Najbliži prior art.** Hansen, *Adaptive Encoding…* (2008), DOI **[10.1007/978-3-540-87700-4_21](https://link.springer.com/chapter/10.1007/978-3-540-87700-4_21)**, daje opšti okvir promene predstavljanja. ACoS, Liu i saradnici, DOI **[10.1109/TCYB.2018.2802912](https://repository.essex.ac.uk/21658/7/08314547.pdf)**, kombinuje izvornu i naučenu bazu uz povratnu spregu uspeha. To su srodni prethodnici; identičan protokol nasumičnih restarta nisam potvrdio.

**Tačna razlika.** Baze se biraju bez podataka i menjaju pri svakom restartu; nema jednokratnog PCA izbeljivanja iz neuspele razvojne probe. Međutim, slučajna rotacija ne smanjuje uslovljenost i ne garantuje korisno poravnanje. Uklanjanje privilegovane orijentacije nije isto što i konkurentnost na spregnutom problemu.

**Dvodnevna falsifikacija.** Uporediti četiri nasumične baze, četiri identične baze i jednu nasumičnu bazu sa svih 12.000 poziva. Time se razdvajaju efekti orijentacije i deljenja budžeta. Meriti i odbijanje predloga zbog granica.

**Gate: NO-GO.** Slaba osnova za metodološku novinu i slabiji mehanistički razlog za očekivani napredak.

Za svaki eventualno odobren dvodnevni eksperiment koristio bih **21 E rot ćeliju, 100 novih semena, 12.000 stvarnih poziva**, iste transformacije i težine E2; dodatnih 42 orig/shift ćelije proveravaju štetu. Kontrole GAdapt-M i IPOP izvršavaju se na istim novim semenima. Unapred zamrznuti zahtevi: pozitivan \(\Delta A_{\rm rot}\), najmanje 20% niži CVaR, neinferiornost prema IPOP-u po \(A\) sa marginom 0,05 i E2 tolerancije štete na nerotiranim ćelijama. Koristiti jednu simultanu porodicu intervala za sve testirane tvrdnje. Ovo ostaje screening poznatih problema, bez dokaza industrijske primenljivosti.

Sve opcije zahtevaju isključenu podrazumevanu granu bez novih RNG poziva i proveru identičnosti tragova. Rad ostaje u izolovanoj kopiji dok postojeći lanci rade.

**Bibliografska ispravka:** `e3_algo.py` pripisuje Hansenu DOI koji završava sa `_20`; proveren ispravan završetak je **`_21`**. Fajlove nisam menjao niti pokretao eksperimente.