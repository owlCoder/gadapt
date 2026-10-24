# ITERATION61: replikacija interakcije H56a (adaptacija × CHT) na mrežama odvojenim od I56 (PREREGISTRACIJA)

**Status: NACRT v2 (NIJE ZAMRZNUT)**, 2026-10-24, pre ijednog I58 test rezultata. Predlog:
[ITERATION61_PROPOSAL_SR.md](ITERATION61_PROPOSAL_SR.md) (Codex 055); recenzija Codex 061 (REVISE) uneta ovde. Zamrzava
se posle Codex 062 provere; tek tada kod i izvršavanje (posle završetka lanca I58 → I60 → I59 i primene ispravke v5).

## 1. Pitanje i domet
I61 je **konceptualna replikacija pozitivnog H56a kontrasta**: da li adaptivna politika mutacije GAdapt-a (AD-N)
relativno više gubi prema podešenoj fiksnoj politici (FX-T) pod pravilima izvodljivosti (FR) nego pod statičkom
kaznom (SP), u ograničenom broju AC proračuna do izvodljivog cilja. Uslovna je na tri unapred izabrane topologije,
scenarije, razvojni izbor budžeta, reference i kalibraciju. Ne predstavlja potpuno nezavisnu validaciju topologija
(iste topologije kao I58, drugi scenariji i drugi kontrast) niti proveru bibliotečkog CHT-a iz patch-a v4.
Izbor mreža fiksiran je pre ijednog I58 test rezultata (commit predloga `419c19d`).

## 2. Instance
case30, case39, case24_ieee_rts (tim redom, i = 0..2); I58 merilo `BusORPD` (jedna VG kontrola po generatorskoj
sabirnici, primenjena na sve aktivne generatore na njoj); ostali model, granice i PF podešavanja nasleđuju I56.
**R = 17 svuda.** Razvojni scenariji (faktor opterećenja; seme scenarija): j = 0 (0,97; 6101), j = 1 (1,03; 6102); test:
j = 2 (0,92; 6201), j = 3 (1,02; 6202), j = 4 (1,08; 6203); spread = 0,1. I58 scenariji 301–303, reference i ishodi se ne
koriste. OPF podobnost svih scenarija utvrđuje se pre razvoja; OPF neuspeh = izuzimanje bez zamene. Potrebna su oba
razvojna i najmanje jedan test scenario svake mreže; inače STOP.

## 3. Instrument i gate
Grane: AD-N/SP, AD-N/FR, FX-T/SP, FX-T/FR — I56 `CHT`, `CHTCostFinder`, `StudyFactory`, fiksni selektori; biblioteka
sa `constraint_handling=None` (bibliotečki FR/ε se NE koristi). SP = f + 1000·V; FR po I56 (1 + f/(f + f_ref) za V = 0;
2 + V/(1 + V) za V > 0; 3 za neuspeo PF); f_ref = gubici kontinualnog OPF-a scenarija; V = Σ max(0, c_k − 10⁻⁶);
neuspeo/nekonačan PF: f = 2 f_ref, V = 10, troši poziv. AD-N oba adaptivna signala čita iz skalara svog CHT-a.

**Gate pre razvoja (obavezan):** iz I56 `test.json.gz` ponoviti arhivirane zadatke za svih 9 mreža × R, scenario
j = 2 (0,90; 201), s = 1: SP/FR × AD-N/FX-T plus AP/EC × AD-N = 54 pokretanja, izvorni I56 ORPD, puni budžeti, nov proces
po pokretanju. Moraju se tačno poklopiti početne populacije, niz poziva (`sequence`), brojači/statusi, ishodi, `trace`,
`cht_trace` i FX zapisi (deterministički sadržaj i numerički bitovi, ne gzip bajtovi), uz postojeće I56 regresione
testove i SP poređenje sa `run_plain`. Svako nepoklapanje blokira trenutnu biblioteku; tada isti gate na `17e9ce7` u
odvojenom stablu. Biblioteka, instrument, okruženje i rezultati gate-a se heširaju.

