# Poglavlje 1. Uvod: problem, istraživačka pitanja i doprinosi

*Nacrt, 24. oktobar 2026. Usklađeno sa završenim I56–I61, I63 STOP i S0/E/E2/E3; I64-I/I2 i E4 su završene; I63-D ostaje otvorena deskriptivna ekstenzija.*

## 1.1 Problem

Planiranje i vođenje infrastrukture, elektroenergetskih i telekomunikacionih mreža pre svega, sve češće se
oslanja na optimizaciju u kojoj je funkcija cilja simulator: proračun toka snage, rešavanje problema rutiranja,
proračun pouzdanosti. Takvi problemi imaju tri zajedničke osobine. Odluke su često diskretne, jer se uređaji
podešavaju u koracima i oprema dolazi u modulima. Svaka evaluacija košta, pa je budžet izražen brojem poziva
simulatora, a ne vremenom procesora. I, možda najvažnije, veliki deo prostora odluka je neizvodljiv, pa je
pronalaženje izvodljivog rešenja često teže od njegovog poboljšanja.

Genetski algoritmi su na ovakvim problemima popularni upravo zato što ne zahtevaju gradijente, prirodno rade sa
diskretnim vrednostima i lako primaju proizvoljan simulator. GAdapt je biblioteka samoadaptivnog genetskog
algoritma koja svoje parametre, broj mutiranih jedinki, broj mutiranih promenljivih i širinu mutacije, prilagođava
na osnovu raznovrsnosti populacije. Cilj ove disertacije je da utvrdi gde se GAdapt-ov pristup susreće sa
stvarnim potrebama infrastrukturne optimizacije i da biblioteku za te potrebe unapredi na proverljiv način.

## 1.2 Kako je istraživanje dobilo svoj oblik

Disertacija nije počela pitanjem kojim se završava, i to je važno za njeno tumačenje. Prva faza bila je
dijagnostička: na izboru ruta i na AC ekonomskom dispečingu GAdapt je zaostajao za jednostavnijim i za
naprednijim metodama, na dispečingu i za nekoliko redova veličine iza CMA-ES. Poglavlje 2 sumira šta je ta
dijagnostika pouzdano utvrdila, a šta nije. Prirodan sledeći korak, popravka zaostatka u konvergenciji, pokazao se
kao istraživački ćorsokak: za svaki proveren predlog, od kontrole koraka iz rasipanja do učenja korelacija,
postoje objavljeni radovi koji ga već sadrže. Više kandidata za novu metodu odbačeno je pre
implementacije, svaki sa proverenim izvorima (tačan broj navesti samo uz zaseban trag kandidata). Istraživanje je preusmereno na kontrolisano ispitivanje GAdapt-a; originalnost tačne faktorske kombinacije ostaje nepotvrđena.

Pregled iz 2025. godine o metaheurističkom optimalnom toku snage beleži da malo radova ispituje kako tehnike za
rukovanje ograničenjima i podešavanje parametara utiču na rad metaheuristika. Na diskretnim kontrolama, gde je
izvodljivost teška, to pitanje je za GAdapt posebno oštro: njegova samoadaptacija čita vrednosti troškova, pa
način na koji se neizvodljivost pretvara u broj direktno ulazi u njegove signale.

## 1.3 Istraživačka pitanja

**IP1.** Da li efekat adaptivne naspram podešene fiksne politike mutacije zavisi od tehnike za ograničenja na diskretnom problemu raspodele reaktivne snage, i da li intervencije nad skalarnim signalima menjaju ishod? (Dizajn ne identifikuje posredovani udeo; H56b nije podržana.) (Poglavlja 3 i 4, studija I56.)

**IP2.** Gde se GAdapt na tom problemu nalazi u odnosu na jake metode za mešovito celobrojnu optimizaciju crnih
kutija pri istom budžetu simulacija? (Poglavlje 5, studija I57, opisno.)

**IP3.** Da li ugrađeni FR i ε smanjuju ograničeni broj simulacija do cilja prema kazni f + 1000V na ispitanim ORPD instancama, i može li se sprovesti unapred planirana telekom provera? I58 i I60 nisu potvrdile korist; I59 je zaustavljen u razvoju. (Poglavlje 6 i studije I58 i I59, konfirmatorno.)

## 1.4 Doprinosi

Doprinosi su empirijski i inženjerski; disertacija ne tvrdi novu optimizacionu metodu.

1. **Eksperimentalni instrumenti** sa evidentiranjem poziva, zamrznutim protokolima i zasebnim proverivačima; ORPD
   studije su završene (I63-D je deskriptivna i otvorena), dok je telekom instrument stigao do razvojnog NO-GO. Potpuna ponovljivost nezavisnim
   izvršavanjem nije ustanovljena.
2. **Kontrolisana procena interakcije** tehnike za ograničenja i GAdapt-ove samoadaptacije (IP1). Interakcija
   ograničenja i adaptacije je u evolutivnim strategijama poznata; doprinos je specifična, kontrolisana
   intervencija na GAdapt-u, čiji prioritet nije dokazan. Ishod se prijavljuje kakav god da je, uključujući i
   „interakcija nije otkrivena pri ovoj snazi“.
3. **Opt-in rukovanje ograničenjima u biblioteci GAdapt** (četiri standardne tehnike, tačan izbor preživelih,
   izveštavanje najboljeg izvodljivog rešenja, bit-identično podrazumevano ponašanje), sa konfirmatornom
   proverom korisnosti (IP3). Uz H58 = N, H60 = N i nedostupan H59, opcija ostaje proverena inženjerska funkcionalnost bez potvrđenog ubrzanja.
4. **Dijagnostički nalazi o stvarnom mehanizmu GAdapt-a** koji menjaju način na koji ga treba koristiti i
   upoređivati: skriveni probni pozivi, raspon kao mera raznovrsnosti, stvarna pravila broja mutiranih promenljivih
   i kolaps Gausove mutacije na diskretnim mrežama.

## 1.5 Šta disertacija ne tvrdi

Ne tvrdi da je GAdapt bolji od CMA-ES ili drugih metoda uopšte, niti na konkretnoj industrijskoj mreži. Mreže
vrednosti uređaja, opsezi šantova i telekom moduli su pretpostavke modelovanja, a javni slučajevi nisu dokaz
rada u stvarnoj proizvodnji. Rezultati važe za proučene mreže, budžete i konfiguracije, i svaki se prijavljuje
sa svojim pretpostavkama i ograničenjima.
