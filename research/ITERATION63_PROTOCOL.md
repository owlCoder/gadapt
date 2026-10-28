# ITERATION63: konačna konceptualna replikacija H56a sa estimandom „kvalitet pri fiksnom budžetu“ (PROTOKOL v2 — ZAMRZNUT ovim komitom, pre koda drajvera i pre ijednog I63 merenja)

Status: ZAMRZNUT. Nacrt iz Codex 077, recenzija Codex 078 (FREEZE AFTER FIXES) uneta u v2. Ništa nije pokrenuto. Kasnije izmene samo kao dokumentovana odstupanja (Dn) pre odgovarajuće faze.
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
Samo eksplicitni neuspeh OPF-a dopušta unapred propisano izuzimanje scenarija; ostale greške ili nekonačan/nepozitivan r_ij = STOP. Svako kasnije konstruisanje scenarija mora odgovarati zamrznutom scenariju i normalizatoru. Redosled mreža: case30, case39, case24_ieee_rts.
Lanac zamrzavanja: posle zamrzavanja protokola, a pre prvog izvršavanja I63, zamrzavaju se drajver, analiza, simulacija, proverivač, svi tranzitivno korišćeni izvori, biblioteka, zavisnosti i razrešena GA podešavanja. Svaka faza proverava provenijenciju pre i posle izvršavanja i objavljuje heševe ulaznih i izlaznih artefakata. Pre potvrde dodatno se vezuju roster scenarija, OPF normalizatori i scenarijski podaci, svi razvojni rezultati, izabrani FX-T i n. Faze su create-once za jedinstveni I63 identitet; novi direktorijum ne dozvoljava ponovno odlučivanje posle STOP-a.
Gate: pre razvoja mora proći regresioni gate instrumenta I61 (54/54 arhiviranih I56 pokretanja bit-identično; početne populacije i
sekvence evaluacija) na zamrznutoj biblioteci; ista provenijencija (heševi biblioteke, koda, okruženja) vezuje sve faze (I61 obrazac).

## 3. Estimand
Za mrežu i, scenario j, seme s, politiku a ∈ {AD-N, FX-T}, CHT c ∈ {SP, FR}:
G^a_{ijsc} = (f_best,feas^{a,c}(B) − r_ij)/r_ij ako postoji izvodljivo rešenje; inače +∞ (najlošija kategorija); r_ij = gubitak kontinualnog OPF-a
scenarija (`problem.opf_losses`, normalizator, NE sertifikovani optimum; negativni jazovi dozvoljeni). Nema novih referentnih pokretanja.
Za uparen par AD-N/FX-T (isto seme, scenario, CHT) skor pobede FX-T:
Izvodljivost ima prvenstvo (bez aritmetike ∞ − ∞). Δ = (f_AD − f_FX)/r_ij kada su oba izvodljiva:
- W_c = 1 ako je FX-T izvodljiv a AD-N nije, ili su oba izvodljiva i Δ > 0,001;
- W_c = 0 ako je AD-N izvodljiv a FX-T nije, ili su oba izvodljiva i Δ < −0,001;
- W_c = 1/2 ako su oba neizvodljiva ili je |Δ| ≤ 0,001 (oba izvodljiva).
Veze nisu tranzitivne, što ne sprečava definisan skor pobede.
Prag 0,001 (0,1% normalizatora) se zamrzava sada i ne optimizuje se prema podacima.
d_ijs = W_FR − W_SP; θ_63 = (1/3) Σ_i (1/m_i) Σ_j E_s[d_ijs], m_i = broj preostalih potvrdnih scenarija mreže i.
θ_63 > 0 znači veću prednost FX-T nad AD-N pod FR nego pod SP. θ_63 = 0,05 = pet procentnih poena razlike očekivanog skora pobede
(NIJE 5% ubrzanja ni 5% manjeg gubitka). Neizvodljivost se ne izbacuje ni imputira. Jedinica: mreža × scenario × seme (četvorovektor
grana); uparivanje semena je deo estimanda. Promena jedinice f, r → a f, a r (a > 0) ne menja ishod (svojstvo definicije).

