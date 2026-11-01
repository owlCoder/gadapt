# ITERATION42 — Faza 0 (strukturni VIG pretest za H1): izveštaj

**22. oktobar 2026.** Protokol: [ITERATION42_PROTOCOL.md](ITERATION42_PROTOCOL.md), zamrznut u komitu `01b3c52`.
Kod i testovi su komitovani pre pokretanja (`57730b9`). Izvršeno je **jedno** pokretanje, bez ikakve izmene posle
gledanja rezultata. Sirovi izlaz je u [results/iteration42/phase0.json](results/iteration42/phase0.json) (SHA-256 izvora i
ulaza, verzije paketa). Ukupno vreme: 21,8 s, samo grafovski račun: nula GA, cost-funkcija i solver poziva.

## Odluka: **H1 NO-GO**

Medijana broja PX komponenti `k` pri 10% različitih gena je ≤ 2 na **23 od 25** evaluabilnih instanci (prag je 2/3).
Odluka ne zavisi od instance ta2, koju je zaštita od eksplozije pretrage (2M heap koraka po zahtevu, §3.4 protokola)
označila kao neevaluiranu: i da je ta2 imala `k ≥ 3`, bilo bi 23/26 ≥ 2/3.

Na skoro svim SNDlib topologijama, sa dve najkraće putanje po zahtevu, geni po kojima se roditelji razlikuju čine
**jednu džinovsku komponentu** (prosečan udeo najveće komponente je 0,9–1,0). PX bi tada samo izabrao celog roditelja,
pa H1 nema mehanizam. H1 se zatvara bez Faze 1 i bez ponavljanja sa drugim parametrima.

## Rezultati po instanci

Kolone `k` su medijane po 1000 uzoraka. „Najveća komp.“ je prosečan udeo najveće komponente pri p = 0,10.

| Instanca | Geni | Fiksni | Gustina VIG | max \|D_e\| | k (5%) | k (10%) | p90 k (10%) | P(k≥3) (10%) | Najveća komp. | k (20%) |
|---|---|---|---|---|---|---|---|---|---|---|
| abilene | 130 | 2 | 0,757 | 81 | 1 | 1 | 1 | 0,000 | 0,998 | 1 |
| atlanta | 210 | 0 | 0,530 | 81 | 1 | 1 | 1 | 0,008 | 0,996 | 1 |
| brain | 12691 | 1620 | 0,551 | 4828 | 1 | 1 | 1 | 0,000 | 1,000 | 1 |
| cost266 | 1332 | 0 | 0,281 | 297 | 1 | 1 | 1 | 0,000 | 1,000 | 1 |
| dfn-bwin | 90 | 0 | 0,434 | 34 | 2 | 1 | 2 | 0,003 | 0,969 | 1 |
| dfn-gwin | 110 | 0 | 0,346 | 34 | 2 | 1 | 2 | 0,054 | 0,917 | 1 |
| di-yuan | 22 | 0 | 0,316 | 7 | 2 | 2 | 2 | 0,000 | 0,656 | 2 |
| **france** | 300 | 0 | 0,285 | 73 | 3 | **3** | 4 | 0,847 | 0,834 | 3 |
| geant | 462 | 0 | 0,381 | 137 | 1 | 1 | 1 | 0,000 | 0,997 | 1 |
| germany50 | 662 | 0 | 0,171 | 105 | 2 | 1 | 2 | 0,064 | 0,985 | 1 |
| giul39 | 1471 | 0 | 0,177 | 134 | 1 | 1 | 1 | 0,000 | 1,000 | 1 |
| india35 | 595 | 0 | 0,193 | 97 | 2 | 1 | 2 | 0,010 | 0,993 | 1 |
| janos-us-ca | 1482 | 0 | 0,287 | 305 | 1 | 1 | 1 | 0,000 | 1,000 | 1 |
| janos-us | 650 | 0 | 0,336 | 149 | 1 | 1 | 1 | 0,000 | 1,000 | 1 |
| newyork | 240 | 0 | 0,270 | 50 | 2 | 1 | 2 | 0,011 | 0,990 | 1 |
| nobel-eu | 378 | 0 | 0,350 | 103 | 1 | 1 | 1 | 0,005 | 0,995 | 1 |
| nobel-germany | 121 | 0 | 0,450 | 52 | 2 | 1 | 3 | 0,106 | 0,908 | 1 |
| nobel-us | 91 | 0 | 0,672 | 37 | 1 | 1 | 1 | 0,000 | 0,985 | 1 |
| norway | 702 | 0 | 0,262 | 122 | 1 | 1 | 1 | 0,000 | 0,999 | 1 |
| pdh | 24 | 0 | 0,312 | 9 | 2 | 2 | 2 | 0,000 | 0,657 | 3 |
| pioro40 | 780 | 0 | 0,194 | 117 | 2 | 1 | 2 | 0,010 | 0,983 | 1 |
| polska | 66 | 0 | 0,558 | 22 | 2 | 1 | 2 | 0,029 | 0,934 | 1 |
| **sun** | 67 | 0 | 0,289 | 14 | 2 | **3** | 4 | 0,567 | 0,652 | 2 |
| ta1 | 326 | 0 | 0,256 | 61 | 3 | 2 | 3 | 0,174 | 0,886 | 1 |
| ta2 | — | — | — | — | — | — | — | — | — | — |
| zib54 | 1244 | 2 | 0,263 | 371 | 1 | 1 | 2 | 0,005 | 0,995 | 2 |

ta2: `not_evaluated_pop_limit` (prekinuta pretraga druge putanje za jedan zahtev).

## Tumačenje i ograde

- **Mehanizam:** dve najkraće putanje između udaljenih čvorova razlikuju se na mnogo linkova, a jezgreni linkovi
  pripadaju stotinama skupova `D_e` (max |D_e| do 4828). Čak i 10% nasumičnih gena zato deli bar jedan link u lancu.
  Ovo je u skladu sa literaturom o gustim realnim VIG-ovima ([H1_PRIOR_ART_AUDIT_SR.md](H1_PRIOR_ART_AUDIT_SR.md) §4).
- **Strukturni VIG je konzervativan** (može biti gušći od stvarnog, §3.5 protokola). Ideja da se gustina smanji
  neinterakcijom specifičnom za par roditelja (ravni delovi stepenaste cene) **ne** otvara H1 ponovo. Protokol
  zabranjuje ponavljanje sa izmenjenom konstrukcijom, ta ideja već je obuhvaćena Def. 1 iz Chicano 2024, a zahteva
  saobraćajne podatke kojih nema.
- APX i DPX (poznati operatori) mogli bi da izvuku nešto i iz guste strukture, ali to su postojeće metode, bez
  novosti za GAdapt.
- Rezultat je strukturan i važi za topohub konverzije, ne za izvorne SNDlib fajlove.

## Status hipoteza za GAdapt posle I42

| Hipoteza | Status |
|---|---|
| I41 (sertifikovana redukcija redova) | NO-GO kao metoda (POST_I41 audit) |
| H1 (gray-box PX) | **NO-GO**: novost nije utvrđena, a Faza 0 je falsifikovala mehanizam |
| H2 (I41 kao redukcija scenarija u GA evaluaciji) | NO-GO (POST_I41 §5) |

Nijedna aktivna hipoteza ne ostaje. Sledeći korak je izbor novog istraživačkog pravca, a to je odluka korisnika.
