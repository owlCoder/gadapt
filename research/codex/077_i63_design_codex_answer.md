**GO za jednu konačnu, ograničenu konceptualnu replikaciju H56a.** Predlažem I63 sa kvalitetom pri zajedničkom fiksnom budžetu i uparenim skorom pobede. Njena vrednost je provera prenosivosti interakcije iz I56 i mogućnost informativnog zatvaranja tog pravca. Kao nova optimizaciona metoda ili samostalna okosnica doktorske originalnosti: **NO-GO**.

Ovo je nacrt za prospektivno zamrzavanje; ništa nije menjano niti pokretano.

**Osnov za promenu.** U [sirovim podacima I61](/Users/danijel/Desktop/gadapt/research/results/iteration61/select_b.json.gz) svih 60 razvojnih pokretanja ima izvodljivo završno rešenje. Ipak, case30/j=0 ima 0/10 dostizanja cilja, a case39/FR/j=1 ima 0/5. Dakle, nedostizanje cilja ovde skriva razlike među izvodljivim rešenjima. Postoji i suprotan problem: na case30/j=1 završni gubici gotovo su identični. Novi dizajn zato mora prepoznati i nedostižnost cilja i zasićenje završnog kvaliteta.

Od četiri kandidata biram poboljšanu varijantu **(ii)**:

- **(i) Kvantilni cilj:** načelno dopušten uz nezavisan pilot, ali medijana završnog kvaliteta pilot-poola ne garantuje informativna vremena dostizanja u četiri potvrdne grane. Zahteva i pravilo prenosa cilja na nove scenarije; pilot svakog potvrdnog scenarija menja domet nezavisnosti.
- **(ii) Fiksni budžet:** uklanja zahtev da jedan cilj bude dostižan u odgovarajućem vremenskom prozoru. Biram ga uz eksplicitno kodiranje neizvodljivosti i poređenje unutar scenarija.
- **(iii) ECDF-površina:** razumna alternativa, ali uvodi izbor ciljeva, njihovih težina i vremenske skale. Neinformativni ciljevi i dalje mogu dominirati površinom. Ne biram je kao dodatni primarni ishod.
- **(iv) Budžet po scenariju:** može izjednačiti težinu zadataka, ali menja računarsku intervenciju između scenarija i traži dodatnu kalibraciju. Za ovu završnu proveru nije potreban.

