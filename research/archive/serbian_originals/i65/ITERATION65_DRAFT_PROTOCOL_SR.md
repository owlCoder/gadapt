# I65-DRAFT — uski benchmark: stagnacija, restart ili prelaz GAdapt→CMA

**Datum:** 2026-11-01  
**Status: DRAFT, NIJE FREEZE / preregistracija / rezultat.**  
**Zavisnosti:** `ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md`, `ITERATION65_INSTRUMENTATION_VALIDATION_SR.md`, I64-S0/E/E3/A/R/I/I2.  
**Repo:** `owlCoder/gadapt`; upstream ne menjati. Nijedna podrazumevana opcija GAdapt-a se ne menja. Implementacija nove algoritamske politike zabranjena pre zatvaranja `AGENTS.md` gate-a za novost/eksplicitnu odluku o inženjerskoj studiji. Nema push/PR/CI bez odgovarajućeg odobrenja.

## Q65: istraživačko pitanje, precizna klasifikacija doprinosa

Može li politika koja nakon 20 **dovršenih** generacija bez značajnog poboljšanja preusmerava GAdapt preostali budžet na CMA smanjiti najgori decil postignute greške na pejzažima bez pravilne globalne strukture, **bez neprihvatljivog pada rane konvergencije**, prema unapred zamrznutim IPOP-CMA-ES i fiksnom hibridu I64-E3? Ovo je **inženjerska empirijska hipoteza**, a ne dokaz naučne novine. `novelty not established` za adaptivne restarte/switching/portfolio/hibrid (vidi audit).

Konačna preporuka je dozvoljena samo za eksplicitno testiranu raspodelu instanci, budžet i zahtev kvaliteta; nikada „garantovano za svaku funkciju“.

## Scope i procedure za problem

1. **Primarni ciljni skup (ne ponavlja I64-E):** originalni COCO jednokriterijumski `bbob` f21 (Gallagher 101 Peaks) i f24 (Lunacek bi-Rastrigin), D ∈ {2,10,20}, tri nezavisne **held-out** COCO instance {6,7,8} po funkciji/dimenziji; ukupno 2×3×3 = **18 primarnih ćelija**. Svaka instanca je već pomerena i transformisana internim, verifikovanim COCO pravilima; ne zamenjivati je proizvoljnom formulom. Nativni pretraživački domen [-5,5]^D; svi algoritmi dobijaju isti fizički domen i granice u istim jedinicama. COCO izvori: https://coco-platform.org/testsuites/bbob/functions/f21.html i https://coco-platform.org/testsuites/bbob/functions/f24.html ; `cocoex.Suite('bbob','year: 2009', ...)` prema javnoj dokumentaciji. **Ne koristiti `bbob-biobj`**: f21/f24 tamo označavaju druge parove.
2. **Kontrole:** Rastrigin i Styblinski–Tang, D ∈ {2,10,20}, po jedna fiksna transformacija `shift` i `rotm` sa **istim pomerajem o** (2×3×2 = **12 kontrolnih ćelija**). I64 `e_common.transform` geometrija, Q generisana QR procedurom, javno seme `np.random.default_rng([65, 3, cell])`; čuvati Q, o, testirati `Q Qᵀ≈I`, vrednost u poznatom optimumu i dosezanje optimuma iz domena. Dodatno sačuvati 2D original/rot referentne probe samo radi hardverskog testa, ne kao potvrdne ćelije.
3. **Ciljana dijagnostika ortogonalne promene f21/f24:** samo COCO instanca 6 × D {2,10,20} × `shift`, `rotm` (12 dijagnostičkih ćelija) × 5 politika (A–E) × 15 semena. Spoljašnja promena koordinata sme se raditi **isključivo ako zvanični COCO core na odvojenom oracle primerku izloži `x_opt` i `f_opt`**, i `f(x_opt)` prođe witness test. Transformacija `f(x_opt + 10 Qᵀ(y-o))`, `y∈[0,1]^D`, Q=I za `shift`; Q i o identični za par. Ako eksponiranje pozicije nije pouzdano/reproduktivno, **ne improvizovati**: izostaviti 12 dodatnih ćelija, obelodaniti, a na COCO native ne donositi uzročnu tvrdnju o dodatnoj Q. Oracle nije dostupan optimizeru i njegovo otkrivanje ne sme kontaminirati benchmark-problem; registrovati/setup pozive odvojeno od svakog run-a.
4. **Razvoj**: COCO instance {1,2,3} (nikad {6,7,8}), D=2,10,20, 10 razvojnih semena po ćeliji, samo dovoljno pokretanja za integracioni gate, vreme izvršavanja i izbor dopuštenih epsilon/detektor varijanti. Nema uvida u held-out ishode pre freeze. Ne proveravati potvrdu periodično tokom razvoja.
5. **Infrastruktura:** ne koristiti stare ORPD ćelije kao novu nezavisnu potvrdu. Samo uz zasebno zamrznut i nezavisno verifikovan skup novih ORPD/dispatch zadataka; dimenzionalnost diskretnih slučajeva izvestiti odvojeno i bez lažne tvrdnje da su isti kao f21/f24. Na postojećim ćelijama samo dijagnostika kompatibilnosti.

