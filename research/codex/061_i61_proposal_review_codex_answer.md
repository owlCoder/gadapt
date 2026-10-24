**Odluka: REVISE pre zamrzavanja.** Pregled je ostao result-blind: zabranjeni rezultati i logovi nisu otvarani; fajlovi nisu menjani. Računao sam varijanse iz dozvoljenih I56 podataka i kratko merio PF na fabričkim mrežama.

1. **Blokirajuće su neusaglašene tvrdnje i kalibracija.** [Izbor B/R samo preko AD-N/SP](/Users/danijel/Desktop/gadapt/research/ITERATION61_PROPOSAL_SR.md:45) uslovljava jedan član kontrasta. Nezavisna razvojna semena sprečavaju neposredno curenje u test, ali izbor nije neutralan prema kontrastu samo zato što eksplicitno ne koristi njegov znak. Zaključak mora važiti za razvojno odabrane uslove. Preporučujem simetričan izbor prema AD-N/SP i AD-N/FR, uz **R=17 svuda**.

   Kalibracija FX-T na R=17, pa prenos na razvojno izabrani R, nepotrebno meša efekat adaptacije sa prenosivošću fiksne politike. Ili kalibrisati na stvarnom R svake mreže ili ukloniti izbor R.

   **Jedan globalni vektor po CHT-u nije sam po sebi greška.** To je legitimna intervencija ako je cilj poređenje sa zajedničkom podešenom politikom. Nije poređenje sa najboljom fiksnom politikom svake mreže. Dva različita FX-T vektora za SP i FR znače da kontrast uključuje i postupak podešavanja komparatora; ne izoluje samo numerički signal adaptacije.

   Reference SP/AP/FR/EC × AD-N nisu curenje podataka ako su nezavisne i zamrznute. Ipak, AP/EC mogu postaviti cilj nedostižan četirima test granama. Reference određuju uslovni benchmark, ne optimum niti neutralnu ocenu kvaliteta svih algoritama.

