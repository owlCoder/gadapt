# ITERATION56: tehnike za ograničenja × samoadaptacija GAdapt-a na diskretnom ORPD-u (PREREGISTRACIJA, NACRT v3)

**Status: NACRT v3 — nije zamrznut.** v1 (`5766674`) → Codex 021 (6 blokirajućih); v2 → Codex 022 (REVISE:
bootstrap slojevi, sudari semena, redosled događaja, prazan skup, razvojne reference, rani prekid); v3 ih ispravlja. Zamrzava se commit-om posle ponovne recenzije, pre koda studije i pre ijednog test-merenja. Predlog i
prior art: [H5_PROPOSAL_SR.md](H5_PROPOSAL_SR.md) (§10). Merilo: [iteration56_orpd.py](iteration56_orpd.py).
Istraživački pilot samo na razvojnom scenariju: [results/iteration56_dev_pilot/](results/iteration56_dev_pilot/).

## Obavezni elementi (CLAUDE.md)
- **Pitanje:** da li efekat samoadaptivne politike mutacije GAdapt-a na vreme do izvodljivog cilja zavisi od
  tehnike za rukovanje ograničenjima (CHT)? I, uže: menja li se efekat pod statičkom kaznom kada signali adaptacije
  koji čitaju VREDNOST troška dobiju zajednički skalar?
