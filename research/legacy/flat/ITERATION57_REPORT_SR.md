# ITERATION57: GAdapt naspram spoljnih metoda na istom diskretnom ORPD-u (IZVEŠTAJ)

**Status: IZVEŠTAJ** (2026-10-24). Studija je **opisna** (protokol §Obim): nema konfirmatornih hipoteza, p-vrednosti,
tvrdnji o superiornosti ili ekvivalenciji, ni generalizacije van ovih instanci.

- Protokol: [ITERATION57_PROTOCOL.md](ITERATION57_PROTOCOL.md) (zamrznut `0f0749e`, pre ijednog I56 test rezultata);
  predlog [ITERATION57_PROPOSAL_SR.md](ITERATION57_PROPOSAL_SR.md); recenzije Codex 027 (predlog), 033 (kod).
- Kod: [iteration57_external.py](iteration57_external.py), testovi [test_iteration57_external.py](test_iteration57_external.py);
  merilo i skalari iz I56 ([iteration56_cht_study.py](iteration56_cht_study.py)).
- Sirovi izlazi: `results/iteration56/i57.json.gz`, `i57_analysis.json.gz`, manifest `i57_manifest.json.gz`
  (napisan PRE pokretanja; heš I56 `test_ref` = `3ada162b…`, isti kao u arhivi I56).
- Nezavisna ponovna analiza iz sirovih zapisa: Codex 049 (vidi §6).