### Referentne vrednosti i normalizacija

`g=max(0,(f_best - f_opt)/s_i)` i `L=g/(1+g)`, kao I64; isti denominator `s_i` za sve algoritme **u istoj ćeliji**. Za COCO `f_opt` dobiti od verifikovanog official oracle u zasebnoj analitičkoj putanji, **ne** koristiti `problem.final_target_fvalue1` kao tačan optimum bez provere (može sadržati ciljnu toleranciju). `s_i`: unapred generisan medijan 4096 uniformnih tačaka sa javnim setup semenom, bez pokušaja optimizacije; čuvati sve vrednosti i SHA. Te 4096 setup evaluacije su odvojeni javni trošak izgradnje benchmarka, ne pojedinačni algoritamski pozivi; ne koristiti f_opt/s_i za algoritamsko odlučivanje/restart (osim ako posebno promenjena politika taj trošak naplati svakom run-u). Rekalkulacije `g < -1e-12` (u norm. skali) ili `s_i≤0` = STOP. Na ORPD-u bez sertifikovanog optimuma ne zvati relativni odnos prema kontinualnom OPF-u „certified gap“.

## Polisa algoritama — svih devet primarnih metoda

| ID | Politika / status | Pravedno poređenje |
|---|---|---|
| M | GAdapt-M kao u I64-E (64, mentorovi operatori), prirodni završetak/restart sa preostalim B | Bez izmene `GA` default-a i bez dodatnog tuninga. |
| DE | SciPy `differential_evolution`, `best1exp`, `init` 64 stvarnih kandidata, `mutation=(0.5,1)`, `recombination=.7`, `polish=False`, `rng` seed | Eksplicitno `tol=0,atol=0`; konvergencija biblioteke nije detektor. Re-evaluacije, ako postoje, naplatiti. |
| CMA | pycma CMA-ES, restart sa konstantnom populacijom | Zamrznuti I64-E parametri. |
| E | pycma IPOP-CMA-ES | Primarni jaki baseline. |
| BIPOP | pycma BIPOP-CMA-ES | Dodatna jaka kontrola portfolija. |
| A | GAdapt-M + zajednički detektor: pri STAGNATION definitivni STOP | Ne troši veštačke pozive da dopuni B; opisati neiskorišćen budžet. Kriva ECDF do B je konstantna posle STOP. |
| B | GAdapt-M + STAGNATION → restart **istog** GAdapt-M | Novi RNG podtok, isti B, global incumbent sačuvan, max jedan restart po STAGNATION. |
| C | GAdapt-M + STAGNATION → CMA-ES do kraja preostalog B | Warm start iz najboljeg validiranog GAdapt svedoka, `sigma0=0.05` kao E3; prirodne CMA restarte pokriti E3 pravilom. Ako nema stagnacije: samo GAdapt. Jedan prelaz, bez oscilovanja nazad. |
| D | Fiksni I64-E3 30% GAdapt → 70% CMA-ES, `sigma0=0.05`; novi restart nakon završetka isti kao E3 | Jak baseline; ne menjati udeo poslе uvida u potvrdu. |

