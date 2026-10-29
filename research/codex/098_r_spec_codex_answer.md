## Zaključak

**Ne zamrzavati još.** Konstrukcija `rotm` objektiva je ispravna, ali bootstrap u c4, reproduktivni gate i provenance imaju pre-freeze nedostatke.

### BUG

- **Bootstrap pogrešno razvezuje konfiguracije.** Spec nalaže isto seme za `gadapt` i `ipop` ([SPEC:7](/Users/danijel/Desktop/gadapt/research/ITERATION64_R_SPEC.md:7)), ali kod resampluje svaki `(k, variant, config)` nezavisno ([r_study.py:199](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:199)). Time se gubi kovarijansa u c4. E pravilno koristi isti indeks resampla za sve konfiguracije iste ćelije ([e_analysis.py:90](/Users/danijel/Desktop/gadapt/research/i64/e_analysis.py:90)).  
  **Fix:** jedan bootstrap indeks po `(k, variant)`, zajednički za `gadapt` i `ipop`; nezavisni indeksi između `shift`, `rot` i `rotm`.

- **`check_repro` proverava pogrešan ishod.** Poredi samo konačni `best_f` ([r_study.py:109](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:109)), dok A zavisi od vremena prvog pogotka. Kontraprimer: stari trag pogodi metu na pozivu 100, novi na 10.000, a oba završe sa istim `best_f`; gate prolazi, A se drastično menja.  
  **Fix:** zahtevati identične `calls`, `best_f`, `best_y` i kompletan `events`, kao u [e2_repro_check.py:49](/Users/danijel/Desktop/gadapt/research/i64/e2_repro_check.py:49). U specu navesti da su ćelije 1/2 zapravo `sphere,d=2`.

- **R kod/spec nisu zamrznuti manifestom.** `es.manifest("r")` hešira samo E fajlove i E protokol ([e_study.py:139](/Users/danijel/Desktop/gadapt/research/i64/e_study.py:139)); ne uključuje `r_study.py`, R spec ni R freeze commit. `stage_run` čak ne poredi sa manifestom iz `check_repro`, već samo Python/pip ([r_study.py:92](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:92), [r_study.py:123](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:123)).  
  **Fix:** poseban `r_manifest()` sa heševima R speca/koda, E koda, GAdapt stabla, mentor HEAD-a, freeze commita i svih postavki; isti manifest zahtevati u `check_repro`, svakom nastavku `run` i `analyse`.

- **E ulazi nisu unapred vezani za autoritativnu arhivu.** Heševi delova se samo beleže na kraju ([r_study.py:88](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:88), [r_study.py:149](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:149)); izmenjena arhiva pre početka bila bi prihvaćena. Nisu vezani ni `freeze`, `normalizers` i `manifest_run`.  
  **Fix:** pre rada proveriti zamrznute SHA-256 za E `run`/svih 63 delova, `freeze`, `normalizers` i `manifest_run`; sačuvati ih u svakom R part-u i konačnom izlazu. Trenutni E izvori odgovaraju heševima iz E manifesta.

- **Nastavak može pomešati različite buildove.** Postojeći `run_part_k` se učitava bez validacije ([r_study.py:129](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:129)). Promena R koda, IPOP parametra ili budžeta između dva pokretanja proizvodi mešani `run`.  
  **Fix:** svaki part mora sadržati manifest hash i očekivani task-set; pri nastavku proveriti manifest, tačno 200 zapisa, očekivana semena, `ok`, `calls==12000` i granice događaja.

- **Analiza ne blokira nevalidne vrednosti/zapise.** `area_of` nema E proveru za nefinite vrednosti i vrednosti ispod \(f^\*\) ([r_study.py:152](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:152) naspram [e_analysis.py:36](/Users/danijel/Desktop/gadapt/research/i64/e_analysis.py:36)). Bootstrap proverava samo `se<=0`; NaN bi završio kao `undecided`, ne `blocked` ([r_study.py:204](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:204)). Arhivirani zapisi se ne proveravaju na `ok/calls`, a seed skup samo implicitno preko `len` ([r_study.py:174](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:174)).  
  **Fix:** preneti `gap_fn` i `finite/zero_variance/blocked` logiku iz E; proveriti tačan seed skup, duplikate, task identitet, `ok`, pozive i događaje.

- **`check_repro` nije create-once.** Bez provere prepisuje postojeći fajl ([r_study.py:104](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:104), [r_study.py:116](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:116)); svi `save` pozivi su neatomarni ([r_study.py:47](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:47)).  
  **Fix:** ekskluzivno/atomarno pisanje i odbijanje postojećeg `check_repro`; `run` mora proveriti njegov manifest i hash, ne samo postojanje.

### MISMATCH

- **Nije uvek „rotacija”.** QR konstrukcija daje Haar \(O(d)\), pa Q može imati determinant −1 ([e_common.py:40](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:40)). U stvarnih 21 E ćelija 9 Q matrica ima det<0; `sphere,d=2` ima det≈−1.  
  **Fix:** svuda pisati „ortogonalna transformacija/mešanje, moguće sa refleksijom”. Ne menjati Q na \(SO(d)\), jer tada više ne bi bio E `rot` Q.

