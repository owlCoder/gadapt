# Dizajn: opt-in rukovanje ograničenjima u biblioteci GAdapt (NACRT, pre rezultata I56)

**Status:** nacrt 2026-10-24, dok I56 radi. Implementacija u `gadapt/` tek POSLE I56 (protokol §10), i to samo
delova koje studija opravda. Podrazumevano ponašanje mora ostati bit-identično (provera: heš niza poziva).

## Problem
GAdapt danas prima samo skalarni trošak. Korisnik sa ograničenjima mora sam da napravi kaznu (f + w·V), što je
tačno grana SP u I56. Deb-ova pravila, ε-ograničenje i adaptivna kazna nisu izrazivi skalarom koji se ne menja kroz
vreme (ε i λ menjaju redosled već ocenjenih jedinki), pa se ne mogu napraviti samo omotačem funkcije troška.

## Predlog API-ja (konvencija iz CLAUDE.md: konstruktor, property + setter, `GAOptions`, docstring, README)
```python
ga = GA(cost_function=f_and_v,            # vraća (objective, violation), violation >= 0, 0 = izvodljivo
        constraint_handling="feasibility_rules")
```
- `constraint_handling: Optional[str] = None` — `None` (podrazumevano, današnje ponašanje), `"penalty"`,
  `"adaptive_penalty"`, `"feasibility_rules"`, `"epsilon"`.
- Parametri: samo `constraint_penalty_weight=1000.0` (≤ 1e100). Konstante adaptivne kazne (×2, ÷1,5, 3 generacije,
  opseg ×10⁶) i ε (20. percentil, polovina generacija, eksponent 5) su FIKSNE (iste kao I56; YAGNI) — odluka posle
  Codex 029.
- Funkcija troška sa uključenom opcijom vraća par; validacija u `GA.execute()` (probni pozivi, ako nisu isključeni)
  proverava oblik para.

## Implementacija (prema I56 kodu, koji je već validiran)
- `gadapt/utils/constraint_handling.py`: klase skalarizacije (iste formule kao I56 §4), stanje λ/ε, brojači.
- `gadapt/operations/cost_finding/constraint_handling_cost_finder.py`: podklasa `ElitismCostFinder`-a, isti
  redosled događaja kao I56 (evaluacija → ažuriranje parametara → ponovna skalarizacija SVIH → odsecanje).
  Keš sirovog (objective, violation) po jedinki (atribut kandidata, ne globalni rečnik).
- `GAFactory._get_cost_finder`: bira ovu klasu samo kad je `constraint_handling` postavljen.
- `GAResults`: dodati `best_objective`, `best_violation`, `feasible` (najbolja izvodljiva jedinka ako postoji,
  inače najmanje neizvodljiva); `min_cost` ostaje skalar (zbog kompatibilnosti).

## Otvoreno do rezultata I56
1. **Vrednost koju čitaju signali adaptacije** (raznovrsnost troškova, raznovrsnost roditelja). U I56 FR skalar
   koristi u(f) = f/(f + f_ref) sa f_ref iz OPF-a; biblioteka nema f_ref. Kandidati: (a) f_ref = medijana |f|
   izvodljivih (ili svih) u početnoj populaciji; (b) signal samo iz objective-a izvodljivih + udeo izvodljivih.
   Odluka zavisi od H56b (da li vrednost u signalu uopšte menja ishod) i od H56a.
2. Da li ponuditi „zajednički signal“ kao opciju (`adaptation_signal="feasibility"`) — samo ako I56 pokaže korist.
3. Podrazumevana tehnika u dokumentaciji (preporuka korisnicima) — iz I56 per_arm rezultata, uz jasnu napomenu da
   važi za diskretni ORPD.

## Provere pre spajanja
Bit-identičnost bez opcije (heš niza poziva na README primerima i na I56 merilu); testovi skalarizacije (isti kao
`test_iteration56_cht_study.py`); README primer koji radi; unos u „Parameters Description“.
