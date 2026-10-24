# I59: pojašnjenja (vodi se pre i tokom izvršavanja)

- P1 (pre merenja): HiGHS u SciPy 1.18.1 je 1.12.0 (potvrđeno `scipy.optimize._highspy._core`).
- P2 (pre merenja): `scipy.optimize.milp` ne izlaže apsolutni gap ni broj niti; postavljeno `mip_rel_gap=0`,
  `time_limit=3600`, `presolve=True`. „Sertifikovano“ = status 0 (HiGHS je dokazao optimalnost unutar gap-a 0).
  Broj niti: podrazumevani HiGHS za MIP kroz SciPy (zabeležiti u manifestu).
- P3 (pre merenja): MILP se jedinično testira samo na sintetičkom grafu (ne na razvojnim instancama), da referenca
  ne bi nastala pre zvanične faze.
