# ITERATION42 — Faza 0 za H1: strukturni VIG pretest partition crossover-a (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre pisanja koda i pre bilo kakvog računa na podacima.** Datum: 2026-10-22.
Prethodni koraci: [POST_I41_NOVELTY_AUDIT_SR.md](POST_I41_NOVELTY_AUDIT_SR.md) §5–6 i
[H1_PRIOR_ART_AUDIT_SR.md](H1_PRIOR_ART_AUDIT_SR.md) (sistematski prior-art audit, završen pre ovog protokola).

## 1. Istraživačko pitanje
Da li model troška sa dve fiksne kandidatske putanje po zahtevu (I38/I39) na stvarnim SNDlib topologijama ima graf
interakcije promenljivih (VIG) dovoljno redak da partition crossover (PX) razbije tipične parove roditelja na
**više od dve** nezavisne komponente? Ako ne, PX se svodi na izbor celog roditelja i H1 nema mehanizam → NO-GO.

Ovo je **nužan, ne dovoljan** uslov za H1. Prolaz Faze 0 ne pokazuje da PX pomaže GAdapt-u. On samo vraća odluku
korisniku: da li je empirijska tvrdnja iz audita (§1.5) vredna Faze 1. Faza 1 i dalje zahteva arhivirane stvarne
vremenske podatke i APX/DPX kao kontrole.

**Status novosti (iz audita):** H1 kao metoda nema utvrđenu novost, jer je specijalan slučaj Chicano i sar. 2024,
Teorema 1 i §3.2. Faza 0 meri samo empirijsku pretpostavku i **ne** odobrava implementaciju PX-a u GAdapt-u.

## 2. Podaci (zamrznuti)
- 26 SNDlib topologija iz topohub v1.5.1 (Zenodo 10.5281/zenodo.19154525, MIT), arhivirane bajt-po-bajt u
  [data/topohub_v1.5.1_sndlib/](data/topohub_v1.5.1_sndlib/) sa `SHA256SUMS` i `SOURCE.md`.
- Ograda: to su topohub konverzije (prosti neusmereni grafovi, jedna statička matrica), ne izvorni SNDlib fajlovi
  i ne izgubljena temporalna TGZ. Paralelni linkovi izvornog SNDlib-a su spojeni. Rezultat je strukturan, ne
  „stvarni dokaz o infrastrukturi“ u smislu Faze 1.
- Nijedna instanca se ne izbacuje posle gledanja rezultata. Pravila isključenja su samo ona iz §3.

## 3. Konstrukcija (identična I38 gde je moguće)
1. Graf: `networkx.node_link_graph(json, edges="edges")`, čvorovi su topohub celobrojni ID-jevi, neusmeren, bez težina.
2. Zahtevi (geni): svaki usmereni par `(u, v)` iz `graph.demands` sa vrednošću > 0, u redosledu JSON ključeva.
   Vrednost zahteva se dalje NE koristi (VIG je strukturan; svaki zahtev sa q > 0 je pretpostavljeno aktivan).
3. Putanje: tačno I38 `two_paths` (najmanji broj skokova, leksikografski tie-break po sortiranim susedima, loopless),
   primenjen na celobrojne ID-jeve. Razlika od I38: I38 je sortirao po imenima čvorova → putanje mogu da se razlikuju
   kod izjednačenja; prihvaćeno i navedeno.
4. Zahtev bez dve različite loopless putanje (npr. preko mosta) nije gen (fiksna promenljiva); broj se izveštava.
   Zaštita od eksplozije: najviše 2.000.000 skidanja sa heap-a po zahtevu; prekoračenje → instanca „nije evaluirana“ (izveštava se).
5. `D_e = {d : putanje 0 i 1 zahteva d se razlikuju na linku e}` (simetrična razlika skupova linkova).
   VIG: geni `d ≠ d'` su susedi akko postoji `e` sa `d, d' ∈ D_e`. (To je tačan VIG funkcije
   `f(z) = Σ_e g_e(z_{D_e})` kad je svaka `g_e` netrivijalna po svim argumentima — konzervativno, tj. VIG može samo
   biti gušći nego stvarni.)
6. Instanca je **evaluabilna** ako ima N ≥ 20 gena posle tačke 4.

## 4. Mera
Za skup gena `S` po kojima se roditelji razlikuju, `k(S)` = broj povezanih komponenti podgrafa VIG-a indukovanog na `S`
(standardni PX graf rekombinacije: zajednički geni se uklanjaju). `k` zavisi samo od `S`, ne od vrednosti roditelja.

- Udeli razlike `p ∈ {0.05, 0.10, 0.20}`; `|S| = max(2, round(p·N))`, `S` uniformno bez ponavljanja.
- 1000 uzoraka po (instanca, p). Generator: `numpy.random.default_rng(SeedSequence([42, i, j]))`,
  `i` = indeks instance u abecednom redu, `j` = indeks `p`.
- Sekundarno (samo izveštaj, ne odlučuje): medijana i 10./90. percentil `k`, udeo uzoraka sa `k ≥ 3`,
  prosečan udeo najveće komponente u `|S|`, gustina VIG-a, `max_e |D_e|`, broj fiksnih zahteva.

## 5. Kriterijum odluke (jedini primarni test)
- Po instanci: `med_k` = medijana `k` pri `p = 0.10`.
- **H1 NO-GO** ako je `med_k ≤ 2` na **najmanje 2/3** evaluabilnih instanci. Tada se H1 zatvara, bez Faze 1 i bez
  ponavljanja sa drugim `p`, putanjama ili podacima.
- **Prolaz** inače. Prolaz dozvoljava samo pisanje protokola Faze 1 (i dalje uz data-gate iz audita §6).
- Ako je evaluabilno manje od 10 instanci → rezultat je **neodlučan** i H1 se ne nastavlja bez nove odluke korisnika.

## 6. Kontrolne provere (sintetičke, pre stvarnog računa)
Jedinični testovi na ručno konstruisanim grafovima (ne na topohub podacima):
- zahtevi sa disjunktnim `D_e` → `k = |S|`; svi zahtevi u jednom `D_e` → `k = 1`;
- `two_paths` reprodukuje I38 funkciju na I38 test grafu (uvoz iz `iteration38_joint_capacity_model`);
- komponente se porede sa `networkx.number_connected_components` na nasumičnim malim instancama (Hypothesis).

## 7. Budžet
Samo grafovski račun: nula poziva GA-a, cost funkcije, LP/MILP solvera. Tvrdo ograničenje 30 min ukupnog vremena;
prekoračenje → instanca „nije evaluirana“. Nijedan CI workflow se ne pokreće.

## 8. Arhiviranje
`research/results/iteration42/phase0.json`: verzije paketa, SHA-256 izvornog koda i ulaza, po instanci sve mere iz §4
(uključujući neevaluirane), konačna odluka. Negativan rezultat se arhivira i komituje isto kao pozitivan.

## 9. Šta se NE radi
Bez promene GAdapt-a, bez PX implementacije u biblioteci, bez stvarnih vremenskih matrica, bez naknadne promene
`p`, praga ili konstrukcije putanja posle gledanja rezultata.