Fiksni budžeti i ECDF nisu metodološka novina; njihovo razlikovanje već je deo [COCO metodologije, DOI 10.1080/10556788.2020.1808977](https://www.tandfonline.com/doi/full/10.1080/10556788.2020.1808977). Poređenja CHT na ORPD-u takođe postoje: [Mallipeddi i sar., DOI 10.1016/j.swevo.2012.03.001](https://www.sciencedirect.com/science/article/pii/S2210650212000247). Precizna nova informacija I63 bila bi unapred definisana provera GAdapt interakcije na novim realizacijama scenarija, drugim estimandom. Prioritet te kombinacije nije ustanovljen; ne tvrdi se nova metoda niti nova teorema.

**Estimand.** Sve grane troše tačno \(B=12\,000\) stvarnih PF poziva. Za mrežu \(i\), scenario \(j\), seme \(s\), politiku \(a\) i CHT \(c\):

\[
G_{ijsc}^{a}=
\begin{cases}
(f_{\mathrm{best,feas}}^{a,c}(B)-r_{ij})/r_{ij},&
\text{ako postoji izvodljivo rešenje},\\
+\infty,&\text{inače},
\end{cases}
\]

gde je \(r_{ij}>0\) gubitak kontinualnog OPF-a tog scenarija, već potreban instrumentu. To je normalizator, **ne sertifikovani optimum**; negativni jazovi ostaju dozvoljeni. Nova referentna optimizaciona pokretanja nisu potrebna.

Za svaki upareni AD-N/FX-T par definiše se \(W_c\):

- \(1\): FX-T je izvodljiv, a AD-N nije; ili su oba izvodljiva i \(G^{AD}-G^{FX}>0,001\);
- \(0\): simetričan ishod u korist AD-N;
- \(1/2\): oba su neizvodljiva ili je apsolutna razlika konačnih jazova ≤0,001.

Prag 0,001 znači 0,1% OPF normalizatora i zamrzava se sada, bez optimizovanja prema podacima.

\[
d_{ijs}=W_{FR}-W_{SP},\qquad
\theta_{63}=\frac13\sum_i\frac1{m_i}\sum_j E_s[d_{ijs}].
\]

Pozitivno \(\theta_{63}\) znači da FX-T ima veću prednost prema AD-N pod FR nego pod SP. Vrednost 0,05 predstavlja pet procentnih poena razlike očekivanog skora pobede. To **nije** 5% ubrzanja niti 5% manjeg gubitka.

Neizvodljivost se ne izbacuje niti statistički imputira; predstavlja najlošiju kategoriju. Ne rade se aritmetičke operacije sa beskonačnostima. Uparivanje semena je deo estimanda. Pretpostavljaju se deterministički evaluator i nezavisna semena između jedinica. Promena fizičke jedinice \(f,r\mapsto af,ar\), \(a>0\), ostavlja ishod nepromenjenim; to je svojstvo definicije, ne teorijski doprinos.

**Instrument, razvoj i potvrdni uzorak.** Ostaju case30, case39 i case24_ieee_rts, \(R=17\), BusORPD, populacija 32 i četiri grane I61. Nasleđuju se SP/FR skalari, operatori i fiksni selektori iz I56; bibliotečki CHT se ne koristi. Nema prekida pri cilju. Beleži se najbolje izvodljivo rešenje među prvih \(B\) stvarnih evaluacija, nezavisno od vraćenog GA rezultata.

I61 razvojni scenariji j=0,1 ostaju razvoj. Budžet 12.000 izabran je nakon uvida u njih i ta zavisnost mora biti objavljena.

FX-T se podešava zasebno za SP i FR, jednom globalnom konfiguracijom po CHT-u. Koristi se nasleđena mreža 27 konfiguracija i tri nova semena po razvojnoj ćeliji. Konfiguracija maksimizuje prosečan skor pobede protiv ostalih 26 konfiguracija, prema istom pravilu \(W\), uz jednake težine mreža, scenarija i semena; veze rešava prvi indeks `FXT_GRID`. Nepotpuna kalibracija znači STOP.

Zatim sledi **jedna razvojna proba**, sa 20 novih semena po razvojnom scenariju. Ona služi samo proveri informativnosti i planiranju \(n\); ne menja budžet, metriku ili FX-T.

Potvrdni scenariji imaju faktore opterećenja 0,92/1,02/1,08, spread=0,1 i nova semena scenarija 630201/630202/630203. To su nove realizacije opterećenja na ponovo korišćenim topologijama. OPF podobnost utvrđuje se pre razvoja, bez optimizacionih ishoda; neuspešni scenariji se izuzimaju bez zamene. Potrebna su najmanje dva potvrdna scenarija svake mreže.

Optimizaciona semena:

\[
1\,700\,000\,000+10^7p+10^6i+10^4j+s,
\]

gde su \(p=1,2,3\) za kalibraciju, probu i potvrdu; \(i=0,1,2\), razvojni \(j=0,1\), potvrdni \(j=2,3,4\). Isto seme koristi se unutar uparenih grana. Seju se Python i NumPy; sudari sa arhivama znače STOP.

Obavezno obelodanjivanje:

> „I63 je prospektivni naslednik motivisan razvojnim STOP-om I61. I61 razvojni podaci korišćeni su kao pilot pri izboru novog estimanda i budžeta. I61 ostaje zatvoren bez zaključka o H61. Topologije se ponovo koriste; potvrdne realizacije scenarija i optimizaciona semena su nova.“

**STOP pravila.** Pre razvoja mora proći I61 regresioni gate instrumenta na zamrznutoj biblioteci, uključujući proveru početnih populacija i sekvenci evaluacija.

Razvojna proba prolazi samo ako:

- svaka razvojna ćelija ima svih 20 potpunih četvorovektora;
- svaka grana u svakoj ćeliji nalazi izvodljivo rešenje u najmanje 10/20 pokretanja;
- među 40 jedinica svake mreže, za svaki CHT najmanje osam poređenja AD-N/FX-T nije veza;
- svaka mreža ima najmanje osam \(d\ne0\) i empirijsku varijansu \(d\), sa imeniocem 40, najmanje 0,02.

Pravila su simetrična prema znaku. Potpuna neizvodljivost, potpune veze i konstantni kontrasti ne mogu proći. Pojedinačan zasićen scenario ostaje uključen; ne bira se povoljniji podskup.

Neprolaz znači konačan STOP: bez novih budžeta, ciljeva, konfiguracija, scenarija ili dodatne probe. Potvrdni rezultati ne služe izboru informativnih ćelija.

Tehnički neuspeh dopušta jedno ponavljanje istog zadatka i semena; ponovljen neuspeh onemogućava potvrdni zaključak. Neuspeo PF unutar pravilno izvršenog pokretanja ostaje algoritamski ishod. Nezavisni proverivač proverava sve prijavljene najbolje izvodljive svedoke; nepoklapanje blokira zaključivanje.

**Snaga i analiza.** Snaga se sada ne može pošteno navesti: I61 nema FX-T podatke za ovaj estimand.

Iz nove probe resampluju se celi četvorovektori. Eksponencijalno naginjanje njihovih težina formira planske raspodele za \(\theta=0,\pm0,05\), bez menjanja ishoda ili dodavanja varijanse. Zahtevaju se stroga dostižnost, greška sredine ≤\(10^{-8}\) i ESS najmanje polovina poola po mreži.

Proveravaju se tri pretpostavke prenosa na potvrdne scenarije: razvojni pool po mreži, samo j=0 i samo j=1. Za \(n\in\{80,160,240,320,480\}\) bira se najmanji \(n\) koji u sve tri varijante daje:

- Wilsonovu donju 95% granicu snage ≥0,80 za pozitivan zaključak pri \(\theta=0,05\);
- istu granicu ≥0,80 za ekvivalenciju pri \(\theta=0\).

Preliminarno: 1.000 simuliranih eksperimenata i 2.000 bootstrap ponavljanja; nezavisna potvrda: 1.000 i 20.000. Kalibracija zahteva Wilsonovu gornju granicu lažno pozitivne stope ≤0,05 pod nulom, odnosno lažne ekvivalencije na obe granice ±0,05. Semena simulacije 63023–63025. Neprolaz do \(n=480\) znači STOP. Ove procene ostaju uslovne na mali razvojni uzorak.

Konačna analiza koristi 20.000 stratifikovanih bootstrap ponavljanja celih četvorovektora unutar mreže×scenarija. Donja 95% granica >0 podržava smer H56a; gornja <0 suprotan smer. Ekvivalencija zahteva 90% interval strogo unutar ±0,05. Degenerisana mreža sa svim \(d=0\) blokira tvrdnju o ekvivalenciji; ne izbacuje se. Ostali rezultati su neodlučni. Sirovi MW jazovi i izvodljivost prikazuju se opisno.

**Trošak i vrednost za tezu.** Pri maksimalnih devet potvrdnih scenarija i \(n=480\): potvrda 207,360 M PF, kalibracija 11,664 M i proba 5,760 M. **Tvrdi plafon je 230 M PF**, uključujući gate, provere i tehnička ponavljanja. To je približno **211–288 CPU-sati**, odnosno idealno **21,1–28,8 sati na deset jezgara**, pri 3,3–4,5 ms/PF. OPF i ostala režija su dodatni; operativni plafon cele studije je 400 CPU-sati. Nepotpuna studija nema potvrdni zaključak.

Najveća pretnja je promena značenja efekta: rangovski kvalitet pri 12.000 poziva može dati interakciju koju vreme dostizanja nema, ili obrnuto. Uz to, kontrast uključuje zasebno podešavanje FX-T po CHT-u; ne identifikuje numerički mehanizam adaptacije.

Tvrdnju teze bih proširio tek uz donju 95% granicu \(\theta_{63}>0,05\), pozitivne procene na najmanje dve mreže i očuvan pozitivan znak pri izostavljanju bilo koje mreže. Tada bi postojala umerena, prenosiva interakcija završnog kvaliteta na definisanom skupu. Informativna ekvivalencija ograničila bi praktični značaj tog proširenja. Samo \(p<0,05\), mali efekat ili razvojni STOP ostavljaju H56a lokalnim nalazom.

**Jedan I63, sa objavljivanjem svakog ishoda; bez narednog naslednika koji ublažava neuspele uslove.**