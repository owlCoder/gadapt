**Numerički rezultati su MATCH za I, I2, E4 i κ predikciju.** Nađena su odstupanja u formulacijama i I2 proveri porekla podataka. Proračun je urađen nezavisnim kodom, bez uvoza ili pokretanja projektnih analizatora. Fajlovi nisu menjani.

**1. I64-I — MATCH.** Iz događaja do odgovarajućeg budžeta rekonstruisani su izvodljivost, sirovi G i L: negativni G odsečen je samo za L; neizvodljivo daje G=∞, L=1. Ćelijski CVaR je prosek tri najveća L među 30; osam ćelija ima jednake težine.

Svih 2.160 zapisa ima `ok=true`, `calls==12000`, jedinstvene ključeve i ispravno uređene događaje. Delovi su identični zbirnom `run.json.gz`. Svih 1.546 izvodljivih završnih rezultata ima `witness_checked=true`; preostalih 614 nema izvodljivog svedoka. Poslednji događaj tačno odgovara `best_feasible`. Ovo potvrđuje arhivirane zastavice i putanju provere u kodu; PF provere nisu ponovo izvršavane.

Slede svih 18 kontrasta; M označava GAdapt-M. Uglaste zagrade su simultani intervali.

| Konkurent c | P(c)−P(M): procena [LB; UB] | CVaR(c)−CVaR(M): procena [LB; UB] |
|---|---|---|
| preset | −0,004167 [−0,016667; 0,008333] | 0,042245 [−0,062639; 0,147129] |
| PyGAD random | −0,079167 [−0,113365; −0,044968] | 0,116561 [−0,002580; 0,235702] |
| PyGAD adaptive | −0,125000 [−0,142867; −0,107133] | 0,172456 [0,012904; 0,332009] |
| DE | −0,120833 [−0,133441; −0,108226] | 0,091432 [−0,027577; 0,210441] |
| CMA | 0,008333 [−0,009631; 0,026298] | −0,046127 [−0,165136; 0,072882] |
| IPOP | 0,025000 [−0,004254; 0,054254] | −0,045415 [−0,164429; 0,073599] |
| BIPOP | 0,020833 [−0,006552; 0,048218] | −0,043960 [−0,162977; 0,075057] |
| ES11 | 0,004167 [−0,024376; 0,032709] | 0,040297 [−0,142949; 0,223543] |

Preostala dva: `0,8CVaR(M)−CVaR(preset)` = **−0,101696 [−0,202022; −0,001370]**; ponovljeni `P(preset)−P(M)` jednak je prvom redu.

Upareni bootstrap: 20.000 ponavljanja, seme 67, zajedničko uzorkovanje semena unutar ćelije. Podela α=0,025/0,025 reprodukovana je; rezervni P-interval je ±0,02984716687, prema propisanoj formuli. Svih 18 kontrasta je aktivno, pa rezerva nije primenjena. **t*=3,1098081557191866; H64c neodlučeno, H64d suprotno.** Samo jedan CVaR kontrast ima LB>0; IPOP-ova gornja P-granica prelazi 0,05.

Maksimalna apsolutna razlika: opisne mere na 3.000/12.000 poziva **0**, procene kontrasta **5,55×10⁻¹⁷**, granice **8,33×10⁻¹⁷**.

**2. I2 — numerički MATCH.** Svih 240 zapisa ima 12.000 poziva; 178 izvodljivih ima proverenu zastavicu svedoka. Potvrđeno je svih 480 uparivanja sa M/IPOP po stvarnoj ćeliji, semenu i identičnom r.

| Kontrast | Procena [LB; UB] |
|---|---|
| CVaR(M)−CVaR(H) | −0,079892 [−0,265624; 0,105841] |
| P(H)−P(M) | −0,004167 [−0,035480; 0,027147] |
| CVaR(IPOP)−CVaR(H) | −0,125307 [−0,250224; −0,000390] |
| P(H)−P(IPOP) | −0,029167 [−0,064279; 0,005946] |

20.000 ponavljanja, seme 68, ista podela α; nema degeneracije. **t*=3,41330997338; H64h1 neodlučeno, H64h2 suprotno.** Maksimalna razlika procena **1,11×10⁻¹⁶**, granica **2,22×10⁻¹⁶**.