- **Prior art:** H5 §2 i §10 (Biswas 2018, Mallipeddi 2012, Premkumar 2023, Ali 2024, Carvalho 2015, Tanabe 2024);
  CHT: Deb 2000 [10.1016/S0045-7825(99)00389-8](https://doi.org/10.1016/S0045-7825(99)00389-8), Ben Hadj-Alouane i
  Bean 1997 [10.1287/opre.45.1.92](https://doi.org/10.1287/opre.45.1.92), Takahama i Sakai 2006
  [10.1109/CEC.2006.1688283](https://doi.org/10.1109/CEC.2006.1688283). Rizik R1 (pun tekst Mallipeddi 2012) otvoren.
- **Novina (uska):** ablacija cele adaptivne politike mutacije sa istim operatorima × CHT × rezolucija diskretnih
  kontrola, plus intervencija na signal pod statičkom kaznom. Nije nova metoda; nije analiza medijacije.
- **GO** (uslovno, H5 §9).

## 1. Mehanizam u kodu (provereno 2026-10-24; Codex 021 potvrdio)
CHT ulazi u GAdapt samo kroz `cost_value`: (a) redosled — elitizam (`ElitismCostFinder`) i izbor roditelja (rulet po
RANGU), invarijantni na monotonu transformaciju; (b) vrednost — `CostDiversityPopulationUpdater` (log-raspon
preživelih / D_0 → broj mutiranih jedinki) i `ParentDiversityCandidateSolutionUpdater` (razlika troškova roditelja).
Ukrštanje (blending, p = 0,5) nije adaptivno. Ista semena → ista početna populacija (Codex 021 proba; ostaje
asercija u kodu).

## 2. Instance (zamrznuto)
- Mreže case14 (9 kontrola), case57 (27), case118 (77); R ∈ {9, 17, 33}; scenariji (load_factor, scenario_seed),
  spread 0,1: **razvojni** (0,95, 101), (1,05, 102); **test** (0,90, 201), (1,00, 202), (1,10, 203), (1,15, 204).
  Test instanca kojoj OPF ne uspe izuzima se i prijavljuje.
- Blok b = (mreža, R), 9 blokova. Jedinica u = (blok, test scenario, s), s = 1..10 → 40 po bloku, 360 ukupno.
- **Semena (bez sudara):** seed = 10^7·namena + 10^5·i_mreže + 10^3·R + 10^2·i_scenarija + s, sa s ∈ 1..99,
  i_mreže ∈ {0, 1, 2}, i_scenarija: razvojni 0, 1; test 2..5; namena: 1 = test, 2 = razvoj (FX-M, FX-T, proba),
  3 = test reference, 4 = razvojne reference. Isto seme u svim granama unutar jedinice (uparivanje). Važi i za 20
  semena (s ≤ 20).

## 3. Evaluacija, prekršaji, budžet, zaustavljanje
- Jedan poziv = jedan `runpf`; budžet **3000** poziva; broje se svi pozivi u omotaču.
- Kategorije c_k ∈ {napon (p.u.), Q generatora, slack P, termika (p.u. baseMVA)}, tol = 1e-6 po kategoriji.
  **V = Σ_k max(0, c_k − tol)**; izvodljivo ⇔ V = 0 (tačna ekvivalencija). f = gubici (MW).
- **Neuspeo PF** (nekonvergiran ili nekonačan): f_fail = 2·f_ref, V_fail = 10 (konvencija); nikad izvodljiv ni
  ε-izvodljiv; broji se.
- **Zaustavljanje (sve grane):** `exit_check="generations"`, `number_of_generations=10**9`, `exit_function` =
  budžet potrošen, `timeout=10**6`, `probe_cost_function=False`. Posle budžeta omotač vraća konstantu koja se ne
  beleži. **Rani prekid** (izuzetak, isteklo vreme, < 3000 poziva): jedno ponovno pokretanje sa istim semenom u novom
  procesu; ako se ponovi, pokretanje je „greška izvršavanja“, cela njegova jedinica se izuzima iz primarne analize
  (analiza potpunih jedinica) i prijavljuje; ako je izuzeto > 5% jedinica, dodaje se analiza osetljivosti sa T = 1. Rezultati (najbolji izvodljiv f, prvi
  poziv dostizanja cilja) dolaze iz omotača, iz stvarnih evaluacija.

## 4. CHT (skalari kao `cost_value`), sa podklasom cost finder-a
f_ref = gubici kontinualnog OPF-a scenarija (poznati unapred; NIJE granica; proverava se f > 0 i f_ref > 0).
u(f) = f/(f + f_ref).
- **SP:** P = f + 1000·V (sirovo, kao uobičajena upotreba GAdapt-a).
- **SP-T (kontrola kodiranja, samo AD-N):** m = 1 + P/(P + f_ref) (isti redosled kao SP, drugačije vrednosti).
- **AP (Ben Hadj-Alouane i Bean 1997):** P_t = f + λ_t·V, λ_0 = 1000. Dva brojača uzastopnih generacija: najbolji
  preživeli neizvodljiv / izvodljiv. Kad brojač neizvodljivih dostigne 3: λ ← 2λ; kad brojač izvodljivih dostigne 3:
  λ ← λ/1,5; posle svake promene oba brojača se vraćaju na 0 (prozori se ne preklapaju).
- **FR (Deb):** m = 1 + u(f) ako V = 0; m = 2 + V/(1+V) ako V > 0; m = 3 za neuspeo PF.
- **EC (Takahama i Sakai 2006):** kao FR uz „V ≤ ε_t“ umesto „V = 0“; ε_t = ε_0 (1 − τ_t/0,5)^5 za τ_t < 0,5, inače 0;
  τ_t = potrošeni udeo budžeta posle evaluacije potomaka generacije t (korak (2) ispod); ε_0 = 20. percentil V cele početne populacije, izračunat
  PRE prvog odsecanja; neuspeo PF m = 3.
- **Podklasa `ElitismCostFinder`-a (preko `GAFactory`), jedini redosled događaja u generaciji t:**
  (1) evaluira nove jedinke (sirovo (f, V) u keš po genotipu); (2) ažurira λ / ε iz završene istorije (preživeli
  generacije t−1; τ_t); (3) dodeli skalar SVIM jedinkama (zatečenim i novim) iz keša sa tim parametrima;
  (4) sortira i odseca; (5) GAdapt-ovi updater-i računaju signale iz tih skalara; (6) izbor roditelja u generaciji
  t+1 koristi te iste skalare. Parametri ostaju zamrznuti od (2) do koraka (2) sledeće generacije. Bez novih PF poziva pri ponovnoj skalarizaciji; imigracija isključena
  (`immigration_number=0`, podrazumevano).
- Stohastičko rangiranje izostavljeno (nije skalar).

## 5. Grane (intervencija = cela adaptivna politika mutacije)
- **AD-N:** podrazumevani GAdapt; signali (b) čitaju skalar CHT-a.
- **AD-C (zajednički signal; za SP, AP, EC):** kao AD-N, ali OBA signala (b), uključujući početni imenilac D_0 i
  početnu raznovrsnost roditelja, čitaju FR skalar m iz keša (podklase updater-a preko `GAFactory`).
- **FX-M / FX-T (fiksno):** istraživačke podklase sa TAČNIM brojevima. Skup kandidata = isti koji koristi GAdapt
  (potomci tekuće generacije sa NaN troškom, bez imigranata i već mutiranih, uključujući one iz popravke duplikata).
  k = 0 ako je skup prazan, inače k = min(|skup|, max(1, round(a·|skup|))), izbor uniformno bez vraćanja (umesto
  GAdapt-ovog izbora po raznovrsnosti roditelja — deo intervencije); v = min(d, max(1, round(b·d))) promenljivih po jedinki (uniformno bez
  vraćanja, bez drugog izvlačenja), Gausova mutacija sa fiksnim σ (menja se samo izračun σ; normalizacija,
  odsecanje, mreža, „pomeri bar jedan korak“ i 50:50 Gaus/reset ostaju). Dodatne mutacije iz popravke duplikata
  ostaju kao u GAdapt-u i beleže se odvojeno.
  - **FX-M:** jedan vektor (a, b, σ) po CHT-u: a = medijana k/|skup| po generacijama sa |skup| > 0, b = medijana
    v/d po mutiranim jedinkama, σ = medijana σ po svim Gausovim mutacijama — u svakom razvojnom AD-N pokretanju,
    zatim medijana preko pokretanja (jednake težine); razvoj: 2 scenarija × 3 mreže × 3 R × 3 semena po CHT-u
    (216 pokretanja ukupno). Zaokruživanje k, v = max(1, round(·)).
  - **FX-T:** mreža k/|skup| ∈ {0,25; 0,5; 0,75} × v/d ∈ {0,1; 0,2; 0,4} × σ ∈ {0,02; 0,05; 0,15} na razvojnim
    scenarijima, R = 17, 3 semena, sve mreže; kriterijum = srednji T (§6) preko razvojnih pokretanja; veze → manji
    indeks u redosledu mreže. Budžet podešavanja: 1944 pokretanja.
- Pokretanja u zasebnim procesima (singleton `ParentDiversityCandidateSolutionUpdater`).
- Po jedinici: SP, AP, EC × {AD-N, AD-C, FX-M, FX-T} + FR × {AD-N, FX-M, FX-T} + SP-T × AD-N = 16 pokretanja.

## 6. Referenca, cilj i primarni ishod
- **Razvojne reference (prve, pre FX-M/FX-T):** isto kao test reference, na razvojnim scenarijima, 4 CHT × AD-N ×
  1 seme (namena 4), 30.000 poziva → razvojni ciljevi za T u podešavanju i probi (72 pokretanja).
- **L\*(instanca, R):** najbolji izvodljiv f iz nezavisnih referentnih pokretanja: 4 CHT × AD-N × 2 semena (tok
  900000+), 30.000 poziva. Najbolje poznato, ne optimum ni granica. Negativni jazovi se prijavljuju.
- **Cilj:** V = 0 i f ≤ L\*(1 + 0,01) + 0,01 MW; ako za instancu × R nema izvodljivog u referenci, cilj = „V = 0“
  (unapred; broj takvih se prijavljuje).
- **Primarni ishod T ∈ (0, 1]:** (redni broj poziva prvog dostizanja cilja)/3000; T = 1 ako cilj nije dostignut
  (ograničeno vreme do cilja; nedostizanje = cenzura na budžetu).
- Sekundarno: izvodljivost na kraju, najbolji izvodljiv f, poziv prvog izvodljivog.

## 7. Hipoteze i zaključivanje (zamrznuto)
- **Kontrast:** d_u = [T(AD-N, FR) − T(FX-T, FR)] − [T(AD-N, SP) − T(FX-T, SP)].
  **Estimand:** θ_a = (1/9) Σ_b mean_{u ∈ b} d_u (jednake težine blokova).
- **Zaključivanje (uslovno na zamrznute reference, FX-M/FX-T konstante i scenarije):** stratifikovani bootstrap —
  celi upareni vektori grana jedinice uzorkuju se sa vraćanjem unutar ćelije (mreža × R × scenario); težine
  scenarija i blokova fiksne (θ = prosek blokova od proseka scenarija od proseka semena); 20.000 ponavljanja, seme
  56; 95% percentilni interval; p = min(1, 2·min(P*(θ* ≤ 0), P*(θ* ≥ 0))); ako su svi θ* = 0, p = 1.
- **H56a (primarna):** θ_a ≠ 0 — potvrđena ako 95% interval isključuje 0.
- **Sekundarne (Holm preko 5, bootstrap p):** H56b — signal pod SP: θ_b = (1/9)Σ_b mean[T(AD-N, SP) − T(AD-C, SP)];
  interakcije AP-protiv-SP i EC-protiv-SP (isti oblik kao θ_a); θ_a sa FX-M umesto FX-T; kodiranje
  (1/9)Σ_b mean[T(AD-N, SP) − T(AD-N, SP-T)].
- **H56c (opisno):** medijana d_u po bloku naspram R, po mreži; bez testa i bez tvrdnje o „veličini mreže“.
- **Snaga (pravilo pre testa):** posle izbora FX-T, proba na razvojnim scenarijima: 2 scenarija × 3 mreže × 3 R ×
  5 semena × 4 pokretanja (AD-N/FR, FX-T/FR, AD-N/SP, FX-T/SP) = 360 pokretanja → razvojni d po bloku. Simulacija:
  2000 puta po bloku uzorkuj sa vraćanjem 40 razvojnih d, centriraj na prosek bloka 0 i dodaj θ = 0,05, primeni
  konačni bootstrap (2000 ponavljanja); snaga = udeo intervala bez 0. Ako je < 80%, semena po instanci → 20 PRE
  testa (jedina dozvoljena promena; beleži se kao odstupanje).
- **Ništa ne obara pitanje** osim H56a: interval koji obuhvata 0 i |θ_a| < 0,02 → „interakcija nije otkrivena
  pri ovoj snazi“ (prijavljuje se kao nalaz).

## 8. Dijagnostički tragovi (opisno)
Po generaciji: sirovi min/max skalara preživelih, D_t, D_0, odsecanje, koeficijent, broj mutiranih jedinki i
promenljivih (nominalno i iz popravke duplikata), σ, razlika troškova roditelja, udeo izvodljivih preživelih, λ_t,
ε_t. Opisno se proverava: pod SP log-raspon dominiraju prekršaji dok populacija nije izvodljiva.

## 9. Van opsega I56
Poredbeni algoritmi (DE, CMA-ES) — posebna iteracija; nisu potrebni za interne kontraste.

## 10. Izvršavanje i arhiva
Kod: `research/iteration56_cht_study.py` + testovi (skalari, ponovna skalarizacija pre odsecanja, ε_0 pre prvog
odsecanja, tačni brojevi u FX granama, zaustavljanje i brojanje, ista početna populacija, AD-N/SP bit-identičan
čistom GAdapt-u sa istim omotačem). Redosled: validacija → razvojne reference → razvoj (FX-M, FX-T) → proba i snaga →
test reference → test JEDNOM → analiza. Arhiva: sirovi ishodi i tragovi po pokretanju, `pip freeze`, SHA-256 koda i protokola. Biblioteka GAdapt
se ne menja (omotač + `GAFactory` podklase); opt-in port posle studije.

## 11. Budžet
Test 5760 × 3000; razvoj (FX-M 216 + FX-T 1944 + proba 360) × 3000; reference (288 + 72) × 30.000 ≈ 35,6
miliona PF poziva × ~3 ms ≈ 30 CPU-sati (sa 20 semena ≈ 47); lokalno, paralelno (8 procesa ≈ 4 h). Bez CI-a.