2. **Eksponencijalno naginjanje je matematički valjano, ali ne potvrđuje realističnost alternative.** Za mrežu \(i\),
   \[
   m_i(\lambda)=\sum_u w_{iu}(\lambda)d_{iu},\qquad
   m_i'(\lambda)=\operatorname{Var}_{w_i}(d)\ge0.
   \]
   Zajednički λ zato daje jedinstveno rešenje kada je 0,02 strogo unutar dostižnog opsega proseka. To je standardna konstrukcija [eksponencijalnog naginjanja empirijske raspodele](https://rweb.cla.umn.edu/R/library/boot/html/exp.tilt.html).

   Čuvanje četvorovektora uklanja konkretnu I56 slabost: blok sa svim \(d=0\) ostaje nula. Međutim, naginjanje menja verovatnoće dostizanja, varijansu i raspodelu efekta između mreža. Ne garantuje realističnu alternativu niti prenos sa dva razvojna scenarija. Wilsonov interval meri samo Monte Karlo neizvesnost, ne neizvesnost razvojne raspodele. Potrebni su dijagnostika težina, ESS i provera ponašanja testa pod nulom.

   **STOP je realan, verovatno čest ishod.** Iz [I56 arhive](/Users/danijel/Desktop/gadapt/research/results/iteration56), RMS unutarćelijske standardne devijacije na informativnom case14 iznosi **0,332 u testu**, odnosno **0,447 u probi**. Za tri mreže × tri scenarija:
   \[
   \mathrm{power}\approx
   \Phi\!\left(0,02\sqrt{9n}/\sigma-1,96\right).
   \]
   Pri n=80 to daje približno **37% odnosno 22%**. Wilsonova donja 95% granica ≥0,8 zahteva najmanje **825/1000** uspešnih simulacija. Normalna aproksimacija tada traži oko **257 odnosno 465 semena po ćeliji**; n=80 zahteva σ približno ≤0,185. Ovo su orijentiri, ne prognoza novih mreža. Manje preostalih test scenarija dodatno smanjuje snagu.

3. **Zona ekvivalencije je koherentna, ali mora imati odvojeno tumačenje.** Interval od 90% potpuno unutar ±0,02 odgovara nominalnom TOST pravilu na nivou 5%; percentilni bootstrap ostaje aproksimacija. [Dokumentacija TOST-a](https://support.sas.com/documentation/cdl/en/statug/66103/HTML/default/statug_ttest_details19.htm) eksplicitno povezuje taj interval i test.

   Pozitivan 95% interval i praktična ekvivalencija mogu istovremeno važiti. Zona se odnosi na **prosečan kontrast ograničenog normalizovanog vremena**, ne na ekvivalentnost algoritama, mreža ili pojedinačnih grana. Za tvrdnju „efekat je najmanje 0,02“ potrebna je donja granica iznad 0,02.

4. **I56 instrument može ostati bit-identičan na v4; završni pasus predloga pogrešno spaja dve putanje.** [StudyFactory](/Users/danijel/Desktop/gadapt/research/iteration56_cht_study.py:410) neposredno vraća `CHTCostFinder`, čime zaobilazi bibliotečki `ConstraintHandlingCostFinder` i njegovu medijanu/arctan/ključ. `ga_options` samo prenosi nova polja; validator sa `constraint_handling=None` prolazi bez intervencije, a `probe_cost_function=False` sprečava dodatne evaluacije. [Novi blok izvršavača](/Users/danijel/Desktop/gadapt/gadapt/execution/ga_executor.py:81) menja izlaz samo kada finder ima `best`; I56 finder ga nema. To podržava očekivanje identičnosti, ali nije izvršena potvrda.

   **Tačan gate:** iz `test.json.gz` preuzeti arhivirane zadatke za svih devet mreža×R, scenario **j=2, (0,90;201), s=1**. Ponoviti SP/FR × AD-N/FX-T, plus AP/EC × AD-N: **54 pokretanja**. Koristiti izvorni ORPD, pune budžete i nov proces po pokretanju. Moraju se tačno poklopiti početne populacije, `sequence`, svi brojači/statusi, ishodi, `trace`, `cht_trace` i FX zapisi; porediti deterministički sadržaj i numeričke bitove, ne gzip bajtove. Dodati postojeće I56 regresione provere i SP poređenje sa `run_plain`. Svako nepoklapanje blokira sadašnju biblioteku; zatim isti gate na `17e9ce7` u odgovarajućem okruženju.

5. **PF računica je tačna, vremenska pretpostavka slaba.** U mikrobenchmarku, 95 merenih PF po fabričkom slučaju, proseci CPU vremena bili su: case30/39/24 **4,0/2,2/4,5 ms**, naspram case14/57/118 **2,8/4,2/4,9 ms**. Preslikavanje novih mreža daje oko **103 CPU-sata** za 104,688 miliona poziva. To nije merenje optimizacionih putanja; OPF, omotači, simulacija i paralelni rad menjaju cenu.

   Najčistija ušteda je **prekid pri prvom cilju** u pokretanjima čiji je jedini inferencijalni ishod T. Time se čuva primarni ishod; gube se završne deskriptivne mere. Reference moraju ostati pune. R=17 dodatno smanjuje razvoj bez gubitka primarnog pitanja o interakciji.

**Predloženi tekst za zamrzavanje** — zamenjuje odgovarajuće odredbe nacrta; ostale eksplicitne formule i postavke nacrta važe:

> **I61 je konceptualna replikacija pozitivnog H56a kontrasta**, uslovna na tri unapred izabrane topologije, scenarije, razvojni izbor budžeta, reference i kalibraciju. Ne predstavlja potpuno nezavisnu validaciju topologija niti proveru integrisanog v4 CHT-a.
>
> Koriste se case30, case39 i case24_ieee_rts, BusORPD, R=17, četiri grane AD-N/FX-T × SP/FR i razvojni/test scenariji navedeni u nacrtu. OPF podobnost svih scenarija utvrđuje se pre razvoja. Potrebna su oba razvojna i najmanje jedan test scenario svake mreže; inače STOP. Isključivanja su bez zamene. Test OPF podaci ne podešavaju budžete ni FX-T.
>
> Pre razvoja obavezan je gate iz tačke 4 ove recenzije. Koristi se I56 StudyFactory, `constraint_handling=None`, bez bibliotečkog FR/ε. Biblioteka, instrument, okruženje i rezultati gate-a heširaju se.
>
> Razvojne i test reference ostaju I56 SP/AP/FR/EC × AD-N, sa budžetima i semenima iz nacrta. L* i cilj su zajednički svim granama. Bez izvodljive reference cilj je izvodljivost; bez uspešne reference STOP. Nijedna test referenca ne menja razvojne odluke.
>
> Za izbor B izvršavaju se AD-N/SP i AD-N/FR, na oba razvojna scenarija i pet semena, do 24.000 poziva. B∈{3000,6000,12000,24000} prolazi samo ako je medijana T za **svaku od dve grane na svakom scenariju** u [0,3;0,8]. Bira se najmanji prolazni B po mreži; bez njega STOP.
>
> FX-T se kalibriše pri R=17 i izabranim budžetima, mrežom 27 konfiguracija iz nacrta. Zadržavaju se dva globalna vektora, po jedan za SP i FR, sa jednakim težinama mreža, scenarija i semena. Veze rešava prvi indeks mreže. Nepotpuna kalibracija znači STOP. Zaključak se odnosi na ovako podešenog globalnog komparatora.
>
> Nezavisna proba koristi deset novih semena po razvojnom scenariju. Ponovo moraju proći simetrični uslovi medijana; svaka grana mora imati ≥20% dostizanja po mreži i kontrast pozitivnu varijansu. Neprolaz znači STOP bez ponovnog izbora.
>
> Snaga koristi postojeće četvorovektore i naginjanje na θ=0,02, bez dodavanja efekta degenerisanim blokovima. Zahtevaju se strogo dostižna alternativa, numerička greška sredine ≤10⁻⁸ i ESS≥10 od 20 vektora po mreži. Simuliraju se stvarni brojevi podobnih test scenarija. Za svaki n∈{20,40,60,80} koriste se 1000 eksperimenata i konačna analiza; bira se najmanji n sa Wilsonovom donjom 95% granicom ≥0,8. Izbor se potvrđuje nezavisnom serijom od 1000 eksperimenata, seme 61024, istim kriterijumom. Dodatna simulacija naginjanja na θ=0, seme 61025, mora imati gornju Wilsonovu granicu lažno pozitivnog primarnog zaključka ≤0,05; nedostižna nula ili neprolaz znači STOP.
>
> Estimator, uparivanje, semena i 20.000 stratifikovanih bootstrap ponavljanja ostaju iz nacrta. Intervali 95% i 90% računaju se iz istih izvlačenja. H61 podržava donja 95% granica >0; gornja <0 podržava suprotan smer. Interval 90% strogo unutar ±0,02 podržava praktičnu ekvivalenciju prosečnog kontrasta. Oznake smera i ekvivalencije prijavljuju se odvojeno; ostalo je neodlučno. STOP ne daje novi empirijski zaključak.
>
> Prekid pri prvom cilju dozvoljen je nakon čuvanja svedoka i razvojne provere identičnog h prema punim putanjama. Reference ostaju pune. Važe zamrzavanje pre test referenci, provere početnih populacija, ponavljanja i osetljivost iz nacrta. Nezavisni proverivač parametrizuje scenario i R i proverava svedoke L*, prvog cilja i prijavljenog najboljeg rešenja. Neuspeh provere onemogućava zaključivanje.