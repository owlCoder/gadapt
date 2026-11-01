# ITERATION46 — ablacija komponenti GAdapt-a: izveštaj

**23. oktobar 2026.** Protokol: [ITERATION46_PROTOCOL.md](ITERATION46_PROTOCOL.md) (`dcb54a1`). Kod `907a124`. Izvršeno je
**jedno** pokretanje: 576 pokretanja, 1645 s, na razvojnim instancama iz I43. Sirovi izlaz je u
[results/iteration46/ablation.json](results/iteration46/ablation.json). Cena je sintetička (kao u I43). Validacioni pozivi
su isključeni.

## 1. Preregistrovani rezultat: **nijedna komponenta nije uzročna; deficit nije objašnjen**

Medijana `r` pri B = 10.000 (negativno je bolje):

| Instanca | A0 GAdapt | A1 turnir | A2 uniformno | A3 elitizam 1 | A4 = A1+A2+A3 | A5 = A4 + 1 gen | TB udžbenički | EA |
|---|---|---|---|---|---|---|---|---|
| polska | −0,103 | −0,115 | −0,109 | **−0,061** | −0,075 | −0,069 | −0,096 | −0,107 |
| nobel-germany | −0,111 | −0,114 | −0,108 | −0,087 | −0,083 | −0,094 | −0,124 | −0,134 |
| atlanta | −0,089 | −0,077 | −0,089 | −0,069 | −0,072 | −0,070 | −0,092 | −0,109 |
| france | −0,024 | −0,021 | −0,028 | −0,009 | +0,001 | +0,001 | −0,036 | −0,041 |
| geant | −0,069 | −0,067 | −0,067 | −0,064 | −0,067 | −0,044 | −0,068 | −0,069 |
| germany50 | −0,012 | −0,010 | −0,010 | −0,005 | −0,008 | −0,002 | −0,022 | −0,045 |

- **Primarno:** A1, A2 i A3 nisu značajno bolji od A0 ni na jednoj instanci (prag je bio ≥ 4/6). Nijedna pojedinačna
  komponenta (selekcija, ukrštanje, elitizam) nije uzročna.
- **A3 (elitizam 1) je lošiji** od A0. Na polska je to značajno (Holm p = 0,009), a na ostalim instancama je trend isti.
  Visok elitizam GAdapt-a (50%) dakle **pomaže** unutar ostatka GAdapt mehanizma.
- **Sekundarno:** A4 je značajno lošiji od TB na 4/6, a A5 na 5/6. Ishod je **NOT_EXPLAINED**: ni kombinacija
  udžbeničkih vrednosti dostupnih kroz postojeće GAdapt opcije ne zatvara razliku prema udžbeničkom GA-u.
- Potvrda (§6) se ne izvršava, jer nijedan krak nije imenovan kao uzrok.

## 2. Eksplorativno (NIJE preregistrovano, jedna instanca i jedno seme): udaljenost evaluacija od najboljeg rešenja
Skripta je [iteration46_exploratory_hamming_probe.py](iteration46_exploratory_hamming_probe.py), a izlaz
[results/iteration46/exploratory_hamming_probe.txt](results/iteration46/exploratory_hamming_probe.txt). Instanca je
france (300 gena), seme 4600, budžet 3000.

| Evaluacije | GAdapt: Hamming do najboljeg (med / p10 / p90), poboljšanja | Udžbenički GA |
|---|---|---|
| 0–300 | 95 / 39 / 145, 13 | 103 / 53 / 151, 13 |
| 300–1000 | 14 / 4 / 40, 8 | 17 / 7 / 46, 16 |
| 1000–3000 | **14 / 5 / 33, 5** | **7 / 3 / 12, 13** |

Udžbenički GA intenzivira pretragu oko najboljeg rešenja: kasne evaluacije su na oko 7 gena od njega, a poboljšanja i
dalje dolaze (iako je potrošio 240 evaluacija na duplikate). GAdapt ostaje na oko 14 gena i retko poboljšava.

**Hipoteza (nije testirana):** mehanizmi koji održavaju raznovrsnost (mutacija vođena raznovrsnošću cene i roditelja,
kolonska raznovrsnost sa najmanje N/5 gena po mutaciji) sprečavaju intenzifikaciju. Na skoro linearnom binarnom
pejzažu to je pogrešan kompromis istraživanja i iskorišćavanja. Ovo je u skladu sa I44 (1 gen u **mutaciji** ne
pomaže, jer udaljenost dolazi i iz ukrštanja raznovrsnih elita) i sa I46 A3.

## 3. Zaključak za program istraživanja
- Deficit GAdapt-a na binarnom izboru ruta je robustan, specifičan za GAdapt i **sistemski**: ne može se ukloniti
  postojećim opcijama.
- Popravka bi zahtevala novi mehanizam intenzifikacije za diskretne promenljive. Takvi mehanizmi su dobro poznati
  (lokalna pretraga i memetički GA, (1+1)-EA, bit-flip 1/n), pa novost za doktorat nije verovatna.
- U skladu sa odgovorima korisnika (PhD prioritet, kontinualni domen), sledeći pravac je **kontinualni infrastrukturni
  problem, za koji je GAdapt dizajniran**: ista strogost (preregistracija, jake kontrole pri istom budžetu, nezavisne
  instance), sa CMA-ES/DE i udžbeničkim real-coded GA-om kao kontrolama.
