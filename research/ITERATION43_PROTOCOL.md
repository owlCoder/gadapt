# ITERATION43 — dijagnostika: budžet ili operatori? GAdapt na binarnom izboru ruta (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre ikakvog pokretanja.** Datum: 2026-10-22. Pravac je izabran posle zatvaranja H1
([ITERATION42_REPORT_SR.md](ITERATION42_REPORT_SR.md)).

**Ovo je dijagnostička studija, ne predlog metode. Tvrdnja o novini se NE postavlja.** Cilj je da se odluči da li
dalji rad na GAdapt-u za diskretne infrastrukturne probleme ima osnovu, i gde (budžet ili operatori).

## 1. Istraživačko pitanje
U I39 GAdapt (272 binarna gena, 360 evaluacija) u 11/12 semena nije popravio rešenje „sve prve najkraće putanje“.
Da li je to (a) **artefakt budžeta**, pa GAdapt sa više evaluacija radi kao jaka jednostavna kontrola, ili (b)
**deficit operatora**, pa GAdapt ostaje lošiji od standardnog (1+1)-EA i pri većem budžetu?

## 2. Instance (zamrznute; sintetička cena nad stvarnom topologijom)
- Topologije i statičke matrice zahteva: topohub v1.5.1 (arhivirano, [data/topohub_v1.5.1_sndlib/](data/topohub_v1.5.1_sndlib/)).
  Šest instanci rastuće veličine: `polska`, `nobel-germany`, `atlanta`, `france`, `geant`, `germany50`.
- Geni i putanje: tačno kao I42 §3 (usmereni parovi sa q > 0, I38 `two_paths`; zahtevi bez dve putanje su fiksirani na 0).
- Opterećenje linka: `L_e(z) = Σ_d q_d · [link e na putanji z_d zahteva d]`, jedan period (topohub ima jednu matricu).
- **Sintetička cena (nije izvorna SNDlib cena):**
  - jedinica modula je `U = 4 × srednja pozitivna vrednost zahteva` instance;
  - moduli imaju kapacitet U i 2U, po ceni `dist_e` i `1.6·dist_e` (`dist_e` je topohub dužina u km);
  - početni kapacitet je 0;
  - kao u I39 (uslov c1 ≤ c2 ≤ 2c1): `n2 = ⌊⌈L_e/U⌉/2⌋`, `n1 = ⌈L_e/U⌉ mod 2`, `f(z) = Σ_e dist_e·(n1 + 1.6·n2)`;
  - sva rešenja su dopustiva.
- Ograda: rezultat važi za ovaj sintetički model troška. To je sintetička validacija, ne dokaz o stvarnoj infrastrukturi.

## 3. Metode (isti broj stvarnih evaluacija; evaluacija = jedan poziv `f`)
1. **GA-I39**: tačna I38/I39 konfiguracija: `population_size=24`, `cost_diversity_metric="log_relative"`,
   `population_mutation="cost_diversity,parent_diversity"`, `add(0,1,1)` po genu, izlaz isključivo po budžetu
   (`exit_function`). Jedina razlika od I39: `number_of_generations=10**6` i `timeout=3600`, da bi budžet bio jedino ograničenje.
2. **GA-default**: `GA(cost_function=...)` sa podrazumevanim parametrima, isti izlaz po budžetu (sekundarno).
3. **(1+1)-EA**: nasumičan početak, standardna mutacija bitova sa verovatnoćom 1/N, uz ponavljanje dok se ne obrne bar
   jedan bit. Prihvata potomka ako `f(y) ≤ f(x)`.
4. **Nasumična pretraga**: uniformni nasumični nizovi bitova.
5. **Referenca `f0`** = `f(0…0)` (sve prve najkraće putanje); jedna evaluacija, van budžeta.

- Budžet: 10.000 evaluacija po pokretanju. Najbolje do tada se beleži na kontrolnim tačkama **B ∈ {360, 2000, 10000}**.
  Pošto se izlazi samo po budžetu, putanja do B je identična kao kod pokretanja sa budžetom B.
- Pozivi preko budžeta vraćaju 1e15 bez evaluacije i broje se, kao u I38.
- Semena 4300–4311 (12, uparena po metodama); seeduju se i `random` i `numpy.random`.
- Ukupno 6 instanci × 12 semena × 4 metode = 288 pokretanja.

## 4. Mera i statistika
- Ishod: `r = (f_best(B) − f0) / f0`. Negativno znači bolje od reference prvih najkraćih putanja.
- **Primarni test:** po instanci, uparen Wilcoxon (dvostrani) GA-I39 vs (1+1)-EA na `r`, pri B=360 i B=10000.
  Holm korekcija preko 12 testova, α = 0,05.
- Sekundarno (izveštaj, ne odlučuje): GA-default, nasumična pretraga, B=2000 i broj semena u kojima je `r < 0`.

## 5. Klasifikacija (po instanci, pri B=10000)
- **DEFICIT_OPERATORA**: (1+1)-EA značajno bolji od GA-I39 (Holm) i medijana `r` EA < medijana `r` GA-I39.
- **ARTEFAKT_BUDŽETA**: GA-I39 nije značajno lošiji od EA, GA-I39 ima `r < 0` u ≥ 10/12 semena pri B=10000, a u ≤ 2/12 pri B=360.
- **MEŠOVITO**: sve ostalo.

Ukupni zaključak je kategorija sa ≥ 4/6 instanci, inače „nerazrešeno“. Ako je GA-I39 značajno **bolji** od EA,
to se izveštava kao takvo.

**Posledice:**
- DEFICIT_OPERATORA → sledeći gate je prior-art audit za binarne/diskretne operatore u samoadaptivnom GA. Mutacija
  bitova je poznata, pa se novost ne pretpostavlja.
- ARTEFAKT_BUDŽETA → I39 zaključak se preformuliše kao ograničenje budžeta, bez promene GAdapt-a.
- Bez ponavljanja sa drugim parametrima dok rezultat ne postane „zanimljiv“.

## 6. Kontrolne provere (sintetičke, pre stvarnog pokretanja)
- formula `f` na ručno izračunatom primeru (3 čvora);
- `f0` i brojanje evaluacija (tačno B poziva, a pozivi preko budžeta se ne evaluiraju);
- (1+1)-EA na OneMax-u: dostiže optimum za N=30 u ≤ 2000 evaluacija za fiksno seme (sanity check);
- GAdapt bit-identičnost: kod GAdapt biblioteke se ne menja (`git diff gadapt/` mora biti prazan).

## 7. Budžet i arhiviranje
2.880.000 evaluacija jeftine numpy funkcije, multiprocessing lokalno, bez CI-a. Tvrdo ograničenje: 3 h ukupno.
Izlaz: `research/results/iteration43/diagnostic.json` (po pokretanju sve kontrolne tačke, broj poziva, vreme, SHA-256
izvora i ulaza, verzije paketa) + izveštaj `ITERATION43_REPORT_SR.md`, uključujući i negativan ishod.
