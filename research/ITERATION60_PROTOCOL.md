# ITERATION60: konfirmatorna provera ε-ograničenja u GAdapt-u (PREREGISTRACIJA)

**Status: ZAMRZNUTO 2026-10-24, PRE ijednog I58 rezultata** (I57 u toku; I58 još nije pokrenut). Predlog:
[ITERATION60_PROPOSAL_SR.md](ITERATION60_PROPOSAL_SR.md); recenzija Codex 048 (tekst ispod je njegov predloženi
zamrznuti tekst, sa jednom promenom rasporeda: jedna putanja od 3000 poziva i N = 188, umesto 10.000 i N = 625 — da bi
ε opadao kao u I56 i kao što bi ga korisnik podesio za budžet od 3000; opisni budžet od 10.000 izostavljen).
Motivacija: opisni nalaz I56 (ε-ograničenje na case14 T 0,28 naspram 0,77), koji nije bio hipoteza I56.

## Grane
GAdapt sa patch-om v4 i `constraint_handling="epsilon"` (**G2**) prema istom build-u sa `constraint_handling=None` i
skalarom f + 1000·V (**G0**). I58 ostaje nepromenjen. Podešavanja nasleđuju I58: populacija 32, elitizam 50%, bez
sondiranja (`probe_cost_function=False`) i imigracije. Obe grane: `exit_check="generations"`,
`number_of_generations=188`, budžetski `exit_function`, `timeout=10**6`. GAdapt troši 32 + 16·g poziva (Codex 048,
provereno u kodu), pa se pri 3000 poziva staje po budžetu pre ograničenja generacija (32 + 16·188 = 3040).

## Evaluacija
Svaka grana izvršava jednu putanju od **3000** stvarnih PF poziva. Broje se inicijalizacija, ponovljeni genotipovi i
neuspešni PF; nema prekida pri cilju. ε koristi izvorni raspored iz v4 (20. percentil početne populacije, eksponent 5,
nula na polovini od `number_of_generations`, tj. posle ≈ 32 + 16·94 = 1536 poziva). Posle budžeta: G0 1e300, G2
(0, 1e150) (kao I58).

## Instance i reference
Primarne mreže: case30, case39, case24_ieee_rts; case300 opisno. R = 17; scenariji (0,95; 301), (1,00; 302),
(1,05; 303), spread = 0,1; jedna VG po generatorskoj sabirnici (I58 merilo). Nasleđuju se I58 OPF izuzimanja bez
zamene; bez scenarija neke primarne mreže nema primarnog zaključivanja. Koriste se isključivo I58 reference svih pet
metoda (p = 7, s = 1, 2, po 30.000 poziva); njihov SHA-256 i manifest vezuju se za I60 pre testiranja. I58 test
rezultati ne menjaju reference, instance ni protokol. Cilj: V = 0 i f ≤ L*(1 + 0,01) + 0,01 MW; bez izvodljive
reference samo izvodljivost.

## Semena
10^7·p + 10^5·i + 10^3·R + 100·j + s; i = 0..3 navedenim redom, j = 0..2, **p = 8**, s = 1..15. Seju se svi RNG-ovi;
identičnost početnih G0/G2 populacija proverava se asercijom.

## Analiza
T = min(prvi poziv dostizanja / 3000, 1), uz nedostizanje = 1. θ prosečava T(G2) − T(G0), jednako po mrežama i
preostalim scenarijima. Bootstrap uparenih vektora unutar mreža × scenario: 20.000, seme 60, percentilni 95% interval.
**H60 je podržana samo ako je ceo interval ispod nule.** Ostali ishodi (izvodljivost, najbolji izvodljiv gubitak,
case300) su opisni.

## Pravila i provera
Nasleđuju se I58 pravila grešaka, ponavljanja i osetljivosti, uz potpune G0/G2 parove. Nezavisna provera (I58
proverivač) obuhvata obe grane i sve svedoke cilja; neuspeh blokira zaključak. Arhiviraju se kompletna podešavanja,
kod, okruženje i manifesti; drugi istraživač ponavlja paket ili se navodi ograničenje.

## Budžet i domet
Maksimum: 3 mreže primarno + case300 × 3 scenarija × 15 semena × 2 grane × 3000 ≈ 1,1 milion novih PF poziva. Tvrdnja
se ograničava na ovu konfiguraciju (ε raspored vezan za budžet od 3000) i skup instanci.