**3. E4 — MATCH.** Korišćeno je isključivo 6.300 `cr` zapisa iz `run4cr_part_*`, uz 18.900 `cg/cu/cp` iz `run4_part_*` i 31.500 relevantnih E baznih zapisa. Prvih 6.300 `cr` zapisa odbačeno je. Ključevi su jedinstveni, svi budžeti tačni; svih 63 heša baznih delova odgovara E4 metapodacima.

| Kontrast, redosled specifikacije | Procena [LB; UB] |
|---|---|
| c1 | 0,014030 [0,005221; 0,022838] |
| c2 | −0,003166 [−0,006589; 0,000258] |
| c3 | 0,003022 [−0,001080; 0,007123] |
| c4 | 0,000867 [0,000532; 0,001202] |
| c5 | −0,002892 [−0,012355; 0,006570] |
| c6 | −0,002920 [−0,011373; 0,005534] |
| c7 | −0,132221 [−0,142040; −0,122403] |

20.000 ponavljanja, seme 69, α=0,05; propisano ponderisanje funkcija/dimenzija. **t*=2,66515095918; k1 neodlučeno, k2 podržano, k3/k4 neodlučeno, k5 suprotno; jezgro nije podržano.** Maksimalna razlika procena **3,47×10⁻¹⁸**, granica **8,33×10⁻¹⁷**, opisnih agregata **6,94×10⁻¹⁸**.

**4. κ — MATCH: P-G1=5/8, P-G2=7/8, ukupno neodlučeno.** Brojevi su prikazani zaokruženo; poređenja koriste pune vrednosti.

| Ćelija | κ | CVaR M / IPOP | Medijana G M / IPOP |
|---|---:|---:|---:|
| case30 j2 | 0,597638 | 0,006526848 / isto | 0,006569727 / isto |
| case30 j3 | 0,616928 | 1 / 1 | ∞ / ∞ |
| case39 j2 | 0,801993 | 0,003877320 / 0,001541598 | −0,006107685 / −0,009803010 |
| case39 j3 | 0,744867 | 0,333333333 / 0 | −0,008193582 / −0,006841790 |
| case39 j4 | 0,722631 | 1 / 1 | ∞ / ∞ |
| RTS j2 | 0,660608 | 0,006448673 / 0,000091021 | 0,000043187 / −0,000000381 |
| RTS j3 | 0,659776 | 0,009375150 / 0,000629478 | 0,002534298 / −0,004160956 |
| RTS j4 | 0,665771 | 0,018505211 / 0,005957168 | 0,012325259 / −0,002818142 |

P-G1 zahteva strogo niži CVaR: tri jednakosti ne broje se. P-G2 dozvoljava jednakost: četiri stroga dobitka i tri jednakosti, uključujući obe ∞=∞. Te ćelije **nisu isključene**.

**5. Tekst i protokol — sledeći MISMATCH nalazi:**

- [E4 izveštaj](/Users/danijel/Desktop/gadapt/research/ITERATION64_E4_REPORT_SR.md:7) kaže „pet kontrasta“; ispravno je **sedam**.
- Njegovo [tumačenje](/Users/danijel/Desktop/gadapt/research/ITERATION64_E4_REPORT_SR.md:69), ponovljeno u [PHD_PROGRESS](/Users/danijel/Desktop/gadapt/research/PHD_PROGRESS.md:323), tvrdi da CVaR ne pada 20%. Ispravno: **pad ≥20% nije potvrđen**; c2 obuhvata nulu.
- „Nema štete orig+shift“ u istom zapisu preteruje: potvrđene su tolerisane margine; tačkasti CVaR raste **16,21%**.
- Formulacije „prednost se NE prenosi“ i „hibrid i preset ne pomažu“ treba suziti: prednost hibrida prema M **nije potvrđena**; prema IPOP-u rep je lošiji. Preset ne ostvaruje zadati cilj.
- I2 `run.json.gz` ima **`i_run_sha256=null`**, a analizator ne proverava propisani heš. Numeričko uparivanje prolazi, ali zahtev porekla podataka ne prolazi. I2 izveštaju nedostaju i specifikacijom tražene medijane G.

Svih **372 proverena numerička polja** u tri izveštaja odgovara arhivama uz prikazano zaokruživanje.