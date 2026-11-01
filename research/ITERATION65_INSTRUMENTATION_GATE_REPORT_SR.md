# I65 — završni tehnički gate instrumentacije (istraživački sandbox)

**Datum:** 2026-11-01. **Status:** lokalni instrumentacioni gate uspešan u ograničenom obimu, integracioni/freeze gate NIJE završen. Novi konfirmatorni optimizacioni rezultati: **0**. Ne menja GAdapt biblioteku, `owlCoder/gadapt` ili upstream `bpzoran/gadapt`.

## Izvršeni testovi — SIROVI podaci i proverljiv trag

`python -m pytest -q -rx` iz direktorijuma `research/i65` (Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2): **54 passed, 3 xfailed**; log: `I65_GATE_TEST_LOG.txt`. To je zbir novih testova i ranijih I65 testova iz 2026-11-01, bez GAdapt/CMA/COCO evaluacija. U `I65_INSTRUMENTATION_FIXTURES.json` su deterministički mali tragovi za tačan budžet, izuzetke, mutable input i 20-generacijsku stagnaciju. Uloga svih fiktivnih ciljnih funkcija je isključivo proveravanje instrumenta.

### Potvrđene granice starog I64 referentnog koda

1. **Evaluator koji baci izuzetak:** `research/i64/e_common.py` rezerviše poziv **nakon** uspešnog povratka vrednosti. U sintetičkom testu dva stvarna pokušaja koja bace `ArithmeticError` ostavljaju `Budget.n == 0`. To je problem fiskalne ispravnosti u prisustvu izuzetaka; nije dokaz da su prethodne I64 optimizacije imale takve izuzetke.
2. **Mutacija prosleđenog vektora:** sa objective koji menja svoj ulaz, I64 `Budget` snima već izmenjen ulaz (`[999]` umesto `[2]`). Nije dokaz da postojeće test funkcije menjaju ulaz; instrument mora da garantuje originalnu tačku i onda kada evaluator nije čist.
3. **Monotoni `nfev` u ranijoj I65 referentnoj stagnaciji:** prvobitni `StagnationMonitor` ne odbacuje opadajući broj evaluacija. Ovo je propust I65 izolovane reference, **ne** greška u `gadapt/`.

Za sva tri postoje očekivano neuspešni regresioni testovi (`xfail(strict=True)`), tako da slučajno popravljanje/menjanje semantike pod starim nazivom zahteva recenziju.

## Šta je novo implementirano ISKLJUČIVO u sandboxu

- `audited_budget.py`: `AuditedBudget` vodi `attempts` **pre** fizičkog poziva, kopira vektor pre moguće mutacije, razdvaja `finite/nonfinite/exception`, vodi faze `init/search/probe/callback/restart/polish/recheck`, zadržava globalni najbolji rezultat sa stvarnim brojem poziva, `BudgetReached(BaseException)` sprečava skriveni B+1, a jednu jedinicu budžeta rezerviše za novi *nezavisni* završni objektiv. Poziv witness-a **ne menja** search incumbent ni `time-to-target`.
- `stagnation_checked.py`: tačno 20 završenih generacija bez značajnog poboljšanja, stroga nejednakost `delta > eps_abs + eps_rel * max(1,abs(previous))`, monotoni `nfev`, bez re-emisije dok se ne desi značajno poboljšanje ili restart; restart ne briše globalni incumbent.
- `test_scipy_de_adapter.py`: proveren stvarni SciPy DE poziv: `init` 12 jedinki, jedna dodatna evaluacija pre prekida na B−1 (B=14), zatim 1 nezavisni svedok; callback poziv eksplicitno naplaćen, a deterministički replay sa istim `rng` dao isti heš traga. SciPy `tol` NIJE korišćen kao stagnacioni kriterijum.
- `test_stagnation_checked.py`: 1000 determinističkih sintetičkih sekvenci upoređeno sa nezavisno napisanom jednostavnom referentnom rekurencijom, bez odstupanja. Ovo NIJE nezavisna ljudska recenzija niti dokaz integracije sa GAdapt.

## Matematička provera granice

Neka `n_0 = 0` i `B` bude konačan pozitivni ceo broj. U sekvencijalnom evaluatoru na svakom pozivu proverava se `n < limit` pre rezervacije; samo ako provera uspe poziv dobija redni broj `n+1`, pa se potom zove objektiv. Indukcijom po broju odobrenih pokušaja: `0 <= n <= limit <= B` i evaluator nije pozvan posle rezervacije `B`. Izuzetak ne vraća stanje brojača unazad. Ovo važi za **sekvencijalne pozive 1 objektiv → 1 fizička evaluacija**, ne automatski za vektorizovan/paralelan evaluator ili više PF solver poziva unutar jedne Python funkcije.

## Šta gate nije obuhvatio

- Nema `gadapt`, `cma` ili `cocoex` u lokalnom Python okruženju; nije moguće testirati instrumentaciju na stvarnoj GAdapt generaciji ili CMA `ask/tell` ili zvaničnim Gallagher/Lunacek instancama. Instalacija iz mreže nije bila dostupna. NIJE obavljen default bit-identity replay biblioteke.
- Nije izvršena nezavisna revizija koda; `stagnation_checked.py` je reference-only i ne obrađuje realne optimizatorske interne generacije. Nema naplate skrivenih unutrašnjih poziva solvera bez zasebnih adaptera.
- `verify()` može zahtevati drugi Python callable ali sama ne može dokazati nezavisnost implementacije simulacionog modela; to zahteva dve implementacije/oracle ili nezavisnu reviziju.
- Detektor ne reaguje na neuspešne/parcijalne generacije (ta semantika je namerna), ali je potreban izričit GAdapt adapter koji prijavljuje završenu generaciju, a ne generički callback koji može biti pozvan pre završetka.
- Na osnovu novih testova nije moguće naučno porediti algoritme, izračunati success rate, CVaR ili ECDF na COCO; ta polja moraju ostati `NOT_MEASURED`.

**Odluka:** **GO** za eksternu recenziju instrumentacije; **NO-FREEZE / NO-CONFIRMATORY-RUN** za I65, sve dok formalni `AGENTS.md` gate, nezavisna recenzija i realni integracioni testovi nisu ispunjeni.