**Posebna ablacija:** semantičko pravilo STAGNATION isto je za sve algoritme u telemetriji, ali A/B/C odlučuju na osnovu **GAdapt** generacija; E/BIPOP/CMA/DE internal generacije nisu ekvivalentne. Merenje u stvarnim `nfev` (sekundarna varijanta „bez napretka tokom N evaluacija“ samo ako je zasebno preregistrovana). DE restarti i CMA politiku iz E dokumentovati eksplicitno.

## Stagnacija i stanja

Po završetku kompletne generacije t, sa `best_previous` kao globalno najboljim konačnim troškom do t−1 i `best_current` do t:

`delta = best_previous - best_current`  
`improved = delta > eps_abs + eps_rel*max(1,abs(best_previous))`

Ako je `improved`, reset na 0; inače +1; tačno nakon **20 uzastopnih završenih generacija** bez značajnog poboljšanja logovati *jedan* `STAGNATION` događaj (timestamp `nfev`, generacija, faza, `best_y`, `best_f`). Init populacija jeste naplaćena ali nije prva završena generacija. Prelaz pri nepotpunoj generaciji usled B nije dozvoljen. Ne smatrati STAGNATION statusom `SUCCESS`. Na restartu se resetuje brojač stagnacije, **ne** globalni incumbent.

**DRAFT epsilon roster za development:** `(eps_abs,eps_rel)∈{(0,0),(1e-10,0),(1e-8,0)}` na sirovoj ceni (bez upotrebe `f_opt`). Razlog za primarni kandidat `eps_rel=0`: COCO dodaje *instance-dependent* `f_opt` pomeraj; sirova relativna tolerancija može zavisiti od proizvoljne aditivne konstante. Ako se pre freeze doda normalizovano, implementabilno centriranje `b_t` za `eps_rel>0`, sve kalibracione probe fizički naplatiti i unapred fiksirati. Posle development samo **jedan** izabrani par i pravilo izbora upisati u FREEZE, bez ponovnog izbora na potvrdi. Na callback statusima: `INVALID_RESULT`, `FAILED`, `BUDGET_EXHAUSTED`, `STOPPED_STAGNATION`, `SUCCESS_VALIDATED`, `NOT_SOLVED` su međusobno jasno razdvojeni.

## Budžeti i brojanje

- B=12.000 fizičkih pokušaja evaluatoru po pokretanju, uključujući početnu populaciju, GAdapt all-min/max probe (`GA.execute()`), validacione pozive, callback-e, ispravke, poliranje, recalc, prelaske i sve restarte. **Rezervisati najmanje 1 od tih B mesta za nezavisni završni witness**: algoritamska pretraga može potrošiti najviše 11.999 pokušaja, a nezavisni objektiv ponovo vrednuje najbolji prijavljeni konačni vektor kao pokušaj ≤12.000, bez čitanja bibliotečkog cached rezultata. Ako svedok ne postoji ili provera otkaže, evidentirati `NOT_SOLVED` / `INVALID_RESULT`; ne nadoknađivati skrivenim B+1 pozivom. Pri ranom STOP-u proveriti svedoka pre završetka. `B=3000` je *snapshot istog traga*, **ne novi run**; pri 3000 označiti rezultat kao privremen/nepotvrđen ukoliko se nezavisna provera još nije dogodila. Trošak metode A može biti ispod B jer prekida; prikazati `unused_B`.
- Obavezan monotoni physical_attempt counter, rezervacija pre poziva, `n<=B`, log `attempted`, `returned_finite`, `nonfinite`, `exception`, `callback`, `recheck`, `phase`, `candidate`. Nezavisni završni witness je naplaćeni, eksplicitno označen poziv unutar B; istorija `time-to-target` razlikuje pretraživački pogodak od nezavisne potvrde uspeha. Revalidacije izvođene van run-a za dodatnu naučnu recenziju imati zaseban javno prijavljen broj fizičkih poziva, bez tvrdnje da su deo režima B=12k. Ako stvarni simulator obuhvata više poziva po “jednoj evaluaciji”, zadati trošak su fizički solver pozivi i eksplicitno razložiti. Ulazni vektor kopirati pre poziva; ne prihvatiti optimizatorov `success=True` bez nezavisnog svedoka.
- Algoritmi mogu koristiti iste budžetske kvote ali različit broj dovršenih generacija. Pri B-preseku sa parcijalnom CMA generacijom ne pozivati `tell` sa fiktivnim rezultatima; završiti bez propagiranja pogrešnog stanja.

