# ITERATION61: replikacija interakcije H56a (adaptacija × CHT) na mrežama odvojenim od I56 (PREREGISTRACIJA)

**Status: ZAMRZNUTO 2026-10-24 (v3), PRE ijednog I58 test rezultata** (u trenutku zamrzavanja postoje samo I58
reference i manifesti; `i58_test`, `i58_check`, `i58_analysis` ne postoje) i pre ijedne linije I61 koda. Predlog:
[ITERATION61_PROPOSAL_SR.md](ITERATION61_PROPOSAL_SR.md) (Codex 055); recenzije Codex 061 (REVISE), 062 (FIX FIRST, 6
ispravki), 063 (FREEZE). Izvršavanje tek posle završetka lanca I58 → I60 → I59 i primene ispravke biblioteke v5.

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

Snaga: zahteva se svih 20 potpunih četvorovektora probe po mreži; inače STOP. Kriterijum ≥ 20% dostizanja znači
≥ 4/20 po grani, udruženo preko razvojnih scenarija. Za oba cilja θ = 0,02 i θ = 0 rešava se
(1/3) Σ_i Σ_u w_iu d_iu = θ sa w_iu ∝ exp(λ d_iu) normalizovanim unutar mreže i zajedničkim λ; zahteva se stroga
dostižnost, greška sredine ≤ 10⁻⁸ i ESS_i = 1/Σ_u w_iu² ≥ 10. Prijavljuju se λ, težine, ESS, najveća težina i ponderisane
stope dostizanja po granama. Degenerisani vektori ostaju takvi — nikakvo dodavanje efekta. Za svaku podobnu test ćeliju
nezavisno se uzorkuje n celih vektora sa vraćanjem iz naginjanog skupa njene mreže (stvarni broj podobnih test scenarija).
Snaga i kalibracija nule su uslovne na ovu empirijsku raspodelu i pretpostavljeni prenos; Wilsonovi intervali mere samo
simulacionu nesigurnost.

Za n ∈ {80, 160, 240, 320, 480} semena po ćeliji: 1000 eksperimenata sa 2000 bootstrap ponavljanja (preliminarni
izbor); bira se najmanji n sa dvostranom 95% Wilsonovom donjom granicom snage ≥ 0,8. Izabrani n se nezavisno potvrđuje
sa 1000 eksperimenata i 20.000 ponavljanja (seme 61024): potrebno ≥ 825 pozitivnih primarnih zaključaka. Nula θ = 0 se
nezavisno kalibriše sa 1000 eksperimenata i 20.000 ponavljanja (seme 61025): dozvoljeno ≤ 36 pozitivnih primarnih
zaključaka. „Pozitivan primarni zaključak“ = donja granica 95% intervala > 0. Svaka serija inicijalizuje RNG jednom;
bootstrap seme 61 se ne resetuje unutar simuliranih eksperimenata; linearna interpolacija percentila svuda. Nedostižna
alternativa/nula, ESS ispod praga, n > 480 ili neprolaz potvrde/kalibracije = STOP bez pokušaja većeg n. Orijentir
(Codex 061, iz I56 arhive): σ unutar ćelije 0,33–0,45 → potrebno n ≈ 257–465; STOP je realan ishod i prijavljuje se kao
takav.

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
seed = 10⁷·p + 10⁶·i + 10⁴·R + 10³·j + s; p = 61 razvojne reference, 62 izbor B, 63 FX-T, 64 proba, 65 test
reference, 66 test, 67 validacija prekida pri cilju; jedinstvenost semena preko različitih (p, i, R, j, s) proverava se
asercijom; isto seme namerno samo između uparenih grana/konfiguracija; s = 1 (razvojne reference, validacija prekida), 1..5 (izbor), 1..3 (kalibracija), 1..10 (proba), 1..2 (test
reference), 1..n (test).
Seju se Python i NumPy RNG; početne populacije četiri grane iste (asercija). Simulacija snage seme 61023 (+ 61024, 61025).

## 10. Izvršavanje, pravila i provera
Populacija 32, bez sondiranja i imigracije; `exit_check="generations"`, `number_of_generations=10**9`, `timeout=10**6`;
prekid po stvarnom PF budžetu. **Test i proba se prekidaju pri prvom dostizanju cilja** (jedini inferencijalni ishod je
T), uz uslov validacije: posle FX-T kalibracije, a pre probe, porede se puna i pri cilju prekinuta pokretanja za sve tri
mreže × oba razvojna scenarija × četiri grane, s = 1, p = 67 (24 para), sa istom inicijalizacijom i slučajnošću; porede
se prvi h (uključujući nedostizanje), generisane početne populacije i tačni prefiksi PF ulaza/izlaza do min(h, B_i).
Svedok cilja se beleži pre prekida; posle njega nema PF poziva. Svako nepoklapanje blokira prekid; ako nijedan par ne
dostigne cilj, validacija je neodlučna i izvršavanje punim budžetom je obavezno. Reference i izbor B uvek puni.
Pokretanje je uspešno ako bez greške ili dostigne provereni cilj ili potroši B_i poziva; ranije neobjašnjeno završavanje
→ ponavljanje. Svako pokretanje u novom procesu. Neuspela grana se ponavlja jednom istim semenom; uspešno ponavljanje se
zadržava, inače je grana nedostupna i cela četvorogranska jedinica se izuzima iz zaključivanja na potpunim slučajevima.
Broj i stopa izuzetih jedinica prijavljuju se globalno i po ćeliji (imenilac: planirane jedinice posle OPF izuzimanja).
Posle svakog izuzimanja radi se analiza osetljivosti (sve planirane jedinice, uspešni ishodi grana zadržani, T = 1 samo
za nedostupne grane); globalno izuzimanje > 5% se označava. Osetljivost je opisna i ne vraća primarno zaključivanje kad je
neka ćelija prazna. Prazna ćelija onemogućava primarno zaključivanje. Nema produžavanja budžeta, dopunjavanja semena ni zaustavljanja prema značajnosti. B, FX-T, n, protokol, kod, zavisnosti i biblioteka heširaju se pre test
referenci; reference pre testa. Nezavisni proverivač (I58 obrazac, parametrizovan scenarijem i R) proverava svedoke L*,
prvog cilja i prijavljenog najboljeg rešenja, vezan heševima; neuspeh = nedostupan zaključak.

## 11. Budžet
Osnovni maksimum bez gate-a, validacije i ponavljanja: 225,504 M PF poziva (razvojne reference 0,72 M; izbor B 0,72 M;
FX-T 11,664 M; proba 2,880 M; test reference 2,16 M; test 207,360 M). Validacija prekida dodaje ≤ 0,576 M; gate ≈ 0,2 M;
ukupno ≈ 226,3 M: 207–283 CPU-sata pri 3,3–4,5 ms/PF, idealno 20,7–28,3 h na deset jezgara, bez OPF-a, regresionih
provera, simulacije i režijskih troškova. Procene, ne gornje granice; ponavljanja dodaju rad. Prekid pri cilju (ako
validiran) očekivano smanjuje test deo. Dozvoljeno (korisnik: računar neograničen, i preko noći).
