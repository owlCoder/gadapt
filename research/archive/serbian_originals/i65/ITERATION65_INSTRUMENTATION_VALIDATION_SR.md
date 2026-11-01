# I65 — provera instrumentacije (lokalni reference-test; 2026-11-01)

**Obim:** bez izmena originalnog repozitorijuma. U izolovanom test paketu `i65/` nalazi se byte-identična kopija `research/i64/e_common.py` iz GitHub-a (Git blob SHA `3aab99773a7e4a95b7972a3c8061c50bd471618d`), referentna mašina stagnacije i unit testovi. Testirani su postojeći `Budget` i nezavisni *proposed monitor*, ali **ne** svi integracioni ulazi GAdapt/DE/CMA/COCO. Rezultati nisu konfirmatorni i nisu nezavisna recenzija.

**Izvršenje:** `python -m pytest -q test_i65_instrumentation.py`, iz `research/i65/`.

**Ishod:** `12 passed, 2 xfailed` (očekivano neuspešna regresiona testa). Nije bilo novih optimizacionih pokretanja i nije napravljen nijedan GitHub commit/push.

| Provera | Ishod | Šta je provereno / ograničenje |
|---|---|---|
| `Budget`: B/B+1 | PASS | B-ti poziv se izvrši, B+1 odbija; `BudgetReached` je `BaseException`. |
| Fizičke probe/duplikati/callback | PASS (direktni test) | Svaki uspešan prolazak kroz omotač se broji. Nije dokazano da svi stvarni bibliotečki callback-i koriste ovaj ulaz. |
| Nevalidni `nan/±inf`, ties | PASS | Broje se i ne postaju najniži konačni svedok; prvi vektor pri istoj ceni ostaje. |
| `deepcopy` | PASS | Omotač vraća isti objekat (važno za GAdapt kopiranje). |
| STAGNATION posle tačno 20 | PASS — referenca | Događaj samo nakon 20 **dovršenih** generacija; u toku nepotpune generacije ne nastaje. |
| Strogo `delta > eps_abs+eps_rel*max(1,abs(previous))` | PASS — referenca | Tie nije značajan; značajno poboljšanje resetuje brojač. |
| Restart, global incumbent, različite dužine generacija | PASS — referenca | Resetuje se brojač, čuva se globalni best; događaj beleži stvarni `nfev`. |
| Seed replay reference mašine | PASS — referenca | Fiksno seme daje identičan heš događaja; ne obuhvata stvarni `GA.execute()` ni SciPy. |
| Originalni brojač na izuzetku | **XFAIL — otkrivena rupa** | `Budget.__call__` radi `v=float(self.g(y))` pre `self.n+=1`; ako evaluacija baci izuzetak, fizički pokušaj nije upisan. Bez safe-fail politike i resurse je moguće ponovo koristiti. |
| Originalni svedok pri mutiranju ulaza | **XFAIL — otkrivena rupa** | `best_y` se kopira tek nakon `g(y)`; evaluator koji mutira listu menja zapis svedoka. Nije dokazano da je to uticalo na već korišćene COCO/I64 funkcije. |

## Predloženo otklanjanje — nije implementirano u repozitorijumu

1. Na samoj granici izvršavanja rezervisati `attempt_id` i uvećati `attempted_physical_evaluations` **pre** poziva. Zasebno brojati `returned_finite`, `returned_nonfinite`, `raised_exception`, `invalid_decoding` i `completed`. Svaki pokušaj u B ulazi u budžet, čak i kada izuzetak ili prekid nastane u spoljašnjem solveru. Obaviti idempotentnost/jedinstveni ID probe kod batch/async poziva.
2. Kopirati ulazni niz `x_pre` pre poziva, a za najboljeg svedoka sačuvati upravo `x_pre` i cenu; nezavisno ponovno proveriti cenu drugim evaluacionim putem. Validation/witness pozivi koji fizički izvršavaju funkciju **moraju** imati obezbeđenu budžetsku rezervaciju (ili biti jasno označeni kao odvojeni, dodatni verifikacioni budžet — ne smeju ulaziti u „B=12k“ uspeh).
3. Instrumentirati GAdapt završetak generacije u adaptorskom sloju (`exit_check` nije ekvivalent), SciPy DE `callback(intermediate_result=...)` bez dodatnog `func(x)` (ako ga pozove — naplatiti), CMA `ask/tell` nakon cele evaluirane serije. Pri B preseku nepotpunu generaciju ne brojati kao novu generaciju stagnacije. Nema `success=True` iz biblioteke kao zamene za kvalitet.
4. Pre FREEZE dopuniti integracione testove nad GAdapt/DE/CMA, proći through `B-1, B, B+1`, `max_calls=1`, nulta poboljšanja, negativne i nefinite vrednosti, mutable witness, callback, replay između **dva procesa**, restart inicijalizaciju, witness i *default bit-identity hash*. `cocoex`/`cma` nisu instalirani u dostupnom lokalnom sandboxu, stoga ovi gateovi nisu ispunjeni.

## Šta nije potvrđeno

Nema nezavisnog code review-a, nijednog integracionog testa stvarnog algoritskog prelaska, nijedne izvedene COCO f21/f24 instance, niti reprodukcije arhiviranih I64 rezultata u ovoj sesiji. U ovom stanju je **NO-FREEZE / NO-RUN** za veliku potvrdu. Dva XFAIL slučaja nisu dokaz da su raniji nalazi kompromitovani, ali su blokatori pre nove konfirmatorne serije.