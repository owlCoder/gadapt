# ITERATION45 — da li je deficit specifičan za GAdapt ili generički za GA? (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre pokretanja.** Datum: 2026-10-22. Prethodno: [ITERATION44_REPORT_SR.md](ITERATION44_REPORT_SR.md).
Dijagnostika, bez tvrdnje o novini.

## 1. Pitanje
I43/I44: (1+1)-EA je bolji od GAdapt-a na 8/12 topologija. Da li bi standardni udžbenički GA, pri istom budžetu i istoj
veličini populacije, bio bolji od GAdapt-a (deficit je **specifičan za GAdapt**)? Ili i on gubi od (1+1)-EA (deficit je
**generički** za populacione GA na ovoj klasi problema)?

## 2. Instance: NOVE (nekorišćene u I43/I44)
Topohub v1.5.1: `dfn-gwin` (110 gena), `newyork` (240), `norway` (702), `pioro40` (780), `zib54` (1244), `cost266` (1332).
Model i sintetička cena su identični I43 §2.

## 3. Metode (budžet 10.000, semena 4500–4511, uparena)
1. **GAdapt-I39**: kao GA-I39 u I44, sa validacionim pozivima isključenim iz budžeta i najboljeg rešenja (`ValidatorFree`).
   Ne koriste se nove opt-in opcije (`64b9c82`), da bi krak bio identičan I44.
2. **Udžbenički GA** (fiksiran unapred, ne podešava se):
   - populacija μ = 24, nasumičan početak;
   - generacijski model sa elitizmom 1: najbolji iz stare populacije + 23 potomka;
   - roditelji se biraju binarnim turnirom (veličina 2, sa vraćanjem);
   - uniformno ukrštanje sa verovatnoćom 0,9 (inače kopija prvog roditelja);
   - mutacija bitova sa verovatnoćom 1/N po bitu (bez prisilnog obrtanja);
   - svaki potomak se evaluira; pretraga staje kad se budžet potroši, i usred generacije.
3. **(1+1)-EA**: kao u I43/I44.

Kontrolne tačke B ∈ {360, 2000, 10000}; ishod `r = (f_best − f0)/f0`.

## 4. Statistika i klasifikacija (B = 10000)
Dve Holm porodice (po 6 testova, α = 0,05, uparen dvostrani Wilcoxon):
- **F1:** udžbenički GA vs GAdapt-I39;
- **F2:** (1+1)-EA vs udžbenički GA.

Ukupna klasifikacija:
- **SPECIFIČAN_ZA_GADAPT:** udžbenički GA je značajno bolji od GAdapt-I39 na ≥ 4/6.
- **GENERIČKI:** udžbenički GA nije značajno bolji od GAdapt-I39 na ≥ 4/6 **i** EA je značajno bolji od udžbeničkog GA na ≥ 4/6.
- **MEŠOVITO:** sve ostalo.

Sekundarno (opisno): GAdapt-I39 vs EA (treća replikacija deficita), B=360 i B=2000.

## 5. Kontrole pre pokretanja
- udžbenički GA na OneMax-u (N=30) dostiže optimum u ≤ 10.000 evaluacija za fiksno seme;
- tačno 10.000 evaluacija po pokretanju, elitizam ne gubi najbolje rešenje (monotonost najboljeg u populaciji);
- `ValidatorFree` provera kao u I44.

## 6. Budžet i arhiviranje
6 × 12 × 3 = 216 pokretanja, oko 15–25 min lokalno, bez CI-a. Izlaz: `research/results/iteration45/generic_vs_specific.json`
+ `ITERATION45_REPORT_SR.md`, i negativan ishod. Bez ponavljanja.
