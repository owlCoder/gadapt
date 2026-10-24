# ITERATION59: ugrađena FR opcija GAdapt-a u telekom planiranju kapaciteta (IZVEŠTAJ)

**Status: IZVEŠTAJ — razvojni NO-GO; H59 zaključak nedostupan** (2026-10-24). Kostur pisan pre rezultata (Codex 069).
Merodavni su zamrznuti protokol [ITERATION59_PROTOCOL.md](ITERATION59_PROTOCOL.md) (zamrznut `0879ff8`, pre ikakvog
razvojnog merenja) i pojašnjenja [ITERATION59_CLARIFICATIONS.md](ITERATION59_CLARIFICATIONS.md).

- Kod: [iteration59_telecom.py](iteration59_telecom.py); ispravke pre ikakvog merenja: Codex 054 (`53ee1ab`), Codex 069
  i nedostajući `sys.path` (`7b0a80e`; bez te ispravke svaka faza pokrenuta kao skripta pala bi na uvozu biblioteke).
- Sirovi izlazi: `results/iteration59/manifest_development.json.gz`, `development.json.gz`.

## 1. Pitanje i izvršavanje
Da li FR opcija (`constraint_handling="feasibility_rules"`, G1) skraćuje vreme do cilja prema kazni f + 1000·V (G0) na
modularnom planiranju kapaciteta (TopoHub SNDlib, statički zahtevi)? Razvoj: abilene, pdh; potvrda (nije izvršena):
polska, nobel-germany, nobel-us.

Izvršeno jednom (prema logu lanca: razvoj 22:25–23:05): MILP reference za obe razvojne instance **sertifikovane** (status 0,
gap 0; abilene C* = 81,79768, pdh C* = 121,97611) i nezavisno proverene (`usable`); izbor: 40 putanja (2 mreže × 10 semena
× G0/G1) po 30.000 poziva, sve uspešne.

## 2. Razvojno pravilo i odluka
> Iz prefiksa se bira najmanji B ∈ {3000, 10.000, 30.000}, zatim najmanji ε ∈ {0,05; 0,10; 0,20}, sa zbirnim G0/G1
> dostizanjem 20–80% na SVAKOJ razvojnoj mreži. Izabrani par mora proći isti uslov na novim validacionim semenima.
> Neuspeh znači NO-GO; nema ponovnog izbora.

Zbirno G0/G1 dostizanje cilja C ≤ (1 + ε)C* do budžeta B (20 putanja po mreži):

| B | abilene ε = 0,05 / 0,10 / 0,20 | pdh ε = 0,05 / 0,10 / 0,20 |
|---|---|---|
| 3000 | 0,75 / 1,00 / 1,00 | 0,00 / 0,00 / 0,50 |
| 10.000 | 1,00 / 1,00 / 1,00 | 0,10 / 0,80 / 1,00 |
| 30.000 | 1,00 / 1,00 / 1,00 | 0,95 / 1,00 / 1,00 |

**Odluka: `NO-GO: no (B, eps) with 20-80% attainment on every development network`.** Nijedan par ne zadovoljava uslov
na obe mreže istovremeno: abilene je pri svim parovima osim (3000; 0,05) iznad 80%, a pri tom paru pdh ima 0%.
Validaciona semena, potvrdne reference i potvrdne putanje se po protokolu ne izvršavaju; nema ponovnog izbora.

**Tumačenje (unapred napisano):** nijedan dozvoljeni par nije zadovoljio razvojni uslov; H59 zaključak je nedostupan, bez
ponovnog izbora. To **nije** ishod „H59 nije podržana“ (N): studija nije stigla do zaključivanja.

## 3. Opisno (razvoj; nije zaključivanje)
Medijana najboljeg izvodljivog troška posle 30.000 poziva: abilene G0 82,608 / G1 82,598 (C* = 81,798; ≈ 1% iznad),
pdh G0 124,237 / G1 124,743 (C* = 121,976; ≈ 2% iznad). Razvojne putanje nisu predviđene za poređenje grana.

## 4. Ograničenja i pouke
- Razvojni skup od dve mreže vrlo različite težine (abilene lak, pdh težak) čini pravilo „20–80% na svakoj mreži“ teško
  ispunjivim; to je svojstvo unapred zadatog dizajna, ne greška izvršavanja. Izmena pravila posle ovog ishoda nije
  dozvoljena; eventualna nova telekom studija zahteva nov protokol (npr. budžet po mreži, kao u I61 §5), nove instance ili
  semena i jasnu oznaku da je motivisana ovim NO-GO-om.
- Postupak sertifikacije optimuma (MILP, 3600 s) radi: obe razvojne reference sertifikovane.
- Kod: ispravka `sys.path` pre merenja (otkrivena kratkim pokretanjem, ne testovima: pytest dodaje radni direktorijum).

## 5. Zaključak (mapa ishoda, Codex 052)
Ishodi H58 / H60 / H59 = **N / N / nedostupno** (grana „neodlučno/prekinuto“ za H59). Praktična korist ugrađenih
tehnika za ograničenja naspram kazne 1000 nije potvrđena ni u jednoj naknadnoj studiji koja je stigla do zaključka; teza
ne sme tvrditi praktično ubrzanje. `constraint_handling` ostaje opt-in; README opisuje semantiku bez preporuke zasnovane na
brzini. Centralni empirijski doprinos ostaje ograničeni H56 nalaz; njegova nezavisna replikacija je I61 (u toku).
