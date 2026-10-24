# ITERATION56: tehnike za ograničenja × samoadaptacija GAdapt-a na diskretnom ORPD-u (PREREGISTRACIJA, NACRT)

**Status: NACRT — nije zamrznut.** Zamrzava se commit-om posle Codex recenzije, pre koda studije i pre ijednog
test-merenja. Predlog i prior art: [H5_PROPOSAL_SR.md](H5_PROPOSAL_SR.md) (Codex 020 revizija, §10). Merilo:
[iteration56_orpd.py](iteration56_orpd.py) (`3577b94`). Istraživački pilot samo na razvojnom scenariju:
[results/iteration56_dev_pilot/](results/iteration56_dev_pilot/).

## Obavezni elementi (CLAUDE.md)
- **Pitanje:** da li efekat samoadaptacije GAdapt-a na dostizanje izvodljivog cilja zavisi od tehnike za rukovanje
  ograničenjima (CHT), i koliko te zavisnosti prolazi kroz signale adaptacije koji čitaju VREDNOST troška (a ne
  samo redosled)?
- **Prior art:** H5 §2 i §10 (Biswas 2018, Mallipeddi 2012, Premkumar 2023, Ali 2024, Carvalho 2015, Tanabe 2024;
  CHT: Deb 2000 [10.1016/S0045-7825(99)00389-8](https://doi.org/10.1016/S0045-7825(99)00389-8), Ben Hadj-Alouane i
  Bean 1997 [10.1287/opre.45.1.92](https://doi.org/10.1287/opre.45.1.92), Takahama i Sakai 2006
  [10.1109/CEC.2006.1688283](https://doi.org/10.1109/CEC.2006.1688283)). Rizik R1 (Mallipeddi 2012 pun tekst) otvoren.
- **Novina (uska):** uzročna ablacija adaptacije sa istim operatorima × CHT × rezolucija, uz razdvajanje puta
  „redosled“ od puta „vrednost troška u signalu“. Nije nova metoda.
- **GO** (uslovno, H5 §9).

## 1. Mehanizam u kodu (provereno 2026-10-24)
CHT ulazi u GAdapt samo kroz `cost_value`: (a) redosled — elitizam (`ElitismCostFinder`) i izbor roditelja
(rulet po RANGU, `RouletteWheelSampling`), invarijantni na monotonu transformaciju; (b) vrednost — raznovrsnost
troškova (`CostDiversityPopulationUpdater`, log-raspon preživelih → broj mutiranih jedinki) i
`ParentDiversityCandidateSolutionUpdater` (razlika troškova roditelja). Kolonska raznovrsnost ne čita trošak.

## 2. Instance (zamrznuto)
- Mreže: case14 (9 kontrola), case57 (27), case118 (77); kontrole VG, otcepi, šantovi (merilo, `3577b94`).
- Rezolucija R ∈ {9, 17, 33} (ugnježdene mreže).
- Radni scenariji (load_factor, scenario_seed), spread 0,1: **razvojni** (0,95, 101), (1,05, 102);
  **test** (0,90, 201), (1,00, 202), (1,10, 203), (1,15, 204). Test instanca kojoj OPF ne uspe izuzima se i
  prijavljuje (ne zamenjuje se).
- Blok = (mreža, R); jedinica = (test scenario, seme); semena 1..10 → 40 jedinica po bloku, 360 ukupno.

## 3. Evaluacija i budžet
- Jedan poziv = jedan `runpf`; budžet **3000 poziva** po pokretanju, broje se SVI pozivi (wrapper; posle budžeta
  vraća konstantu i GAdapt se zaustavlja `exit_function`-om; `probe_cost_function=False`).
- f = gubici (MW); V = zbir bezdimenzionih prekršaja (napon p.u.; Q generatora, slack P, termika u p.u. baseMVA);
  izvodljivo ako je svaka komponenta ≤ 1e-6. Nekonvergiran PF: neizvodljivo, f nedefinisan, V = 10 (veće od
  svakog izmerenog u pilotu), broji se.
- Ishod pokretanja: (izvodljivo nađeno, najbolji izvodljiv f, najmanji V, poziv prvog izvodljivog).

## 4. CHT (skalari koje GAdapt dobija kao `cost_value`)
f_ref = gubici kontinualnog OPF-a scenarija (poznati pre pretrage; NIJE donja granica). u(f) = f / (f + f_ref)
∈ (0, 1), monotono.
- **SP (statička kazna, uobičajena upotreba GAdapt-a):** P = f + 1000·V (iz pilota; zamrznuto).
- **AP (adaptivna kazna, Ben Hadj-Alouane i Bean 1997):** P_t = f + λ_t·V, λ_0 = 1000; posle svake generacije:
  ako je najbolji preživeli neizvodljiv k = 3 uzastopne generacije, λ ← 2λ; ako je izvodljiv k = 3 uzastopne,
  λ ← λ/1,5; inače nepromenjeno. Svi preživeli se ponovo skalarizuju sa λ_t (bez novih poziva).
- **FR (Deb-ova pravila):** m = 1 + u(f) ako izvodljivo, inače m = 2 + V/(1+V).
- **EC (ε-ograničenje, Takahama i Sakai 2006):** kao FR, ali „izvodljivo“ znači V ≤ ε(τ), τ = potrošeni udeo
  budžeta; ε(τ) = ε_0 (1 − τ/0,5)^5 za τ < 0,5, inače 0; ε_0 = V jedinke na 20. percentilu početne populacije.
  Ponovna skalarizacija preživelih posle svake generacije.
- Stohastičko rangiranje izostavljeno: nije skalar (stohastičko poređenje parova); razlog se navodi.

## 5. Grane adaptacije (za svaku CHT; isti operatori, ista semena → ista početna populacija)
- **AD-N (GAdapt podrazumevano, signal nativan):** podrazumevane opcije GAdapt-a; signali (b) čitaju skalar CHT-a.
- **AD-C (zajednički signal):** isto, ali signali (b) čitaju FR skalar m nezavisno od CHT-a (za FR = AD-N).
- **FX-M (fiksno, usklađeno):** `population_mutation="random"`, `candidate_solution_mutation="random"`,
  Gausova mutacija sa fiksnim σ (istraživačka podklasa preko `GAFactory`); konstante = medijane (preko generacija i
  pokretanja) broja mutiranih jedinki, broja mutiranih promenljivih i σ iz AD-N pokretanja na RAZVOJNIM
  scenarijima (case × R, 3 semena), po CHT-u.
- **FX-T (fiksno, podešeno):** mreža 3×3×3 (udeo mutiranih jedinki {0,25; 0,5; 0,75} × udeo promenljivih
  {0,1; 0,2; 0,4} × σ {0,02; 0,05; 0,15}) na razvojnim scenarijima, R = 17, 3 semena, sve mreže; bira se
  konfiguracija sa najboljim srednjim rangom po CHT-u. Deklarisan budžet podešavanja: 27 × 2 × 3 × 3 × 4 = 1944
  pokretanja.
- Mešavina Gaus / nasumičan reset i ukrštanje ostaju podrazumevani u svim granama.

## 6. Referenca i ishod
- L*(instanca, R): najbolji izvodljiv f iz NEZAVISNIH referentnih pokretanja (GAdapt AD-N i FX-T sa FR, 30.000
  poziva, semena 9001–9003) — ne iz evaluacionih pokretanja. Bez izvodljivog u referenci → instanca × R se prijavljuje
  kao „bez reference“ i ishod je samo izvodljivost.
- **Primarni ishod Y** (rang): u svakom (blok, scenario) svi pokretanja svih grana i CHT-ova rangiraju se po ključu
  (izvodljivo nađeno, zatim najbolji izvodljiv f rastuće; neizvodljivi po najmanjem V rastuće); veze = srednji rang.
- Sekundarno: stopa izvodljivosti; jaz (f − L*)/L* uz cenzuru; ECDF dostizanja (izvodljivo i jaz ≤ 1%) po broju
  poziva; poziv prvog izvodljivog.

## 7. Hipoteze i testovi (zamrznuto)
Za jedinicu u: d_u(A, B; C1, C2) = [Y(A, C1) − Y(B, C1)] − [Y(A, C2) − Y(B, C2)].
- **H56a (primarna, interakcija):** d_u(AD-N, FX-T; FR, SP) ≠ 0. Test: Wilcoxon signed-rank na 360 jedinica
  (dvostrano, α = 0,05). Potvrđena ako p < 0,05; smer i medijana se prijavljuju; po bloku opisno (9 blokova).
- **H56b (put kroz vrednost troška):** deo interakcije prolazi kroz signale (b): d_u(AD-N, AD-C; SP, FR) ≠ 0
  (Wilcoxon, 360 jedinica). Potvrđena ako p < 0,05.
- **H56c (moderacija rezolucijom, opisno + test):** Spearman između R i medijane d_u(H56a) po bloku, unutar mreže;
  opisno, bez tvrdnje o generalizaciji na „veličinu mreže“ (3 mreže).
- Sekundarne interakcije (AP, EC naspram SP; FX-M umesto FX-T): Holm preko 4 testa.
- Snaga: 360 uparenih jedinica → ~0,15 SD (normalna aproksimacija); po bloku 40 → ~0,45 SD (samo opisno).
- **Šta obara pitanje:** p ≥ 0,05 za H56a uz |medijana d_u| < 5% raspona rangova → „interakcija nije otkrivena
  pri ovoj snazi“ (prijavljuje se kao nalaz).

## 8. Dijagnostički tragovi (opisno)
Po generaciji: koeficijent raznovrsnosti troškova, broj mutiranih jedinki, udeo izvodljivih preživelih, λ_t, ε(τ).
Mehanizam koji se proverava opisno: pod SP log-raspon preživelih dominiraju prekršaji dok populacija nije
izvodljiva, a pri prelasku u izvodljivost naglo pada (skok mutacije).

## 9. Poredbeni algoritmi (sekundarno, kontekst)
SciPy `differential_evolution` sa `integrality` (indeksi mreže) i pycma sa `integer_variables`, oba sa FR skalarom,
isti budžet i semena. Bez hipoteza.

## 10. Izvršavanje
Kod studije: `research/iteration56_cht_study.py` (posle zamrzavanja) + testovi (merit funkcije, ponovna
skalarizacija, brojač, bit-identičnost AD-N/SP sa čistim GAdapt-om). Redosled: razvojni FX-M/FX-T → reference →
test (JEDNOM) → analiza. Arhiva: sirovi ishodi po pokretanju, tragovi, `pip freeze`, SHA-256 koda i protokola.
Bez izmene biblioteke GAdapt (sve preko omotača i `GAFactory` podklasa); opt-in port u biblioteku tek posle studije.

## 11. Budžet
Test: 4 CHT × 4 grane × 9 blokova × 40 = 5760 pokretanja × ~10 s ≈ 16 CPU-sati; razvoj ≈ 6 CPU-sati; reference
3 mreže × 3 R × 4 scenarija × 2 grane × 3 semena × 30.000 ≈ 6 CPU-sati. Lokalno, paralelno; bez CI-a.