## Uzorak, semena, veličina i CPU cap

- **Held-out native COCO:** 18 ćelija × 9 metoda × 30 semena = **4.860 runova**, najviše 58.320.000 pokušaja.
- **Analitičke kontrole:** 12 ćelija × 9 metoda × 15 semena = **1.620 runova**, najviše 19.440.000 pokušaja.
- **Opciona unapred zamrznuta dijagnostika dodatne Q:** 12 ćelija × 5 A–E metoda × 15 semena = **900 runova**, najviše 10.800.000 pokušaja. Ukupni cap glavne i kontrolne faze = **77.760.000**; sa dijagnostikom = **88.560.000**. `A` može koristiti manje poziva. Odgovarajući račun je zaseban od development/setup/witness rezervacije.
- **Seme:** `seed(stage,c,s)=65_000_000+1_000_000*stage+1_000*c+s`; `stage=1` za razvoj, `stage=3` za potvrdu, `s=1..10` dev, `s=1..30` held-out, `s=1..15` kontrole; par (cell,seed) identičan između metoda. COCO instance {1,2,3} dev, {6,7,8} confirm. Bibliotečki potok po metodi deterministički izveden iz seed-a i ID-a, eksplicitno zamrznut; **isti seed nije ista realizovana populacija**.
- **Realni CPU plan:** pre velikog run-a pilot od ≤0,5 CPUh samo na razvojnim instancama, u fiksnom okruženju, meri `t_f` i algoritamski overhead za svaku dimenziju/metodu. Ukupni cilj 24–72 CPUh za primary+controls (procena, ne garancija); hard cap **120 CPUh** za potvrdni deo. Pri projekciji preko cap-a — STOP i nova odobrena specifikacija pre uvida u held-out, nikakvo tiho smanjivanje semena. Najviše 4 radnika, `maxtasksperchild=1` za kontaminaciju RNG; bez automatskog GitHub Actions. Arhive particionisane po ćeliji, `create-once`, resume samo nedostajućih uspešno zaključanih ćelija, SHA-256 svake particije.

## Metrički protokol i statistički kontrasti

- Za τ∈{1e−2,1e−4,1e−6}, `T_tau=prvi fizički pokušaj s g<=τ` ili ∞; `A = (1/(3B)) ∑τ max(0,B−T_tau+1)`; `P(hit by B)`, `P(hit by 3000)`; ECDF kriva po fiz. evaluacijama i AUC, time-to-target/censored.
- Završni `g` i `L=g/(1+g)`; po ćeliji median, q10/q90/q95 i CVaR 10% najgorih L; za 30 semena CVaR je najgora 3, uz eksplicitno upozorenje o nepreciznosti. `L=1` kod rezultata bez konačnog svedoka. Outcome i failure-rate/invalid-rate/overrun/recheck mismatch odvojeno. Izvodljivost za ORPD **pre** kvaliteta; gap računati samo za izvodljive ako je referenca definisana.
- Primarna težina COCO: jednaka f21/f24, jednaka D, jednaka held-out instanca; kontrole i dodatna Q **ne ulaze** u primarnu odluku. Zajednička prednost uzorka kod CVaR: semena se uparuju po (f,d,instance,s); ne mešati instance i semena kao nezavisne jedinice za generalizaciju.
- Preregistrovana porodica kontrasta **C vs E i D** na native f21/f24: `CVaR(ref)−CVaR(C)` (pozitivno povoljno), `A(C)−A(ref)` (pozitivno povoljno) za ref∈{E,D}. Četiri simultana jednostrana 95% donja intervala (max-t paired bootstrap, 20.000 ponavljanja, seme 65065), uz hijerarhijski resampling instanca/semena i izvještavanje koliko se rezultat menja ako je instanca jedinica replikacije. 3 instance nisu čvrsta osnova za univerzalnu generalizaciju.
- **GO za ograničeni praktični izbor C**, samo ako istovremeno: (i) donja simultana granica `CVaR(E)−CVaR(C)` > +0,01 **i** `CVaR(D)−CVaR(C)` > 0,00; (ii) obe donje simultane granice `A(C)−A(E)` i `A(C)−A(D)` ≥ −0,03; (iii) potvrđen `P(g≤1e-2)` ne pada više od 0,05 prema oba ref (simultani intervali u istoj porodici — **proširiti porodicu na 6 pre freeze**); (iv) nijedan budget overrun, neprihvaćen svedok ili prikriven invalid; (v) ORPD nije prikazan kao potvrđen bez posebne infrastrukturne studije. Ako tačka odstupi: **NO-GO** za praktičnu preporuku C; ako intervali seku granicu: **UNDECIDED**, nema retuning-a ni repeticije radi pozitivnog ishoda. Sekundarni svi-parovi, medijane, CVaR u kontrolama i 3000 presek su opisni.

