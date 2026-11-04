# M5 — nezavisna metodološka revizija (za potpis recenzenta)

**4. novembar 2026. DRAFT / NO-FREEZE / NOT_ESTABLISHED.**
Ovaj dokument nije samostalno nezavisno stručno mišljenje, ne potpisuje
naučni zaključak i ne odobrava nove eksperimente.

## Mehanički dokazano, ali još ne naučno odobreno

| Tema | Sačuvani i verifikovani izvor | Otvorena recenzentska odluka |
|---|---|---|
| I55 originalni A | 620/620 originalnih NPZ, 295.445 vrednosti funkcija, 86 read-only regresionih testova prošlo | C1/C2 su pravila evidentiranja, ne potvrđene greške. 1.956 od 2.105 C1 događaja preklapa se sa C2; nema nezavisne procene osetljivosti/specifičnosti. |
| I55 A′/B | Originalni agregatni odnosi sekvencijalnih hešova za 620 validnih ćelija | Originalni potpuni A′/B koordinatni nizovi nisu sačuvani sa A NPZ izvorom. |
| I64-R | Arhivirani zaključak c4 ≈ 0,07079178 za fiksnih 21 kombinacija iz devet funkcijskih porodica | Originalni van-Git fajl sa 4.200 semenskih zapisa nedostaje; bootstrap od 20.000 replikacija zato nije nezavisno ponovljen. Izostavljanje Rastrigina je *post-hoc*. |
| I64-I2 | Originalnih 13/13 inferencijalnih vrednosti reprodukovano iz 720 arhivskih ishoda | Retka naknadno izabrana ćelija case39/j=3; originalna odluka H64h2 ostaje OPPOSITE. |
| I32 | Sedam originalnih Git blobova obnovljeno na draft PR #15, 19/19 izvornih testova prošlo, 72 arhivska ishoda aritmetički potvrđena | Uparena originalna neadjustirana p-vrednost za GAdapt fixed-stop i DE fixed-stop je **0,0625**, ne ispunjava prag 0,05. Bez nove nezavisne fizičke validacije. |

## Novo pitanje M5: pseudo-replikacija i težina pojedinačnih C1 poziva

Naknadna, read-only provera originalnih 109 C1-pozitivnih NPZ
tragova pokazuje dva bitno različita imenitelja:
**2.050/2.105 (97,39%) C1 poziva na punom negativnom uglu**,
ali samo **97/149 (65,10%) prvih pojavljivanja negativnog
ugla unutar pojedinačne ćelije**. Od 1.956 identičnih ponavljanja
**1.953 su negativna**, tri pozitivna. Pet originalnih ćelija
daje 851/2.105 događaja. Četiri naknadno izabrane biblioteke sa
najviše C1 ponavljanja daju 1.918/1.956 ponavljanja.

**Izričit zadatak recenzenta:** razdvojiti estimand na nivou
poziva od estimanda na nivou jedinstvenog (ćelija, ugao)
para; ne tretirati 2.105 poziva ili 149 parova kao nezavisne
realizacije slučajno izabrane populacije. Post-hoc isključivanje
četiri biblioteke **nije** novi registrovani eksperiment, a
observirana C1 dominacija **nije** nezavisno dokazan softverski
defekt ni uzročna pristrasnost algoritma.

[Originalni izvor, izračunavanje i interpretacija](
I65_I55_ORIGINAL_C1_EVENT_WEIGHTING_REPETITION_COMPOSITION_2026-11-04.md) ·
[Mašinski dokaz](
I65_I55_ORIGINAL_SIGNED_C1_DEDUP_WEIGHTING_AND_LIBRARY_CONCENTRATION_2026-11-04.json).
Ovaj dodatak **ne menja status M5_REVIEW_PENDING**.

## Obavezne recenzentske provere

1. Jesu li biblioteke, funkcijske porodice, semena i sintetički IEEE14 scenariji jasno predstavljeni kao **fiksni ograničeni uzorci**, a ne kao slučajan uzorak industrijske populacije?
2. Razdvajaju li se originalni simultani intervali, neadjustirane p-vrednosti, višestruka poređenja i post-hoc analize uticajnih ćelija?
3. Jesu li pozivi funkcije i C1/C2 događaji odvojeni od nezavisnih statističkih jedinica i potvrđenih softverskih defekata?
4. Je li uz svaku tvrdnju o I64-R bootstrap-u navedeno da originalni sirovi R fajl nedostaje i da izvorni bootstrap nije nezavisno reprodukovan?
5. Jesu li originalnost algoritma, uzrok ponavljanja vektora, električna fizička izvodljivost i generalizacija jasno odvojeni od identičnog reprodukovanja arhive?
6. Koje tvrdnje treba ukloniti, ograničiti ili izložiti drugoj, **prospektivno odobrenoj** analizi?

**Recenzent, ustanova i sukob interesa:** _________________________

**Pregledani Git SHA / Actions artefakti:** ________________________

**Odluka:** [ograničeni opseg prihvatljiv / traže se ispravke / nedovoljni dokazi]

**Obrazloženje i zahtevane korekcije:** ___________________________

**Datum i potpis:** ______________________________________________

Bez popunjene, datirane i potpisane odluke: **M5_REVIEW_PENDING**.

Povezani dokazi: [tehničko zatvaranje](I65_2026_11_04_TECHNICAL_CLOSEOUT_AND_HUMAN_DECISION_GATES.md),
[mentorova odluka M6/C1](I65_M6_C1_REVIEW_READY_SOURCE_UPDATE_2026-11-04.md),
[originalni R/A′/B podaci](I65_EXTERNAL_ORIGINAL_SOURCE_RECOVERY_HANDOFF_2026-11-04.md),
[I55 read-only CI](https://github.com/owlCoder/gadapt/actions/runs/41804478669),
[I32 source-only CI](https://github.com/owlCoder/gadapt/actions/runs/41812770932).

Nijedan novi optimizer, AC/OPF ili held-out COCO nije izvršen radi ovog dokumenta.
