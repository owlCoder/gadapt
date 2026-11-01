# ITERATION43 — dijagnostika „budžet ili operatori“: izveštaj

**22. oktobar 2026.** Protokol: [ITERATION43_PROTOCOL.md](ITERATION43_PROTOCOL.md) (`9821ff1`) sa dodatkom A1, unetim
pre pokretanja. Kod `16c2e95`. Izvršeno je **jedno** pokretanje: 288 pokretanja, 2.880.000 evaluacija, 524 s, svi
pozivi tačno 10.000. Sirovi izlaz je u [results/iteration43/diagnostic.json](results/iteration43/diagnostic.json).
Cena je sintetička, nad stvarnim topohub topologijama i zahtevima. Ovo nije dokaz o stvarnoj infrastrukturi.

## 1. Preregistrovani rezultat: **UNRESOLVED**

| Instanca | Geni | Klasa (B=10000) | Holm p (B=10000) | med r GA-I39 | med r (1+1)-EA | med r GA-default | med r nasumična |
|---|---|---|---|---|---|---|---|
| polska | 66 | MIXED | 1,00 | −0,097 | −0,111 | −0,107 | −0,001 |
| nobel-germany | 121 | MIXED | 0,55 | −0,109 | −0,130 | −0,119 | −0,007 |
| atlanta | 210 | **OPERATOR_DEFICIT** | 0,006 | −0,086 | −0,101 | −0,087 | +0,068 |
| france | 300 | **OPERATOR_DEFICIT** | 0,007 | −0,025 | −0,044 | −0,026 | +0,063 |
| geant | 462 | MIXED | 1,00 | −0,071 | −0,070 | −0,072 | +0,002 |
| germany50 | 662 | **OPERATOR_DEFICIT** | 0,006 | −0,014 | −0,045 | −0,017 | +0,070 |

`r = (f_best − f0)/f0`; negativno je bolje od „sve prve najkraće putanje“.

- **Prag nije dostignut.** Za ukupnu klasu potrebno je ≥ 4/6 instanci, a DEFICIT_OPERATORA je dobio 3/6, pa je rezultat
  UNRESOLVED. Nijedna instanca nije ARTEFAKT_BUDŽETA.
- **Kad (1+1)-EA pobeđuje:** pri B=10000 medijana (1+1)-EA je bolja od GA-I39 na 5/6 instanci (na geant su jednaki).
  Prednost raste sa brojem gena: na germany50 je GA-I39 3,2 puta slabiji.
- **Pri B=360 GA-I39 je značajno bolji** od EA na geant, france i germany50 (Holm p ≈ 0,006). Na france i germany50 to je
  delom artefakt iz §2.
- **Podrazumevani GAdapt nije bolji od I39 konfiguracije:** GA-default je skoro identičan GA-I39 (razlike ≤ 0,01).
  Problem dakle nije u I39 izboru parametara.

## 2. Post-hoc nalaz (nije preregistrovan): validacioni pozivi GAdapt-a

`GA.execute()` → `CommonOptionsValidator._check_cost_function`
([common_options_validator.py:82-89](../gadapt/adapters/validation/common_options_validator.py#L82-L89)) poziva funkciju troška
na vektoru **svih minimuma** i na vektoru **svih maksimuma**, pre nego što pretraga počne. Potvrđeno praćenjem poziva
na sintetičkom grafu: prvi evaluirani vektor ima 0 jedinica, a drugi N jedinica.

- Kod binarnog izbora ruta vektor svih minimuma je **tačno** rešenje „sve prve najkraće putanje“ (`f0`). Omotač budžeta
  (u I39 i u I43) taj poziv broji i beleži kao najbolje rešenje GA-a.
- **Posledica za I43:** GA dobija `f0` besplatno, a EA i nasumična pretraga ne. Pristrasnost ide **u korist GA-a**.
  - Zato su tri oznake DEFICIT_OPERATORA konzervativne.
  - Pri B=360 je medijana `r` GA-a na france i germany50 tačno 0: najbolji je bio validacioni poziv, ne rezultat pretrage.
  - Prednost GA-a pri B=360 na tim instancama je zato artefakt.
- **Posledica za I39 (reinterpretacija, nije ponovo izmereno):** „GA nije popravio trivijalno početno rešenje 1.614.560
  u 11/12 semena“ najverovatnije znači da populacija GA-a **nikad nije dostigla f0**, a da je zabeležena vrednost došla
  iz validacionog poziva. To je jači negativan nalaz o GA-u nego što je I39 izveštaj tvrdio. Originalni I39 podaci su
  izgubljeni, pa ovo ostaje verovatna, a ne dokazana reinterpretacija.
- Za skupe funkcije troška validacija troši **2 stvarne evaluacije** po `execute()`, a za korisnika je nevidljiva.

## 3. Mehanizam (hipoteza iz čitanja koda, NIJE testirana)

Podrazumevano `percentage_of_mutation_decision_variables=20.0`: mutirana jedinka menja oko 20% gena, kod 662 gena oko
132 bita. (1+1)-EA menja u proseku 1 bit. To je u skladu sa nalazom da EA-ova prednost raste sa brojem gena, ali
uzročnost nije pokazana. „Blending“ ukrštanje se na binarnom genu ponaša kao uniformno.

## 4. Zaključak i sledeći korak

- Preregistrovano: UNRESOLVED (3/6 deficit, 3/6 mešovito, 0/6 artefakt budžeta).
- Hipoteza „samo budžet“ nije podržana ni na jednoj instanci.
- Validacioni artefakt menja tumačenje I39 i čini I43 oznake deficita konzervativnim.
- Prema §5 protokola nema ponavljanja sa izmenjenim parametrima. Sledeće pitanje je novo i mora se zasebno
  preregistrovati: **da li intenzitet mutacije (20% gena) objašnjava deficit**, uz isključen validacioni artefakt.
  Dodatno je potrebna prior-art provera, jer je teorija stope mutacije 1/n za binarne EA dobro poznata (novost se ne očekuje).