## 4. Reference i cilj
Razvojne reference: svaki razvojni scenario × {SP, AP, FR, EC} × AD-N × jedno seme, po 30.000 PF poziva. Test
reference posle konačnog zamrzavanja izbora (§5–§7): svaki test scenario × iste četiri grane × dva semena, po 30.000.
L* = najmanji izvodljiv gubitak među uspešnim referentnim pokretanjima; cilj: V = 0 i f ≤ 1,01·L* + 0,01 MW; zajednički
svim granama. Bez izvodljive reference cilj je samo izvodljivost; bez nijedne uspešne reference STOP. Reference su uslovni
benchmark, ne optimum. Nijedna test referenca ne menja razvojne odluke.

## 5. Izbor budžeta B (simetričan)
AD-N/SP i AD-N/FR, oba razvojna scenarija, pet semena, putanje do 12.000 poziva. T_B = min(h/B, 1) za
B ∈ {3000, 6000, 12000}. B prolazi ako je medijana T_B **za svaku od dve grane na svakom razvojnom scenariju** u
[0,3; 0,8]. Po mreži se bira najmanji prolazni B; bez prolaznog B za bilo koju mrežu: STOP (bez proširivanja skupa mreža
ili budžeta).

## 6. FX-T kalibracija
R = 17, izabrani B svake mreže, oba razvojna scenarija, tri semena; mreža 27 konfiguracija a ∈ {0,25; 0,5; 0,75},
b ∈ {0,1; 0,2; 0,4}, σ ∈ {0,02; 0,05; 0,15}, zasebno za SP i FR. Bira se jedan globalni vektor po CHT-u, najmanjeg
srednjeg T uz jednake težine mreža, scenarija i semena; veze → prvi indeks `FXT_GRID`. I56 formule za tačne k i v,
uniformni izbor bez vraćanja, fiksni σ, isti Gaus/reset operatori i popravke duplikata. Nepotpuna kalibracija = STOP.
Zaključak se odnosi na ovako podešenog globalnog komparatora (ne na najbolju fiksnu politiku svake mreže); dva različita
vektora (SP, FR) znače da kontrast uključuje i postupak podešavanja komparatora.

## 7. Razvojna proba i snaga
Proba: četiri grane, deset novih semena po razvojnom scenariju, izabrani B i FX-T. Svaka mreža mora imati: medijanu T
obe AD-N grane u [0,3; 0,8] na oba scenarija; ≥ 20% dostizanja u svakoj grani; pozitivnu empirijsku varijansu kontrasta d.
Neprolaz = STOP bez ponovnog izbora.

Snaga: po mreži se udružuju potpuni upareni četvorovektori probe (20 po mreži); alternativa θ_a = 0,02 dobija se
eksponencijalnim naginjanjem w_λ(u) ∝ exp(λ d_u) unutar mreže sa zajedničkim λ (jedinstveno rešenje ako je 0,02 strogo
unutar dostižnog opsega). Degenerisani vektori ostaju takvi — nikakvo dodavanje efekta. Zahteva se: strogo dostižna
alternativa, numerička greška sredine ≤ 10⁻⁸, efektivna veličina uzorka ESS ≥ 10 (od 20) po mreži. Simulira se stvarni
broj podobnih test scenarija. Za n ∈ {80, 160, 240, 320, 480} semena po ćeliji: 1000 eksperimenata sa konačnom analizom
(§8; za brzinu 2000 bootstrap ponavljanja u simulaciji); bira se najmanji n sa Wilsonovom donjom 95% granicom snage
≥ 0,8, potvrđen nezavisnom serijom od 1000 (seme 61024). Pod θ = 0 (naginjanje na 0, seme 61025) gornja Wilsonova granica
lažno pozitivnog primarnog zaključka mora biti ≤ 0,05. Nedostižna alternativa/nula, ESS ispod praga, n > 480 ili neprolaz
= STOP (nema povećavanja posle zamrzavanja). Orijentir (Codex 061, iz I56 arhive): σ unutar ćelije 0,33–0,45 → potrebno
n ≈ 240–430; STOP je realan ishod i prijavljuje se kao takav.

