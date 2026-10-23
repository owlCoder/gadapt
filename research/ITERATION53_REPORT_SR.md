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

## 2. Deo B — AC dispečing

(u toku)
