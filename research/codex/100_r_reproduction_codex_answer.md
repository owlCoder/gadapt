Ukupan rezultat: **MATCH za sva četiri zahteva**. Analiza je izvedena sopstvenim read-only kodom nad gzip/JSON arhivama, bez uvoza projektnih analizatora i bez izmene fajlova.

## 1 — MATCH: ECDF površine, sredine, agregati i kontrasti

Ponovo je izračunato svih **12.600** vrednosti A: 4.200 R i 8.400 relevantnih E pokretanja. Korišćeni su zadati jaz, tri cilja i doprinos `(12000-hit+1)/12000`.

Sredine po paru, prikazane kao `GAdapt / IPOP`:

| par | shift | rot | rotm |
|---|---:|---:|---:|
| sphere\|2 | .975948 / .991039 | .975378 / .991240 | .976119 / .991167 |
| sphere\|7 | .910489 / .960733 | .909430 / .960829 | .907093 / .959430 |
| sphere\|20 | .625601 / .894601 | .616368 / .892283 | .626393 / .893123 |
| rosenbrock\|2 | .708801 / .989093 | .705011 / .989780 | .795988 / .989946 |
| rosenbrock\|7 | .600014 / .934117 | .615844 / .930195 | .602960 / .930208 |
| rosenbrock\|20 | .343924 / .784881 | .322547 / .774987 | .296711 / .769265 |
| rastrigin\|2 | .937565 / .808817 | .522191 / .780940 | .551875 / .826453 |
| rastrigin\|7 | .534019 / .025845 | .002638 / .034365 | .008078 / .013926 |
| rastrigin\|20 | .013246 / 0 | 0 / 0 | 0 / 0 |
| ackley\|2 | .922921 / .980054 | .916954 / .979928 | .922048 / .980470 |
| ackley\|7 | .530988 / .912682 | .468662 / .912380 | .504001 / .919241 |
| ackley\|20 | .161195 / .778308 | .023384 / .784588 | .031363 / .778113 |
| griewank\|2 | .589678 / .393113 | .500186 / .434121 | .557657 / .326723 |
| griewank\|7 | .069040 / .496515 | .041417 / .474197 | .050206 / .463120 |
| griewank\|20 | .160192 / .680235 | .073914 / .696834 | .065206 / .707425 |
| styblinski_tang\|2 | .967580 / .967214 | .965484 / .950960 | .952967 / .962674 |
| styblinski_tang\|7 | .862261 / .307766 | .458500 / .205209 | .356564 / .094399 |
| styblinski_tang\|20 | .339817 / 0 | .046369 / 0 | .068911 / 0 |
| beale\|2 | .949250 / .985959 | .907941 / .989359 | .879972 / .991600 |
| himmelblau\|2 | .968160 / .985192 | .944905 / .955145 | .964434 / .988468 |
| booth\|2 | .971251 / .991163 | .976324 / .991405 | .975989 / .991171 |

Ponderi sabiraju na 1: d=2 nosi 5/9, d=7 i d=20 po 2/9.

| varijanta | GAdapt | IPOP |
|---|---:|---:|
| shift | 0.700713374486 | 0.770072355967 |
| rot | 0.616732808642 | 0.762983734568 |
| rotm | 0.619827006173 | 0.759977767490 |

Kontrasti:

- c1 = **0.003094197531**
- c2 = **0.080886368313**
- c3 = **0.010094588477**
- c4 = **0.070791779835**

Maksimalna apsolutna razlika prema `analysis.json.gz`:

- sredine po parovima: **0**
- agregati: **2.22×10⁻¹⁶**
- procene kontrasta: **3.33×10⁻¹⁶**
- ukupno: **3.33×10⁻¹⁶**, tj. samo redosled floating-point sabiranja.

## 2 — MATCH: simultani max-studentizovani bootstrap

Korišćeno je 20.000 replika, `default_rng(70)`, α=0.05 i tačno jedan indeks po `(par, varijanta)`, deljen između GAdapt-a i IPOP-a.

| kontrast | procena | SE | donja | gornja |
|---|---:|---:|---:|---:|
| c1 | .003094197531 | .004588680764 | -.008051439513 | .014239834575 |
| c2 | .080886368313 | .003611517326 | .072114204076 | .089658532550 |
| c3 | .010094588477 | .002658594932 | .003637016969 | .016552159985 |
| c4 | .070791779835 | .004520450659 | .059811869726 | .081771689945 |

`t* = 2.4289414792633934`.

Verdikti:

- H64r1: **supported** — ceo c1 interval je unutar ±0.03.
- H64r2: **supported** — LB(c2)=0.0721142 > 0.05.
- H64r3: **supported** — LB(c4)=0.0598119 > 0.05 i H64r2 je podržana.

RNG redosled je isti kao projektni: replikacija → par → `shift, rot, rotm` → `integers(0,100,100)`. Potvrđena je identičnost eksplicitnog i blokovskog toka. Razlika za **SE, t*, obe granice i sve procene je tačno 0**.

## 3 — MATCH: strukturni integritet

Za svih **4.200** R zapisa:

- `calls == 12000`: 4.200/4.200; grešaka **0**
- `ok == true`: 4.200/4.200
- tačno očekivano seme: grešaka **0**
- duplikati ili nedostajući `(k, konfiguracija, s)`: **0**
- provereno **696.044** događaja; neispravnih nizova **0**
- pozivi događaja su strogo rastući i unutar `[1,12000]`
- opseg semena: `67063001–67083100`.

Konstrukcija `rotm` odgovara izvorima: `Q` dolazi iz ćelije `3k+2`, `o` iz `3k+1`, a cilj je `f(x* + w Qᵀ(y-o))`; videti [e_common.py](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:28), [e_study.py](/Users/danijel/Desktop/gadapt/research/i64/e_study.py:57) i [r_study.py](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:69).

Nezavisnom rekonstrukcijom svih 21 transformacija:

- maksimalno `|QᵀQ-I|`: **1.11×10⁻¹⁵**
- maksimalna razlika između rekonstruisanog cilja u `best_y` i arhiviranog `best_f`, preko svih 4.200 zapisa: **4.34×10⁻¹⁹**.

`check_repro` i manifest:

- svih **5/5** kontrolnih ponavljanja označeno je identičnim; kriterijum u kodu poredi `calls`, `best_f`, `best_y` i kompletne `events`;
- svih **67** E heševa odgovara stvarnim fajlovima i kopijama u `check_repro`, R `run` i `analysis`;
- svih **21/21** R delova nosi isti manifest i iste E heševe;
- zamrznuti komit: `b38c6fd5fc854353b70a021dae7d58110680f8df`;
- SHA-256 specifikacije i `r_study.py` poklapa se sa blobovima iz zamrznutog komita.

## 4 — MATCH: tekst izveštaja

U [ITERATION64_R_REPORT_SR.md](/Users/danijel/Desktop/gadapt/research/ITERATION64_R_REPORT_SR.md:1) nisam našao prekomerne tvrdnje:

- govori se o ortogonalnoj transformaciji Q, uz eksplicitno „moguće sa refleksijom”;
- ne tvrdi se širi mehanizam;
- nalaz je ograničen na 21 ćeliju i dve konfiguracije;
- izričito nema generalizacije na proizvoljne Haar transformacije;
- neizvesnost je jasno ograničena na semena, bez neizvesnosti izbora funkcija, dimenzija, Q ili o.

**Konačno: MATCH / MATCH / MATCH / MATCH.**