**FIX FIRST — još ne zamrzavati.** Pregled je read-only; datoteke nisu menjane. I-A1 rešava većinu nejasnoća cilja, ali ostaju blokatori u PyGAD-u, provenijenciji i analizi.

1. **Cilj i budžet uglavnom su ispravni.** [InfraBudget](/Users/danijel/Desktop/gadapt/research/i64/i_study.py:39) pravilno mapira normalizovane indekse u fizičke granice; `BusORPD.evaluate` zatim snapuje. SP odgovara I56:
   `V = Σ max(0, violation_component − 1e−6)`, cilj `f + 1000V`; neuspešan PF daje **`2r + 10000`**. Ispraviti docstring „+10 penalty”. Izvodljivost zahteva konvergenciju i `V=0`; najbolji izvodljiv svedok prati se nezavisno od najboljeg skalara.

   `BudgetReached(BaseException)` prekida pre PF poziva B+1. Izvršno sam proverio GAdapt/preset, CMA/IPOP/BIPOP, SciPy DE i ES: svaki je završio sa tačno 67 evaluacija. PyGAD 3.5.0 na relevantnim putanjama hvata `Exception`, pa ovaj izuzetak prolazi; izvršna provera PyGAD-a ostaje potrebna u `ienv`. Restart petlje dele isti budžet; BIPOP koristi sopstveni raspoređivač. Nema pronađenog blokatora tu.

