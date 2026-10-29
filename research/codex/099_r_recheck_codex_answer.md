## BUG

- Spec je kontradiktoran: [SPEC:17](/Users/danijel/Desktop/gadapt/research/ITERATION64_R_SPEC.md:17) još navodi 3 zapisa i samo `best_f`, dok kod proverava 5 zapisa i kompletne `calls/best_f/best_y/events` ([r_study.py:138](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:138)). Ispraviti §8 prema kodu. Uz to, komentar na [r_study.py:137](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:137) pogrešno kaže ćelije 40/41; kod koristi 28/29 (`ackley,d=2`).

- Freeze commit se beleži ([r_study.py:98](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:98)), ali ga `same_build` ne poredi ([r_study.py:102](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:102)). Dodati `git_head` u obavezne ključeve i u manifest uključiti heševe korišćenih `research_experiments/functions/*.py`; trenutno njihove radne verzije nisu vezane.

- `check_repro` nije strogo create-once pri konkurentnim procesima: `exists` provera ([r_study.py:132](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:132)) i kasniji `os.replace` ([r_study.py:49](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:49)) imaju TOCTOU i drugi proces može prepisati prvi. Uvesti ekskluzivnu rezervaciju (`O_CREAT|O_EXCL`) ili atomarni no-clobber `save_once`.

- `run_part_k` ne čuva vezane `e_inputs` ([r_study.py:207](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:207)), pa ih resume ni ne poredi ([r_study.py:190](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:190)). Sačuvati `e_inputs=cr["e_inputs"]` u svakom delu i zahtevati jednakost pri nastavku.

- Spec i dalje navodi `r_report.py` ([SPEC:19](/Users/danijel/Desktop/gadapt/research/ITERATION64_R_SPEC.md:19)), ali fajl ne postoji. Napraviti ga pre zamrzavanja ili ukloniti tvrdnju da je deo realizacije.

## OK

Bootstrap indeks je pravilno zajednički po `(pair, variant)` za obe konfiguracije; validacija zapisa radi pri resume i analizi; E ulazi su vezani u `check_repro`; blocked put, nazivi presuda i uslov H64r3→H64r2 su ispravni; težine daju 5/9 za `d=2`; `N_SEEDS==100` i `B==12000` su tvrdo provereni.

Izolovani in-memory mock sa 4.200 lažnih zapisa prošao je celu analizu i bootstrap bez pada, sa konačnim presudama i konačnim izlazom.

Nije još spremno za zamrzavanje.