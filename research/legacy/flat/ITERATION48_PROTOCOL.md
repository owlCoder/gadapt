# ITERATION48 — da li GAdapt-ova raznovrsnost donosi prednost na multimodalnom dispečingu? (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre pokretanja.** Datum: 2026-10-23. Odluka korisnika: opcija „C pa A“
([STRATEGY_AFTER_I47_SR.md](STRATEGY_AFTER_I47_SR.md)).

## 0. Predlog (format iz `CLAUDE.md`)
- **Pitanje:** GAdapt čuva raznovrsnost po cenu intenzifikacije (I43–I47). Da li mu to donosi prednost tamo gde bi
  trebalo, na **jako multimodalnom** stvarnom problemu, protiv jakih metoda sa restartima?
- **Prior art:** valve-point dispečing je standardni multimodalni benchmark, sa desetinama metaheuristika, npr.
  Li, Zhang, Lu 2019, [10.1109/ACCESS.2019.2927574](https://doi.org/10.1109/ACCESS.2019.2927574) (DOI proveren).
- **Novost: ne tvrdi se.** Ovo je falsifikacija GAdapt-ove prednosti, za dijagnostičku studiju (opcija A).
- **GO/NO-GO:** GO, jeftino, samo lokalno.

## 1. Podaci (stvarni, sa sertifikovanim optimumom)
Pedroso, Kubo, Viana (2013), arXiv:1404.4944 (proveren); podaci su arhivirani u
[data/pedroso_valve_2013/](data/pedroso_valve_2013/) sa `SHA256SUMS` i `SOURCE.md`. Instance i sertifikovani globalni
optimumi (Gurobi, gap 0,0%):

| Instanca | Optimum |
|---|---|
| eld13 @ 1800 MW | 17963,8287998 |
| eld13 @ 2520 MW | 24169,9169018 |
| eld40 @ 10500 MW | 121412,532719 |

Formula: `F_i(p) = a_i + b_i p + c_i p² + |e_i sin(f_i (p_min,i − p))|`, uz `Σ p_i = opterećenje`, bez gubitaka.

## 2. Formulacija (ista za sve metode)
- **Promenljive:** snage svih jedinica osim balansne, u `[p_min, p_max]`, u MW.
- **Balansna jedinica:** prva jedinica sa najvećim `p_max − p_min` (eld13: jedinica 1; eld40: jedinica 13). Njena
  snaga je `opterećenje − Σ ostale`.
- **Prekoračenje:** ako je balansna snaga van granica, trošak se računa sa odsečenom vrednošću plus `1000 · |prekoračenje|`
  [$/MW]. Rešenje je izvodljivo ako je prekoračenje ≤ 1e-6 MW.
- **Ishod:** najbolji penalizovani trošak, odnosno relativni jaz `(F − F*)/F*` prema sertifikovanom optimumu.

## 3. Metode (isti budžet, B = 50.000 evaluacija, kontrolne tačke 5.000 / 20.000 / 50.000)
1. **GAdapt podrazumevano:** `GA(cost_function=...)`, `probe_cost_function=False`, izlaz isključivo po budžetu.
2. **GAdapt dokumentovana konfiguracija:** kao 1, plus `normal_distribution_mutation_min_std_dev=1e-4` i
   `normal_distribution_mutation_min_std_dev_decay_generations=2.5`. Ovo je preporuka iz `CLAUDE.md`, izvedena ranije
   na drugim benchmark-ovima; ovde se ne podešava.
3. **IPOP-CMA-ES** (`cma` 4.5.0), u normalizovanim koordinatama [0, 1]:
   - σ0 = 0,3, granice preko opcije `bounds`, x0 uniforman;
   - restart kada `es.stop()` javi bilo koji uslov osim budžeta, sa populacijom udvostručenom pri svakom restartu.
4. **SciPy DE:** podrazumevana strategija (best1bin, popsize 15), `polish=False`, `tol=0`, prekid tačno na budžetu.

- Semena 5000–5024 (25, uparena); seeduju se i `random` i `numpy.random`.

## 4. Statistika i odluka (B = 50.000)
- **Primarno:** GAdapt podrazumevano vs IPOP-CMA-ES, uparen dvostrani Wilcoxon po instanci, Holm preko 3.
  - **PREDNOST_GADAPT:** GAdapt je značajno bolji na ≥ 2/3.
  - **DEFICIT_GADAPT:** IPOP-CMA-ES je značajno bolji na ≥ 2/3.
  - **NEODLUČNO:** sve ostalo.
- **Sekundarno (odvojene Holm porodice po 3):** GAdapt dokumentovana vs IPOP-CMA-ES; GAdapt podrazumevano vs DE.
- **Opisno:** stopa uspeha (jaz ≤ 1e-4), medijana i najgori jaz na svim kontrolnim tačkama.

## 5. Kontrole pre pokretanja
- Funkcija troška, primenjena na objavljene optimalne vektore, reprodukuje sertifikovane troškove do zaokruživanja.
- Balansna jedinica i kazna se testiraju ručnim primerom.
- Budžet je tačan; DE se prekida tačno na budžetu; IPOP restartuje.
- Biblioteka je na `cc2f357` (`git diff` prazan).

## 6. Arhiviranje
`research/results/iteration48/valve_dispatch.json` i `ITERATION48_REPORT_SR.md`, i negativni. Bez ponavljanja.
