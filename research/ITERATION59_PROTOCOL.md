# ITERATION59: modularno planiranje kapaciteta telekom mreže — FR naspram kazne u GAdapt-u (PREREGISTRACIJA)

**Status: ZAMRZNUTO 2026-10-24, pre ikakvog razvojnog merenja** (i pre I56/I58 rezultata). Predlog:
[ITERATION59_PROPOSAL_SR.md](ITERATION59_PROPOSAL_SR.md); recenzija Codex 039 (tekst ispod je njegov predloženi
zamrznuti tekst). Arhiviraju se kod, podešavanja, verzije i SHA-256 manifest. I56–I58 ishodi ne menjaju izbor.
Izvršava se posle primene patch-a v4 u biblioteku.

## Grane i izbor
G1: integrisani GAdapt / `constraint_handling="feasibility_rules"`; G0: isti build, `constraint_handling=None`, cilj
f + 1000·V. Nasleđuju se I58 kontrole izvršavanja, populacija 32, isključeno sondiranje i imigracija. Početne
populacije su identične (asercija); bez ubacivanja SP/MILP rešenja.

## Instance
TopoHub v1.5.1 SNDlib (`research/data/topohub_v1.5.1_sndlib/`, manifest SHA256SUMS potvrđen). Razvoj: Abilene
(12/15/132 čvorova/ivica/zahteva), PDH (11/34/24). Potvrda: Polska (12/18/66), Nobel-Germany (17/26/121), Nobel-US
(14/21/91). GÉANT nije deo H59. Ranija izloženost topologijama i LP probe (Codex 037/039) se navode. Samo statički
zahtevi; izgubljena vremenska TGZ je van opsega.

## Kontekst
MILP i SP rešenje. Ostali predloženi poredbeni metodi zahtevaju zasebno zamrznuta podešavanja (nisu deo I59).

## Semena
seed = 59000000 + 100000·p + 1000·i + s; i = 0..5 redom (Abilene, PDH, Polska, Nobel-Germany, Nobel-US, GÉANT).
p = 0: izbor, 10 parova; p = 1: razvojna validacija, 10 novih parova; p = 2: potvrda, 15 parova; s = 1..10,
odnosno 1..15. Seju se svi RNG-ovi; bootstrap seme 59.

## Evaluacija
Sortirati numeričke ID-jeve i kanonske ivice (šema: `nodes[].id`, `edges[].{source,target,dist}`,
`graph.demands[source][target]`, ključevi u cele brojeve; svaki unos zahteva tačno jednom, suprotni smerovi ostaju
zasebni). SP = minimalan broj skokova, zatim leksikografski najmanji niz numeričkih ID-jeva. q = max(L_sp)/8,
x_sp = ceil(L_sp/q), x ∈ {0, …, 16}, c = 1 + dist/1000, f = C/C_sp.

Sa h = d/q, nenegativnim tokovima y i manjkom u:
B y_k = (h_k − u_k)(e_s − e_t);  Σ_k (y_{k,ij} + y_{k,ji}) ≤ x_e;  0 ≤ u_k ≤ h_k;  V = Σ u_k / Σ h_k.

`linprog(method="highs-ds")`: jedna nit, presolve uključen, Devex, primalna/dualna tolerancija 1e-8, limit 30 s.
Verzije: Python 3.14.3, SciPy 1.18.1, NumPy 2.5.4, HiGHS ugrađen u SciPy 1.18.1 (Codex: 1.12.0; zabeležiti tačno).

Svaki uspešan LP mora zadovoljiti elastične jednačine, kapacitete i granice do 1e-7. V ≤ 1e-8 postaje nula samo ako
tok zadovoljava i PUNE zahteve, na svim čvorovima, do 1e-7. Broji se svaki poziv, uključujući inicijalizaciju,
duplikate i neuspehe; bez keširanja i ranog prekida. Trajna greška posle jednog ponavljanja istim semenom sprečava
primarni zaključak.

## Reference i cilj
MILP koristi iste tokove i kapacitete, bez manjka; samo x je celobrojan. Limit 3600 s po instanci, jedna nit,
relativni i apsolutni gap nula. Nezavisno se proverava incumbent. Razvojne reference prethode razvoju; potvrdne
slede posle zamrzavanja (B, ε), pre potvrdnih putanja.

Cilj: V = 0 i C ≤ (1 + ε)C*. **Bez sertifikovanog optimuma na bilo kojoj potrebnoj instanci: nema H59 zaključka**;
granice ostaju opisne. Zahteva se i (1 + ε)C* < C_sp; inače se cilj označava trivijalnim, bez zamene instance ili
ponovnog podešavanja.

## Razvojni izbor
Putanje do 30.000 poziva. Iz prefiksa se bira najmanji B ∈ {3000, 10.000, 30.000}, zatim najmanji
ε ∈ {0,05; 0,10; 0,20}, sa zbirnim G0/G1 dostizanjem 20–80% na SVAKOJ razvojnoj mreži. Izabrani par mora proći isti
uslov na novim validacionim semenima. Neuspeh znači NO-GO; nema ponovnog izbora.

## Analiza
T = min(prvi pogodak/B, 1); nedostizanje daje 1. Jednake težine mreža; upareni bootstrap unutar mreža, 20.000
ponavljanja, percentilni 95% interval. **H59: θ = E[T_G1 − T_G0] < 0, podržana samo intervalom potpuno ispod nule.**
Potpuno cenzurisani blokovi se zadržavaju.

## Nezavisna provera i domet
Nezavisan proverivač rekonstruiše trošak, granice i tokove za vraćena rešenja i svedoke koji određuju cilj/T.
Zaključak važi samo za ove tri mreže i kaznu 1000.

## Budžet
LP 12–22 ms po pozivu (9 probnih). Potvrda G0/G1 ≈ 1,3 / 4,4 / 13,3 CPU-h za tri budžeta; razvoj 1,2 miliona + 40B
poziva; ukupno sa potvrdom i najviše 5 MILP sati ≈ 9–35 CPU-h (praktična rezerva ×2).
