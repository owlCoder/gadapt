Brojevi se poklapaju sa generisanim izveštajima, uz pravilno zaokruživanje: 12.000; 0,0033; 14/21; 0,081 [0,072; 0,090]; 0,010 [0,004; 0,017]; 0,131; 0,178; 0,746; 5/8 i 7/8. Jedina netačna brojčana interpretacija jeste „najniži rep među devet“. `ITERATION64_G_REPORT_SR.md` ne postoji; konačan ishod je upisan u `ITERATION64_G_SPEC.md`.

Nalazi, po ozbiljnosti:

1. **Kritično — prvi red: netačan superlativ i prejaka preporuka.** GAdapt-M ima CVaR 0,0033, ali preset ima niži CVaR: 0,0031 na `orig` i 0,0032 na `shift`. Podela po varijantama i 14/21 su post hoc opisi. „GAdapt je opravdan izbor“, „najbolji rep“ i „konkurentna preciznost“ prelaze dopušteni zaključak S0/CH8.

   **Zamena:** „Na 21 klasičnoj ćeliji S0, među četiri konfiguracije i sa 20 semena, GAdapt-M je imao veći ponderisani ECDF A do 12.000 stvarnih poziva od oba PyGAD-a i DE-a; u post hoc analizi E njegov CVaR₀,₉ iznosio je 0,0033 na originalnim i pomerenim ćelijama, dok je preset imao 0,0031 odnosno 0,0032.“

   **Zamena smernice:** „Na ispitanim osno-poravnatim klasičnim funkcijama nalaz podržava veću efikasnost GAdapt-M prema konkurentima iz S0, ali ne ustanovljava najbolji rep, opštu veću preciznost niti pravilo izbora algoritma.“

   Takođe označiti: „Post hoc, DE ima nižu završnu medijanu u 14/21 ćelija pri izvornom zaustavljanju; pri najviše 12.000 poziva odnos je 10 : 10 : 1.“ [E tabela](/Users/danijel/Desktop/gadapt/research/ITERATION64_E_REPORT_SR.md:79)

2. **Visoko — drugi red: „CMA porodica je pouzdaniji izbor“ nije ustanovljeno.** R poredi samo GAdapt-M i IPOP, meri A, ne opštu pouzdanost, i neizvesnost obuhvata samo semena. Formulacija „E, R: isti pomeraj“ je neprecizna: isti pomeraj izoluje R, ne izvorni E.

   **Zamena:** „U R, na 21 fiksnoj ćeliji i samo dve konfiguracije, uvođenje Haar-ortogonalne matrice Q uz isti pomeraj smanjilo je A GAdapt-M za 0,081 [0,072; 0,090], a IPOP-a za 0,010 [0,004; 0,017]; intervali obuhvataju samo varijaciju 100 algoritamskih semena, ne izbor funkcija, dimenzija, Q ili pomeraja.“

   **Zamena smernice:** „Na tim ćelijama GAdapt-M je bio znatno osetljiviji od IPOP-a na ispitanu ortogonalnu transformaciju; nalaz ne ustanovljava opštu pouzdanost CMA porodice niti univerzalno pravilo izbora.“ [R ograničenja](/Users/danijel/Desktop/gadapt/research/ITERATION64_R_REPORT_SR.md:52)

3. **Visoko — treći red: doprinos faze i odnos prema IPOP-u moraju biti usko formulisani.** A, za razliku od ranijeg Codex 093/E3, sada podržava efekat zamene prve faze, ali samo u fiksiranom hibridu. Ne dokazuje mehanizam ni opštu korisnost GAdapt faze. „Hibrid nije zamena za IPOP“ je preširoko.

   **Zamena:** „U fiksiranom hibridu sa 30% GAdapt-M, 70% CMA-ES i σ₀ = 0,05, zamena prve faze uniformnim slučajnim uzorkovanjem smanjila je A za 0,131 pod ortogonalnom transformacijom i 0,178 na `orig+shift`; time je ustanovljen efekat zamene u ovoj konfiguraciji, uz neizvesnost samo preko semena.“

   **Zamena smernice:** „U ovom fiksiranom hibridu GAdapt faza nije bila zamenljiva uniformnim slučajnim uzorkovanjem; neinferiornost prema IPOP-u na sintetičkim ćelijama nije potvrđena, a na ORPD-u hibrid nije bio dokazano bolji od GAdapt-M i imao je lošiji rep od IPOP-a.“ [A ograničenja](/Users/danijel/Desktop/gadapt/research/ITERATION64_A_REPORT_SR.md:29)

4. **Srednje — ORPD: „konkurentna opcija“ je preskriptivnije od neodlučenog H64c.** Broj 0,746 i poređenja izvodljivosti jesu tačni, ali nedostaju tri mreže, 30 semena, dve skoro potpuno neizvodljive ćelije i zavisnost agregata od preostalih šest.

   **Zamena:** „Na osam ORPD ćelija iz tri mreže, sa 30 semena, GAdapt-M je imao izvodljivost 0,746 i bio je dokazano bolji od oba PyGAD-a i DE-a u toj meri; razlike prema CMA, IPOP i BIPOP nisu razrešene, H64c je neodlučena, a agregat zavisi pretežno od šest ćelija.“  
   
   **Zamena smernice:** „Nalaz ne daje osnov za preporuku GAdapt-M umesto CMA porodice niti za tvrdnju o industrijskoj spremnosti.“ [CH8 ORPD](/Users/danijel/Desktop/gadapt/research/thesis/CH8_MENTOR_BENCHMARK_SR.md:65)

5. **Niže — κ red je suštinski ispravan, ali nepotpun.** Razvojni odnos u E bio je post hoc; prag je zahtevao oba rezultata ≥6/8, a dve gotovo neizvodljive ćelije uključuju beskonačne medijane.

   **Zamena:** „Razvojni nalaz za κ u E bio je post hoc; preregistrovana ORPD predikcija dala je 5/8 ćelija po CVaR-u i 7/8 po medijani prema pragu 6/8 za oba ishoda, pa je ukupni ishod neodlučen i κ se ne koristi kao selektor algoritma.“ [G ishod](/Users/danijel/Desktop/gadapt/research/ITERATION64_G_SPEC.md:17)

Dodatna kontradikcija je u §9.4: „sprega → CMA/hibrid; osno poravnanje → GAdapt“ ponovo uvodi upravo selektor koji tabela ne dokazuje. Zameniti sa: „Da li industrijski problemi imaju spregu promenljivih i koje su dodatne instance potrebne za poređenje GAdapt-a, CMA porodice i hibrida; sadašnji nalazi ne opravdavaju izbor algoritma samo prema spregnutosti ili osnom poravnanju.“