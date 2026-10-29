**Sada postoji osnova za empirijsku disertaciju, ali još nema dovoljno dokaza da se bezuslovno proglasi završenim doktorskim doprinosom.** Četiri otvorene studije ostaju bez pretpostavljenog ishoda.

**1. Najjača odbranjiva formulacija doprinosa sada**

„Disertacija daje novu, ograničenu empirijsku karakterizaciju GAdapt-a i pouzdanosti njegovog poređenja sa drugim optimizatorima: instrumentovanom replikacijom i preregistrovanim proširenjem mentorovog eksperimenta razdvaja efikasnost po stvarnom broju evaluacija, završnu tačnost i rizik loših ishoda, te pokazuje da njihovo rangiranje zavisi od metrike i ispitane transformacije problema. Kontrolisane ORPD studije utvrđuju lokalnu interakciju politike mutacije i rukovanja ograničenjima, uz jasno dokumentovane granice prenosa. Doprinos obuhvata i implementaciju alata za proveru odabranih svojstava izvršavanja optimizacionih biblioteka, konkretne dijagnostičke nalaze i negativne rezultate intervencija. Originalnost se nalazi u prikupljenim dokazima, njihovoj sintezi i preciziranju granica ranijih tvrdnji; ne tvrdi se nova optimizaciona metoda, teorema ili prvenstvo samih evaluacionih postupaka.“ Osnova: [CH8](/Users/danijel/Desktop/gadapt/research/thesis/CH8_MENTOR_BENCHMARK_SR.md), [CH4](/Users/danijel/Desktop/gadapt/research/thesis/CH4_CHT_ADAPTATION_RESULTS_SR.md) i [revizija integriteta](/Users/danijel/Desktop/gadapt/research/paper_integrity_audit/manuscript.md).

**Ne sme tvrditi:**

- „GAdapt nadmašuje sve osim jednog algoritma“ kao potvrđen opšti zaključak. S0 podržava usku operacionalizaciju; E daje suprotan ishod zamrznutog pravila. Naknadno grupisanje tri CMA konfiguracije nije potvrda.
- Opštu veću tačnost ili stabilnost, dominaciju na većini problema, industrijsku spremnost ili pouzdanu procenu veoma retkih otkaza.
- Da rotacija ili odsustvo učenja korelacija predstavljaju izolovan uzrok: shift/rot koriste različite pomeraje; osno poravnanje nije separabilnost.
- Da je κ validiran selektor algoritma; čak ni uspešne P-G1/P-G2 to ne bi ustanovile.
- Da je H56a opšta ili replicirana; da I61/I63 STOP opovrgavaju interakciju; da nepotvrđena korist znači ekvivalenciju.
- Novinu diferencijalnog operatora, hibrida, kompenzacione mutacije, brojanja evaluacija ili sprege CHT–adaptacija. Auditi H3–H8 ograničavaju te tvrdnje.
- Da E3 dokazuje doprinos GAdapt faze: ukupni kriterijum nije ispunjen, a 70% budžeta troši CMA.

**2. Rečenice prema budućim ishodima**

Koristiti ih tek posle završenih provera i konačne analize, sa imenovanom merom i konfiguracijom.

- **I64-I: CMA bolji na ORPD-u:** „Na osam ispitanih ORPD ćelija, pri 12.000 stvarnih PF evaluacija, [CMA konfiguracija] ima niži CVaR od GAdapt-M prema simultanim intervalima, uz [zaseban nalaz izvodljivosti]; sintetička agregatna prednost GAdapt-a ne prenosi se uniformno.“
- **I64-I: H64c podržana:** „GAdapt-M zadovoljava unapred zadati kriterijum konkurentnosti: izvodljivost nije slabija za više od pet procentnih poena prema svim konkurentima, a CVaR je niži prema najmanje četiri od osam konfiguracija.“ To nije dominacija nad CMA.
- **I64-I: mešovito/neodlučeno:** „Rezultati pokazuju zavisnost od ćelije i mere, bez ispunjenog kriterijuma koji opravdava jedinstvenu preporuku.“ Slične tačkaste ocene nisu ekvivalencija.

- **I64-I2: hibrid bolji od GAdapt-a i IPOP-a:** „Hibrid smanjuje CVaR prema obe referentne konfiguracije bez nedozvoljenog gubitka izvodljivosti na ispitanom ORPD skupu; rezultat pripada hibridu, dok zaseban doprinos GAdapt faze ostaje neidentifikovan.“
- **I2: bolji samo od GAdapt-a:** „Prenos koristi hibridizacije prema GAdapt-M je podržan, ali prednost prema IPOP-u nije ustanovljena.“
- **I2: suprotno/neodlučeno:** „ORPD provera pokazuje štetu po [meru]“ odnosno „ne razrešava korist hibrida“; nijedno ne opravdava opštu preporuku.

- **I63-D: istosmeran rezultat:** „Deskriptivna ekstenzija pokazuje obrazac saglasan sa lokalnim nalazom I56, pri drugačijem estimandu; konfirmatorna replikacija nije ostvarena.“
- **I63-D: suprotan:** „Deskriptivna procena ima suprotan smer, što ograničava prenos lokalnog nalaza.“
- **I63-D: mali/neprecizan:** „Procena ukazuje na mali efekat pri ovom estimandu“ odnosno „ostaje nedovoljno precizna za razrešenje smera“. Informativni interval ekvivalencije ne obnavlja H63.

