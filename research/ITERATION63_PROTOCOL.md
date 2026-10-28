# ITERATION63: konačna konceptualna replikacija H56a sa estimandom „kvalitet pri fiksnom budžetu“ (NACRT PROTOKOLA — NIJE ZAMRZNUT)

Status: nacrt iz Codex 077 (`research/codex/077_i63_design_codex_answer.md`), pre recenzije (Codex 078). Ništa nije pokrenuto.
Zamrzavanje = poseban komit pre ijednog I63 merenja, pre koda drajvera koji pokreće optimizaciju.

## 0. Obelodanjivanje (obavezno u izveštaju i tezi)
I63 je prospektivni naslednik motivisan razvojnim STOP-om I61 (nijedna mreža nije imala B sa sve četiri razvojne medijane T u [0,3; 0,8]).
I61 razvojni podaci (`results/iteration61/select_b.json.gz`, 60 pokretanja, B ≤ 12.000) korišćeni su kao pilot pri izboru novog estimanda i budžeta
B = 12.000; ta zavisnost je ovim obelodanjena. I61 ostaje zatvoren bez zaključka o H61. Topologije se ponovo koriste (case30, case39,
case24_ieee_rts); potvrdne realizacije scenarija i sva optimizaciona semena su nova. Postoji JEDAN I63; nema naslednika koji ublažava uslove
(I63 → I64 bi bilo ponavljanje do pozitivnog rezultata). Svaki ishod, uključujući STOP, prijavljuje se.
Prior art estimanda i dizajna: fiksni budžet i ECDF — COCO (10.1080/10556788.2020.1808977); poređenje CHT na ORPD — Mallipeddi i sar.
(10.1016/j.swevo.2012.03.001). Novina nije tvrđena: ovo je provera prenosivosti interakcije iz I56, ne nova metoda ni teorema.

## 1. Pitanje
Da li je prednost podešene fiksne politike (FX-T) nad podrazumevanom samoadaptacijom (AD-N) veća pod pravilima izvodljivosti (FR) nego pod
statičkom kaznom (SP), kada se meri kvalitet najboljeg izvodljivog rešenja pri istom budžetu stvarnih PF poziva? (Isto pitanje kao H56a;
drugi estimand.)

## 2. Instrument
I56 instrument (CHT, `CHTCostFinder`, `StudyFactory`, SP/FR skalari, operatori i fiksni selektori), BusORPD iz I58, R = 17,
populacija 32, `constraint_handling=None` (bibliotečki CHT se ne koristi), `probe_cost_function=False`, `exit_check="generations"`,
`number_of_generations=10**9`, prekid po stvarnom PF budžetu. Svaka grana troši TAČNO B = 12.000 stvarnih PF poziva; nema prekida pri cilju.
Beleži se najbolje izvodljivo rešenje među prvih B evaluacija iz evaluatora (ne vraćeno rešenje GA). Mreže: case30, case39, case24_ieee_rts.
Razvojni scenariji (isti kao I61): j=0 (0,97; seme 6101), j=1 (1,03; 6102). Potvrdni scenariji (NOVI): j=2 (0,92; 630201), j=3 (1,02; 630202),
j=4 (1,08; 630203), spread = 0,1. OPF podobnost svakog scenarija utvrđuje se PRE ijedne optimizacije (bez optimizacionih ishoda); scenario
sa neuspelim OPF-om se izuzima bez zamene. Obavezna su oba razvojna i najmanje dva potvrdna scenarija svake mreže, inače STOP.
Gate: pre razvoja mora proći regresioni gate instrumenta I61 (54/54 arhiviranih I56 pokretanja bit-identično; početne populacije i
sekvence evaluacija) na zamrznutoj biblioteci; ista provenijencija (heševi biblioteke, koda, okruženja) vezuje sve faze (I61 obrazac).

