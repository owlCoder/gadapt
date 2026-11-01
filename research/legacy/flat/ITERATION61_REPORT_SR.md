# ITERATION61: replikacija H56a — izveštaj (STOP u §5, bez zaključka o H61)

Protokol: [ITERATION61_PROTOCOL.md](ITERATION61_PROTOCOL.md) (zamrznut pre ijednog I58 test rezultata). Kod: [iteration61_replication.py](iteration61_replication.py).
Sirovi izlazi: `research/results/iteration61/` (roster, gate, dev_ref, select_b i manifesti sa heševima).

## 1. Ishod
Lanac je izvršio faze gate → dev_ref → select_b i **stao na unapred zadatom pravilu §5**
(„bez prolaznog B za bilo koju mrežu: STOP, bez proširivanja skupa mreža ili budžeta“). Izlaz `select_b.json.gz`:
`chosen = {}` — nijedna mreža nema B ∈ {3000, 6000, 12000} sa sve četiri razvojne medijane T_B u [0,3; 0,8].
Faze fxt, stopcheck, rehearsal, power, test_ref, test, check i analyse **nisu izvršene**; nijedan test scenario nije otvoren.
**H61 nije ocenjena. Ovo nije negativan rezultat za H56a**: interakcija ostaje nereplikovana, a njen prenos nepoznat.
(STOP je protokolom predviđen i označen kao realan ishod; datum završetka faze: 2026-10-25 02:40, evidentirano naknadno
jer lanac nije beležio u PHD_PROGRESS.)

## 2. Prethodne faze
Gate: prošao na trenutnoj biblioteci (54/54 arhiviranih I56 pokretanja bit-identično). Roster: 6 razvojnih
(case30, case39, case24_ieee_rts × j=0,1), 8 test scenarija, izuzet case30 j=4 (OPF). dev_ref: L* za svih 6 razvojnih
scenarija (npr. case30: 2,159 i 2,482 MW; case39: 40,11 i 45,32; case24: 54,89 i 43,09). select_b: 60/60 pokretanja `ok`, bez ponavljanja.

## 3. Medijane T_B (SP|j0, SP|j1, FR|j0, FR|j1)
| Mreža | B=3000 | B=6000 | B=12000 |
|---|---|---|---|
| case30 | 1 / 1 / 1 / 0,971 | 1 / 0,894 / 1 / 0,486 | 1 / 0,447 / 1 / 0,243 |
| case39 | 1 / 1 / 1 / 1 | 0,501 / 1 / 1 / 1 | 0,251 / 0,704 / 1 / 1 |
| case24_ieee_rts | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 | 0,537 / 1 / 0,549 / 0,951 |

## 4. Opisni uzrok (post hoc, bez posledica za odluku)
Cilj f ≤ 1,01·L* + 0,01 MW je na nekim scenarijima nedostižan u 12.000 poziva (case30 j=0: 0/10 dostizanja u obe grane;
case39 FR j=1: 0/5), a na drugima se dostiže pri vrlo različitim budžetima po scenariju. Zahtev da svih
četiri medijane (po grani i scenariju) upadnu u [0,3; 0,8] uz tri mogućih B je pod ovom heterogenošću retko ispunjiv.
Nijedna promena pravila (veća mreža B, širi prozor, cilj po scenariju) ne sme da se primeni na I61; to bi bila nova studija (§5).

## 5. Posledica za tezu
Primenjuje se grana „I61 STOP“ iz Codex 075: interakcija iz I56 ostaje ograničen lokalni nalaz (case14), nereplikovana;
praktično ubrzanje ugrađenih opcija nije potvrđeno (H58/H60 = N, H59 nedostupno).
