# I59: pojašnjenja (vodi se pre i tokom izvršavanja)

- P1 (pre merenja): HiGHS u SciPy 1.18.1 je 1.12.0 (potvrđeno `scipy.optimize._highspy._core`).
- P2 (pre merenja; ISPRAVLJENO po Codex 040): SciPy 1.18.1 prosleđuje HiGHS-u `threads=1` i `mip_abs_gap=0.0`
  doslovno (uz upozorenje „Unrecognized options … passed verbatim“, ne odbijanje). LP: `threads=1`; MILP:
  `mip_rel_gap=0`, `mip_abs_gap=0`, `threads=1`, `time_limit=3600`, `presolve=True`. Očekivana upozorenja se beleže
  (MILP) ili prigušuju samo za `threads` (LP). „Sertifikovano“ = status 0 I provera svedoka (celobrojnost, granice,
  ravnoteže u SVIM čvorovima, kapaciteti, rekonstruisan trošak = `res.fun`) I nema neočekivanih upozorenja.
- P3 (pre merenja): MILP se jedinično testira samo na sintetičkom grafu (ne na razvojnim instancama), da referenca
  ne bi nastala pre zvanične faze.
- P4 (pre merenja, Codex 040): provere reziduala koriste pune ravnoteže u svim čvorovima (LP izbacuje jedan red po
  zahtevu); krajevi ivica u cele brojeve; `ceil` bez pomaka; ulaz evaluatora mora biti konačan ceo vektor u [0, 16].
- P5 (pre merenja, Codex 041): istraživačko okruženje je `.venv` (Python 3.14.3, SciPy 1.18.1, NumPy 2.5.4, HiGHS
  1.12.0), zabeleženo u manifestu svake faze; pinovi biblioteke u `setup.py`/`requirements.txt` (Python 3.12, NumPy
  1.26.4) se ne menjaju — biblioteka podržava 3.10+, a studija beleži stvarno okruženje.
- P6 (pre merenja, Codex 041): redosled faza: `development` → `confirmation` → `check` → `analyse`; H59 se računa
  samo ako je razvoj GO, reference sertifikovane I nezavisno proverene, inventar tačan (3 mreže × 15 semena × 2
  grane, jedinstveni, isti budžet), nema trajnih neuspeha i `check` nema grešaka. Cilj bez dodatne tolerancije
  (C ≤ (1 + ε)C*). Trivijalni ciljevi se označavaju i za razvojne mreže posle izbora ε (bez zamene).
