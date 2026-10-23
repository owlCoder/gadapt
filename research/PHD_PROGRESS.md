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

Odgovori korisnika 2026-10-22: cilj = PhD doprinos (prioritet) + praktično bolji GAdapt; domen ako je deficit generički =
kontinualni infra problemi; računar = neograničeno, i preko noći; opt-in ubrzanja GAdapt-a dozvoljena (bit-identično).
- I43–I46 GOTOVO (binarni izbor ruta): deficit GAdapt-a robustan i specifičan; nije ga izazvala nijedna pojedinačna
  opcija (I46); eksplorativno: GAdapt ne intenzivira oko najboljeg rešenja.
- I5 (ranije): i na kontinualnom IEEE14 GAdapt gubi 12/12 od CMA-ES/SLSQP/DE.
- Novi nalaz (eksplorativno, `research/iteration47_exploratory_*`): kolonska raznovrsnost na log((v−min)+1) NIJE
  invarijantna na jedinice/položaj → optimum blizu gornje granice promenljive velikog opsega ~10^3 lošije.
  Opt-in ispravka `columnar_diversity_metric="linear"` (`cc2f357`, default bit-identičan).
- I47 GOTOVO → `research/ITERATION47_REPORT_SR.md`: A1 NIJE PODRŽANO (1/4), `linear` tačno invarijantna, B1 OPOVRGNUTO
  (0/5). CMA-ES 3–5 redova veličine bolji od GAdapt-a na stvarnom AC dispečingu pri istom budžetu.
- Korisnik izabrao „C pa A“ (2026-10-23).
- I48 GOTOVO → `research/ITERATION48_REPORT_SR.md`: DEFICIT_GADAPT (IPOP bolji 2/3), ali razlika samo 1,3–1,5×
  (naspram 10³–10⁵ na glatkom dispečingu). GAdapt bolji od DE 2/3.
- A: nacrt `research/DIAGNOSTIC_STUDY_DRAFT_SR.md` popunjen (I42–I48); objavljen i kao Claude Docs dokument
  „Dijagnostika GAdapt-a na infrastrukturnim problemima“ (https://claude.ai/artifact/1H1BBk1RUdJ7T6Gzc22CdM, privatan
  dok ga korisnik ne podeli).
- H3 prior-art gate GOTOVO → `research/H3_PRIOR_ART_AUDIT_SR.md`: NO-GO kao PhD metoda (EMDE 2008, MA-LS-Chains 2010,
  HSES 2018 već sadrže suštinu). Moguće samo kao opt-in praktična funkcija (opcija B).
- Korisnik (2026-10-23): opcija 1 — studija I42–I48 = poglavlje teze; mentor cilja promenu prakse u industriji.
- H4 prior-art GOTOVO → `research/H4_PRIOR_ART_AUDIT_SR.md`: GO kao uski metodološki doprinos (klasifikacija poziva,
  doslednost rezultata, dokumentacija vs ponašanje, studija rasprostranjenosti); invarijantnost i brojanje = prior art.
- I49 GOTOVO → `research/ITERATION49_REPORT_SR.md`: ČESTO (4/9; samo protivrečnost dokumentaciji 2/9); svi pojedinačni
  nalazi već poznati/dokumentovani; alat validiran; GAdapt artefakt potvrđen. Nevergrad pad sa NumPy 2.5 (#1707).
- I49 dodat u Docs dokument studije i u `research/DIAGNOSTIC_STUDY_DRAFT_SR.md` (§7).
- Nevergrad naknadno (I49 izveštaj §6): D3 = #1572 (ne #966); uzrok nađen, ispravka 16/16; objavljen jedan komentar
  na #1572 (korisnik prepustio odluku). #966/#1707 bez komentara. Nema PR-a (CLA = odluka korisnika).
- I50 GOTOVO → `research/ITERATION50_REPORT_SR.md`: preregistrovano 11/12 PONOVLJENO, ali C1 nije specifičan
  (legitimne tačke u uglu); bez C1 (post hoc) 4/12, zajedno sa I49 8/21 (CI 18–62%). Protivreči dokumentaciji 2/12:
  GFO (negiran best_score) i SMAC (seme zavisi od PYTHONHASHSEED) — oba NOVA, prijavljena: GFO #106, SMAC #1380.
  scikit-opt DE R3 (mehanizam nađen) nije prijavljen (pravilo: praznina u dokumentaciji).
- Pratiti odgovore: Nevergrad #1572, SMAC #1380, GFO #106.
- SLEDEĆE: uneti I50 u poglavlje; redefinisati C1 za sledeću verziju alata (samo pozivi izvan pretrage).

- Okruženje: u `.venv` dodati `pypower` 5.1.19 i `cma` 4.5.0 (pip, 2026-10-23).

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
- 2026-10-22: I45: deficit SPECIFIČAN ZA GADAPT. Korisnik odgovorio na 4 pitanja (vidi gore). Push serije I42–I45 + lib sa [skip ci].
- 2026-10-23: I46 bez uzročne komponente. Otkrivena neinvarijantnost kolonske raznovrsnosti; opt-in `linear`. I47 pokrenut.
- 2026-10-23: I47: ispravka invarijantnosti ne poboljšava dispečing; dominantna slabost GAdapt-a je konvergencija (vs CMA-ES). Strateški gate.
- 2026-10-23: Korisnik: C pa A. I48 pokrenut; nacrt dijagnostičke studije započet.
- 2026-10-23: I48: DEFICIT_GADAPT (mala razlika na multimodalnom). Studija A popunjena. C pa A završeno.
- 2026-10-23: Studija objavljena kao Docs dokument. Pokrenut H3 prior-art audit.
- 2026-10-23: H3 NO-GO (prior art). Autonomni deo stao na pravom gate-u (CLAUDE.md: STOP bez novine).
- 2026-10-23: Korisnik izabrao opciju 1 (studija kao poglavlje; industrijska praksa). Pokrenut H4 prior-art audit.
- 2026-10-23: H4 GO (uski). I49 preregistrovan, alat validiran podmetnutim greškama, pokrenut.
- 2026-10-23: I49: problemi integriteta česti (4/9), svi već poznati; doprinos = validirani alat + rasprostranjenost.
- 2026-10-23: Korisnik: „uradi kako je najbolje autonomno“. Nevergrad: uzrok + ispravka, komentar na #1572; citat #966 ispravljen.
- 2026-10-23: Korisnik: „radi dalje“. I50 preregistrovan (replikacija na novom uzorku, D3x između procesa); pokrenut.
- 2026-10-23: I50 završen: 2 nova nalaza protiv dokumentacije prijavljena (SMAC #1380, GFO #106); C1 nespecifičan.
