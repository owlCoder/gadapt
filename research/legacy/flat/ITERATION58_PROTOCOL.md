# ITERATION58: validacija ugrađenog `constraint_handling` u GAdapt-u na svežim mrežama (PREREGISTRACIJA)

**Status: ZAMRZNUTO 2026-10-24, PRE ijednog I56 test rezultata** (I56 je u fazi probe/snage). Predlog:
[ITERATION58_PROPOSAL_SR.md](ITERATION58_PROPOSAL_SR.md); recenzija Codex 035 (tekst ispod je njegov predloženi
zamrznuti tekst, uz pojašnjenja u zagradama). Izvršava se POSLE I56 i I57 i posle primene patch-a v4 u biblioteku.

## Grane i izbor
I58 proverava integrisani GAdapt (patch v4, `research/patches/constraint_api.patch`) sa unapred fiksiranim
`constraint_handling="feasibility_rules"` (**G1**), prema istom build-u sa `constraint_handling=None` i korisničkim
skalarom f + 1000·V (**G0**). Izbor NE zavisi od I56/I57 ishoda (pravilo iz predloga je zamenjeno). Ostala
podešavanja su jednaka, sa podrazumevanom populacijom 32, bez sondiranja (`probe_cost_function=False`) i imigracije;
zaustavljanje po budžetu (`exit_check="generations"`, `number_of_generations=10**9`, `exit_function`). Arhiviraju se
verzije, kompletna podešavanja i SHA-256 manifest. (Razlike biblioteke od I56: f_ref = medijana |f| početne
populacije, arctan skalar; za FR se selekcija vrši tačnim ključem.)

## Instance
Primarni skup: case30, case39, case24_ieee_rts; case300 je opisni dodatak (bez termičkih ograničenja ispod 9900 MVA).
R = 17; scenariji tačno (0,95; 301), (1,00; 302), (1,05; 303), spread = 0,1. Model nasleđuje I56 merilo, uz JEDNU VG
kontrolu po generatorskoj sabirnici, primenjenu na sve generatore na njoj (case24_ieee_rts: 33 generatora na 11
sabirnica → 11 VG kontrola). OPF neuspeh znači izuzimanje bez zamene, pre optimizacionih pokretanja. Bez preostalog
scenarija neke primarne mreže nema primarnog zaključivanja.

## Kontekst
CMAwM/FR, DE/FR i nasumična pretraga, prema zamrznutim I57 podešavanjima (opisno).

## Semena
seed = 10^7·p + 10^5·i + 10^3·R + 100·j + s; mreže navedenim redom (case30, case39, case24_ieee_rts, case300)
i = 0..3; scenariji j = 0..2; test p = 6, s = 1..15; reference p = 7, s = 1, 2. Seju se svi RNG-ovi; G0/G1 početne
populacije moraju biti identične (asercija u drajveru).

## Evaluacija
Svaka metoda izvršava jednu putanju od 10.000 stvarnih PF poziva; prvih 3000 određuje primarni ishod. Broje se
inicijalizacija, ponavljanja i neuspešni PF; nema prekida pri dostizanju cilja. Primenjuju se I56 pravila grešaka,
ponavljanja, potpunih jedinica i osetljivosti.

## Reference i cilj
Reference obuhvataju svih pet metoda (G0, G1, CMAwM/FR, DE/FR, nasumična), po 30.000 poziva i dva nezavisna semena.
L* i cilj nasleđuju I56 formulu (V = 0 i f ≤ L*(1 + 0,01) + 0,01 MW) i fallback na izvodljivost. Reference se heširaju
pre testiranja.

## Analiza
T = min(prvi poziv dostizanja / 3000, 1), uz T = 1 za nedostizanje. θ je prosek razlika T(G1) − T(G0), jednako po
mrežama i preostalim scenarijima. Upareni vektori resampliraju se unutar mreža × scenario: 20.000 bootstrap uzoraka,
seme 58, percentilni 95% interval. **H58: θ < 0; podržana ako je ceo interval ispod nule.** Ostali ishodi
(budžet 10.000, izvodljivost, najbolji izvodljiv gubitak, kontekst, case300) su opisni.

## Nezavisna provera
Nezavisno implementiran proverivač (bez koda merila) rekonstruiše kontrole, granice, gubitke i sve prekršaje za
vraćena rešenja obe GAdapt grane i za rešenja koja određuju cilj/T. Drugi istraživač ponavlja zamrznuti paket u
čistom okruženju (ako nije moguće, navodi se kao ograničenje).

## Domet tvrdnje
Ako je H58 podržana: „Integrisana FR opcija smanjuje ograničeno vreme do evaluiranog izvodljivog cilja u odnosu na
kaznu 1000 na ovom skupu.“ Nije dokaz opšte superiornosti, industrijske koristi, nove metode niti kvaliteta vraćenog
rešenja (to traži zasebnu uspešnu proveru izlaza).

## Budžet
Planirani maksimum: 9 miliona test + 3,6 miliona referentnih PF poziva, bez provera i ponavljanja.