## 3. Estimand
Za mrežu i, scenario j, seme s, politiku a ∈ {AD-N, FX-T}, CHT c ∈ {SP, FR}:
G^a_{ijsc} = (f_best,feas^{a,c}(B) − r_ij)/r_ij ako postoji izvodljivo rešenje; inače +∞ (najlošija kategorija); r_ij = gubitak kontinualnog OPF-a
scenarija (`problem.opf_losses`, normalizator, NE sertifikovani optimum; negativni jazovi dozvoljeni). Nema novih referentnih pokretanja.
Za uparen par AD-N/FX-T (isto seme, scenario, CHT) skor pobede FX-T:
- W_c = 1 ako je FX-T izvodljiv a AD-N nije, ili su oba izvodljiva i G^AD − G^FX > 0,001;
- W_c = 0 simetrično u korist AD-N;
- W_c = 1/2 ako su oba neizvodljiva ili je |G^AD − G^FX| ≤ 0,001 (oba izvodljiva).
Prag 0,001 (0,1% normalizatora) se zamrzava sada i ne optimizuje se prema podacima.
d_ijs = W_FR − W_SP; θ_63 = (1/3) Σ_i (1/m_i) Σ_j E_s[d_ijs], m_i = broj preostalih potvrdnih scenarija mreže i.
θ_63 > 0 znači veću prednost FX-T nad AD-N pod FR nego pod SP. θ_63 = 0,05 = pet procentnih poena razlike očekivanog skora pobede
(NIJE 5% ubrzanja ni 5% manjeg gubitka). Neizvodljivost se ne izbacuje ni imputira. Jedinica: mreža × scenario × seme (četvorovektor
grana); uparivanje semena je deo estimanda. Promena jedinice f, r → a f, a r (a > 0) ne menja ishod (svojstvo definicije).

## 4. FX-T kalibracija (razvoj)
Zasebno za SP i FR, jedna globalna konfiguracija po CHT-u: mreža 27 konfiguracija FXT_GRID iz I61 (a ∈ {0,25; 0,5; 0,75}, b ∈ {0,1; 0,2; 0,4},
σ ∈ {0,02; 0,05; 0,15}); 3 nova semena (p = 1) po razvojnoj ćeliji (3 mreže × 2 scenarija); B = 12.000. Konfiguracija maksimizuje prosečan
skor pobede protiv ostalih 26 konfiguracija (isto W pravilo, isto seme/scenario, jednake težine mreža, scenarija i semena); veza → prvi indeks
FXT_GRID. Nepotpuna kalibracija = STOP. Zaključak se odnosi na ovako podešenog globalnog komparatora.
Cena: 27 × 2 × 3 × 2 × 3 × 12.000 = 11,664 M PF.

## 5. Razvojna proba (jedna, bez ponovnog izbora)
Četiri grane, 20 novih semena (p = 2) po razvojnom scenariju, B = 12.000, izabrani FX-T. Služi samo proveri informativnosti i planiranju n;
ne menja B, metriku ni FX-T. Prolazi samo ako: (i) svaka razvojna ćelija ima svih 20 potpunih četvorovektora; (ii) svaka grana u svakoj
ćeliji nalazi izvodljivo rešenje u ≥ 10/20 pokretanja; (iii) među 40 jedinica svake mreže, za svaki CHT, najmanje 8 poređenja AD-N/FX-T nije veza;
(iv) svaka mreža ima ≥ 8 jedinica sa d ≠ 0 i empirijsku varijansu d (imenilac 40) ≥ 0,02. Pravila su simetrična prema znaku. Potpuna
neizvodljivost, potpune veze i konstantni kontrasti ne prolaze. Pojedinačan zasićen scenario ostaje uključen. Neprolaz = KONAČAN STOP
(bez novih budžeta, ciljeva, konfiguracija, scenarija ili dodatne probe). Cena: 5,76 M PF.

## 6. Snaga
Iz probe se resampluju celi četvorovektori; eksponencijalno naginjanje težina w_iu ∝ exp(λ d_iu) (normalizovano unutar mreže, zajednički λ)
daje planske raspodele za θ ∈ {0, +0,05, −0,05}: zahteva se stroga dostižnost, greška sredine ≤ 10⁻⁸ i ESS_i ≥ polovina probe-pool-a mreže
(≥ 20 od 40). Bez dodavanja efekta ili varijanse. Tri pretpostavke prenosa na potvrdne scenarije: pool po mreži (svih 40), samo j=0, samo j=1.
Za n ∈ {80, 160, 240, 320, 480} (semena po potvrdnoj ćeliji): preliminarno 1.000 simuliranih eksperimenata sa 2.000 bootstrap ponavljanja;
bira se najmanji n koji u SVE tri varijante daje (a) Wilsonovu donju dvostranu 95% granicu snage ≥ 0,80 za pozitivan zaključak (donja granica
95% intervala > 0) pri θ = +0,05, i (b) istu granicu ≥ 0,80 za ekvivalenciju (90% interval strogo u (−0,05; +0,05)) pri θ = 0. Nezavisna potvrda
izabranog n: 1.000 eksperimenata, 20.000 ponavljanja. Kalibracija nule: Wilsonova GORNJA granica lažno pozitivne stope pod θ = 0 ≤ 0,05 (za
pozitivan i za negativan zaključak) i lažne ekvivalencije pod θ = ±0,05 ≤ 0,05. Semena simulacije 63023, 63024 (potvrda), 63025 (nula);
RNG se inicijalizuje jednom po seriji; bootstrap seme 63 se ne resetuje; percentili linearnom interpolacijom. Neprolaz do n = 480, nedostižna
alternativa/nula, ESS ispod praga ili neprolaz potvrde/kalibracije = KONAČAN STOP. Procene snage su uslovne na mali razvojni uzorak i
pretpostavljeni prenos (Wilsonovi intervali mere samo simulacionu nesigurnost).

