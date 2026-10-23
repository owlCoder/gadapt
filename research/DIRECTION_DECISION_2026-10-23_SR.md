# Odluka o pravcu metode za GAdapt — 23. oktobar 2026 (veče)

Rad: Claude (vodi, piše, komituje) + Codex (gpt-6.1-sol, high, samo čitanje; zadaci i odgovori u [codex/](codex/)).

## Pitanje

Da li iz poznatog zaostatka GAdapt-a na kontinualnim infrastrukturnim problemima (I47: CMA-ES 3–5 redova veličine bolji
u penalizovanom skoru na 4 slučaja AC dispečinga) može da se izvede **originalan metodološki doprinos samom GAdapt-u**?

## Dokazi prikupljeni danas

| Korak | Šta | Ishod |
|---|---|---|
| Codex 001 | nezavisna analiza mehanizma | ispravio 3 premise (rang-roulette, log-raspon, korak iz kolonske raznovrsnosti); otkrio mešavinu Gaus/reset 50/50 po koordinati |
| I53 (preregistrovan, Codex recenzija 002 uneta) | oracle korak × reset, dispečing + sintetički | **H53 OPOVRGNUTO** (usko): oracle korak zatvara ≤ 29% jaza na dispečingu; sfera 61%, elipsoidi 23% / 9% |
| Codex 004 | ponovna analiza sirovih podataka I53 | brojevi tačni; tumačenje suženo (korelacije = kandidat, ne utvrđen uzrok) |
| Codex 003 + provera DOI | prior art: kontrola koraka iz rasipanja + množilac po uspehu | **PRIOR ART** (AMBOA 2004, AVS 2006, SDR 2007, RV-GOMEA 2017) |
| Codex 005 + provera DOI | prior art: varijacija koja uči korelacije / invarijantna na rotaciju | **PRIOR ART** (PCX 2002, AREX 2009, eigen-DE 2015, CoBiDE 2014, RV-GOMEA 2017/2021, AMaLGaM 2013) |
| I54 nacrt (oracle geometrija) | uzročni test hipoteze o korelacijama | **povučen pre merenja**: Codex 007 našao 2 blokirajuće greške dizajna |
| Codex 006 + provera DOI | prior art: Codex-ov kandidat „sertifikovano ukrštanje po dopustivim intervalima AC toka“ | **NO-GO**: rigorozno praćenje grane (van den Berg i sar. 2010) + SIVIA (Jaulin i Walter 1993) daju konstrukciju; procena 5% |

## Zaključak

1. **Popravka zaostatka GAdapt-a ne daje originalnu metodu.** Oba kandidat-uzroka (kontrola koraka; varijacija po
   koordinatama bez učenja korelacija) imaju poznate, objavljene lekove. Ugradnja nekog od njih u GAdapt bila bi
   praktično poboljšanje biblioteke (opt-in), ali ne doprinos za doktorat. **NO-GO** po pravilu iz `CLAUDE.md`.
2. **Dijagnostičko poglavlje je ojačano.** I53 je prvi preregistrovani uzročni test u nizu I42–I53: pokazuje da
   kontrola koraka ne objašnjava zaostatak na stvarnom dispečingu (≤ 29%), uz verodostojan, ali neutvrđen preostali
   uzrok. Uz to, opisno: na case118 oracle korak daje izvodljivost 12/12 naspram 2/12.
3. **Šta ostaje otvoreno (nijedno nije GO bez zasebne provere prior art-a):**
   - kontroler koraka centriran na potomcima sa novim dokazom konvergencije (Codex procena ~25%);
   - „spektralna restauracija“ vođena GAdapt-ovim signalima raznovrsnosti troškova i roditelja (~15%);
   - sertifikovano ukrštanje za AC tok snage samo uz novi matematički doprinos (dokazano amortizovano smanjenje
     složenosti sertifikacije ili rigorozno rukovanje PV/PQ promenama); trenutno nije specificirano (Codex 006: 5%).
4. **Najodbranjiviji okvir teze** (nezavisno su ga predložili i Claude i Codex): pouzdana evaluacija i mehanistička
   dijagnoza adaptivnog optimizacionog softvera za infrastrukturu — revizija integriteta (I49–I52, rad), dijagnostička
   studija (I42–I48) i uzročni test (I53).

## Odluka koja pripada korisniku/mentoru

- (a) Prihvatiti okvir iz tačke 4 i završiti rad o reviziji integriteta + poglavlje sa I53; ili
- (b) uložiti jednu sistematsku proveru prior art-a u najjači preostali kandidat iz tačke 3 (rizik: verovatno NO-GO); ili
- (c) praktični opt-in u GAdapt (poznati lek, citiran kao takav) — korisno za biblioteku, ne za tezu.

## Dopuna (20:45): sistematska provera preostalih kandidata (Codex 008 + moja provera)

- **C1 (kontroler koraka centriran na potomcima + teorema o konvergenciji): NO-GO.** da Silva, Borges, Nepomuceno,
  Soler 2025 ([10.1016/j.asoc.2025.113635](https://doi.org/10.1016/j.asoc.2025.113635)) već daju „pozitivno
  adaptivnu“ mutaciju u elitističkom EA (GA, ES, DE), dokaz linearne prosečne brzine konvergencije sa eksplicitnom
  donjom granicom i primenu na ekonomski dispečing sa valve-point efektom. Uz Jägersküpper i Witt 2005, Touré, Auger,
  Hansen 2022 ([10.1007/s10898-022-01249-6](https://doi.org/10.1007/s10898-022-01249-6)) i Akimoto i sar. 2022
  ([10.1137/20M1373815](https://doi.org/10.1137/20M1373815)), preostala razlika je inkrementalna.
- **C2 (spektralna restauracija): NO-GO.** Operator je relaksirana projekcija na pod sopstvenih vrednosti (poznata
  matrična analiza); jedina razlika je kapija po potomku, bez utvrđene koristi.
- **Stanje:** nijedan kandidat za originalnu GAdapt metodu iz linije „popravka zaostatka“ ne prolazi proveru.
  Novi kandidat mora doći iz drugačijeg pitanja, ne iz popravke poznatih slabosti.
