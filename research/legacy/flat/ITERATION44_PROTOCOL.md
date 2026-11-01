# ITERATION44 — mehanizam: da li intenzitet mutacije objašnjava deficit GAdapt-a na binarnom izboru ruta? (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre pokretanja.** Datum: 2026-10-22. Prethodno: [ITERATION43_REPORT_SR.md](ITERATION43_REPORT_SR.md).

**Ovo je dijagnostika, ne predlog metode. Novost se NE tvrdi.** Teorija stope mutacije ~1/n za binarne EA je dobro
poznata. Rezultat može da utiče samo na praktičnu preporuku za GAdapt (podrazumevane vrednosti ili dokumentaciju), i
to tek uz posebnu odluku korisnika, jer se ponašanje biblioteke bez odobrenja ne menja.

## 1. Pitanje i hipoteza
**H-mut:** GAdapt sa I39 konfiguracijom, ali sa najviše **1** mutiranim genom po mutiranoj jedinki
(`number_of_mutation_decision_variables=1`), postiže manji `r` od iste konfiguracije sa podrazumevanih „do 20% gena“,
pri B = 10.000 evaluacija.

Vrednost 1 je izabrana iz teorije (1/n), a ne iz I43 podataka. Nijedna druga vrednost se ne isprobava.

## 2. Instance: NOVE, nekorišćene u I43
Topohub v1.5.1 (arhivirano): `nobel-us`, `abilene`, `ta1`, `nobel-eu`, `india35`, `janos-us` (od 91 do 650 gena).
Model, geni, putanje i sintetička cena su identični I43 §2 (kod iz I43 se koristi neizmenjen).

## 3. Metode (isti budžet od 10.000 evaluacija pretrage, semena 4400–4411, uparena)
1. **GA-I39**: tačna I43 konfiguracija (posle A1).
2. **GA-I39-m1**: isto, plus `number_of_mutation_decision_variables=1`.
3. **(1+1)-EA**: kao u I43.

**Validacioni artefakt je uklonjen:**
- za oba GA kraka se prva dva poziva funkcije troška (validator GAdapt-a) proveravaju: moraju biti vektor svih nula i
  vektor svih jedinica, inače je greška;
- ta dva poziva se **ne broje** u budžet i **ne ulaze** u najbolje rešenje;
- sve metode tako počinju bez besplatne tačke `f0`.

Kontrolne tačke: B ∈ {360, 2000, 10000}. Ishod je `r = (f_best − f0)/f0`, kao u I43.

## 4. Statistika i odluka
- **Primarno:** po instanci, uparen dvostrani Wilcoxon GA-I39-m1 vs GA-I39 pri B=10000. Holm preko 6 testova, α = 0,05.
- **H-mut PODRŽANA:** značajno i medijana `r` m1 < medijana `r` GA-I39 na ≥ 4/6 instanci.
- **H-mut OPOVRGNUTA:** takvo poboljšanje na ≤ 1/6 instanci.
- **DELIMIČNO:** sve ostalo.
- **Sekundarno** (odvojena Holm porodica, ne odlučuje):
  - GA-I39 vs EA i GA-I39-m1 vs EA pri B=10000. Prvo poređenje je replikacija I43 deficita bez validacionog artefakta,
    na novim instancama.
  - Isto pri B=360 i B=2000 (samo opisno).

## 5. Kontrole pre pokretanja
- test da su prva dva GAdapt poziva vektori svih nula i svih jedinica i da se ne broje;
- test da `number_of_mutation_decision_variables=1` stvarno menja najviše 1 gen po mutaciji: praćenje Hamming
  rastojanja na sintetičkom primeru, samo provera, bez optimizacije na instancama iz §2;
- `git diff gadapt/` mora biti prazan.

## 6. Budžet i arhiviranje
6 × 12 × 3 = 216 pokretanja, oko 10–15 min lokalno, bez CI-a. Izlaz: `research/results/iteration44/mechanism.json` +
`ITERATION44_REPORT_SR.md`, i negativan ishod. Bez ponavljanja sa drugim vrednostima mutacije.

## Dodatak A1 (pre stvarnog pokretanja, 2026-10-22)
Kontrola iz §5 je na **sintetičkom** grafu pokazala da `number_of_mutation_decision_variables=1` **ne** ograničava
mutaciju: jedan poziv je menjao do 52 gena.

Uzrok je u biblioteci. `VariableColumnarDiversityDecisionVariableMutationRateDeterminator._get_number_of_mutation_decision_variables`
prepisuje korisnikovu gornju granicu vrednošću `max(round(N/5), round(diversity·N))`. U podrazumevanoj konfiguraciji
(`candidate_solution_mutation="variable_columnar_diversity,random"`) parametar je zato tiho ignorisan, iako ga
dokumentacija opisuje kao gornju granicu. To je zaseban nalaz o GAdapt-u. Biblioteka se ne menja bez odobrenja.

Ispravka: krak **GA-I39-m1** koristi `number_of_mutation_decision_variables=1` **i** `candidate_solution_mutation="random"`.
`RandomDecisionVariableMutationRateDeterminator` poštuje granicu.

Konfuzija: m1 menja i način izbora gena (uniformno umesto ruletom po kolonskoj raznovrsnosti). Pozitivan rezultat se
zato pripisuje paketu „1 gen + uniforman izbor“, ne samo intenzitetu. Nijedan rezultat na instancama iz §2 nije bio
poznat u trenutku ove izmene.

Dopuna A1 (isti dan, i dalje pre pokretanja): ukrštanje ima poseban mehanizam popravke duplikata
(`BaseCrossover`: posle `MUTATE_AFTER_ATTEMPT` neuspešnih pokušaja mutira potomka sa limitom `broj_pokušaja − MUTATE_AFTER_ATTEMPT`).
To nije operator mutacije populacije, isti je u oba GA kraka i ne menja se. Kontrola iz §5 se zato proverava kao
„svaki poziv poštuje svoj prosleđeni limit, a poziv sa limitom 1 menja tačno 1 gen“.
