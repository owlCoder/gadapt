# Sažetak za mentora (2026-10-28, međustanje) — GAdapt: stabilnost, tačnost, primenljivost

Pisano za: mentora doktorata (stanje rada i šta je utvrđeno; ono što još nije, jasno je označeno).

## 1. Šta je mentor tražio i šta smo uradili
Mentorova ocena (prenos korisnika): GAdapt je dobar, nadmašuje sve algoritme osim jednog, ali je tačniji; cilj je stabilnost i primena u industriji.
Njegov eksperiment (`bpzoran/gadapt_experiments`, komit `0e388356`) smo **replicirali nepromenjen** (isti kod, parametri, 9 klasičnih funkcija, 21 ćelija, stagnacija 20) uz jedinu novinu: **nezavisno brojanje stvarnih poziva funkcije cilja**
(I64-S0, 1.680 pokretanja, protokol zamrznut pre merenja, rezultati nezavisno reprodukovani).

## 2. Šta S0 pokazuje (poštena slika)
- **Efikasnost (ECDF površina do 12.000 poziva): GAdapt je ispred sva tri konkurenta** (PyGAD random/adaptive, SciPy DE); simultani intervali potvrđuju (zamrznuto pravilo H64a: podržano). Prema DE razlika je mala (0,047 na skali 0–1), prema PyGAD velika (0,16–0,20).
- **Završna preciznost pri originalnom zaustavljanju:** GAdapt ima niži agregatni medijalni jaz od sva tri, ali to dolazi uglavnom iz dve teške ćelije (Rastrigin-20, Griewank-7). **Po ćelijama SciPy DE ima manju završnu grešku u 14 od 21 ćelije**
  (na glatkim funkcijama DE stiže ≈ 1e-14, GAdapt ≈ 1e-5 do 1e-8). Pri jednakih 12.000 poziva odnos GAdapt:DE je 10:10 po ćelijama (agregatno GAdapt bolji zbog teških ćelija).
- **Računovodstvo:** „generacije“ nisu jedinica troška. PyGAD u mentorovom kodu troši oko 2× više poziva (re-evaluacije u `best_solution()`), a PyGAD adaptive još 2×; DE u 20D troši ≈ 36.000 poziva, GAdapt ≈ 19.000.
  Zato je poređenje „po generacijama“ pristrasno u korist DE-a po brzini i protiv PyGAD-a po preciznosti.
- **Ograničenja:** funkcije nisu pomerene ni rotirane (četiri imaju optimum u ishodištu); 20 semena; ne sme se tvrditi opšta veća preciznost, industrijska pouzdanost ni uzročna uloga mutacije.

## 3. Šta je završeno posle S0 (rezultati)
- **I64-E (pomereno/rotirano, jednak budžet od 12.000 stvarnih poziva, devet konfiguracija, 100 semena):** po zamrznutom pravilu H64a **suprotan ishod** — tri varijante CMA-ES (CMA, IPOP, BIPOP) su dokazano efikasnije od GAdapt-a; GAdapt je dokazano efikasniji od oba PyGAD-a, DE-a i (1+1)-ES. **Rep raspodele (prosek najgorih 10%, CVaR) je kod GAdapt-a najbolji od svih na osno-poravnatim funkcijama (0,0033), ali 2× lošiji od CMA porodice pod rotacijom (0,039 naspram ≈ 0,019).** Dakle prednost u tačnosti/stabilnosti važi za osno-poravnate (separabilne) probleme; za spregnute promenljive, tipične u infrastrukturi, CMA porodica je bolja. Preset „stabilnosti“ ne pomaže.
- **I64-E2 (negativan, preregistrovan):** opcioni diferencijalni krosover u biblioteci NE zatvara taj jaz (pogoršava efikasnost na svim varijantama).
- **I63** (replikacija jedne ORPD interakcije): konačan STOP u fazi snage zbog nedostižnog kriterijuma kalibracije (greška dizajna protokola, ne podatak); deskriptivna ekstenzija I63-D i infrastrukturna studija **I64-I** (stvarni ORPD, devet konfiguracija) su u toku.

## 4. Šta nije utvrđeno (bez uljepšavanja)
Originalna nova metoda ili teorema nije nađena: 16 kandidata odbačeno je na proverenoj literaturi (npr. kontrola koraka, invarijantnost signala, teorija kazne, ograničena jedinstvenost). Doprinos disertacije je trenutno: replikacija i proširenje
benchmarka sa stvarnim brojanjem poziva, revizija integriteta evaluacija (alat + studije), preregistrovane studije (uključujući negativne i nezaključne) i inženjerski ispravne opcione funkcije biblioteke. Da li to dovoljno za doktorat je odluka mentora.

## 5. Šta treba od mentora
(1) Koji je tačno „jedan algoritam“ koji GAdapt ne nadmašuje (verovatno SciPy DE ili CMA-ES) i na kojim problemima je to video (rezultati/tabela)? (2) Da li su klasične funkcije bez rotacije prihvatljive kao dokaz, ili traži rotirane/stvarne infrastrukturne probleme?
(3) Šta je „stabilno“ za njega: mali raspon rezultata između pokretanja, odsustvo retkih loših ishoda, ili ponovljivost sa istim semenom?
