# H4 — izvodljivost (pre prior-art odluke i pre preregistracije)

**23. oktobar 2026.** Samo tehnička provera da li se biblioteke mogu pokretati sa korisničkom funkcijom troška. Funkcija
troška je konstanta. **Obrasci poziva (prve tačke, broj evaluacija prema budžetu) namerno NISU gledani**, da se ne
bi videla merena veličina pre preregistracije.

- **Okruženje:** zaseban venv (Python 3.14), zaključane verzije u [h4_requirements_lock.txt](h4_requirements_lock.txt).
- **Skripta:** [h4_api_smoke.py](h4_api_smoke.py).

| Biblioteka | Verzija | Pokreće se sa korisničkom funkcijom |
|---|---|---|
| pymoo (GA) | 0.6.2 | da |
| DEAP (eaSimple) | 1.4.4 | da |
| PyGAD | 3.9.2 | da |
| geneticalgorithm | 1.0.2 | da (štampa izlaz i kada je progress bar isključen) |
| Nevergrad (NGOpt) | 1.0.12 | da |
| Optuna (CmaEsSampler, uz `cmaes` 0.13.1) | 5.0.0 | da |
| PySwarms (GlobalBestPSO) | 1.3.0 | da |
| cma (fmin2) | 4.5.0 | da |
| SciPy differential_evolution | 1.18.1 | da |
| mealpy | — | **ne:** build ne uspeva na Python 3.14 (stari numpy) |
