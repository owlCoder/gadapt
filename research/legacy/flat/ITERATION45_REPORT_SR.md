# ITERATION45 — deficit je specifičan za GAdapt, ne generički: izveštaj

**22. oktobar 2026.** Protokol: [ITERATION45_PROTOCOL.md](ITERATION45_PROTOCOL.md) (`7061d7f`). Kod `f8dcb04`. Izvršeno je
**jedno** pokretanje: 216 pokretanja, 837 s, na 6 **novih** instanci (od 110 do 1332 gena). Sirovi izlaz je u
[results/iteration45/generic_vs_specific.json](results/iteration45/generic_vs_specific.json). Cena je sintetička (kao u
I43). Validacioni pozivi GAdapt-a su isključeni (kao u I44).

## 1. Preregistrovana klasifikacija: **SPECIFIČNO ZA GADAPT** (5/6)

| Instanca | Geni | med r GAdapt-I39 | med r udžbenički GA | med r (1+1)-EA | F1 Holm p (udžb. vs GAdapt) | F2 Holm p (EA vs udžb.) |
|---|---|---|---|---|---|---|
| dfn-gwin | 110 | −0,340 | −0,361 | −0,377 | 0,11 | 0,19 |
| newyork | 240 | −0,085 | −0,109 | −0,127 | **0,021** | **0,003** |
| norway | 702 | +0,008 | −0,001 | −0,006 | **0,014** | **0,048** |
| pioro40 | 780 | +0,007 | −0,009 | −0,010 | **0,006** | 0,23 |
| zib54 | 1244 | +0,036 | +0,024 | +0,006 | **0,006** | **0,003** |
| cost266 | 1332 | +0,013 | +0,006 | −0,004 | **0,021** | **0,004** |

B = 10.000; `r = (f_best − f0)/f0`.

- Fiksirani udžbenički GA (populacija 24, turnir, uniformno ukrštanje, mutacija 1/N) je značajno bolji od GAdapt-a na
  **5/6** instanci, uz **istu veličinu populacije i isti budžet**.
- (1+1)-EA je bolji od udžbeničkog GA-a na 4/6. Na ovoj klasi problema lokalna pretraga je jaka, ali to ne objašnjava
  zaostajanje GAdapt-a.
- Sekundarno: GAdapt je lošiji od (1+1)-EA na **6/6** (sve Holm p < 0,01). Ukupno, u I43–I45 GAdapt je značajno lošiji
  od (1+1)-EA na **14 od 18** topologija i nije bolji ni na jednoj.
- Na četiri najveće instance GAdapt posle 10.000 evaluacija ne dostiže rešenje prvih najkraćih putanja (`r > 0`).
- Pri B=360 je GAdapt na manjim instancama ispred obe kontrole, ali tu prednost gubi do B=2000.

## 2. Šta je isključeno kao uzrok (I43–I45)

| Kandidat | Status |
|---|---|
| Samo premali budžet | Isključeno (I43: 0/6) |
| I39 izbor parametara | Isključeno (I43: GA-default ≈ GA-I39) |
| Intenzitet mutacije (20% gena) | Isključeno (I44: 0/6) |
| Validacioni artefakt | Isključeno kao uzrok deficita (I44/I45: deficit postoji i bez njega) |
| Generička slabost populacionog GA-a | Isključeno (I45: udžbenički GA bolji na 5/6) |

## 3. Šta ostaje

Razlike GAdapt-a u odnosu na udžbenički GA su:
- selekcija ruletom po trošku umesto turnira;
- „blending“ ukrštanje sa adaptivnom verovatnoćom;
- mutacija 50% populacije, sa izborom jedinki po raznovrsnosti roditelja i cene;
- elitizam (`keep_elitism_percentage`);
- popravka duplikata.

Neka od ovih komponenti (ili njihova kombinacija) uzrokuje deficit. Sledeći korak je **preregistrovana ablacija
komponenti** sa udžbeničkim GA-om kao referencom.

## 4. Ograde
- Cena je sintetička (modularna, nad stvarnim topologijama i zahtevima), a problemi su binarni. Rezultat se ne prenosi
  automatski na kontinualne probleme, za koje je GAdapt prvenstveno dizajniran.
- Udžbenički GA je fiksiran unapred i nije podešavan. Bolje podešen GA bi verovatno samo povećao razliku.