2. **PyGAD: rešetka i semena zahtevaju izmenu.** [Linije 87–90](/Users/danijel/Desktop/gadapt/research/i64/i_study.py:87): `step` jeste podržan, ali `high=1` daje samo 16 tačaka inicijalizacije/mutacije; crossover ipak može proizvesti 1. Takođe, samo `np.random.seed` ne seeduje Python `random`, koji PyGAD koristi. [Dokumentacija](https://pygad.readthedocs.io/en/stable/gene_values.html), [izvor 3.5.0](https://github.com/ahmedfgad/GeneticAlgorithmPython/blob/3.5.0/pygad/pygad.py).

   Konkretna zamena, uz postojeći konstruktor:

   ```python
   step = 1.0 / (R - 1)
   rs = int(rng.integers(1, 2**31))
   space = [dict(low=0.0, high=np.nextafter(1.0, np.inf),
                 step=step) for _ in range(d)]

   def cross(parents, size, inst):
       return np.clip(blend_crossover_pygad(parents, size, inst), 0.0, 1.0)
   ```

   Proslediti `gene_space=space, random_seed=rs, crossover_type=cross`. Ovo zadržava mentorovo čitanje `step` iz dict-a. GAdapt-ov `step=0.0625` pravilno postavlja `decimal_places=4` i daje svih 17 tačaka.

3. **Freeze/resume i provera svedoka su blokatori.** [Drajver](/Users/danijel/Desktop/gadapt/research/i64/i_study.py:130) nema pre-run manifest niti proveru njegovog identiteta pri nastavku. Završni hash nije zamrzavanje. Štaviše, neuspešan `run_part` se sačuva, a sledeće pokretanje ga slepo preskače. Pre prihvatanja svakog dela proveriti kompletan skup zadataka, jedinstvenost, `ok`, B i isti manifest.

   Manifest mora unapred vezati kod, specifikaciju, GAdapt stablo, mentorov komit, zavisnosti, roster, E-freeze, B/N/semena. Dostupni `.venv` ima NumPy 2.5.4/SciPy 1.18.1; E manifest navodi 1.26.4/1.17.1.

   Scenario-signature provera jeste pravilna. Nezavisni checker, međutim, nije pozvan. Koristiti I61 adapter zbog I63 scenarija:

   ```python
   q = i61.independent_check((net, j, b.best_x))
   if not (q.get("valid") and q.get("converged") and q.get("feasible")
           and math.isclose(q["losses"], b.best_f,
                            rel_tol=1e-8, abs_tol=1e-8)):
       raise RuntimeError("independent witness check failed")
   ```

   Pozivati samo kada svedok postoji, van optimizacionog budžeta. Sačuvati svedok i za 3.000 ako se taj rezultat nezavisno proverava.

4. **Estimandi:** P je prosek osam ćelijskih proporcija; CVaR je prosek osam ćelijskih proseka **tri najgora L od 30**, uključujući neuspehe kao `L=1`. Kod to sprovodi. To nije CVaR objedinjenih 240 ishoda. Upareni vektori resampluju se pravilno po ćeliji. Postoji 18 zapisanih kontrasta, ali 17 različitih: presetov P kontrast je dupliran.

   [Medijana G](/Users/danijel/Desktop/gadapt/research/i64/i_study.py:202) pogrešno izbacuje neizvodljive ishode. Koristiti `np.median(a[:, 2])`, uz eksplicitnu oznaku beskonačne medijane u JSON-u; uslovnu medijanu izvodljivih eventualno prikazati dodatno. Razjasniti da li A1 ukida ranije obećane q90/q95 i ECDF.

5. **Nulta varijansa: obavezna dopuna pre freeze-a.** Na n=30, pri P=0,99 cela ćelija je izvodljiva sa verovatnoćom 0,74. Degeneracija nije tehnička greška. Ne koristiti tačkaste intervale niti epsilon u imenitelju.

   Predlog čuva estimande, pragove i ukupno α=0,05: 0,025 za aktivne bootstrap kontraste, 0,025 za konzervativni fallback. Posle izračunavanja `se`, zameniti linije 185–188:

   ```python
   blocked = not finite
   lo, hi = np.full(18, -1.0), np.ones(18)
   hi[16] = 0.8
   t = float("nan")
   if finite:
       active = (se > 0) & (np.ptp(boots, axis=0) > 0)
       t = (float(np.quantile(
           np.max(np.abs(boots[:, active] - point[active])
                  / se[active], axis=1), 0.975))
            if active.any() else 0.0)
       lo[active] = point[active] - t * se[active]
       hi[active] = point[active] + t * se[active]
       u = 1 - (0.025 / 36)**(1 / (len(cw) * N))
       for h, c in list(enumerate(comps)) + [(17, "gadapt_preset")]:
           diff = np.concatenate([
               A[((ci, c), B)][:, 1]
               - A[((ci, "gadapt"), B)][:, 1] for ci in cw])
           if np.all(diff == 0):
               lo[h], hi[h] = -u, u
   ```

   Za 240 nezavisnih parova `u≈0,02985`; granica ostaje konzervativna i uz različite ćelijske verovatnoće. Ostali degenerisani kontrasti dobijaju pun dozvoljeni interval i mogu dati „neodlučeno”. Bootstrap pokrivenost ostaje aproksimativna, posebno za diskretni CVaR.

6. **Pravila odluke:** H64c može istovremeno zadovoljiti oba kriterijuma pri raspodeli 4/4. Minimalno, bez promene postojećih pragova:

   ```python
   support = notworse and better >= 4
   oppose = sum(con[f"CVaR({c})-CVaR(G)"]["upper"] < 0
                for c in comps) >= 4
   H64c = ("blocked" if blocked else
           "supported" if support and not oppose else
           "opposite" if oppose and not support else "undecided")
   ```

   H64d je koherentan, ali „suprotno” pokriva samo CVaR, ne dokazani pad izvodljivosti. Predznaci su ispravni: pozitivni P(c)−P(G) šteti G; pozitivni CVaR(c)−CVaR(G) koristi G.

7. **Uporedivost i CPU:** I57 je samo opisni kontekst: CMAwM ima marginalnu zaštitu, a ovde je kontinualni pycma sa snappingom; razlikuju se mreže, kontrole, budžeti i DE konfiguracije. I63 instrument/scenariji/normalizatori jesu zajednički, ali I-A1 daje mrežama težine 2/8, 3/8, 3/8.

   **25.920.000 PF × 3,3–4,5 ms = 23,76–32,40 CPU-sati**, plus OPF inicijalizacije, algoritamski overhead i provere. Na deset efektivnih jezgara idealno 2,4–3,2 h; „oko 3 h” je optimistična procena. Freeze tek posle navedenih ispravki i provere svih devet konfiguracija u stvarnom `ienv`.