## FREEZE gate (strogo pre prvog held-out poziva)

1. **Literatura** + mentorska odluka: `novelty not established`; dopuštena samo uska empirijska studija ili zaseban originalni diferencijator s proverljivim theorem-claim-om. U suprotnom, obustaviti implementaciju C (AGENTS).
2. Nezavisni pregled implementacije i metodologije, naročito referentnog `Budget` izuzetka/svedoka; integracioni testovi B-1/B/B+1, izuzeci, NaN, ties, inicijalizacija, callback, replay u dva procesa, transform `f(y=o)=fopt`, COCO true fopt, Q ortogonalnost, nezavisno re-vrednovanje. Za COCO internal oracle implementacija bez curenja informacija optimizeru.
3. Za sve metode zaključati verzije Python, NumPy, SciPy, pycma, cocoex, GAdapt i referentnih transformacija; sha256 source tree, Git commit, promenljive okruženja, CPU model, `pip freeze`, `PYTHONHASHSEED`, seeds, transform matrice, COCO IDs, f_opt, s_i, izabrane eps vrednosti i CMA restart schedule. Sačuvati `manifest_freeze.json`, heš manifest-a i commit *pre* koda/konfirmatornih podataka prema pravilima repozitorijuma. Ako ne postoji potpuni manifest — NO-FREEZE.
4. Proći dev-isključivo pipeline test. Nema „preview“ prvih konfirmatornih semena (I64-S0 pre-run slučaj je dokumentovan rizik). Jedna kompletna potvrda, nikakvo biranje metode po held-out.
5. Ispisati `FROZEN: <commit>, <manifest_sha256>, <review_reference>, <date>` **tek kad je to stvarno urađeno**. Trenutno se ove vrednosti namerno ne popunjavaju.

## Infra deployment gate i statusi

Ulaz → deterministička validacija → optimizacija B → nezavisna provera granica, diskretnih koraka, AC PF ograničenja, i ponovo izračunate cene po *istom* modelu → ako validno i predefinisani prag kvaliteta, `SUCCESS_VALIDATED` → inače, ako ima budžeta, unapred specificirani fallback (npr. sertifikovano bezbedno bazno stanje ili prethodna odobrena konfiguracija, uz jasno prebrojanu proveru) → ako ni to ne zadovoljava, `NOT_SOLVED`. Fallback mora imati sopstveni sigurnosni dokaz i nije automatski „optimum“. Prijaviti neuspehe, nerazrešene AC PF proračune, constraint feasibility posebno, nema industrijske garancije.

**Trenutna odluka:** audit/jeftina validacija = GO; novelty = NO-GO; FREEZE i held-out benchmark = **BLOCKED** dok se ne zatvore gore navedeni gateovi. Nijedna nova optimizaciona vrednost nije izmerena.