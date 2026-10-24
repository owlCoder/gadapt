# ITERATION56: tehnike za ograničenja × samoadaptacija GAdapt-a na diskretnom ORPD-u (IZVEŠTAJ)

**Status: KOSTUR — napisan pre rezultata** (2026-10-24, dok lanac faza radi). Brojevi se upisuju tek iz
`results/iteration56/analysis.json.gz`; tumačenje prati unapred zadata pravila protokola.

- Protokol: [ITERATION56_PROTOCOL.md](ITERATION56_PROTOCOL.md) (zamrznut `3f09eb9`); pojašnjenja P1–P5:
  [ITERATION56_CLARIFICATIONS.md](ITERATION56_CLARIFICATIONS.md).
- Kod: [iteration56_cht_study.py](iteration56_cht_study.py), merilo [iteration56_orpd.py](iteration56_orpd.py),
  testovi [test_iteration56_cht_study.py](test_iteration56_cht_study.py) (9/9). Recenzije: Codex 021–025.
- Sirovi izlazi: [results/iteration56/](results/iteration56/) (`.json.gz`).

## 1. Pitanje i šta je novo
Da li efekat samoadaptivne politike mutacije GAdapt-a na vreme do izvodljivog cilja zavisi od tehnike za
rukovanje ograničenjima (CHT), i menja li se efekat pod statičkom kaznom kad signali adaptacije koji čitaju
vrednost troška dobiju zajednički skalar? Uska novina (H5 §10): ablacija cele adaptivne politike sa istim
operatorima × CHT × rezolucija diskretnih kontrola. Rizik R1 (Mallipeddi 2012): [upisati ishod Codex 026].

## 2. Instance i izvršavanje
- case14 / case57 / case118 (9 / 27 / 77 kontrola), R ∈ {9, 17, 33}; test scenariji 0,90 / 1,00 / 1,10 / 1,15.
- Izuzeto po §2: case57 (1,10) i (1,15) — OPF ne uspeva.
- [upisati: broj jedinica, ok pokretanja, ponavljanja, izuzete jedinice, ćelije bez reference]

## 3. Kalibracija (razvojni scenariji)
- Razvojne reference: 72/72 ok. Bez izvodljivog i pri 30.000 poziva: case14 R=9 i case118 R=9 (oba scenarija).
- FX-M vektori (a, b, σ) po CHT-u: [upisati]
- FX-T izbor po CHT-u: [upisati]
- Proba i snaga: [upisati snagu i broj semena]

## 4. Primarni ishod (H56a)
[θ_a, 95% interval, p; podržano / nije otkriveno — po pravilu §7]

## 5. Sekundarni ishodi (Holm preko 5)
[H56b signal pod SP; AP-protiv-SP; EC-protiv-SP; θ_a sa FX-M; kodiranje SP/SP-T]

## 6. Opisno (H56c, per-arm, tragovi)
[medijana d po bloku naspram R; izvodljivost i dostizanje po grani; tragovi raznovrsnosti pod SP]

## 7. Pretnje validnosti
- Mreže vrednosti, opsezi šantova i scenariji su naše pretpostavke (merilo); termički pritisak slab (9900 MVA).
- Referenca L* je najbolje poznata, ne optimum; ciljevi zavise od nje.
- Tri mreže: nema tvrdnje o „veličini mreže“.
- R1 [upisati].

## 8. Zaključak i posledice za GAdapt
[šta ide u opt-in API (`GADAPT_CONSTRAINT_API_DESIGN_SR.md`), šta ne]
