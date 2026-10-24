# ITERATION56: tehnike za ograničenja × samoadaptacija GAdapt-a na diskretnom ORPD-u (IZVEŠTAJ)

**Status: KOSTUR — napisan pre rezultata** (2026-10-24, dok lanac faza radi). Test zaključivanje i sažeci:
`analysis.json.gz`; pokretanja, ponavljanja i tragovi: `test.json.gz`; kalibracija i snaga: razvojni izlazi i
`rehearsal.json.gz`. Tumačenje prati unapred zadata pravila protokola.

- Protokol: [ITERATION56_PROTOCOL.md](ITERATION56_PROTOCOL.md) (zamrznut `3f09eb9`); pojašnjenja P1–P5:
  [ITERATION56_CLARIFICATIONS.md](ITERATION56_CLARIFICATIONS.md).
- Kod: [iteration56_cht_study.py](iteration56_cht_study.py), merilo [iteration56_orpd.py](iteration56_orpd.py),
  testovi [test_iteration56_cht_study.py](test_iteration56_cht_study.py) (9/9). Recenzije: Codex 021–025.
- Sirovi izlazi: [results/iteration56/](results/iteration56/) (`.json.gz`).

## 1. Pitanje i šta je novo
Da li efekat samoadaptivne politike mutacije GAdapt-a na vreme do izvodljivog cilja zavisi od tehnike za
rukovanje ograničenjima (CHT), i menja li se efekat pod statičkom kaznom kad signali adaptacije koji čitaju
vrednost troška dobiju zajednički skalar? Uska novina (H5 §10): ablacija cele adaptivne politike sa istim
operatorima × CHT × rezolucija diskretnih kontrola. Rizik R1 (Mallipeddi 2012): i dalje neproveren (Codex 026).

**Srodni radovi (Codex 032, H5 §12):** Interakcija rukovanja ograničenjima i adaptacije parametara već je teorijski i
empirijski proučavana u evolutivnim strategijama, naročito za CSA i popravku neizvodljivih rešenja (Arnold 2013;
Hellwig i Arnold 2016). Numerički prekršaji ulaze i u adaptaciju istorije uspeha CAL-SHADE-a (Zamuda 2017), dok
Atamna i sar. (2020) analiziraju invarijantnost adaptivnog augmented-Lagrangian pristupa. I56 ispituje užu,
konkretnu intervenciju: promenu numeričkih signala GAdapt-ove politike mutacije uz zadržavanje pravila selekcije,
uključujući transformaciju statičke kazne koja čuva poredak. Doprinos je kontrolisana dijagnostička studija na
diskretnom ORPD-u; prioritet te tačne kombinacije nije dokazan.

## 2. Instance i izvršavanje
- case14 / case57 / case118 (9 / 27 / 77 kontrola), R ∈ {9, 17, 33}; test scenariji 0,90 / 1,00 / 1,10 / 1,15.
- Izuzeto po §2: case57 (1,10) i (1,15) — OPF ne uspeva.
- [upisati: broj jedinica, ok pokretanja, ponavljanja, izuzete jedinice, ćelije bez reference]

## 3. Kalibracija (razvojni scenariji)
- Razvojne reference: 72/72 ok. Bez izvodljivog i pri 30.000 poziva: case14 R=9 i case118 R=9 (oba scenarija).
- FX-M vektori (a, b, σ), medijana medijana preko 54 razvojna AD-N pokretanja po CHT-u: SP (0,571; 0,111; 0,001),
  AP (0,533; 0,111; 0,001), FR (0,500; 0,111; 0,001), EC (0,533; 0,111; 0,001). **σ = 0,001 je donja granica
  GAdapt-a:** kolonska raznovrsnost na diskretnim mrežama brzo kolabira, pa Gausova mutacija radi sa minimalnim σ
  (na mreži to je pomak od jednog koraka, zbog „mutiraj dok se ne promeni“).
- FX-T izbor (a, b, σ) iz mreže 27 konfiguracija: SP (0,75; 0,2; 0,05), AP (0,5; 0,4; 0,05), FR (0,75; 0,4; 0,05),
  EC (0,75; 0,4; 0,15).
- Proba (360 razvojnih pokretanja) i snaga: simulirana snaga 0,968 ≥ 0,8 → 10 semena po instanci (bez odstupanja).
  **Ograničenje simulacije:** u 4 od 9 razvojnih blokova (case118 svi R, case57 R = 33) nijedna od četiri grane
  probe ne dostiže cilj (T = 1 svuda, d = 0, sd = 0). Simulacija svaki takav blok pretvara u konstantno d = 0,05,
  što θ_a doprinosi 0,0222 bez varijabilnosti. Snaga 0,968 je uslovna na nametnutu alternativu; može precenjivati
  snagu testa i ne utvrđuje snagu ako ti blokovi ostanu degenerisani. Izvršavanje se ne menja (pravilo je zamrznuto).

## 4. Primarni ishod (H56a)
[`results.H56a.{estimate, ci, p, supported}`; samo ako je `primary_available`, inače `empty_cells` i `sensitivity`.
Formulacija „interakcija nije otkrivena pri ovoj snazi“ samo ako interval obuhvata 0 I |θ_a| < 0,02 (§7).]

## 5. Sekundarni ishodi (Holm preko 5)
[H56b signal pod SP; AP-protiv-SP; EC-protiv-SP; θ_a sa FX-M; kodiranje SP/SP-T — odluke po `p_holm` preko svih
pet; `ci` su nekorigovani.] Obrasci po blokovima, rangovi na toplotnoj mapi, razdvajanje krivih i tragovi su
OPISNI.

## 6. Opisno (H56c, per-arm, tragovi)
[medijana d po bloku naspram R (`median_d_by_block`); izvodljivost („ikad nađeno izvodljivo“) i dostizanje po
grani (`per_arm`, potpune jedinice); tragovi min/max CHT skalara i udela izvodljivih preživelih (test zapisi nemaju
D_t/D_0, koeficijente mutacije, razlike troškova roditelja ni istoriju σ).]

## 7. Pretnje validnosti
- Mreže vrednosti, opsezi šantova i scenariji su naše pretpostavke (merilo); termički pritisak slab (9900 MVA).
- Referenca L* je najbolje poznata, ne optimum; ciljevi zavise od nje.
- Tri mreže: nema tvrdnje o „veličini mreže“.
- R1: pun tekst Mallipeddi i sar. 2012 nije dostupan; novina formulisana uslovno.

## 8. Zaključak i posledice za GAdapt
[šta ide u opt-in API (`GADAPT_CONSTRAINT_API_DESIGN_SR.md`), šta ne]