## 1. Pitanje
Pri istom budžetu od 3000 AC proračuna, gde je GAdapt (AD-N, pod SP i FR) u odnosu na CMA-ES sa marginom (CMAwM,
Hamano i sar. 2022, [10.1145/3512290.3528827](https://doi.org/10.1145/3512290.3528827)), SciPy DE sa `integrality` i
uniformnu nasumičnu pretragu, na istim I56 test instancama, ciljevima i ishodu T (normalizovan broj poziva do prvog
izvodljivog rešenja na cilju; T = 1 ako cilj nije dostignut)?

## 2. Izvršavanje
- Izvršeno jednom (prema logu lanca u scratchpad-u: 17:06–18:11, komanda `run 8`; vremena nisu u artefaktima): 300 jedinica (30 instanci × 10 semena) × 7 putanja; svaka putanja tačno
  3000 stvarnih `runpf` poziva. Nijedna jedinica izuzeta, nijedna prazna ćelija → primarna analiza dostupna,
  analiza osetljivosti nije bila potrebna.
- Ciljevi su I56 `test_ref` ciljevi, nepromenjeni (potiču iz GAdapt referentnih pokretanja — §5).

## 3. Primarni opisni kontrasti (T(metod) − T(GAdapt), isti CHT)
Jednake težine blokova (mreža × R) i scenarija u bloku; upareni bootstrap celih vektora unutar ćelija, 20.000
ponavljanja, seme 57, 95% percentilni intervali. Negativno = metod brže dostiže cilj od GAdapt-a.

| Kontrast | Procena | 95% interval |
|---|---|---|
| CMAwM − GAdapt, SP | −0,101 | [−0,117; −0,084] |
| CMAwM − GAdapt, FR | −0,105 | [−0,124; −0,086] |
| DE − GAdapt, SP | +0,012 | [−0,005; +0,029] |
| DE − GAdapt, FR | +0,008 | [−0,009; +0,026] |
| Nasumična − GAdapt, SP | +0,060 | [+0,045; +0,075] |
| Nasumična − GAdapt, FR | +0,057 | [+0,042; +0,073] |

Opisno: CMAwM ima niži opaženi srednji T od GAdapt-a pod obe tehnike. Procene DE − GAdapt su +0,012 (SP) i
+0,008 (FR); oba opisna intervala obuhvataju nulu (ekvivalencija nije ispitana). Nasumična pretraga ima viši T.
Znaci šest agregatnih procena isti su pod SP i FR; odsustvo interakcije nije utvrđeno.

## 4. Po blokovima (opisno)
Srednji T po bloku / broj pokretanja sa bar jednim izvodljivim rešenjem (od 40 za case14, od 20 za case57, od 120 za spojeni red case118):

| Blok | GAdapt SP | GAdapt FR | CMAwM SP | CMAwM FR | DE SP | DE FR | Nasumična |
|---|---|---|---|---|---|---|---|
| case14 R=9 | 0,980 / 6 | 0,962 / 10 | 1,000 / 3 | 1,000 / 4 | 1,000 / 7 | 1,000 / 6 | 1,000 / 1 |
| case14 R=17 | 0,714 / 40 | 0,725 / 40 | 0,231 / 39 | 0,233 / 39 | 0,688 / 40 | 0,697 / 40 | 1,000 / 34 |
| case14 R=33 | 0,762 / 40 | 0,811 / 40 | 0,316 / 40 | 0,302 / 40 | 0,872 / 40 | 0,855 / 40 | 0,992 / 36 |
| case57 R=9 | 1,000 / 20 | 1,000 / 20 | 1,000 / 14 | 1,000 / 9 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case57 R=17 | 1,000 / 20 | 1,000 / 20 | 1,000 / 17 | 0,993 / 20 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case57 R=33 | 1,000 / 20 | 0,979 / 20 | 1,000 / 15 | 1,000 / 16 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case118 (svi R) | 1,000 / 1 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |

Zbirno (bez težina, 300 pokretanja): dostizanje cilja GAdapt 15% / 14% (SP / FR), CMAwM 25% / 25%, DE 18% / 21%,
nasumična 0,3%; bar jedno izvodljivo rešenje GAdapt 49% / 50%, CMAwM 43% / 43%, DE 29% / 29%, nasumična 24%.

Tri jasna obrasca:
1. **Najveći doprinos kontrastima T dolazi iz case14 R = 17 i R = 33**; nenulti doprinosi postoje i u case14 R = 9
   i case57 R = 17/33. Na case14 R = 17/33 odnos srednjih T po bloku GAdapt/CMAwM je 2,4–3,1 (po scenarijima T
   0,18–0,38 naspram 0,58–0,89), a CMAwM ima nižu medijanu najboljeg izvodljivog gubitka u svakom scenariju (npr.
   R = 17, scenario 2: CMAwM 9,028 SP / 9,027 FR naspram GAdapt 9,204 SP / 9,323 FR MW); dostizanje cilja 92,5–95% naspram 47,5–60%. DE na R = 17 dostiže cilj često
   (87,5–92,5%), ali kasno (T ≈ 0,69), pa je kontrast DE − GAdapt blizu nule: dostizanje i T opisuju različite
   aspekte. Tačno četiri bloka (case57 R = 9, case118 svi R) imaju T = 1 za sva pokretanja svih konfiguracija; u
   ostalima je dostizanje uglavnom retko (na case57 samo dva dostizanja: CMAwM FR R = 17 na pozivu 2593, GAdapt FR
   R = 33 na 1714).
2. **Na case57 GAdapt nađe izvodljivo rešenje u 10/10 pokretanja u svakoj ćeliji scenario × R × CHT** (60/60 po
   CHT-u); CMAwM 1–10/10 po ćeliji (FR R = 17: 10/10 u oba scenarija), DE i nasumična 0/10. Nijedno GAdapt
   pokretanje nije izvodljivo u početnih 32 evaluacije (prvo izvodljivo na pozivu 183–910), pa izvodljivost ne
   potiče iz inicijalizacije; dekodiranje mreže bez greške (Codex 057). Ipak, raspodela operatora/populacije GAdapt-a
   i CMAwM početak u sredini opsega sa σ = (R−1)/3 su konfundovani sa metodom. Medijana najboljeg izvodljivog gubitka GAdapt-a je niža od CMAwM u 9 od 12
   ćelija scenario × R × CHT (opisno; T ne beleži tu prednost jer cilj nije dostignut; medijane su uslovne na
   pokretanja sa izvodljivim rešenjem, pa poređenje nije upareno).
3. **case118 (77 kontrola): niko** ne nađe izvodljivo rešenje u 3000 poziva (jedno GAdapt SP pokretanje izuzetak).

## 5. Pretnje validnosti i ograničenja
- **Ciljevi potiču samo iz GAdapt referentnih pokretanja** (I56 `test_ref`); smer i veličina mogućeg uticaja na
  poređenje nisu utvrđeni (ciljevi utiču na dostizanje, ne na brojeve izvodljivosti).
- **SciPy DE pri 3000 poziva:** podrazumevani `popsize=15` množi se brojem promenljivih (case57: 405, case118:
  1155 jedinki), pa je pri 3000 poziva case57: 405 inicijalnih evaluacija + 6 punih evolucionih generacija + 165
  kandidata sedme; case118: 1155 inicijalnih + 1 puna generacija + 690 kandidata druge (proveren izvor SciPy
  1.18.1, Codex 057). Rezultat DE na case57/case118 ne govori o DE pri većem budžetu ili manjoj populaciji;
  konfiguracije su po protokolu „ograničene budžetom“ i nisu podešavane.
- Četiri ćelije imaju cilj „samo izvodljivost“ (bez izvodljive reference, I56 §6); referenca L* je najbolje
  poznata, ne optimum; jednak broj PF poziva ne znači jednako vreme izvršavanja ni jednak trud podešavanja.
- Podrazumevana podešavanja spoljnih metoda; nema L-SHADE / jDE (protokol); 3 mreže, jedna vrsta merila.
- Samo dva preostala case57 scenarija (OPF izuzimanja); jaka cenzura (T = 1); bootstrap nesigurnost uslovna na
  fiksne instance i reference; intervali tačkasti; inicijalizacija specifična za konfiguraciju; pretpostavke mreže
  vrednosti i opsega su naše (merilo).
- Opisna studija: nijedan obrazac iz §4 nije potvrđen kao hipoteza.

## 6. Nezavisna provera
Codex 049 je napisao sopstveni čitač sirovih zapisa (bez koda analize iz drajvera):
[codex/049_i57_independent_analysis_codex_answer.md](codex/049_i57_independent_analysis_codex_answer.md).
Svih 6 tačkastih procena se poklapa tačno; intervali (drugi redosled uzorkovanja) odstupaju najviše 0,0003 T.
Potvrđeno: 2100 pokretanja, 300 potpunih jedinica, svako tačno 3000 poziva (ukupno 6,3 miliona), 0 grešaka,
ponavljanja i izuzimanja; T, izvodljivost, dostizanje i svih 30 referenci se nezavisno rekonstruišu; heševi koda i
protokola u manifestu odgovaraju fajlovima; heš I56 `test_ref` isti u izlazu, analizi i manifestu.

## 7. Zaključak i posledice
1. Na case14 R = 17 i R = 33, gde je dostizanje često, CMA-ES sa marginom ima višestruko niži opaženi srednji T od
   GAdapt-a; to je u skladu sa ranijim opisnim nalazima I47/I53 (prednost CMA-ES na glatkim AC problemima; mehanizam
   ovde nije ispitan).
2. Na case57 GAdapt je u ovom uzorku nalazio izvodljivo rešenje u svih 120 pokretanja (CMAwM 91/120, DE i
   nasumična 0) — kandidat-nalaz koji
   bi trebalo potvrditi preregistrovano (ishod: verovatnoća izvodljivosti i najbolji izvodljiv gubitak pri fiksnom
   budžetu, a ne T), ne tumačiti kao opšta prednost.
3. I57 daje spoljni kontekst za I56: primarna interakcija H56a (θ_a ≈ 0,02) je mala u poređenju sa razlikom između
   metoda na case14 (opisni glavni efekat ε u I56 na case14 jeste velik); za tezu to znači da se doprinos ne sme predstavljati kao „GAdapt konkurentan CMA-ES“.
4. Pouka za buduće protokole (I61): blokovi sa T = 1 svuda ne nose informaciju; budžet i rezoluciju birati
   unapred zadatim razvojnim pravilom. Tumačenje već zamrznutih I58/I60 ne koristi I57 ishode.
