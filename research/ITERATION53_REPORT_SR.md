# ITERATION53 — oracle test uzroka zaostatka GAdapt-a (IZVEŠTAJ)

**Datum:** 2026-10-23.
- Protokol: [ITERATION53_PROTOCOL.md](ITERATION53_PROTOCOL.md) (`5937063`). Recenziju protokola pre zamrzavanja uradio je
  Codex (gpt-6.1-sol, samo čitanje): [research/codex/002_*](codex/); svih 6 primedbi uneto pre merenja.
- Kod: [iteration53_oracle_step.py](iteration53_oracle_step.py) (`10e7e80`), testovi 8/8.
- Sirovi izlazi: [results/iteration53/](results/iteration53/) (`synthetic.json`, `reference.json`, `runs.json`,
  `analysis.json`; verzije paketa i SHA-256 izvora u svakom).
- Merenje je pokrenuto jednom.
- Saradnja: mehanizam „Gausov pomak ili uniformni reset, 50/50 po koordinati“ i sintetički faktorski dizajn
  predložio je Codex ([codex/001_*](codex/)); proverio sam ih u kodu pre uvođenja.

## 1. Deo A — sintetički mehanizam (N = 10, 12 semena, 3000 evaluacija)

Medijana log10 gapa (f* = 0):

| Problem | DR (podraz.) | DN | FR | FN | OR | ON (oracle, bez reseta) | CMA |
|---|---|---|---|---|---|---|---|
| sfera | −3,19 | −5,01 | −1,88 | −0,36 | −4,91 | **−8,56** | −12,00 |
| elipsoid (dijag., κ = 10⁶) | 0,15 | 3,21 | 1,85 | 3,98 | −0,15 | −0,10 | −0,95 |
| rotirani elipsoid | 4,14 | 3,72 | 4,22 | 3,96 | 3,99 | 3,93 | 1,67 |

D = podrazumevani korak, F = bez donje granice σ, O = oracle; R = sa uniformnim resetom, N = bez njega.

- **A1 (ON bolji od DR na sva 3 problema): NIJE PODRŽANO.** Holm p: sfera 0,0007; elipsoid 0,26; rotirani 0,09.
- **A2 (ON zatvara ≥ 90% jaza na dijagonalnom elipsoidu, < 50% na rotiranom): NIJE PODRŽANO.** Zatvaranje:
  sfera 0,61; elipsoid 0,23; rotirani 0,09.
- Opisno (Holm p, jednostrano, Holm preko 3 problema po kontrastu; smerovi definisani u kodu `10e7e80`):
  * Uklanjanje donje granice σ (F naspram D) nigde ne pomaže (p = 1 svuda); medijane su gore.
  * Bez reseta, uz podrazumevani korak (DN naspram DR): bolje na rotiranom elipsoidu (11/12 semena, p = 0,018, ~2,65×),
    a na dijagonalnom elipsoidu gore na svih 12 semena (medijana 0,15 → 3,21).
  * Oracle korak bez reseta (ON naspram DN): bolje na sferi i dijagonalnom elipsoidu (p = 0,0007 oba), ne na rotiranom.
  * Bez reseta, uz oracle korak (ON naspram OR): bolje na sferi (p = 0,0007), ne na elipsoidima.
- Brojeve, presude A1/A2 i p-vrednosti nezavisno je ponovo izračunao Codex iz svih 252 sirova zapisa
  ([codex/004_*](codex/)): sve se poklapa.

**Tumačenje (post hoc, uže od prvog nacrta, posle Codex provere 004):**
- Na sferi kombinovana intervencija (oracle korak + bez reseta) zatvara 61% jaza do CMA (na log skali sa podom 10⁻¹²);
  sam korak bez reseta (DN → ON) ~40%, sam korak uz reset (DR → OR) ~20%. Kontrola koraka je, dakle, važan, ali ne
  jedini deo jaza ni na izotropnom problemu.
- Na elipsoidima ni oracle korak ni uklanjanje reseta ne zatvaraju jaz (zatvaranje 0,23 i 0,09). Na rotiranom
  elipsoidu jedini merljiv efekat je uklanjanje reseta (~2,65×). Rotacija pogoršava podrazumevani GAdapt za ~4 reda
  veličine (DR), ali je taj pad zavisan od grane (DN ~0,5, FN ~0).
- Kandidat-objašnjenje: GAdapt radi po koordinatama (mutacija po promenljivoj; blending crossover sa koeficijentom
  po koordinati) i ne uči korelacije. To je **verodostojno, ali nije utvrđeno**: nijedna grana ne izoluje učenje
  kovarijanse, oracle je skalarni (bez informacije o zakrivljenosti), mutiraju se potomci, a CMA-ES na rotiranom
  elipsoidu ni sam nije konvergirao pri 3000 evaluacija (medijana gapa ~46).
- Dijagonalni elipsoid, DN ≫ DR: verodostojno je da resetovi obnavljaju raznovrsnost po koordinati i vrednosti oko
  optimuma, koje blending po koordinati koristi na separabilnoj funkciji; trajektorije nisu arhivirane, pa nije provereno.

## 2. Deo B — AC dispečing (5 slučajeva, 12 semena, 3000 `runpf` po pokretanju)

Referenca (CMA-ES, 60.000 evaluacija, najbolje od 3 semena) zamrznuta je i komitovana pre pokretanja grana (`5774553`).
Svih 360 pokretanja ima tačno 3000 poziva; 538 s. Nijedno pokretanje nije bolje od reference.

