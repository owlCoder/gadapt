# I63 — beleške pre pokretanja (obelodanjivanje; ne menja zamrznuti protokol 7c1f698)

1. **Smoke test pre gate-a (Codex 079, tačka 6).** Prva verzija testa `test_iteration63_replication.py::SmokeRun` pokrenula je JEDNU GA optimizaciju
   (case30, scenario j=2, CHT FR, AD-N, seme `seed63("rehearsal","case30",2,1)`, budžet 60 poziva) da proveri polja zapisa. Dodirnuta su samo polja strukture
   (`ok`, `calls`, `best_feasible` postoji, dužina `generated`); vrednosti ishoda nisu gledane niti sačuvane. Test je potom zamenjen čistim testom omotača
   (bez optimizacije). Nikakva odluka dizajna ne zavisi od te probe; rezultat se ne koristi.
2. **Ispravke koda posle recenzije Codex 079** (pre gate-a, pre svakog I63 merenja): redosled ciljeva RNG toka (+0,05; 0; −0,05) po §6; roster sa
   heševima scenarija i OPF normalizatora i provera pri svakoj kasnijoj konstrukciji; gate bez automatskog fallback-a i sa proverom provenijencije pre/posle;
   vezivanje gate/roster/freeze identiteta u lancu; fiksan identitet eksperimenta (jedan direktorijum; `STOP.json` blokira sve kasnije pozive);
   arhiviranje neuspelih prvih pokušaja i ponavljanja; svedoci svih pokušaja u proveri; sirovi MW jazovi u opisnoj analizi; skeniranje arhiva semena
   ograničeno na I56, I58–I61 uz grešku pri nečitljivoj arhivi.
3. **Probno izvršavanje kompletnog cevovoda** (režim `I63_TESTING=1`, privremeni direktorijum van repozitorijuma, B=300, smanjene mreže/semena, relaksirani pragovi,
   uniformne težine umesto nedostižnog naginjanja) služi SAMO za proveru da sve faze rade; njegovi izlazi se brišu i ne koriste se. Zamrznute vrednosti
   (B=12.000, pragovi, mreže, semena, N_GRID, SIM) važe samo u režimu bez te promenljive okruženja.
4. Operativni nadzor troškova: ponavljanja tehničkih neuspeha se prate; plafon 230 M PF / 400 CPU-sati važi uključujući ponavljanja.