## 7. Potvrdni test
Mreža × potvrdni scenario × n semena (p = 3), četiri grane, B = 12.000, FX-T iz §4 i n iz §6 zamrznuti (heš) PRE ijednog potvrdnog pokretanja.
Seme optimizacije: 1.700.000.000 + 10⁷·p + 10⁶·i + 10⁴·j + s, p = 1,2,3 (kalibracija, proba, potvrda), i = 0,1,2, j = 0..4, s ≥ 1; isto
seme samo unutar uparenih grana/konfiguracija; asercija jedinstvenosti; sudar sa arhivama (I56, I58–I61) = STOP; Python i NumPy RNG.
Pokretanje je uspešno ako je bez greške i potrošilo tačno B poziva; svako pokretanje u novom procesu; neuspeh se ponavlja jednom istim semenom;
ponovljen neuspeh: cela četvorogranska jedinica se izuzima iz primarnog zaključivanja (potpuni slučajevi), uz osetljivost (T=… ne važi:
nedostupna grana tretira se kao +∞; uspešni ishodi ostaju); globalno izuzimanje > 5% se označava; prazna ćelija onemogućava primarni zaključak.
Neuspeo PF unutar pravilno izvršenog pokretanja je algoritamski ishod. Nezavisni proverivač (I58 obrazac) proverava SVE prijavljene najbolje
izvodljive svedoke (vektor, R-mreža, gubitak, V = 0); nepoklapanje blokira zaključivanje.

## 8. Analiza i zaključivanje
20.000 stratifikovanih bootstrap ponavljanja celih četvorovektora unutar mreža × scenario, seme 63; 95% i 90% percentilni intervali iz istih
izvlačenja. H63 PODRŽANA (smer H56a) ako je donja granica 95% intervala θ_63 > 0; gornja < 0 = suprotan smer; ekvivalencija ako je 90% interval
strogo unutar (−0,05; +0,05) i nijedna mreža nije degenerisana (sve d = 0 blokira tvrdnju o ekvivalenciji); ostalo = neodlučno. Oznake se
prijavljuju odvojeno. Opisno: sirovi MW jazovi, izvodljivost, W po grani, d po ćeliji, jedna-mreža-izostavljena osetljivost.
Proširenje tvrdnje teze (ne više od „umerena, prenosiva interakcija završnog kvaliteta na definisanom skupu“) samo ako: donja 95% granica
θ_63 > 0,05, pozitivne procene na ≥ 2 mreže i očuvan pozitivan znak pri izostavljanju bilo koje mreže. Inače H56a ostaje lokalni nalaz. STOP ne daje
zaključak o H63.

## 9. Budžet
Gate ≈ 0,2 M; kalibracija 11,664 M; proba 5,76 M; potvrda ≤ 207,36 M (devet scenarija, n = 480); tvrdi plafon 230 M PF = 211–288 CPU-sati
= 21–29 h na deset jezgara pri 3,3–4,5 ms/PF (bez OPF-a, provera, simulacije, režije); operativni plafon 400 CPU-sati. Nepotpuna studija
nema potvrdni zaključak. Računar neograničen (korisnik), i preko noći.

## 10. Prijavljene pretnje validnosti (unapred)
Rangovski kvalitet pri 12.000 poziva može dati interakciju koju vreme dostizanja nema (i obrnuto); estimand ≠ H56a-T. Kontrast uključuje
zasebno podešavanje FX-T po CHT-u i ne identifikuje numerički mehanizam adaptacije. Ponovna upotreba topologija; B izabran posle uvida u
I61 razvojne medijane; razvojni pool je mali; r_ij je kontinualni OPF, ne sertifikovan optimum diskretnog problema.
