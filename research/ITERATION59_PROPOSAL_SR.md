# I59 (PREDLOG): drugi infrastrukturni domen — modularno planiranje kapaciteta telekom mreže

**Status:** predlog 2026-10-24 (Codex 037), pre I56/I58 rezultata. Zasebno preregistrovano proširenje; H58 ostaje
nepromenjena. Svrha: širina dokaza za ugrađeni `constraint_handling` (komisija: „samo jedan domen“).

## Problem
TopoHub v1.5.1 SNDlib topologije (`research/data/topohub_v1.5.1_sndlib/`, SHA256SUMS) sa ORIGINALNIM statičkim
zahtevima d_k (svaki unos tačno jednom; bez simetrizacije). Izgubljena vremenska TGZ je van opsega (ne
rekonstruisati). Odluke: x_e ∈ {0, …, 16} modula po ivici (diskretna mreža vrednosti). Veličina modula
q = max_e L_e^SP / 8, gde je L^SP opterećenje pri rutiranju svakog zahteva leksikografski prvim najkraćim putem
(daje poznato izvodljivo rešenje x^SP ≤ 8). Trošak C(x) = Σ c_e x_e, c_e = 1 + dist_e/1000; f = C/C(x^SP).
**Mreža kapaciteta i trošak su eksplicitne sintetičke pretpostavke planiranja** (arhiva nema module ni cene).

## Evaluacija (deterministička)
Elastični LP rutiranja (višeproizvodni tok, deljiv, kapacitet deljen u oba smera): min V = Σ u_k / Σ d_k uz
d_k − u_k, 0 ≤ u_k ≤ d_k; `scipy.optimize.linprog(method="highs-ds")`, jedna nit, fiksne opcije, tok skaliran sa
q. V ≤ 1e-8 je nula tek posle provere reziduala svedoka ≤ 1e-7. Greška rešavača = neuspela evaluacija. Probno
vreme (Codex 037, nasumični vektori): Polska 8,6 ms, Nobel-Germany 23,1 ms, Nobel-US 19,7 ms po LP-u.

## Instance
Razvoj: Abilene, PDH. Potvrda: Polska, Nobel-Germany, Nobel-US. GÉANT: opisno (skala). Topologije su ranije
korišćene u repozitorijumu (navesti; nove su samo odluke i eksperiment).

## Pitanje i analiza (ogledalo H58)
GAdapt G1 (FR) naspram G0 (f + 1000·V), isti build, iste početne populacije, I58 kontrole izvršavanja. Cilj:
izvodljivo i C ≤ (1 + ε)C*; C* iz MILP-a (`scipy.optimize.milp`/HiGHS) gde je sertifikovan, inače najbolje poznato
uz oznaku. **Izbor budžeta i ε samo na razvojnim instancama** (B ∈ {3000, 10.000, 30.000}, ε ∈ {0,05; 0,10; 0,20}:
najmanji budžet, pa najstroži cilj sa 20–80% dostizanja u svakom razvojnom bloku; potvrda na odvojenim razvojnim
semenima; ako nijedan ne prolazi → razvojni NO-GO), zamrzava se pre potvrde. T = min(prvi pogodak/B, 1); jednake
težine topologija; uparena semena; 20.000 stratifikovanih bootstrap ponavljanja. **H59: θ = E[T_FR − T_kazna] < 0**,
podržana samo ako je 95% interval ispod nule. Svi cenzurisani blokovi se zadržavaju; simulacija snage mora čuvati
cenzuru (pouka iz I56: veštački pomak u blokovima sa T = 1 precenjuje snagu).

## Poredbeni metodi
MILP (sertifikovan optimum ili incumbent + dual bound + gap), relaksacija + deterministično brisanje modula,
multistart brisanje, DE/FR, nasumična pretraga; vreme izvršavanja uz broj evaluacija.

## Najbliži prior art (DOI)
- Khelifi, Saidi, Boudjit 2017, ASTESJ 2(3), 10.25046/aj020339 (GA izbor topologije + LP kapaciteti na SNDlib) —
  DOI postoji, ali Crossref vraća naslov broja časopisa, ne članka (delimično provereno).
- Binh i Ngo 2014, [10.1186/s13673-014-0013-y](https://doi.org/10.1186/s13673-014-0013-y) (modularni troškovi, GA).
- Bauknecht 2021, [10.1145/3449639.3459379](https://doi.org/10.1145/3449639.3459379) (GA, višeslojne mreže).
Doprinos bi bio kontrolisana validacija GAdapt opcije, ne nova metoda planiranja.

## Sledeći koraci
Codex recenzija → zamrzavanje pre bilo kakvog razvojnog merenja → implementacija evaluatora i MILP reference →
razvoj (B, ε) → potvrda.
