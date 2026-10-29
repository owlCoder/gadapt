# Beleške za sastanak sa mentorom (izvor: Codex 093 i 097, 2026-10-29; I63-D završena 2026-10-29)

**Najjača odbranjiva formulacija doprinosa SADA:** disertacija daje novu, ograničenu empirijsku karakterizaciju GAdapt-a i pouzdanosti njegovog poređenja sa drugim optimizatorima — instrumentovanom replikacijom i preregistrovanim proširenjem mentorovog eksperimenta razdvaja efikasnost po stvarnom broju evaluacija, završnu tačnost i rizik loših ishoda i pokazuje da njihovo rangiranje zavisi od metrike i ispitane transformacije problema; kontrolisane ORPD studije utvrđuju lokalnu interakciju politike mutacije i rukovanja ograničenjima uz dokumentovane granice prenosa; uz to alat za proveru svojstava izvršavanja biblioteka, dijagnostički i negativni rezultati. Ne tvrdi se nova optimizaciona metoda, teorema niti prvenstvo evaluacionih postupaka.

**Ne sme se tvrditi:** opšta veća tačnost/stabilnost; „nadmašuje sve osim jednog“ kao potvrđen opšti zaključak; industrijska spremnost; rotacija/odsustvo učenja korelacija kao izolovan uzrok; κ kao validiran selektor; H56a kao replicirana; novinu diferencijalnog operatora, hibrida ili kompenzacione mutacije; doprinos GAdapt faze u hibridu.

**Pet teza za razgovor:**
1. Koji algoritam je taj jedan izuzetak i na kojim problemima ste to videli? (konfiguracije, budžeti, tabela)
2. Da li stabilnost znači ponovljivost istog semena, mali raspon između pokretanja ili mali rizik lošeg rešenja? Koji numerički pragovi?
3. S0 podržava usku tvrdnju o efikasnosti, E je ograničava: koji nalaz bi promenio Vašu ocenu primenljivosti?
4. Prihvatate li empirijski doktorat o granicama primenljivosti GAdapt-a (uključujući negativne rezultate) ili zahtevate originalnu metodu? Molim eksplicitnu odluku o obimu.
5. Koje dve publikacione jedinice podržavate i koji minimalni dodatni dokaz tražite?

**Publikacione jedinice (kandidati, nisu gotove):** (1) granice efikasnosti/tačnosti/rizika GAdapt-a pri stvarnom budžetu (S0/E/E2/E3 + I): Evolutionary Computation, odnosno Energies ako je fokus ORPD; nedostaju nezavisne instance, jači diskretni konkurenti, kontrola istog pomeraja za rotaciju, ablacija hibrida. (2) proverljivost izvršavanja optimizacionih biblioteka (alat + 21 biblioteka): TELO; traži jasnu centralnu tezu i potpuniju validaciju detektora.

**Preostale nedelje:** posle završenih I64-I, I2, E4 i I63-D i nezavisne numeričke provere: dogovoriti obim sa mentorom; najviše jedna ciljana dopuna; uskladiti CH1–CH8; pisati radove i reprodukcioni paket; ako mentor traži novu metodu, priznati da sadašnji paket to ne ispunjava i dogovoriti rok.

## Ažuriranje 2026-10-29 (posle I64-I, I2, E4)
- **Stvarni ORPD:** GAdapt je u izvodljivosti dokazano bolji od PyGAD-a i DE-a; za CMA, IPOP i BIPOP simultani intervali razlika izvodljivosti i CVaR-a obuhvataju nulu, pa smer razlike ostaje nerazrešen (ekvivalencija nije ustanovljena); u repu dokazano bolji samo od PyGAD-adaptive; kriterijum konkurentnosti H64c neodlučen. To podržava „primenljiv uz CMA porodicu“, a NE „bolji od svih osim jednog“.
- **Intervencije u samom GAdapt-u** (preset, diferencijalni krosover, kompenzaciona mutacija): nijedna nije dala potvrđenu korist; hibrid sa CMA-om pomaže na sintetici (E3); na ORPD-u prednost hibrida prema GAdapt-M nije potvrđena, a njegov rep je lošiji od IPOP-ovog (I2), pa I2 ne ustanovljava korist hibrida.
- **Za mentora:** (1) Nova metoda nije nađena; 16+ kandidata odbačeno na prior art, a tri opt-in intervencije su testirane i nisu podržane. (2) Opšta industrijska preporuka se ne može dati: na osam ispitanih ORPD ćelija GAdapt-M ima konkurentnu izvodljivost, dok smer razlike prema CMA porodici ostaje nerazrešen; nalazi na sintetičkim transformacijama ne određuju izbor algoritma za čitave klase problema. (3) Odluka o obimu: empirijski doktorat sa negativnim rezultatima ili nova metoda (novi rok).

- **I63-D (2026-10-29):** I63-D (deskriptivna ekstenzija zamrznutog I63 dizajna, n = 160 po ćeliji, 8 ćelija) daje θ₆₃ = 0,0139 (95% interval [−0,0090; 0,0372]); znak je isti kao u I56, ali je procena mala i neprecizna, estimand se razlikuje, a konfirmatorna replikacija nije ostvarena.
