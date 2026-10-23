# Eksplorativno (NIJE preregistrovano): SciPy globalni optimizatori kroz alat za praksu

**Datum:** 2026-10-23. Alat: `research/integrity_audit_tool.py`, budžet 1000, N ∈ {2, 10}, 3 semena, okruženje iz
`h4_requirements_lock.txt` (SciPy 1.18.1). Izlazi su `<optimizator>.json` u ovom direktorijumu.

| Optimizator | Nalaz | Dokumentacija | Razvrstavanje |
|---|---|---|---|
| `dual_annealing` | C4 u 1/18 (najviše 1050 poziva) | `maxfun`: „Soft limit … will be exceeded … just after the local search is done“ | dokumentovano |
| `shgo` | C4 u 18/18 (najviše **5131** poziva za `maxfev` 1000) | `maxfev` je tačan samo za neke lokalne metode; inače se proverava po globalnoj iteraciji | dokumentovano, ali do 5× |
| `direct` | C4 u 6/18 (najviše 1013) | `maxfun`: „Approximate upper bound“ | dokumentovano |
| `basinhopping` | R3 u 3/18, samo na platou | „`lowest_optimization_result` will only be updated if a local minimization was successful.“ | dokumentovano |

`basinhopping` ima istu politiku kao `differential_evolution` (neuspeh lokalne minimizacije poništava bolji rezultat),
ali je dokumentuje. Ta napomena je dodata kao komentar na [scipy #26479](https://github.com/scipy/scipy/issues/26479).
Nova prijava nije potrebna. `basinhopping` nema parametar budžeta, pa C4 tu nije primenljiv.