Medijana log10(score − score_ref):

| Slučaj | G0 | GN | OR1 | ORN | ORN01 | CMA | jaz G0−CMA | C(ORN) | C(OR1) | C(GN) |
|---|---|---|---|---|---|---|---|---|---|---|
| case14 | 2,01 | 1,99 | 1,97 | 2,01 | 2,27 | −2,31 | 4,32 | 0,00 | 0,01 | 0,00 |
| case30 | 2,02 | 2,35 | 1,87 | 1,69 | 2,19 | −2,00 | 4,02 | 0,08 | 0,04 | −0,08 |
| case39 | 3,10 | 4,62 | 2,34 | 1,66 | 3,04 | −1,89 | 4,98 | 0,29 | 0,15 | −0,30 |
| case57 | 1,11 | 2,06 | 0,36 | 0,17 | 1,83 | −2,85 | 3,96 | 0,24 | 0,19 | −0,24 |
| case118 | 4,08 | 4,65 | 3,96 | 3,91 | 4,26 | 3,73 | 0,35 | — | — | — |

Holm p (jednostrano, preko 5 slučajeva po testu):

| Test | case14 | case30 | case39 | case57 | case118 |
|---|---|---|---|---|---|
| primarni: ORN bolji od G0 | 0,28 | 0,14 | **0,001** | 0,14 | **0,001** |
| S1: GN bolji od G0 (reset) | 1 | 1 | 1 | 1 | 1 |
| S2: ORN bolji od GN (korak bez reseta) | 0,60 | **0,002** | **0,001** | **0,002** | **0,001** |
| S3: OR1 bolji od G0 (korak uz reset) | 0,42 | 0,19 | **0,006** | 0,42 | **0,006** |

## 3. Preregistrovana odluka: **H53 OPOVRGNUTO** (u uskom smislu iz protokola)

- Odlučujući slučajevi: case14, case30, case39, case57 (case118 ima jaz G0−CMA 0,35 < 0,5 i ne ulazi u odluku).
- C(ORN) < 0,5 na 4/4 odlučujuća slučaja; ≥ 0,9 ni na jednom.
- **Značenje (kako je preregistrovano posle Codex recenzije 002):** izotropni korak skaliran udaljenošću najboljeg
  rešenja od reference (κ = 1), bez uniformnog reseta, NIJE dovoljan da zatvori jaz GAdapt-a do CMA-ES na AC
  dispečingu: zatvara 0–29%. To ne isključuje mutaciju kao uzrok uopšte (mutiraju se potomci, ne najbolje rešenje;
  κ fiksno; bez informacije o zakrivljenosti).

## 4. Opisno (izvodljivost i atribucija)

- **Izvodljivost (preregistrovano izveštavanje):** case14–case57: 0 izvodljivih rešenja u svim granama, uključujući
  CMA-ES (kao u I47; poređenje važi za penalizovani score). **case118:** izvodljivo rešenje nađeno u G0 2/12,
  GN 0/12, OR1 9/12, **ORN 12/12**, ORN01 0/12, CMA 12/12. Na jedinom slučaju gde je izvodljivost dostižna, oracle
  korak izjednačava GAdapt sa CMA-ES po izvodljivosti, iako penalizovani score ostaje malo lošiji.
- Uklanjanje reseta samo po sebi (GN) nigde ne pomaže, a na case39 i case57 šteti (medijane 3,10 → 4,62; 1,11 → 2,06).
  Korak i reset deluju zajedno: oracle korak pomaže tek kad nema reseta (S2 značajan na 4/5), slabije uz reset (S3 2/5).
- κ = 0,1 (ORN01) je svuda gore od κ = 1: oracle sa premalim korakom stagnira.
- PF neuspesi (nekonvergiran `runpf`, kazna 1e12): ukupno 2691 od 1.080.000 poziva; raspodela po granama je u
  `runs.json`.

## 5. Zaključak (deo A + deo B)

1. Na stvarnom AC dispečingu zaostatak GAdapt-a za CMA-ES (4–5 redova veličine u penalizovanom skoru na 4 slučaja)
   **nije objašnjen kontrolom koraka mutacije niti uniformnim resetom**: idealizovani (oracle) korak zatvara najviše 29%.
2. Na sintetičkim kvadratnim funkcijama isti oracle zatvara 61% na sferi, ali 23% na dijagonalnom i 9% na rotiranom
   elipsoidu. Obrazac sa dispečinga (malo zatvaranje) liči na elipsoide, ne na sferu.
3. Preostali kandidat-uzrok je **varijacija po koordinatama bez učenja korelacija i skala** (mutacija po promenljivoj,
   blending crossover po koordinati). To je verodostojno, ali NIJE utvrđeno ovim eksperimentom; uzročni test bi bila
   intervencija koja GAdapt-u daje ispravnu geometriju (npr. izbeljivanje koordinata kovarijansom iz reference) bez
   promene ostatka algoritma.
4. Prior-art provera (Codex 003, DOI provereni): ispravka kontrole koraka tipa „rasipanje × množilac po uspehu“ je
   poznata (AMBOA 2004, AVS 2006, SDR 2007, RV-GOMEA 2017). Ni kao PhD metoda ni kao glavni uzrok ne vodi dalje.
5. Praktično (opisno, case118): oracle korak bez reseta daje izvodljivost 12/12 naspram 2/12 za podrazumevani GAdapt.
   To je dijagnostička gornja procena, ne metoda; realan kontroler koraka bez oracle-a nije testiran.