## 4. FX-T kalibracija (razvoj)
Zasebno za SP i FR, jedna globalna konfiguracija po CHT-u: mreža 27 konfiguracija FXT_GRID iz I61 (a ∈ {0,25; 0,5; 0,75}, b ∈ {0,1; 0,2; 0,4},
σ ∈ {0,02; 0,05; 0,15}); 3 nova semena (p = 1) po razvojnoj ćeliji (3 mreže × 2 scenarija); B = 12.000. Za konfiguraciju k i CHT c:
Q_kc = (1/(3·2·3·26)) Σ_{i=0..2} Σ_{j=0..1} Σ_{s=1..3} Σ_{ℓ≠k} S_ijsc(k, ℓ), gde je S skor konfiguracije k protiv ℓ po W pravilu sa istim semenom i
scenariom (ne porede se različita semena niti sva međusobna ukrštanja). Bira se k sa najvećim Q_kc; pri tačno jednakom skoru najmanji indeks
FXT_GRID; poređenje preko celobrojnog zbira 2S, bez numeričke tolerancije. Nepotpuna kalibracija = STOP. Zaključak se odnosi na ovako podešenog globalnog komparatora.
Cena: 27 × 2 × 3 × 2 × 3 × 12.000 = 11,664 M PF.

## 5. Razvojna proba (jedna, bez ponovnog izbora)
Četiri grane, 20 novih semena (p = 2) po razvojnom scenariju, B = 12.000, izabrani FX-T. Služi samo proveri informativnosti i planiranju n;
ne menja B, metriku ni FX-T. Prolazi samo ako: (i) svaka razvojna ćelija ima svih 20 potpunih četvorovektora; (ii) svaka grana u svakoj
ćeliji nalazi izvodljivo rešenje u ≥ 10/20 pokretanja; (iii) među 40 jedinica svake mreže, za svaki CHT, najmanje 8 poređenja AD-N/FX-T nije veza;
(iv) svaka mreža ima ≥ 8 jedinica sa d ≠ 0 i empirijsku varijansu d (imenilac 40) ≥ 0,02. Pravila su simetrična prema znaku. Potpuna
neizvodljivost, potpune veze i konstantni kontrasti ne prolaze. Pojedinačan zasićen scenario ostaje uključen. Neprolaz = KONAČAN STOP
(bez novih budžeta, ciljeva, konfiguracija, scenarija ili dodatne probe). Cena: 5,76 M PF.

## 6. Snaga
Za svaku mrežu formiraju se tri pool-a iz probe: svih 40 razvojnih jedinica, 20 jedinica j=0 i 20 jedinica j=1 (tri pretpostavke prenosa). Svaki red čuva ceo
upareni četvorovektor normalizovanih ishoda, oznake izvodljivosti i njegov d; prenosi se raspodela normalizovanih ishoda (ne preračunava se prema
normalizatoru potvrdnog scenarija). Ponovljeni jednaki redovi zadržavaju multiplicitet.
Za svaku varijantu v i cilj t ∈ {0, +0,05, −0,05} određuje se zajednički λ_vt za tri mreže: w_iu = exp(λ d_iu)/Σ_h exp(λ d_ih) (stabilan softmax),
(1/3) Σ_i Σ_u w_iu d_iu = t. Stroga dostižnost: (1/3) Σ_i min_u d_iu < t < (1/3) Σ_i max_u d_iu. Greška sredine ≤ 10⁻⁸. Za svaku varijantu v i mrežu i,
N_iv = broj redova pool-a (40 objedinjeni, 20 za j=0 ili j=1): ESS_iv = 1/Σ_u w_ivu² ≥ N_iv/2 (20 odnosno 10). Naginjanje se rešava zasebno za
svaku kombinaciju varijante i cilja. Objavljuju se λ, težine i ESS. Bez dodavanja efekta ili varijanse.
Simulirani eksperiment: za svaku stvarno podobnu potvrdnu ćeliju (i,j) nezavisno C_ij ~ Multinomial(n, w_i) (sve ćelije iste mreže koriste istu
izvornu raspodelu, nezavisna izvlačenja). Unutrašnji bootstrap: za svaku ćeliju nezavisno C*_ijb ~ Multinomial(n, C_ij/n) (ne koristi ponovo
naginjane težine). θ̂*_b = (1/3) Σ_i (1/m_i) Σ_j (1/n) Σ_u C*_ijbu d_iu; procena koristi C umesto C*. Ne resampluju se mreže ni scenariji.
CI95 = linearni percentili 2,5/97,5, CI90 = 5/95 ISTIH izvlačenja. Funkcija odlučivanja (ista u simulaciji i u završnoj analizi): pozitivan zaključak
L95 > 0; negativan U95 < 0; ekvivalencija L90 > −0,05 i U90 < +0,05 uz najmanje jedan opaženi d ≠ 0 u svakoj mreži simuliranog eksperimenta.
Za n ∈ {80, 160, 240, 320, 480} (semena po potvrdnoj ćeliji), po rastućem n: 1.000 simuliranih eksperimenata, 2.000 bootstrap ponavljanja; bira se najmanji n
koji u SVE tri varijante daje Wilsonovu donju dvostranu 95% granicu ≥ 0,80 (a) za pozitivan zaključak pri θ = +0,05 i (b) za ekvivalenciju pri θ = 0. Nezavisna
potvrda izabranog n (oba kriterijuma, sve tri varijante): 1.000 eksperimenata, 20.000 ponavljanja. Kalibracija: Wilsonova GORNJA granica lažno pozitivne
stope pod θ = 0 ≤ 0,05 (pozitivan zaključak i, zasebno, negativan) i lažne ekvivalencije pod θ = ±0,05 ≤ 0,05, u sve tri varijante (za 1.000 eksperimenata: ≥ 825
uspeha, odnosno ≤ 36 grešaka). Ovo je konzervativno (pri stvarnoj grešci 5% prolazi ≈ 2,1% serija); rizik STOP-a se prihvata unapred i granice se ne
ublažavaju. Provera svakog smera zasebno ne potvrđuje ukupnu grešku „bilo koji smer“ ≤ 5%. Nema povećanja n posle neuspele potvrde.
RNG: jedan `numpy.random.default_rng` po seriji, semena 63023 (preliminarno), 63024 (potvrda), 63025 (nula/kalibracija), bez resetovanja između eksperimenata.
Redosled: rastući n, zatim pool objedinjeni/j=0/j=1, ciljevi +0,05/0/−0,05 kada su potrebni, pa sortirane ćelije. Završni bootstrap koristi zaseban
`default_rng(63)`. Neprolaz do n = 480, nedostižan cilj, ESS ispod praga ili neprolaz potvrde/kalibracije = KONAČAN STOP. Procene snage su uslovne na
mali razvojni uzorak i pretpostavljeni prenos (Wilson mere samo simulacionu nesigurnost).

