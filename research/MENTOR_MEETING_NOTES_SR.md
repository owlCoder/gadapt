# Beleške za sastanak sa mentorom (izvor: Codex 093, 2026-10-29; ažurirati kad stignu I64-I, I2, I63-D, E4)

**Najjača odbranjiva formulacija doprinosa SADA:** disertacija daje novu, ograničenu empirijsku karakterizaciju GAdapt-a i pouzdanosti njegovog poređenja sa drugim optimizatorima — instrumentovanom replikacijom i preregistrovanim proširenjem mentorovog eksperimenta razdvaja efikasnost po stvarnom broju evaluacija, završnu tačnost i rizik loših ishoda i pokazuje da njihovo rangiranje zavisi od metrike i ispitane transformacije problema; kontrolisane ORPD studije utvrđuju lokalnu interakciju politike mutacije i rukovanja ograničenjima uz dokumentovane granice prenosa; uz to alat za proveru svojstava izvršavanja biblioteka, dijagnostički i negativni rezultati. Ne tvrdi se nova optimizaciona metoda, teorema niti prvenstvo evaluacionih postupaka.

**Ne sme se tvrditi:** opšta veća tačnost/stabilnost; „nadmašuje sve osim jednog“ kao potvrđen opšti zaključak; industrijska spremnost; rotacija/odsustvo učenja korelacija kao izolovan uzrok; κ kao validiran selektor; H56a kao replicirana; novinu diferencijalnog operatora, hibrida ili kompenzacione mutacije; doprinos GAdapt faze u hibridu.

**Pet teza za razgovor:**
1. Koji algoritam je taj jedan izuzetak i na kojim problemima ste to videli? (konfiguracije, budžeti, tabela)
2. Da li stabilnost znači ponovljivost istog semena, mali raspon između pokretanja ili mali rizik lošeg rešenja? Koji numerički pragovi?
3. S0 podržava usku tvrdnju o efikasnosti, E je ograničava: koji nalaz bi promenio Vašu ocenu primenljivosti?
4. Prihvatate li empirijski doktorat o granicama primenljivosti GAdapt-a (uključujući negativne rezultate) ili zahtevate originalnu metodu? Molim eksplicitnu odluku o obimu.
5. Koje dve publikacione jedinice podržavate i koji minimalni dodatni dokaz tražite?

**Publikacione jedinice (kandidati, nisu gotove):** (1) granice efikasnosti/tačnosti/rizika GAdapt-a pri stvarnom budžetu (S0/E/E2/E3 + I): Evolutionary Computation, odnosno Energies ako je fokus ORPD; nedostaju nezavisne instance, jači diskretni konkurenti, kontrola istog pomeraja za rotaciju, ablacija hibrida. (2) proverljivost izvršavanja optimizacionih biblioteka (alat + 21 biblioteka): TELO; traži jasnu centralnu tezu i potpuniju validaciju detektora.

**Preostale nedelje:** završiti 4 studije bez menjanja kriterijuma; nezavisno reprodukovati; dogovoriti obim sa mentorom; najviše jedna ciljana dopuna; uskladiti CH1–CH8; pisati radove i reprodukcioni paket; ako mentor traži novu metodu, priznati da sadašnji paket to ne ispunjava i dogovoriti rok.

## Ažuriranje 2026-10-29 (posle I64-I, I2, E4)
- **Stvarni ORPD:** GAdapt je u izvodljivosti dokazano bolji od PyGAD-a i DE-a i nerazlučiv od CMA porodice; u repu dokazano bolji samo od PyGAD-adaptive; kriterijum konkurentnosti H64c neodlučen. To podržava „primenljiv uz CMA porodicu“, a NE „bolji od svih osim jednog“.
- **Intervencije u samom GAdapt-u** (preset, diferencijalni krosover, kompenzaciona mutacija): nijedna nije dala potvrđenu korist; hibrid sa CMA-om pomaže na sintetici (E3), ali ne prenosi se na ORPD (I2).
- **Za mentora:** (1) Nova metoda nije nađena; 16+ kandidata odbačeno na prior art, a tri opt-in intervencije su testirane i nisu podržane. (2) Preporuka za industriju trenutno: GAdapt-M kao pouzdana opcija za diskretne ograničene probleme; za kontinualne spregnute probleme CMA porodica. (3) Odluka o obimu: empirijski doktorat sa negativnim rezultatima ili nova metoda (novi rok).
