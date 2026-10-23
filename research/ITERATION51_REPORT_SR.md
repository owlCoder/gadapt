# ITERATION51: D3x na I49 uzorku (IZVEŠTAJ)

**Datum:** 2026-10-23.
- Protokol: [ITERATION51_PROTOCOL.md](ITERATION51_PROTOCOL.md) (`6a22aad`).
- Kod: [iteration51_d3x.py](iteration51_d3x.py) (`a424169`).
- Sirovi izlaz: [results/iteration51/d3x.json](results/iteration51/d3x.json), sa `pip freeze`.
- Merenje je pokrenuto jednom i trajalo je 88 s.

## Ishod
- **Validacija D3x:** 3/3 (čista referenca, `hash_seeded`, `time_seeded`).
- **D3x:** **1 od 9** biblioteka, i to **Nevergrad** `NGOpt`, u 5 od 20 završenih ćelija (plato 10D). U istim ćelijama
  je i D3. Preostalih 10 ćelija pada zbog NumPy 2.5 greške (`only 0-dimensional arrays…`, [#1707](https://github.com/facebookresearch/nevergrad/issues/1707),
  ispravljeno samo na `main`).
- **Bez D3 i D3x:** pymoo, DEAP, PyGAD, geneticalgorithm, Optuna, PySwarms, cma, SciPy DE i GAdapt (kontrola), u
  30/30 ćelija.

## Tumačenje
- I49 zaključak se ne menja. Jedina nereproduktivna biblioteka iz I49 (Nevergrad) nereproduktivna je i između
  procesa, a nova nije pronađena.
- **Na celom uzorku od 21 biblioteke**, reproduktivnost uz zadato seme ne važi za 2 biblioteke: Nevergrad (D3 i D3x)
  i SMAC (samo D3x). SMAC slučaj otkriva samo provera između procesa.
