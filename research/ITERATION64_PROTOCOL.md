# ITERATION64: replikacija i proširenje mentorovog benchmarka (GAdapt „stabilan, tačan, primenjiv“) — NACRT PROTOKOLA, NIJE ZAMRZNUT

Izvor pitanja: mentor (preko korisnika, 2026-10-28): GAdapt je dobar, nadmašuje sve algoritme osim jednog, ali je tačniji; cilj je stabilnost i primena u industriji.
Eksperiment mentora: https://github.com/bpzoran/gadapt_experiments (verzija `0e388356`; GAdapt diversity mutation, PyGAD random/adaptive mutation, SciPy DE best1exp;
9 klasičnih funkcija, dimenzije 2/7/20, 1000 pokretanja, zaustavljanje stagnacijom 20 generacija, limit 600). Codex 083 (`research/codex/083_*`).
Doprinos: replikacija, proširenje i karakterizacija pouzdanosti — NE nova metoda ni teorema (prior art poređenja adaptivnih mutacija na klasičnim funkcijama:
Srinivas–Patnaik 1994 10.1109/21.286385; Marsili Libelli–Alba 2000 10.1007/s005000000042). Nema tvrdnje o industrijskoj spremnosti.

## Faze (svaka sa sopstvenim GO/STOP; skupa faza se ne pokreće bez prethodne)
- **I64-S (sintetika, jeftina)**: najpre ovde. Odgovara na mentorovo pitanje na njegovom domenu.
- **I64-I (infrastruktura)**: ORPD (case14/30/39/57/118 × R ∈ {9,17,33} × 2 nova scenarija) i penalizovani AC dispečing (5 mreža × 2 scenarija). Zasebna zamrznuta dopuna
  posle uvida samo u razvojni deo I64-S; procena do ≈ 3000 CPU-sati (Codex 083), pokreće se tek po odluci.

## I64-S dizajn
1. **Replikacija (R)**: 21 kombinacija funkcija/dimenzija (Sphere, Rosenbrock, Rastrigin, Ackley, Griewank, Styblinski–Tang × {2,7,20}; Beale, Himmelblau, Booth 2D), originalne četiri konfiguracije
   sa originalnim parametrima (pop 64, elitizam 50%, stagnacija 20, limit 600 generacija), 100 pokretanja po ćeliji sa uparenim semenima, **nezavisno brojanje stvarnih poziva** funkcije cilja po
   fazama (inicijalizacija, generacije, probe/validacija, callback) kroz omotač; zapis putanje „najbolje do sada“ po stvarnom pozivu. Bez izmene koda mentorovih runnera (uvoz iz klona na zamrznutom heš-u).
2. **Proširenje (E)**: iste 21 kombinacije × {originalna, pomerena, pomerena+rotirana} = 63 ćelije; konfiguracije: GAdapt (podrazumevano), GAdapt preset
   (`normal_distribution_mutation_min_std_dev=1e-4`, `normal_distribution_mutation_min_std_dev_decay_generations=2.5`), PyGAD random, PyGAD adaptive, SciPy DE (best1exp, kao u originalu),
   CMA-ES, IPOP-CMA-ES, BIPOP-CMA-ES (`cma`), (1+1)-ES sa restartima; L-SHADE i jDE samo ako postoji validirana implementacija (CEC-provera) u zasebnom okruženju, inače izostavljeno i prijavljeno.
   **Budžet po pokretanju: tačno 12.000 stvarnih poziva** (spoljni omotač prekida), bez stagnacionog zaustavljanja (restarti su deo zamrznute konfiguracije); snimci na 3000 i 12.000.
   100 semena po ćeliji; isto seme = isti početni uzorak gde je moguće; pomeraji i ortogonalne matrice iz javnog semena; minimum ostaje u domenu; rotacija sfere je negativna kontrola.
3. **Mere** (jaz g = (f − f*)/(scale) ≥ 0, f* poznat; L = g/(1+g), neuspeh/izvršni otkaz L = 1; ne izbacuju se pokretanja): medijana jaza; kvantili 90/95%; **CVaR₀,₉** (prosek najlošijih 10%);
   verovatnoća dostizanja ciljeva g ≤ 1e−2, 1e−4, 1e−6; ECDF dostizanja ciljeva po broju evaluacija (nedostizanje u imeniocu); SD samo opisno (nije definicija stabilnosti).
4. **Analiza**: uparena semena, Wilcoxon + rank-biserial efekat, Holm; medijane/CVaR/verovatnoće stratifikovanim bootstrapom celih uparenih vektora (20.000, 95%); sintetika sa jednakim težinama funkcija.
   Replikacija (R) i proširenje (E) odvojeno.
5. **Hipoteze** (Codex 083): H64a (mentorova): „bolji“ = veća površina ispod ECDF-a dostizanja ciljeva; GAdapt nadmašuje sve konkurente osim najviše jednog, i ima niži završni medijalni jaz od tog izuzetka;
   simultani intervali moraju podržati oba dela, neznačajno nije pobeda. Suprotan ishod: ≥ 2 konkurenta efikasnija, ili izuzetak i tačniji. Neodlučeno ako intervali ne razrešavaju.
   H64b (preset): agregatni CVaR gubitka manji ≥ 20% bez pada verovatnoće dostizanja većeg od 5 procentnih poena naspram podrazumevanog GAdapt-a.
6. **Budžet (S)**: R ≈ 21 × 4 × 100 pokretanja (do 600 generacija); E ≈ 63 × 9 × 100 × 12.000 ≈ 680 M jeftinih evaluacija; GAdapt overhead ~ms/generaciji — procena CPU-sati posle merenja na razvoju.
7. **Zamrzavanje**: protokol, zavisnosti (zaključane verzije), javna semena, raspored pomeraja/rotacija, heš mentorovog repoa i biblioteke pre prvog merenja; kod omotača i
   nezavisni proverivač (nezavisno brojanje poziva vs. prijavljeni najbolji) pre merenja; create-once faze kao u I63.

## Otvorena pitanja pre zamrzavanja (za Codex recenziju)
(a) Koji tačno algoritam mentor misli kao „izuzetak“ (verovatno DE ili CMA-ES) — protokol ne zavisi od toga, hipoteza se ocenjuje preko rangiranja. (b) Validacija L-SHADE/jDE implementacije. (c) Kako tačno uračunati
GAdapt-ove probe (`probe_cost_function`) — prijavljuju se zasebno, i uračunavaju se u budžet. (d) Da li preset zahteva i varijantu sa bit-identičnim podrazumevanim (da).
