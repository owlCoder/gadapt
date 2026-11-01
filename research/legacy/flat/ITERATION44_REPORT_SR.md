# ITERATION44 — mehanizam (intenzitet mutacije): izveštaj

**22. oktobar 2026.** Protokol: [ITERATION44_PROTOCOL.md](ITERATION44_PROTOCOL.md) (`a39e599`) sa dodatkom A1, unetim pre
pokretanja. Kod `4c2b8cf`. Izvršeno je **jedno** pokretanje: 216 pokretanja, 599 s, sve na **novim** instancama
(nekorišćenim u I43). Sirovi izlaz je u [results/iteration44/mechanism.json](results/iteration44/mechanism.json). Cena je
sintetička (kao u I43). Validacioni pozivi GAdapt-a su provereni (vektori svih nula i svih jedinica) i isključeni iz
budžeta i iz najboljeg rešenja u svih 144 GA pokretanja.

Napomena o verziji biblioteke: opt-in ispravke u `gadapt/` (`64b9c82`) unete su dok je ovo pokretanje trajalo, ali posle
učitavanja biblioteke u radne procese. Podrazumevano ponašanje je u svakom slučaju bit-identično (proveren heš celog niza
poziva). Krakovi ovog eksperimenta ne koriste nove opcije, pa izmena ne utiče na rezultat.

## 1. Primarni rezultat: **H-mut OPOVRGNUTA** (0/6)

| Instanca | Geni | med r GA-I39 | med r GA-I39-m1 | Holm p (m1 vs I39) | med r (1+1)-EA |
|---|---|---|---|---|---|
| nobel-us | 91 | −0,087 | −0,081 | 1,00 | −0,095 |
| abilene | 130 | −0,011 | −0,009 | 1,00 | −0,022 |
| ta1 | 326 | −0,023 | +0,007 | 0,097 | −0,060 |
| nobel-eu | 378 | −0,001 | −0,007 | 1,00 | −0,022 |
| india35 | 595 | +0,003 | +0,005 | 1,00 | −0,007 |
| janos-us | 650 | +0,020 | +0,017 | 1,00 | −0,004 |

B = 10.000; `r = (f_best − f0)/f0`, negativno je bolje od „sve prve najkraće putanje“.

- Mutacija sa najviše 1 genom i uniformnim izborom gena **ne poboljšava** GAdapt ni na jednoj instanci (prag je bio ≥ 4/6).
- Na ta1 je m1 čak nešto lošiji, ali bez statističke značajnosti.
- **Hipoteza iz I43 (§3) da preveliki intenzitet mutacije objašnjava deficit je opovrgnuta.** Konfuzija iz A1
  (uniforman izbor gena) ne spašava hipotezu: paket „1 gen + uniforman izbor“ nema nikakav efekat.

## 2. Sekundarno: deficit je **repliciran** bez validacionog artefakta

| Instanca | Holm p GA-I39 vs EA | Holm p GA-I39-m1 vs EA |
|---|---|---|
| nobel-us | 0,42 | 0,34 |
| abilene | **0,007** (EA bolji) | **0,003** (EA bolji) |
| ta1 | **0,007** | **0,003** |
| nobel-eu | **0,007** | **0,005** |
| india35 | **0,007** | **0,004** |
| janos-us | **0,003** | **0,003** |

- (1+1)-EA je značajno bolji od oba GA kraka na **5/6** novih instanci. Zajedno sa I43 to je deficit na 8 od 12
  topologija, a GA nije bolji ni na jednoj pri B=10000.
- **Bez besplatne tačke `f0`, GAdapt na india35 i janos-us (595 i 650 gena) posle 10.000 evaluacija ostaje lošiji od
  rešenja prvih najkraćih putanja** (medijana `r > 0`). (1+1)-EA ga prestiže na svih 6 instanci.
- Ovo je nezavisna, merena podrška reinterpretaciji I39 iz I43 §2: populacija GAdapt-a na ~300+ binarnih gena
  malim budžetom ne dostiže ni trivijalno rešenje.
- Pri B=360 je GAdapt bolji od EA na većini instanci (EA tada počinje od nasumičnog rešenja i još se penje). Prednost se
  gubi do B=2000.

## 3. Zaključak

- Deficit GAdapt-a na binarnom izboru ruta je robustan (2 nezavisna skupa instanci, sa i bez validacionog artefakta).
- **Nije ga izazvao intenzitet mutacije.**
- Otvoreno pitanje: da li je deficit specifičan za GAdapt, ili je **generički** za GA sa populacijom na ovoj klasi
  problema? Na skoro linearnim pseudo-Bulovim funkcijama (1+1)-EA je poznat kao jak (Droste, Jansen, Wegener 2002,
  [10.1016/S0304-3975(01)00182-7](https://doi.org/10.1016/S0304-3975(01)00182-7); Witt 2013,
  [10.1017/S0963548312000600](https://doi.org/10.1017/S0963548312000600)).
- Odgovor traži kontrolu koja do sada **nedostaje u svim eksperimentima**: standardni udžbenički GA pri istom budžetu.
  Bez nje se ne može reći da je GAdapt lošiji od GA-a; može se reći samo da je lošiji od (1+1)-EA.
