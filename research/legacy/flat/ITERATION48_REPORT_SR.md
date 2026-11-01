# ITERATION48 — multimodalni valve-point dispečing sa sertifikovanim optimumima: izveštaj

**23. oktobar 2026.** Protokol: [ITERATION48_PROTOCOL.md](ITERATION48_PROTOCOL.md) (`d61d796`). Kod `646e881`. Biblioteka
`cc2f357`. Izvršeno je **jedno** pokretanje: 300 pokretanja (3 instance × 4 metode × 25 semena), tačno 50.000 evaluacija
svako, ukupno 142 s. Sirovi izlaz: [results/iteration48/valve_dispatch.json](results/iteration48/valve_dispatch.json).
Podaci su stvarni javni test-sistemi sa sertifikovanim globalnim optimumima (Pedroso, Kubo, Viana; arXiv:1404.4944).

Transparentno: pre pokretanja su testovi izvršili smoke test sve četiri metode na eld13@1800 (seme 1, B = 3000), bez
ispisa vrednosti. Nijedan parametar nije menjan.

## 1. Preregistrovani ishod: **DEFICIT_GADAPT** (IPOP-CMA-ES značajno bolji na 2/3)

Medijana relativnog jaza do sertifikovanog optimuma pri B = 50.000 (najgori jaz u zagradi):

| Instanca | GAdapt podrazumevano | GAdapt dokumentovano | IPOP-CMA-ES | SciPy DE | Holm p (GAdapt vs IPOP) |
|---|---|---|---|---|---|
| eld13 @ 1800 | 7,3e-3 (1,2e-2) | 9,7e-3 (1,4e-2) | **5,5e-3** (9,5e-3) | 1,9e-2 (2,5e-2) | **0,005** (IPOP bolji) |
| eld13 @ 2520 | 4,2e-3 (1,5e-2) | 8,7e-3 (1,6e-2) | 6,5e-3 (9,7e-3) | **5,0e-5** (6,2e-3) | 0,37 |
| eld40 @ 10500 | 6,1e-3 (8,7e-3) | 7,3e-3 (1,0e-2) | **4,0e-3** (8,9e-3) | 3,7e-2 (4,5e-2) | **0,047** (IPOP bolji) |

- Sekundarno: GAdapt sa dokumentovanom konfiguracijom (min std 1e-4 + decay 2,5) je značajno **lošiji** od IPOP-CMA-ES
  na 3/3 instance i lošiji od podrazumevanog GAdapt-a na svima. Preporuka iz `CLAUDE.md` se ne prenosi na ovaj problem.
- Sekundarno: GAdapt podrazumevano je značajno **bolji od SciPy DE** na eld13@1800 i eld40 (Holm p < 1e-6), a
  značajno lošiji na eld13@2520, gde DE dostiže jaz ≤ 1e-4 u 52% semena.
- Jaz ≤ 1e-4 (stopa uspeha): GAdapt 0/75, IPOP 1/75, DE 13/75 (svi na eld13@2520). Pri 50.000 evaluacija nijedan
  opšti metod pouzdano ne dostiže sertifikovani optimum.

## 2. Tumačenje
- **Razlika prema IPOP-CMA-ES je ovde mala:** faktor 1,3–1,5 po medijani jaza. Na glatkom AC dispečingu (I47) iznosila
  je 3–5 redova veličine, a na IEEE14 naponima (I5) GAdapt je gubio 12/12. Raznovrsnost GAdapt-a, dakle, **delimično
  nadoknađuje** slabu intenzifikaciju upravo tamo gde je pejzaž jako multimodalan. To je u skladu sa dijagnozom iz I46/I47.
- **Ipak nema prednosti:** IPOP-CMA-ES je značajno bolji na 2/3, a na trećoj instanci razlika nije značajna. Hipoteza
  da GAdapt-ova raznovrsnost daje prednost na multimodalnim infrastrukturnim problemima **nije podržana** pri ovom
  budžetu.
- DE je izrazito bimodalan po instancama (najbolji na eld13@2520, najlošiji na eld40). GAdapt je stabilniji, ali je
  takođe treći po kvalitetu.

## 3. Ograde
- Jedan budžet (50.000) i bez gubitaka u mreži.
- Pedroso skup podataka za 13 jedinica (poznato je da u literaturi postoje dve varijante).
- IPOP restartuje na podrazumevane `cma` uslove zaustavljanja.
