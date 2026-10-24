**Predlog treba doraditi pre zamrzavanja.** Pregled je bio read-only; fajlovi nisu menjani, razvojna optimizaciona pokretanja nisu izvršavana.

Potvrđeni su svi brojevi iz 037, redom čvorovi/ivice/zahtevi: Abilene **12/15/132**, PDH **11/34/24**, Polska **12/18/66**, Nobel-Germany **17/26/121**, Nobel-US **14/21/91**, GÉANT **22/36/462**. Svih 27 JSON fajlova odgovara manifestu. Šema je `nodes[].id`, `edges[].{source,target,dist}`, `graph.demands[source][target]`; ključeve zahteva konvertovati u celobrojne ID-jeve. Abilene i GÉANT imaju zasebne suprotne smerove; svaki unos ostaje jednom.

`q` iz SP nije leakage: to je unapred definisana transformacija poznatog saobraćaja, ali znači sintetički, instancno skaliran problem. `f=C/Csp` je prihvatljivo; ne opravdava tvrdnju o univerzalnoj pravičnosti kazne 1000.

**Blokade:** neodređen fallback za optimum, neprecizan razvojni izbor i semena, nepotpuna definicija reziduala i trivijalnog cilja. Mali prosečni manjak i dobar rezidual *elastičnog* sistema ne dokazuju zadovoljavanje punih zahteva.

Veličine modela, sa jednom uklonjenom jednačinom očuvanja po zahtevu:

| Instanca | LP promenljive | MILP promenljive, od toga celobrojne | Redovi |
|---|---:|---:|---:|
| Polska | 2442 | 2394; 18 | 744 |
| Nobel-Germany | 6413 | 6318; 26 | 1962 |
| Nobel-US | 3913 | 3843; 21 | 1204 |

Ova veličina **ne garantuje sertifikat za 1 h**; MILP nije pokretan. SciPy omogućava vremenski limit i izveštava incumbent, dualnu granicu i gap; podrazumevani relativni gap nije nula. [Dokumentacija](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html).

Sledeći tekst je predlog za zamrzavanje, sa konzervativnim pravilom bez primarnog fallback-a.

## ITERATION59 — protokol

**Status:** zamrznuti pre razvoja; arhivirati kod, podešavanja, verzije i SHA-256 manifest. I56–I58 ishodi ne menjaju izbor.

### Grane i izbor

G1: integrisani GAdapt/FR; G0: isti build, `constraint_handling=None`, cilj `f+1000V`. Naslediti I58 kontrole izvršavanja, populaciju 32, isključeno sondiranje i imigraciju. Početne populacije su identične, proverene asercijom; bez ubacivanja SP/MILP rešenja.

### Instance

Razvoj: Abilene, PDH. Potvrda: Polska, Nobel-Germany, Nobel-US. GÉANT nije deo H59. Ranija izloženost topologijama i LP smoke provere eksplicitno se navode.

### Kontekst

MILP i SP. Ostali predloženi baselineovi zahtevaju zasebno zamrznuta operativna podešavanja.

### Semena

`seed=59000000+100000p+1000i+s`; `i=0..5` prema prethodno navedenom redosledu. `p=0`: izbor, deset parova; `p=1`: razvojna validacija, deset novih parova; `p=2`: potvrda, petnaest parova. `s=1..10`, odnosno `1..15`. Seju se svi RNG-ovi; bootstrap seme 59.

### Evaluacija

Sortirati numeričke ID-jeve i kanonske ivice. SP znači minimalan broj skokova, zatim leksikografski najmanji niz numeričkih ID-jeva. `q=max(Lsp)/8`, `xsp=ceil(Lsp/q)`, `x∈{0,…,16}`, `c=1+dist/1000`, `f=C/Csp`.

Sa `h=d/q`, nenegativnim tokovima `y` i manjkom `u`:

\[
By_k=(h_k-u_k)(e_s-e_t),\quad
\sum_k(y_{k,ij}+y_{k,ji})\le x_e,\quad
0\le u_k\le h_k;\qquad V=\frac{\sum u_k}{\sum h_k}.
\]

`highs-ds`: jedna nit, presolve uključen, Devex, primalna/dualna tolerancija `1e-8`, limit 30 s. Pinovati Python 3.14.3, SciPy 1.18.1, NumPy 2.5.4, HiGHS 1.12.0.

Svaki uspešan LP mora zadovoljiti elastične jednačine, kapacitete i granice do `1e-7`. `V≤1e-8` postaje nula samo ako tok zadovoljava i **pune zahteve**, na svim čvorovima, do `1e-7`. Brojati svaki poziv, uključujući inicijalizaciju, duplikate i neuspehe; bez keširanja i ranog prekida. Trajna greška posle jednog ponavljanja istim semenom sprečava primarni zaključak.

### Reference i cilj

MILP koristi iste tokove i kapacitete, bez manjka; samo `x` je celobrojan. Limit 3600 s po instanci, jedna nit, relativni i apsolutni gap nula. Nezavisno proveriti incumbent. Razvojne reference prethode razvoju; potvrdne slede posle zamrzavanja `B,ε`, pre potvrdnih putanja.

Cilj: `V=0` i `C≤(1+ε)C*`. Bez sertifikovanog optimuma na bilo kojoj potrebnoj instanci: nema H59 zaključka; granice ostaju opisne. Zahtevati i `(1+ε)C*<Csp`; inače cilj označiti trivijalnim, bez zamene instance ili ponovnog podešavanja.

### Razvojni izbor

Izvršiti putanje do 30.000 poziva. Iz prefiksa birati najmanji `B∈{3000,10000,30000}`, zatim najmanji `ε∈{0,05;0,10;0,20}`, sa zbirnim G0/G1 dostizanjem 20–80% na **svakoj** razvojnoj mreži. Izabrani par mora proći isti uslov na novim validacionim semenima. Neuspeh znači NO-GO; nema ponovnog izbora.

### Analiza

`T=min(prvi pogodak/B,1)`; nedostizanje daje 1. Jednake težine mreža; upareni bootstrap unutar mreža, 20.000 ponavljanja, percentilni 95% interval. H59: `θ=E[TG1−TG0]<0`, podržana samo intervalom potpuno ispod nule. Zadržati potpuno cenzurisane blokove.

### Nezavisna provera i domet

Nezavisan proverivač rekonstruiše trošak, granice i tokove za vraćena rešenja i svedoke koji određuju cilj/T. Zaključak važi samo za ove tri mreže i kaznu 1000.

### Budžet

Devet LP provera dalo je **12–22 ms/pozivu**. Potvrda G0/G1: približno **1,3/4,4/13,3 CPU-h** za tri budžeta. Razvoj zahteva `1,2 miliona+40B` poziva; uz nemerenu pretpostavku 8–25 ms, ukupno sa potvrdom i najviše pet MILP sati: **9–35 CPU-h**, bez overhead-a i ponavljanja. Praktična rezerva: približno dvostruko.