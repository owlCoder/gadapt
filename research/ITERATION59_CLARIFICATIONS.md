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