- **H64r1 je preširoko nazvana.** c1 proverava samo potpisani ponderisani prosečni efekat zamene dva offseta pri fiksnom Q. Veliki efekti +0,20 i −0,20 mogu se poništiti i dati „equivalent”.  
  **Fix:** formulacija: „agregatni efekat zamene `o_rot` sa `o_shift`, uslovno na 21 fiksni Q, nalazi se u ±0,03”; zabraniti tvrdnju da su pomeraji generalno nematerijalni ili po svakoj ćeliji.

- **`opposite` može biti semantički pogrešan.** Interval c2=[0,02,0,04] daje `opposite` ([r_study.py:210](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:210)), iako pokazuje pozitivan pad — samo manji od 0,05. Numeričke odluke ne mogu protivurečiti intervalu, ali naziv može protivurečiti prirodnom čitanju hipoteze.  
  **Fix:** H64r2 eksplicitno nazvati „pad najmanje 0,05”; koristiti `below_threshold`, ne „suprotna”. Isto za H64r3.

- **H64r3 jeste smislen kao potpisana interakcija**, ali nije apsolutna „osetljivost”. Kontraprimer: c2=−0,01, c3=−0,07 daje c4=0,06 i podršku, iako oba algoritma imaju korist od Q.  
  **Fix:** nazvati je „Q više umanjuje performansu GAdapt-a nego IPOP-a”. Ako se zahteva stvarni pad GAdapt-a, podršku za H64r3 usloviti i podrškom H64r2.

- Spec pominje `r_report.py` ([SPEC:19](/Users/danijel/Desktop/gadapt/research/ITERATION64_R_SPEC.md:19)), ali fajl trenutno ne postoji.

### OK

- **Izolacija objektiva je tačna za svih 21 par.** `CELLS` garantuje `orig=3k`, `shift=3k+1`, `rot=3k+2` ([e_study.py:39](/Users/danijel/Desktop/gadapt/research/i64/e_study.py:39)); `rotm` uzima tačno `Q_rot` i `o_shift`, a ostalo iz shift ćelije ([r_study.py:57](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:57)). `make_objective` koristi baš te članove ([e_common.py:50](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:50)). Ovo važi i za tri funkcije samo sa d=2; `orig` se ne koristi u kontrastima.

- RNG tok je ispravan: `rot` prvo izvlači svoj `o`, zatim A ([e_common.py:37](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:37)); R poziva isti `cell_transform`, pa dobija arhivski Q. `shift` i `rot` imaju zasebne generatore `[64,3,3k+1]` i `[64,3,3k+2]` ([e_study.py:69](/Users/danijel/Desktop/gadapt/research/i64/e_study.py:69)), pa `o_shift` ne troši rot RNG. Za `sphere,d=2`, stvarni Q počinje `[[0.280348,-0.959898],…]`; izvlačenje A pre o dalo bi `[-0.878863,-0.477073,…]`.

- Pri fiksnim postavkama semena su jedinstvena: E završava na 67.062.100, R počinje na 67.063.001; I studija počinje na 68.000.000. Ipak treba tvrdo zahtevati `N_SEEDS==100`, jer trenutni kod nasleđuje `E_SEEDS`, a assertion na [r_study.py:134](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:134) ne otkriva međučelijske kolizije.

- Budžetski wrapper i retry za nove runove korektno zahtevaju tačno B poziva ([r_study.py:65](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:65), [e_common.py:61](/Users/danijel/Desktop/gadapt/research/i64/e_common.py:61)).

- Težine su ispravna, po varijanti renormalizovana verzija E težina: E ima dodatni faktor `/3` za tri varijante ([e_analysis.py:65](/Users/danijel/Desktop/gadapt/research/i64/e_analysis.py:65)), R nema jer svaki \(A_c(v)\) treba da sabira na 1 ([r_study.py:181](/Users/danijel/Desktop/gadapt/research/i64/r_study.py:181)). Beale/Himmelblau/Booth svaki nose 1/9; ostale funkcije po 1/27 po dimenziji. Zato d=2 ukupno nosi 5/9, a d=7 i d=20 po 2/9 — ovo eksplicitno navesti.

- Max-studentizovana porodica nad sva četiri kontrasta i uključivanje zavisnog c4 korektno rešavaju multiplicitet. Ekvivalencija c1 pomoću simultanog 95% intervala je konzervativna, ali validna.

Pre freeze-a spec još treba da definiše \(\tau=(10^{-2},10^{-4},10^{-6})\), jednaku težinu meta, formulu `(B-hit+1)/B`, nepostignutu metu kao 0 i target-specifične rezultate kao isključivo deskriptivne. Takođe treba eksplicitno reći da bootstrap obuhvata samo seed varijaciju: ne obuhvata neizvesnost izbora funkcija, dimenzija, Q ili o i ne dozvoljava generalizaciju na proizvoljne Haar transformacije.