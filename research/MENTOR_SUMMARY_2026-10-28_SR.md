# Sažetak za mentora (stanje 29. oktobra 2026. posle E4, I64-I i I64-I2; I63-D ostaje u toku) — GAdapt: stabilnost, tačnost, primenljivost

Pisano za: mentora doktorata (stanje rada i šta je utvrđeno; ono što još nije, jasno je označeno).

## 1. Šta je mentor tražio i šta smo uradili
Mentorova ocena (prenos korisnika): GAdapt je dobar, nadmašuje sve algoritme osim jednog, ali je tačniji; cilj je stabilnost i primena u industriji.
Njegov eksperiment (`bpzoran/gadapt_experiments`, komit `0e388356`) smo **replicirali** (mentorove funkcije i konfiguracije, 9 klasičnih funkcija, 21 ćelija, stagnacija 20) uz instrumentaciju: **nezavisno brojanje stvarnih poziva funkcije cilja**, seedovanje DE-a i obelodanjena odstupanja (tri od dvadeset semena bila su viđena u probi pre glavnog pokretanja)
(I64-S0, 1.680 pokretanja, protokol zamrznut pre merenja, rezultati nezavisno reprodukovani).

## 2. Šta S0 pokazuje (poštena slika)
- **Efikasnost (ECDF površina do 12.000 poziva): GAdapt je ispred sva tri konkurenta** (PyGAD random/adaptive, SciPy DE); simultani intervali potvrđuju (zamrznuto pravilo H64a: podržano). Prema DE razlika je mala (0,047 na skali 0–1), prema PyGAD velika (0,16–0,20).
- **Završna preciznost pri originalnom zaustavljanju:** GAdapt ima niži ponderisani prosek ćelijskih završnih medijana normalizovanog jaza; prema DE-u veliki deo razlike potiče iz dve teške ćelije (Rastrigin-20, Griewank-7). **Po ćelijama SciPy DE ima manju završnu grešku u 14 od 21 ćelije**
  (na glatkim funkcijama DE stiže ≈ 1e-14, GAdapt ≈ 1e-5 do 1e-8). Post hoc, pri najviše 12.000 poziva odnos ćelijskih medijana GAdapt:DE:jednako iznosi 10:10:1 (agregatno GAdapt bolji zbog teških ćelija).
- **Računovodstvo:** „generacije“ nisu jedinica troška. približno 32/64/96 poziva po generaciji za GAdapt/PyGAD random/PyGAD adaptive (uz re-evaluacije u `best_solution()`); DE u 20D troši ≈ 36.000 poziva, GAdapt ≈ 19.000.
  Generacije zato nisu uporediva jedinica troška.
- **Ograničenja:** funkcije nisu pomerene ni rotirane (četiri imaju optimum u ishodištu); 20 semena; ne sme se tvrditi opšta veća preciznost, industrijska pouzdanost ni uzročna uloga mutacije.

## 3. Šta je završeno posle S0 (rezultati)
- **I64-E (pomereno/rotirano, jednak budžet od 12.000 stvarnih poziva, devet konfiguracija, 100 semena):** po zamrznutom pravilu H64a **suprotan ishod** — prema simultanim intervalima CMA, IPOP i BIPOP imaju veći ponderisani A od GAdapt-a; GAdapt ima veći A od oba PyGAD-a, DE-a i (1+1)-ES. Post hoc, opisno: CVaR GAdapt-a je 0,0033 na originalnim i pomerenim funkcijama, a 0,0386 pod rotacijom (CMA porodica oko 0,019). Osno poravnanje ne znači separabilnost; nalaz ne ustanovljava prednost na infrastrukturnim problemima. Preset: H64b nije podržana (CVaR 0,0117 → 0,0121).
- **I64-E2 (negativan, preregistrovan):** opcioni diferencijalni krosover ne zatvara taj jaz; A je niži pod rotacijom i na objedinjenom orig+shift podskupu. Uzrok nije izolovan.
- **I64-I (stvarni diskretni ORPD, devet konfiguracija, 8 ćelija × 30 semena, 12.000 stvarnih PF) i I64-I2 (hibrid):** GAdapt je među najboljima u izvodljivosti (0,746) i dokazano bolji od PyGAD-a i DE-a, ali smer razlike prema CMA porodici je nerazrešen (kriterijum H64c neodlučen); preset suprotno; prednost hibrida prema GAdapt-M nije potvrđena, a rep je lošiji od IPOP-ovog (H64h1 neodlučeno, H64h2 suprotno). **Napomena o poreklu:** polje `i_run_sha256` u I2 arhivi je prazno; heševi I artefakata dokumentovani su naknadnom dopunom u vreme analize, pa preregistrovana pre-run provera heša nije ispunjena (numerički nalazi su nezavisno reprodukovani). Indeks sprege κ kao pokazatelj izbora: neodlučeno (5/8, 7/8).
- **I63** (replikacija jedne ORPD interakcije): konačan STOP u fazi snage jer zamrznuti strogi kriterijum kalibracije nije zadovoljen (ishod ne daje podatak o H56a); deskriptivna ekstenzija I63-D je u toku.

- **I64-E3 (hibrid GAdapt → CMA-ES, 30% / 70% budžeta):** E3 poboljšava rotacijske ishode prema GAdapt-M: H64g1 podržana, H64g2 suprotna (rep na orig+shift 1,8× veći), H64g3 neodlučena; ukupni kriterijum nije ispunjen. Post hoc: među šest prikazanih konfiguracija hibrid ima najniže agregate CVaR/M (0,0070/0,00293), A je 0,7511 prema 0,7699 za IPOP; neinferiornost nije potvrđena. To NIJE čist GAdapt (većinu budžeta troši CMA); bez ablacija nije utvrđen doprinos pojedinih faza.

## 4. Šta nije utvrđeno (bez uljepšavanja)
Originalna nova metoda ili teorema nije nađena: 16 kandidata odbačeno je na proverenoj literaturi (npr. kontrola koraka, invarijantnost signala, teorija kazne, ograničena jedinstvenost). Doprinos disertacije je trenutno: replikacija i proširenje
benchmarka sa stvarnim brojanjem poziva, revizija integriteta evaluacija (alat + studije), preregistrovane studije (uključujući negativne i nezaključne) i opcione funkcije biblioteke sa dokumentovanim implementacionim proverama (opšta pouzdanost, empirijska korist i industrijska spremnost nisu ustanovljene). Da li to dovoljno za doktorat je odluka mentora.

## 5. Šta treba od mentora
(1) Koji je tačno „jedan algoritam“ koji GAdapt ne nadmašuje i na kojim problemima je to video (rezultati/tabela)? (2) Da li su klasične funkcije bez rotacije prihvatljive kao dokaz, ili traži rotirane/stvarne infrastrukturne probleme?
(3) Šta je „stabilno“ za njega: mali raspon rezultata između pokretanja, odsustvo retkih loših ishoda, ili ponovljivost sa istim semenom?
