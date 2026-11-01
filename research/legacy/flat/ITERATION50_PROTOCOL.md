# ITERATION50: potvrdna replikacija revizije integriteta evaluacija na novom uzorku biblioteka (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre snimka okvira uzorka, pre adaptera i pre ijednog posmatranog obrasca poziva.**
Datum: 2026-10-23.

- Prethodno: [ITERATION49_PROTOCOL.md](ITERATION49_PROTOCOL.md) i [ITERATION49_REPORT_SR.md](ITERATION49_REPORT_SR.md).
- Prior art i odluka GO: [H4_PRIOR_ART_AUDIT_SR.md](H4_PRIOR_ART_AUDIT_SR.md).

## 0. Obavezni elementi predloga (CLAUDE.md)
- **Istraživačko pitanje:** da li se nalaz iz I49 („problemi integriteta evaluacija su česti“, 4/9, 95% CI 14–79%)
  ponavlja na novom uzorku biblioteka izabranom spoljnim pravilom? Koliko je uži zajednički interval?
- **Najbliži prior art:** Ravber i sar. 2025, [10.15388/25-INFOR603](https://doi.org/10.15388/25-INFOR603). Njihovih
  13 okvira izabrano je po citatima i zvezdicama, a poredi se kvalitet rešenja, ne integritet poziva. Dalje: COCO
  ([10.1080/10556788.2020.1808977](https://doi.org/10.1080/10556788.2020.1808977)) i IOHexperimenter
  ([10.1162/evco_a_00342](https://doi.org/10.1162/evco_a_00342)) za brojanje evaluacija.
- **Tvrdnja o novini:** nema nove tvrdnje. Ovo je potvrdna replikacija uskog doprinosa H4 (GO), sa poboljšanim alatom
  (D3x, §4) i unapred zadatim pravilom razvrstavanja (§6), koje je u I49 bilo post hoc.
- **Pretpostavke:** biblioteke se koriste kroz dokumentovani API uz podrazumevana podešavanja. Funkcija troška je
  deterministička i čista. Omotač vidi svaki poziv.
- **Hipoteza (falsifikovana ako):** problemi integriteta su česti i na novom uzorku. Hipoteza je opovrgnuta ako
  je gornja granica Clopper–Pearson 95% intervala za k/N **< 1/3**.
- **Baseline i kontrole:** referentni optimizator sa podmetnutim greškama (osetljivost), čista referenca
  (specifičnost), GAdapt kao pozitivna kontrola za C1.
- **Budžet:** CPU, bez GPU-a. Najviše 600 s po pokretanju, inače se beleži greška (`timeout`), ne nalaz.
- **GO/NO-GO:** GO (H4 GO važi). Bez podešavanja posle gledanja rezultata. Jedno pokretanje.

## 1. Okvir uzorka (spoljno pravilo; snimak se arhivira)
Okvir je unija dva izvora:
- **A. GitHub snimak:** repozitorijumi sa jezikom Python, ≥ 300 zvezdica i bar jednom od tema `black-box-optimization`,
  `derivative-free-optimization`, `evolutionary-algorithms`, `evolutionary-algorithm`, `metaheuristics`, `metaheuristic`,
  `genetic-algorithm`, `particle-swarm-optimization`, `differential-evolution`, `cma-es`, `bayesian-optimization`,
  `global-optimization`. Pretraga se radi preko `gh search repos` (do 200 po temi), a snimak se čuva u
  `research/results/iteration50/frame_snapshot.tsv`.
  - Tema `hyperparameter-optimization` je namerno izostavljena, jer su to uglavnom ML cevovodi, a ne opšti optimizatori.
- **B.** Python okviri iz tabele 1 rada Ravber i sar. 2025: DEAP, MEALPY, NiaPy, Nevergrad, EvoloPy, pymoo i pygmo
  (pagmo2 sa Python vezom).

**Isključuje se** 9 biblioteka iz I49 i GAdapt. Uzorak je nov.

**Napomena o izvodljivosti:** pre zamrzavanja pogledan je samo broj i imena kandidata iz pravila A (57 repozitorijuma),
bez ijednog pokretanja. Zbog toga je izostavljena tema `hyperparameter-optimization` i dodat izvor B.

## 2. Kriterijumi prihvatljivosti (primenjuju se na snimak pre ijednog stvarnog pokretanja)
Biblioteka ulazi u uzorak ako ispunjava **sve** uslove:
1. Biblioteka je za opštu upotrebu, a ne tutorijal, aplikacija, AutoML/NAS cevovod ili LLM agent.
2. Repozitorijum nije arhiviran u trenutku snimka.
3. Postoji paket na PyPI-ju koji se instalira na Python 3.14 sa NumPy 2.x, bez GPU-a i bez ručnog kompajliranja.
4. Postoji dokumentovan API za minimizaciju korisničke Python funkcije realnog vektora nad kutijom, sa jednim ciljem.
5. Smoke test sa **konstantnom** funkcijom troška (N = 2, budžet 20) završava se bez greške. Obrasci poziva se ne
   gledaju; beleži se samo da li se pokretanje završilo.

Ako prihvatljivih ima više od 25, uzima se 25 sa najviše zvezdica. Za izvor B, zvezdice se čitaju u istom snimku.
Odluka za svaku biblioteku, sa razlogom, upisuje se u `research/ITERATION50_ELIGIBILITY.md`, koji se komituje **pre**
glavnog pokretanja.

## 3. Konfiguracija i problemi
- **Algoritam:** podrazumevani ili prvi dokumentovani jednokriterijumski optimizator iz README/quickstart-a. Tačan izbor i
  parametri upisuju se u `ITERATION50_ELIGIBILITY.md` pre pokretanja.
- **Budžet:** cilj je **200 evaluacija**, zadat preko dokumentovanog parametra. Ako biblioteka zadaje generacije ili
  iteracije, budžet se računa iz dokumentovane veličine populacije (najbliže ≤ 200).
- **Seme:** dokumentovani mehanizam. Ako on ne postoji, seme se zadaje za `random` i `numpy.random`, i to se beleži.
- **Problemi:** isti kao u I49: pomerena sfera, Rastrigin i plato, N ∈ {2, 10}, kutija [−5, 5]^N, semena 6000–6004.
  Ukupno 30 ćelija po biblioteci.
- Invarijantnost G1 se **ne meri**. To je prior art i nije deo primarnog ishoda.

## 4. Mere
Mere iz I49 ostaju nepromenjene: C1, C2, C3, C4, C5, R1, R2, R3, D2 i D3. Kod I49 se ponovo koristi bez izmene
klasifikatora. Uvodi se jedna nova mera:
- **D3x, nereproduktivnost između procesa:** ista ćelija se pokreće u dva sveža procesa (`python -I`), sa
  `PYTHONHASHSEED=1` i `PYTHONHASHSEED=2`. Ako se heševi niza poziva razlikuju, to je D3x.
  - Uvodi se zato što je u I49 D3 meren samo u istom procesu (naknadna provera Nevergrad-a, I49 §6).

**Nalaz integriteta za biblioteku:** bar jedan od C1, C3, C4, C5, R1, R2, R3, D2, D3 ili D3x, u bar jednom
pokretanju. C2 se, kao i u I49, prijavljuje kao udeo rasipanja. C4 važi samo tamo gde je dokumentovan maksimum
broja evaluacija (dokaz se upisuje u `ITERATION50_ELIGIBILITY.md`).

## 5. Validacija alata (pre glavnog pokretanja; mora proći)
- Svih 5 mutanata iz I49 i čista referenca daju tačno očekivane klase.
- GAdapt sa podrazumevanim podešavanjima daje C1, a sa `probe_cost_function=False` ne daje.
- **Novi mutanti za D3x:**
  - `hash_seeded`: seme se izvodi iz `hash()` niske. Mora dati D3x, a **ne** D3.
  - `time_seeded`: seme se uzima iz `time.time_ns()`. Mora dati i D3 i D3x.
- Čista referenca ne sme dati ni D3 ni D3x.

## 6. Primarni ishod i unapred zadato razvrstavanje
- **Primarno:** k/N biblioteka sa nalazom, uz Clopper–Pearson 95% interval [lo, hi].
  - **PONOVLJENO (ČESTO):** k/N ≥ 1/3 i lo ≥ 0,10.
  - **OPOVRGNUTO (RETKO):** hi < 1/3.
  - **NEODLUČENO:** sve ostalo.
- **Sekundarno:**
  - zajednička procena I49 + I50 (9 + N biblioteka) sa CP intervalom;
  - medijane udela duplikata (C2).
- **Razvrstavanje svakog nalaza (pravilo zadato sada; dokumentacioni citati se zamrzavaju pre pokretanja):**
  - **protivreči dokumentaciji:**
    - dokumentacija kaže da je parametar budžeta maksimum evaluacija, a javlja se C4;
    - dokumentacija kaže da seme daje reproduktivnost, a javlja se D3 ili D3x;
    - dokumentacija kaže da je vraćeno najbolje evaluirano rešenje, a javlja se R1, R2 ili R3;
    - dokumentacija kaže da se granice poštuju, a javlja se C3;
  - **dokumentovano ponašanje:** dokumentacija eksplicitno opisuje ponašanje;
  - **praznina u dokumentaciji:** sve ostalo.
  - Za svaku biblioteku se u `ITERATION50_ELIGIBILITY.md` pre pokretanja upisuju URL i citat dokumentacije za
    budžet, seme, vraćeni rezultat i granice. Ako citat ne postoji, upisuje se „nema“.
- **Sekundarni ishod:** broj biblioteka sa nalazom koji protivreči dokumentaciji, sa CP intervalom.
- **„Već poznato“:** posle pokretanja se za svaki nalaz pretražuje issue tracker biblioteke (termini: seed,
  reproducible, deterministic, bounds, budget, max evaluations, duplicate, best). Rezultat se beleži sa linkom.

## 7. Etika, objava i arhiviranje
- Za nov, neprijavljen nalaz koji protivreči dokumentaciji, prvo se proverava najnovija verzija ili glavna grana.
  Ako nalaz i dalje stoji, prijavljuje se **jedan** činjenični issue po biblioteci, sa minimalnim primerom. Korisnik
  je ovakve radnje prepustio autonomnoj proceni (2026-10-23).
- PR-ovi ka tuđim repozitorijumima (CLA) zahtevaju posebno odobrenje.
- Izlazi:
  - `research/results/iteration50/integrity_audit.json`, sa verzijama, SHA-256 izvora i svim ćelijama, uključujući
    greške;
  - `ITERATION50_REPORT_SR.md`, i kada su rezultati negativni.
- Jedno pokretanje. Posle gledanja rezultata ne menjaju se ni konfiguracije ni uzorak.
