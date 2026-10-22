# GAdapt PhD — PROGRESS (jedini fajl za nastavak rada)

> Nova sesija / posle nestanka struje: pročitaj ovaj fajl, pa `CLAUDE.md`, pa nastavi od **SLEDEĆI KORAK**.
> Ažurira se i komituje (direktno na `main`) posle svakog značajnog koraka.

## Trenutno stanje (ažurirano 2026-10-22)

- Repo: `~/Desktop/gadapt` = `owlCoder/gadapt:main`. Upstream `bpzoran/gadapt` samo fetch (push onemogućen).
- Polazni handoff: `main` `8394236` (I41), 0 otvorenih PR-ova, I41 CI #39836240752 SUCCESS.
  Robustness run #39836609270: sva 4 job-a zelena, ali run je pri proveri još bio `in_progress` → ne tvrditi SUCCESS.
- Lokalno: `.venv` (Python 3.14, numpy 2.5.4, scipy 1.18.1, hypothesis 6.170.5). 12/12 postojećih I39/I41 testova prolazi.
- Podaci: originalna SNDlib temporalna TGZ (SHA `2c3ca706…`) i dalje NEDOSTUPNA. Ne rekonstruisati.
  Provera 2026-10-22: `sndlib.put.poznan.pl` ne odgovara (curl 000); `sndlib.zib.de` → 302 na poznanjski server;
  Wayback nema snimak TGZ-a (ni zib ni poznan URL). Zenodo: `SNDlib-MIPs` (10.5281/zenodo.8021237, samo MPS instance)
  i `topohub` v1.5.1 (10.5281/zenodo.19154525, samo konvertovane topologije, BEZ vremenskih matrica) → NISU oporavak izvora.

## Aktivni zadatak: nezavisna kritička provera originalnosti I41 (bez novih stvarnih eksperimenata)

| Korak | Status | Rezultat |
|---|---|---|
| 1. Verifikacija GitHub stanja | GOTOVO | vidi gore |
| 2. Trajna pravila (`CLAUDE.md`), agenti (`.claude/agents/`), ovaj fajl | GOTOVO | |
| 3. Matematička recenzija + Hypothesis falsifikacija I41 | GOTOVO | `research/test_iteration41_property_falsification.py`: 0 kontraprimera; sertifikat je dovoljan, NE potpun |
| 4. Prior-art audit (literatura, DOI provereni) | GOTOVO | I41 = specijalan slučaj (Gemander 2020 §3.3; Ben-Ameur/Pavón-Mariño/Pióro 2011 Def.1, Prop.1 jača) |
| 5. Arhitektonska procena: da li I41 doprinosi samom GAdapt GA | GOTOVO | Ne; samo MILP referenca |
| 6. Završni dokument `research/POST_I41_NOVELTY_AUDIT_SR.md` + GO/NO-GO + plan | GOTOVO | I41: NO-GO kao PhD metoda. H1 (partition crossover): GO samo za gate |

## SLEDEĆI KORAK

Pravac (moj savet, korisnik: „to radi“, „ne staj“): dijagnostika GAdapt-a na binarnom izboru ruta. Bez tvrdnje o novini.
- I43 GOTOVO: UNRESOLVED (3/6 deficit, 0/6 budžet). I44 GOTOVO: H-mut opovrgnuta (0/6); deficit vs (1+1)-EA repliciran 5/6.
- I45 [U TOKU, pozadina] → protokol `research/ITERATION45_PROTOCOL.md` (`7061d7f`), kod `f8dcb04`:
  udžbenički GA kao kontrola → SPECIFIČAN_ZA_GADAPT / GENERIČKI / MEŠOVITO.
  Posle: `research/ITERATION45_REPORT_SR.md`, lokalni komit, pa JEDAN push za ceo blok (I42–I45 + lib).
  Ako pukne zbog struje: ponovo pokrenuti isti kod (rezultat još nije viđen).
- Posle I45: strateška odluka korisnika (vidi izveštaj I45 §Odluka).

### Nalazi o biblioteci GAdapt (korisnik: „sređuj“ → ispravljeno kao opt-in u `64b9c82`, default bit-identičan)
1. `CommonOptionsValidator._check_cost_function` poziva cost funkciju na vektoru svih min i svih max (2 skrivene stvarne
   evaluacije po `execute()`). Ovo je verovatno izvor „trivijalnog rešenja“ u I39 (vidi I43 izveštaj §2).
2. `VariableColumnarDiversityDecisionVariableMutationRateDeterminator` prepisuje `number_of_mutation_decision_variables`
   vrednošću ≥ round(N/5) → dokumentovana gornja granica se tiho ignoriše u podrazumevanoj konfiguraciji.

## Dnevnik odluka

- 2026-10-22: Rad direktno na `main`, bez PR-ova; effort najviše `high`; najviše jedan agent istovremeno.
- 2026-10-22: I41 audit završen: teorema tačna, nije originalna, nije GA doprinos. Robustness run #39836609270 naknadno: SUCCESS.
- 2026-10-22: Korisnik odobrio H1 gate (sistematski prior-art audit, pa preregistracija Faze 0). Implementacija i dalje NIJE odobrena pre gate-a.
- 2026-10-22: H1 audit: nema ekvivalenta; „high-arity“ diferencijator opovrgnut (Chicano 2024). Faza 0 preregistrovana kao čisto strukturno merenje.
- 2026-10-22: I42 Faza 0 izvršena jednom (kod `57730b9`): H1 NO-GO (23/25 instanci sa medijanom k ≤ 2; ta2 neevaluirana zbog pop-limita, ne menja odluku). Korisnik traži autonomni rad kroz faze; zaustavljanje samo na pravim gate-ovima.
- 2026-10-22: Na korisnikov zahtev („šta je tvoj savet, to radi“) izabran pravac I43: dijagnostika budžet vs operatori, sintetička cena nad topohub topologijama.
- 2026-10-22: Push samo u serijama (CI minuti). I43 UNRESOLVED; otkrivena 2 nalaza o biblioteci. I44 preregistrovan na novim instancama.
- 2026-10-22: Korisnik: „sređuj, radi dalje, ne staj“ → opt-in `probe_cost_function`, `strict_mutation_decision_variable_limit` (bit-identičnost proverena hešom niza poziva). I44: H-mut NO. I45 pokrenut.