- **E4: k1–k4 podržane:** „Kompenzaciona opcija ispunjava unapred zadate kriterijume poboljšanja i kontrolnih poređenja na ovom sintetičkom skupu; algoritamska originalnost i industrijska korist nisu ustanovljene.“ k5 prijaviti zasebno.
- **E4: delimično pozitivna:** „Opcija poboljšava [ishod], ali ne ispunjava sve kriterijume korisnosti i kontrolnih poređenja.“ Ako ne nadmaši `resample`, nema dokaza prednosti nad tom poznatom konstrukcijom.
- **E4: negativna/neodlučena:** „Preregistrovana provera pokazuje pogoršanje [mere]“ odnosno „ne ustanovljava korist; rezultat ostaje neodlučen.“

E4 zahteva ispravljenu `resample` kontrolu iz dopune A1. `Permuted` poređenje ne izoluje samo ispravnost povezivanja koordinata; `ungated` je opisna kontrola. [Specifikacija E4](/Users/danijel/Desktop/gadapt/research/ITERATION64_E4_SPEC.md)

**3. Da li je to dovoljno za doktorat i dve publikacione jedinice**

**Moguće jeste; sada to nije dokazano.** Originalna metoda nije obavezan oblik originalnog znanja. Uobičajeni kriterijumi traže značajan originalni doprinos, metodološku sposobnost, koherentnu argumentaciju i rezultate vredne recenzije i objavljivanja. To ilustruju [QAA](https://www.qaa.ac.uk/the-quality-code/characteristics-statements/characteristics-statement-doctoral-degrees) i [Bristol](https://www.bristol.ac.uk/academic-quality/pg/code-of-practice/assessment/award-criteria/); nisu zamena za merodavne FTN uslove.

Ovde je proceduralna transparentnost jaka, ali ograničene instance, konfuzije transformacija, nereplikovana interakcija i greška kalibracionog dizajna ograničavaju zaključke. Preregistracija i veliki broj pokretanja sami ne stvaraju značaj. Ni 16 odbačenih kandidata nije pozitivan doprinos.

Dve najodbranjivije publikacione jedinice su **kandidati za razvoj, ne dva spremna rada**:

1. **Granice efikasnosti, tačnosti i rizika GAdapt-a pri stvarnom budžetu evaluacija.** S0/E/E2/E3, uz završene infrastrukturne provere. Cilj: **Evolutionary Computation**, koji objavljuje empirijska istraživanja; za rad usredsređen na ORPD, **Energies** ima neposredan domenski fit. [ECJ](https://mitpress.mit.edu/a-conversation-with-emma-hart-editor-of-evolutionary-computation/), [Energies](https://www.mdpi.com/journal/energies/about). Nedostaju nezavisne problem-instance, poređenje sa jačim diskretnim/adaptivnim konkurentima, kontrola istog pomeraja za tvrdnju o rotaciji i ablacija inicijalizacije hibrida za atribuciju. Bez toga tvrdnju treba suziti.

2. **Proverljivost izvršavanja optimizacionih biblioteka i granice revizije iz tragova.** Studije 21 konkretne bibliotečke konfiguracije i alat. **TELO** je tematski moguć zbog reproduktivnosti i evaluacione metodologije, što potvrđuje [objavljen rad](https://doi.org/10.1145/3466624). Potrebni su jasna centralna teza, legitimne negativne kontrole, potpunija validacija detektora i dokaz vrednosti preko običnog logovanja. Interni pregled #15 već je odbacio sadašnji oblik; rukopis je zatim zadržan kao interni dokument. Povratak na njega traži odluku o obimu, a ne kozmetičko doterivanje.

**4. Pet teza za sastanak**

1. „Koji algoritam je taj jedan izuzetak i na kojim problemima ste to videli? Molim konfiguracije, budžete i tabelu rezultata.“
2. „Da li stabilnost znači ponovljivost istog semena, mali raspon između pokretanja ili mali rizik lošeg rešenja? Koje numeričke pragove prihvatamo?“
3. „S0 podržava usku tvrdnju o efikasnosti; E je ograničava. Koji nalaz bi promenio Vašu ocenu primenljivosti?“
4. „Prihvatate li empirijski doktorat o granicama primenljivosti GAdapt-a, sa negativnim rezultatima, ili zahtevate originalnu metodu? Molim eksplicitnu odluku o obimu i prihvatljivom završnom doprinosu.“
5. „Koje dve publikacione jedinice podržavate, koje formalne uslove moraju ispuniti i koji minimalni dodatni dokaz tražite pre završetka?“

**5. Preostale nedelje — redosled**

1. Završiti četiri postojeće studije bez menjanja kriterijuma; proveriti kompletnost, svedoke, heševe i poreklo rezultata.
2. Nezavisno reprodukovati analize; odvojiti podržano, suprotno, neodlučeno, STOP i deskriptivno.
3. Usaglasiti sa mentorom obim, kriterijume i publikacioni plan pre novih istraživačkih grana.
4. Izabrati najviše jednu ciljanu dopunu prema glavnoj tvrdnji: kontrolisana transformacija, ablacija hibrida ili jači ORPD konkurent.
5. Uskladiti CH1–CH8 i sažetak; ukloniti zastarele statuse i preširoke formulacije.
6. Napisati radove oko istraživačkih pitanja, pripremiti reprodukcioni paket i dokumentovati granice upotrebe biblioteke.
7. Ako mentor zahteva novu metodu, odmah priznati da sadašnji paket taj zahtev ne ispunjava i dogovoriti novi rok; prestati sa serijskim dodavanjem operatora.