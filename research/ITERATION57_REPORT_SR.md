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
- Izvršeno jednom (17:06–18:11, 8 radnika): 300 jedinica (30 instanci × 10 semena) × 7 putanja; svaka putanja tačno
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

Opisno: CMAwM je u proseku brži od GAdapt-a pod obe tehnike; DE se od GAdapt-a ne razlikuje jasno; nasumična
pretraga je sporija. Izbor tehnike (SP / FR) ne menja sliku ni za jedan metod.

## 4. Po blokovima (opisno)
Srednji T po bloku / broj pokretanja sa bar jednim izvodljivim rešenjem (od 40 za case14 i case118, od 20 za case57):

| Blok | GAdapt SP | GAdapt FR | CMAwM SP | CMAwM FR | DE SP | DE FR | Nasumična |
|---|---|---|---|---|---|---|---|
| case14 R=9 | 0,980 / 6 | 0,962 / 10 | 1,000 / 3 | 1,000 / 4 | 1,000 / 7 | 1,000 / 6 | 1,000 / 1 |
| case14 R=17 | 0,714 / 40 | 0,725 / 40 | 0,231 / 39 | 0,233 / 39 | 0,688 / 40 | 0,697 / 40 | 1,000 / 34 |
| case14 R=33 | 0,762 / 40 | 0,811 / 40 | 0,316 / 40 | 0,302 / 40 | 0,872 / 40 | 0,855 / 40 | 0,993 / 36 |
| case57 R=9 | 1,000 / 20 | 1,000 / 20 | 1,000 / 14 | 1,000 / 9 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case57 R=17 | 1,000 / 20 | 1,000 / 20 | 1,000 / 17 | 0,993 / 20 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case57 R=33 | 1,000 / 20 | 0,979 / 20 | 1,000 / 15 | 1,000 / 16 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |
| case118 (svi R) | 1,000 / 1 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 |

Zbirno (bez težina, 300 pokretanja): dostizanje cilja GAdapt 15% / 14% (SP / FR), CMAwM 25% / 25%, DE 18% / 21%,
nasumična 0,3%; bar jedno izvodljivo rešenje GAdapt 49% / 50%, CMAwM 43% / 43%, DE 29% / 29%, nasumična 24%.

Tri jasna obrasca:
1. **Ceo kontrast T potiče sa case14 (R = 17, 33).** Tamo CMAwM dostiže cilj oko 2,5–3× brže (T 0,18–0,38 naspram
   0,58–0,89) i ima nižu medijanu najboljeg izvodljivog gubitka u svakom scenariju (npr. R = 17, scenario 2: 9,028
   naspram 9,204 / 9,323 MW). U ostalih 7 blokova T ≈ 1 za sve metode (neinformativno, kao u I56).
2. **Na case57 GAdapt je jedini metod koji uvek nađe izvodljivo rešenje** (20/20 u svakom bloku, pod obe tehnike);
   CMAwM 9–20/20, DE i nasumična 0/20. Medijana najboljeg izvodljivog gubitka GAdapt-a je niža od CMAwM u 9 od 12
   ćelija scenario × R × CHT (opisno; T ne beleži tu prednost jer cilj nije dostignut; medijane su uslovne na
   pokretanja sa izvodljivim rešenjem, pa poređenje nije upareno).
3. **case118 (77 kontrola): niko** ne nađe izvodljivo rešenje u 3000 poziva (jedno GAdapt SP pokretanje izuzetak).

## 5. Pretnje validnosti i ograničenja
- **Ciljevi potiču iz GAdapt referentnih pokretanja** (I56 `test_ref`). To može ići u korist GAdapt-a (ciljevi
  dostižni putanjom sličnom GAdapt-ovoj); činjenica da je CMAwM ipak brži na case14 zato je konzervativna.
- **SciPy DE pri 3000 poziva:** podrazumevani `popsize=15` množi se brojem promenljivih (case57: 405, case118:
  1155 jedinki po generaciji), pa DE završi samo ~7 odnosno ~2,6 generacija — u praksi je to latinska hiperkocka
  plus nekoliko generacija. Rezultat DE na case57/case118 ne govori o DE pri većem budžetu ili manjoj populaciji;
  konfiguracije su po protokolu „ograničene budžetom“ i nisu podešavane.
- Podrazumevana podešavanja spoljnih metoda; nema L-SHADE / jDE (protokol); 3 mreže, jedna vrsta merila.
- Opisna studija: nijedan obrazac iz §4 nije potvrđen kao hipoteza.

## 6. Nezavisna provera
Codex 049 je napisao sopstveni čitač sirovih zapisa (bez koda analize iz drajvera) i ponovio primarne procene,
tabele po blokovima i provere budžeta/heševa. Rezultat provere: vidi
[codex/049_i57_independent_analysis_codex_answer.md](codex/049_i57_independent_analysis_codex_answer.md).

## 7. Zaključak i posledice
1. Na jedinoj mreži gde su ciljevi dostižni pri 3000 poziva (case14), CMA-ES sa marginom je višestruko brži od
   GAdapt-a; to je u skladu sa I47/I53 (prednost CMA-ES na glatkim AC problemima, učenje korelacija).
2. GAdapt je opisno najpouzdaniji u nalaženju izvodljivog rešenja na srednjoj mreži (case57) — kandidat-nalaz koji
   bi trebalo potvrditi preregistrovano (ishod: verovatnoća izvodljivosti i najbolji izvodljiv gubitak pri fiksnom
   budžetu, a ne T), ne tumačiti kao opšta prednost.
3. I57 daje spoljni kontekst za I56: efekti CHT unutar GAdapt-a (I56) su mali u poređenju sa razlikom između metoda
   na case14; za tezu to znači da se doprinos ne sme predstavljati kao „GAdapt konkurentan CMA-ES“.
4. Pouka za I58/I60 (već zamrznute): blokovi sa T = 1 svuda ne nose informaciju; I58 je zato uveo sveže mreže i
   unapred definisane uslove informativnosti — tumačenje I58 ne sme koristiti I57 ishode.
