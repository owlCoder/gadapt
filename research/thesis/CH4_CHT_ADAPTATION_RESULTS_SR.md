# Poglavlje 4. Rukovanje ograničenjima i samoadaptacija: rezultati

*Nacrt, 24. oktobar 2026, posle studije I56 (protokol zamrznut 3f09eb9, izveštaj ITERATION56_REPORT_SR.md; svi
brojevi nezavisno preračunati iz sirovih zapisa).*

## 4.1 Šta je izvršeno

Studija je izvršena jednom, prema zamrznutom protokolu. Na tri mreže, tri rezolucije kontrola i preostalim test
scenarijima izvedeno je 300 uparenih jedinica sa po šesnaest grana, ukupno 4800 pokretanja po 3000 proračuna toka
snage. Svako pokretanje je završeno uredno, bez ponavljanja i bez grešaka, pa nijedna jedinica nije izuzeta, a
analiza osetljivosti nije bila potrebna. Za četiri instance najmanje rezolucije referentna pokretanja nisu našla
izvodljivo rešenje, pa je tamo cilj, po unapred zadatom pravilu, bila sama izvodljivost.

## 4.2 Primarni rezultat

Unapred zadati kontrast interakcije iznosi θ_a = +0,021, sa 95% intervalom [0,002; 0,040] (p = 0,03). Po pravilu
iz protokola hipoteza je podržana. Znak znači sledeće: razlika u vremenu do cilja između podrazumevane GAdapt
adaptacije i fiksne politike podešene na razvojnim scenarijima veća je, odnosno nepovoljnija za adaptaciju, pod
Deb-ovim pravilima izvodljivosti nego pod statičkom kaznom.

Brojka sama po sebi bi zavela, pa je važno pokazati odakle dolazi. U šest od devet blokova, na mrežama sa 57 i
118 sabirnica, nijedna od četiri grane koje ulaze u kontrast nije dostigla cilj u 3000 proračuna. U tim blokovima
kontrast nema nikakvu varijabilnost i doprinosi nulom; procena je zato u praksi zasnovana na mreži sa 14
sabirnica. Tamo je slika jasna: pri 17 nivoa kontrola fiksna politika pod pravilima izvodljivosti dostiže cilj u
85% pokretanja, a podrazumevani GAdapt u 40%; pod kaznom je odnos 57,5% prema 42,5%. Fiksna politika je, dakle,
bolja od podrazumevane adaptacije pod obe tehnike, ali znatno više pod pravilima izvodljivosti. Ako se iz analize
izostavi samo taj blok, procena pada na 0,012, a interval obuhvata nulu; to je opisna provera, ne deo protokola,
ali pokazuje koliko je rezultat krhak. Efekat je mali, reda dva procenta budžeta.

## 4.3 Sekundarni rezultati i mehanizam

Nijedan od pet sekundarnih kontrasta nije statistički značajan posle Holm-ove korekcije. Najvažniji među njima,
zamena vrednosti koje GAdapt-ovi signali čitaju zajedničkim skalarom pod statičkom kaznom, ne pokazuje merljiv
efekat, kao ni transformacija kazne koja čuva poredak, a menja vrednosti. Ovo ne dokazuje da put „vrednost troška
u signalu“ ne postoji; pokazuje samo da ga ova studija nije mogla da izmeri. Za interakcije adaptivne kazne i ε-ograničenja sa adaptacijom i za primarni kontrast sa medijanski usklađenom (umesto podešene) fiksnom politikom nije utvrđena statistička značajnost posle Holm-ove korekcije; jednakost nuli nije dokazana.

## 4.4 Opisni nalaz koji nije bio hipoteza

Najupečatljivija razlika u podacima nije interakcija, već glavni efekat tehnike. Na mreži sa 14 sabirnica, pri 17
i 33 nivoa kontrola, ε-ograničenje skraćuje srednje vreme do cilja podrazumevanog GAdapt-a sa 0,77 i 0,82 (pravila
izvodljivosti) na 0,28 i 0,39, i dostiže cilj u 37 i 36 od 40 pokretanja. Na mreži sa 57 sabirnica ε-ograničenje
retko dostiže cilj, a cilj tamo povremeno dostižu i dve druge grane. ε-ograničenje nije uniformno najbolje: pri
najgrubljoj rezoluciji ni ono ne pomaže. Ovaj nalaz nije bio predmet preregistrovane hipoteze i ne sme se
tumačiti konfirmatorno; on je kandidat za sledeću preregistrovanu proveru. Konfirmatorna validacija ugrađene
opcije (studija I58) zamrznuta je sa pravilima izvodljivosti pre ovih rezultata i ostaje takva.

## 4.5 Šta ovo znači i šta ne znači

Prvo, na case14/R = 17 podešena fiksna politika imala je veći opaženi udeo dostizanja od podrazumevane adaptacije pod FR i SP, uz veću razliku pod FR; nema potvrđenog univerzalnog rangiranja politika. To je
konkretan, proverljiv nalaz o samoj biblioteci, u skladu sa ranijim zapažanjem da Gausova mutacija na diskretnim
mrežama brzo pada na minimalnu širinu (poglavlje 3, kalibracija).

Drugo, za tvrdnju o interakciji: ona je statistički podržana, ali mala i zasnovana na jednoj mreži, pa je ispravno
nazvati je nalazom o case14, a ne opštim svojstvom. Treće, pri 3000 poziva kontrast je bio degenerisan na većim mrežama. I59 nije pronašao prihvatljiv razvojni par; I61 pokušava razvojni izbor informativnog budžeta, uz mogućnost STOP-a. Razvojno pravilo ne garantuje uspeh. Opisni ε nalaz ostaje tačan, ali njegov prenos nije potvrđen u I60. Najzad, zaključci su uslovni na zamrznute reference, kalibracione konstante i
scenarije, a pretpostavke modela (mreže vrednosti, opsezi, scenariji) su navedene u poglavlju 3.