## 7. Potvrdni test
Mreža × potvrdni scenario × n semena (p = 3), četiri grane, B = 12.000, FX-T iz §4 i n iz §6 zamrznuti (heš) PRE ijednog potvrdnog pokretanja.
Seme optimizacije: 1.700.000.000 + 10⁷·p + 10⁶·i + 10⁴·j + s, p = 1,2,3 (kalibracija, proba, potvrda), i = 0,1,2 (redosled mreža §2), j = 0..4; opsezi s: 1..3 (p=1), 1..20 (p=2), 1..n (p=3); isto
seme namerno samo unutar uparenih grana/konfiguracija jedinice (jedinstvenost se proverava nad različitim jedinicama); identične generisane početne populacije svih uparenih pokretanja (asercija); sudar sa arhivama (I56, I58–I61) = STOP; Python i NumPy RNG.
Pokretanje je uspešno ako je bez greške i potrošilo tačno B poziva; svako pokretanje u novom procesu. Svaka tehnički neuspešna grana ponavlja se jednom, istim zadatkom i semenom, u novom procesu. Ponovljen neuspeh bilo koje planirane grane znači KONAČAN STOP bez potvrdnog zaključka (nema selekcije prema tehničkom uspehu, nema izuzimanja cele jedinice). Svi pokušaji ostaju arhivirani. Tehnički neuspeh ne kodira se kao algoritamska neizvodljivost. Prazna ćelija ili izuzet scenario (samo eksplicitni neuspeh OPF-a pre optimizacije, §2) prijavljuje se. Neuspeo PF unutar pravilno izvršenog pokretanja je algoritamski ishod. Nezavisni proverivač (I58 obrazac) proverava SVE prijavljene najbolje
izvodljive svedoke (vektor, R-mreža, gubitak, V = 0); nepoklapanje blokira zaključivanje.

## 8. Analiza i zaključivanje
20.000 stratifikovanih bootstrap ponavljanja celih četvorovektora unutar mreža × scenario, `numpy.random.default_rng(63)`, jedan niz izvlačenja; 95% i 90% percentilni intervali (linearna interpolacija) iz istih izvlačenja. H63 PODRŽANA (smer H56a) ako je donja granica 95% intervala θ_63 > 0; gornja < 0 = suprotan smer; ekvivalencija ako je 90% interval
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
