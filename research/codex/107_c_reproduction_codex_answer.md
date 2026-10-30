Ukupan rezultat: **MATCH u svim proverama; nema numeričkih ni strukturnih odstupanja.** Računanje je izvedeno direktno iz arhiva, bez uvoza projektnih analizatora i bez izmene datoteka.

## 1. Tačkaste statistike — MATCH

Reizračunato je svih 1.260 vrednosti H:

- svih 1.260 je konačno;
- raspon H: 0,0074230884–1,0838442446;
- izostavljen je prvi zapis svakog pokretanja; svih 1.260 početnih vektora bilo je tačno jedinica;
- nije bilo generacija sa sredinom koeficijenata 0, pa nije bilo stvarnih preskakanja po tom pravilu.

Po parovima:

| Par | Δ | ΔA | E | Poređenje |
|---|---:|---:|---:|---|
| sphere\|2 | -0,016482 | -0,000171 | -0,038741 | MATCH |
| sphere\|7 | 0,000732 | 0,003396 | 0,177370 | MATCH |
| sphere\|20 | 0,006805 | -0,000792 | 0,020255 | MATCH |
| rosenbrock\|2 | -0,198455 | -0,087187 | -0,575698 | MATCH |
| rosenbrock\|7 | 0,135843 | -0,002946 | 0,112942 | MATCH |
| rosenbrock\|20 | 0,038209 | 0,047213 | 0,138083 | MATCH |
| rastrigin\|2 | -0,017793 | 0,385690 | 3,182420 | MATCH |
| rastrigin\|7 | 0,101413 | 0,525940 | 0,365397 | MATCH |
| rastrigin\|20 | 0,115009 | 0,013246 | 0,264956 | MATCH |
| ackley\|2 | 0,036256 | 0,000872 | -0,043089 | MATCH |
| ackley\|7 | 0,015574 | 0,026987 | 0,179187 | MATCH |
| ackley\|20 | 0,026447 | 0,129832 | 0,094243 | MATCH |
| griewank\|2 | 0,027576 | 0,032021 | -0,116562 | MATCH |
| griewank\|7 | 0,096720 | 0,018834 | 0,157839 | MATCH |
| griewank\|20 | 0,001082 | 0,094986 | -0,000285 | MATCH |
| styblinski_tang\|2 | -0,084415 | 0,014613 | 0,507780 | MATCH |
| styblinski_tang\|7 | -0,071451 | 0,505697 | 1,386490 | MATCH |
| styblinski_tang\|20 | 0,144909 | 0,270905 | 0,166796 | MATCH |
| beale\|2 | 0,167619 | 0,069278 | 1,241413 | MATCH |
| himmelblau\|2 | -0,144860 | 0,003726 | 0,442595 | MATCH |
| booth\|2 | -0,023424 | -0,004738 | -1,431473 | MATCH |

Maksimalna apsolutna razlika prema `analysis.json.gz` za sva tri niza je tačno **0,0**.

Sa težinama \(w_{f,d}=(1/9)/m_f\), čiji je zbir 1:

- ponderisana srednja Δ: **0,013184452070368674 — MATCH**
- ρ(Δ, ΔA): **0,274025974025974 — MATCH**
- ρ(E, ΔA): **0,5779220779220778 — MATCH**
- razlika korelacija: **−0,30389610389610383 — MATCH**
- pozitivni parovi: **14/21 — MATCH**
- nenulti parovi: **21/21**
- opisni binomni p: **0,09462356567382812 — MATCH**

## 2. Funkcijski klaster-bootstrap — MATCH

Reimplementiran je traženi redosled svakog kopiranog para:

1. C-shift, 30 indeksa;
2. C-rotm, 30;
3. arhivirani shift, 100 — zajednički za ΔA i E-shift;
4. arhivirani rotm, 100 — zajednički za ΔA i E-rotm.

Sa 20.000 ponavljanja, `default_rng(72)` i percentilima α/3:

| Statistika | Donja | Gornja | Razlika prema analizi |
|---|---:|---:|---:|
| ponderisana Δ | -0,04656357089101746 | 0,07086710694863661 | 0 / 0 |
| ρ(Δ, ΔA) | -0,08498023715415019 | 0,6176143790849671 | 0 / 0 |
| ρ(Δ, ΔA) − ρ(E, ΔA) | -0,7211619033140771 | 0,14805194805194802 | 0 / 0 |

Validno je **20.000/20.000** uzoraka.

- H64c1: **undecided — MATCH**; interval prelazi 0, a pozitivnih parova je 14 < 16.
- H64c2: **undecided — MATCH**; tačkasto ρ=0,2740 < 0,60, interval obuhvata prag 0,30.
- H64c3: **undecided — MATCH**; interval razlike prelazi 0.
- `signature_supported=False` i `stronger_marginal_than_baseline=False` — **MATCH**.

## 3. Strukturne i provenance provere — MATCH

- Zadaci: **1.260/1.260 jedinstvenih**, 0 duplikata.
- `ok=true`: **1.260/1.260**.
- `calls==1200`: **1.260/1.260**.
- Logovi: tačno **36 po pokretanju**, ukupno 45.360 vektora.
- Dimenzija vektora: **45.360/45.360 ispravnih**.
- Koeficijenti: raspon **[0,0; 1,0]**; 0 nekonačnih i 0 izvan intervala.
- Markeri loga: **66–1.186**, svuda neopadajući; 0 grešaka.
- Markeri događaja: **1–1.200**, 39.833 događaja, svuda neopadajući.
- Semena: 0 odstupanja; po 30 semena po paru/varijanti:
  - shift: 67.100.001–67.120.030;
  - rotm: 67.130.001–67.150.030.
- Arhivirani podaci: za svaki od 21 para tačno 100 GAdapt shift i 100 rotm zapisa, svi sa 12.000 poziva.
- Ulazni SHA-256: **27/27 MATCH** zasebno u `run`, `preflight` i `analysis`.
- Freeze commit: **`122178d3251ce347051b285ccc0f7ba93c9786ca` — MATCH**.
- Svih **8/8** zamrznutih izvora/specifikacija odgovara i manifestu i blobovima tog komita.

## 4. Tekst izveštaja — MATCH

[ITERATION64_C_REPORT_SR.md](/Users/danijel/Desktop/gadapt/research/ITERATION64_C_REPORT_SR.md) ne preuveličava nalaze:

- sve tri hipoteze su označene kao **undecided**;
- koeficijentni potpis je označen kao nepodržan (`False`);
- eksplicitno piše da je studija **korelaciona**, na **21 fiksnoj ćeliji**;
- navodi da se meri **samo log-relative koeficijent**, ne dijagonala kovarijanse;
- navodi da nema intervencije ni medijacije i da se **ne tvrdi uzrok**, što semantički odgovara tvrdnji da mehanizam nije potvrđen.

Doslovna rečenica „mehanizam nije potvrđen” nije upotrebljena, ali njen zahtevani smisao jeste eksplicitno pokriven navedenim ograničenjima.