## 8. Ishod i zaključivanje
T = h/B_i (prvi poziv dostizanja / izabrani budžet mreže), 1 pri nedostizanju. Jedinica: mreža × scenario × seme;
d_u = [T(AD,FR) − T(FX,FR)] − [T(AD,SP) − T(FX,SP)]; θ_a = (1/3) Σ_i mean_j mean_s d_ijs (jednake težine mreža i preostalih
scenarija). Bootstrap: 20.000 stratifikovanih ponavljanja celih uparenih četvorovektora unutar ćelija mreža × scenario,
seme 61; 95% i 90% percentilni intervali iz istih izvlačenja.
- **H61 podržana** ako je donja granica 95% intervala > 0; gornja < 0 podržava suprotan smer.
- **Praktična ekvivalencija** prosečnog kontrasta ako je 90% interval strogo unutar [−0,02; +0,02] (TOST-analogno,
  bootstrap aproksimacija). Oznake smera i ekvivalencije prijavljuju se odvojeno (mogu važiti istovremeno); ostalo =
  neodlučno. Tvrdnja „efekat ≥ 0,02“ zahtevala bi donju granicu > 0,02.
- STOP ne daje empirijski zaključak o H61.

## 9. Semena
seed = 10⁷·p + 10⁵·i + 10³·R + 100·j + s; p = 61 razvojne reference, 62 izbor B, 63 FX-T, 64 proba, 65 test reference,
66 test; s = 1 (razvojne reference), 1..5 (izbor), 1..3 (kalibracija), 1..10 (proba), 1..2 (test reference), 1..n (test).
Seju se Python i NumPy RNG; početne populacije četiri grane iste (asercija). Simulacija snage seme 61023 (+ 61024, 61025).

## 10. Izvršavanje, pravila i provera
Populacija 32, bez sondiranja i imigracije; `exit_check="generations"`, `number_of_generations=10**9`, `timeout=10**6`;
prekid po stvarnom PF budžetu. **Test i proba se prekidaju pri prvom dostizanju cilja** (jedini inferencijalni ishod je
T); dozvoljeno tek pošto razvojna provera na 20 pokretanja pokaže identičan h za prekinute i pune putanje; reference i
izbor B ostaju puni. Svako pokretanje u novom procesu; greška ili manjak poziva → jedno ponavljanje istim semenom;
ponovljena greška izuzima celu uparenu jedinicu. Prazna ćelija onemogućava primarno zaključivanje; > 5% izuzetih jedinica
ili prazna ćelija → analiza osetljivosti (uspešni ishodi ostaju, neuspeli T = 1). Nema produžavanja budžeta, dopunjavanja
semena ni zaustavljanja prema značajnosti. B, FX-T, n, protokol, kod, zavisnosti i biblioteka heširaju se pre test
referenci; reference pre testa. Nezavisni proverivač (I58 obrazac, parametrizovan scenarijem i R) proverava svedoke L*,
prvog cilja i prijavljenog najboljeg rešenja, vezan heševima; neuspeh = nedostupan zaključak.

## 11. Budžet
Gornja granica bez ponavljanja (PF poziva): gate ≈ 0,2 M; razvojne reference 0,72 M; izbor B 0,72 M; FX-T
2 × 27 × 3 × 2 × 3 × ≤ 12.000 ≈ 11,7 M; proba ≤ 2,9 M; test reference 2,16 M; test ≤ 3 × 3 × 4 × 480 × 12.000 ≈ 207 M
(sa prekidom pri cilju očekivano manje). Ukupno ≤ ~225 M PF ≈ ≤ 230 CPU-sati (≈ 3,3–4,5 ms/PF, Codex 061 merenje),
≤ ~24 h na 10 jezgara. Dozvoljeno (korisnik: računar neograničen, i preko noći).
