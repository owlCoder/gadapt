Čitani su samo navedeni izvori; nijedan I58/I60 rezultat ni log nije otvoren. Nema izmena datoteka. Ispod su dve skice; `{{putanja}}` označava neposredno prepisivanje JSON vrednosti. **Pronađeni su blokirajući propusti u I60.**

## ITERATION58 — ugrađena FR opcija (KOSTUR IZVEŠTAJA)

**Status:** kostur pripremljen bez uvida u rezultate. Merodavan je [zamrznuti protokol](/Users/danijel/Desktop/gadapt/research/ITERATION58_PROTOCOL.md), koji zamenjuje pravilo izbora iz predloga.

### 1. Pitanje, instance i izvršavanje

Da li integrisana FR opcija G1 skraćuje ograničeno vreme do cilja prema G0, sa kaznom f + 1000·V?

> Izbor NE zavisi od I56/I57 ishoda (pravilo iz predloga je zamenjeno).

Primarno: case30, case39, case24_ieee_rts; case300 opisno. R = 17, scenariji 301–303, jedna VG kontrola po generatorskoj sabirnici; 15 semena, p = 6. Kontekst: CMAwM/FR, DE/FR, Random.

> OPF neuspeh znači izuzimanje bez zamene, pre optimizacionih pokretanja. Bez preostalog scenarija neke primarne mreže nema primarnog zaključivanja.

> Seju se svi RNG-ovi; G0/G1 početne populacije moraju biti identične (asercija u drajveru).

> Svaka metoda izvršava jednu putanju od 10.000 stvarnih PF poziva; prvih 3000 određuje primarni ishod. Broje se inicijalizacija, ponavljanja i neuspešni PF; nema prekida pri dostizanju cilja. Primenjuju se I56 pravila grešaka, ponavljanja, potpunih jedinica i osetljivosti.

> Reference obuhvataju svih pet metoda (G0, G1, CMAwM/FR, DE/FR, nasumična), po 30.000 poziva i dva nezavisna semena. L* i cilj nasleđuju I56 formulu (V = 0 i f ≤ L*(1 + 0,01) + 0,01 MW) i fallback na izvodljivost. Reference se heširaju pre testiranja.

### 2. Potpunost i primarni ishod

Sve putanje u tabeli pripadaju `i58_analysis.json.gz`; naziv je izveden iz izvornog koda.

| Ćelija izveštaja | JSON putanja → placeholder |
|---|---|
| Sve jedinice, uključujući case300 | `units` → `{{units}}` |
| Potpune primarne jedinice | `complete_primary` → `{{complete_primary}}` |
| Izuzete primarne jedinice | `excluded` → `{{excluded}}` |
| Prazne ćelije mreža × scenario | `empty_cells` → `{{empty_cells}}` |
| OPF izuzimanja | `excluded_instances` → `{{excluded_instances}}` |
| θ | `H58.estimate` → `{{H58.estimate}}` |
| 95% interval | `H58.ci[0]`, `H58.ci[1]` → `[{{H58.ci[0]}}; {{H58.ci[1]}}]` |
| Podržana | `H58.supported` → `{{H58.supported}}` |
| Osetljivost: θ | `sensitivity.estimate` → `{{sensitivity.estimate}}` |
| Osetljivost: interval | `sensitivity.ci[0]`, `sensitivity.ci[1]` → `[{{sensitivity.ci[0]}}; {{sensitivity.ci[1]}}]` |

Ako je `H58` ili `sensitivity` jednak `null`, upisati „nije izračunato”; ne popunjavati njihove podključeve.

> T = min(prvi poziv dostizanja / 3000, 1), uz T = 1 za nedostizanje. θ je prosek razlika T(G1) − T(G0), jednako po mrežama i preostalim scenarijima. Upareni vektori resampliraju se unutar mreža × scenario: 20.000 bootstrap uzoraka, seme 58, percentilni 95% interval.

> **H58: θ < 0; podržana ako je ceo interval ispod nule.**

Posle uspešnih provera izabrati jednu rečenicu:

- **Gornja granica < 0:** „H58 je podržana. Integrisana FR opcija smanjuje ograničeno vreme do evaluiranog izvodljivog cilja u odnosu na kaznu 1000 na ovom skupu.“
- **Donja granica ≤ 0 ≤ gornja:** „H58 nije podržana: interval obuhvata nulu; rezultat ne dokazuje odsustvo efekta.“
- **Donja granica > 0:** „H58 nije podržana; interval je pozitivan, što označava duže ograničeno vreme G1 prema G0.“
- **`H58=null`:** „Primarni zaključak nije dostupan; razloge pokazuju potpunost jedinica, prazne ćelije i zastupljenost primarnih mreža.“
- **Izuzimanja >5% ili prazna ćelija:** „Aktivirana je analiza osetljivosti sa T = 1 za neuspešna pokretanja; prikazani su primarni i rezultat osetljivosti.“ Prag je iz koda; nazivnik je `complete_primary + len(excluded)`, bez OPF izuzimanja. Ne uvoditi novo pravilo potvrđivanja prema osetljivosti.

### 3. Opisni ishodi

> Ostali ishodi (budžet 10.000, izvodljivost, najbolji izvodljiv gubitak, kontekst, case300) su opisni.

Ponoviti tabelu za svaki ključ `k = "<mreža>|<metoda>"`, metode `G0/G1/CMAwM/DE/Random`.

| Ćelija | JSON putanja → placeholder |
|---|---|
| n | `descriptive[k].runs` → `{{descriptive[k].runs}}` |
| Srednje T, 3000 | `descriptive[k].mean_T3000` → `{{descriptive[k].mean_T3000}}` |
| Srednje T, 10000 | `descriptive[k].mean_T10000` → `{{descriptive[k].mean_T10000}}` |
| Izvodljivost do 10000 | `descriptive[k].feasible` → `{{descriptive[k].feasible}}` |
| Medijana najboljeg izvodljivog gubitka | `descriptive[k].median_best` → `{{descriptive[k].median_best}}` |

### 4. Provera, ograničenja i zaključak

> Nezavisno implementiran proverivač (bez koda merila) rekonstruiše kontrole, granice, gubitke i sve prekršaje za vraćena rešenja obe GAdapt grane i za rešenja koja određuju cilj/T. Drugi istraživač ponavlja zamrznuti paket u čistom okruženju (ako nije moguće, navodi se kao ograničenje).

**STOP/neuspeh provere:** „Zaključivanje je blokirano zbog neuspešne ili nedostajuće nezavisne provere, nepodudarnosti artefakata/manifesta ili početnih populacija.“ Ovaj status nije „H58 nije podržana“.

Provera i nezavisno ponavljanje nemaju ključeve u `analysis`; dokumentovati ih zasebno, bez izmišljanja placeholdera.

> Nije dokaz opšte superiornosti, industrijske koristi, nove metode niti kvaliteta vraćenog rešenja (to traži zasebnu uspešnu proveru izlaza).

## ITERATION60 — ugrađeno ε-ograničenje (KOSTUR IZVEŠTAJA)

**Status:** kostur pripremljen bez uvida u rezultate. Merodavan je [zamrznuti protokol](/Users/danijel/Desktop/gadapt/research/ITERATION60_PROTOCOL.md); opisni budžet 10.000 iz predloga je izostavljen.

### 1. Pitanje i izvršavanje

G2 (`epsilon`) prema G0; iste mreže i scenariji kao I58, nova semena p = 8, 15 parova. Obe grane: populacija 32, elitizam 50%, N = 188, budžetsko zaustavljanje.

> Svaka grana izvršava jednu putanju od **3000** stvarnih PF poziva. Broje se inicijalizacija, ponovljeni genotipovi i neuspešni PF; nema prekida pri cilju. ε koristi izvorni raspored iz v4 (20. percentil početne populacije, eksponent 5, nula na polovini od `number_of_generations`, tj. posle ≈ 32 + 16·94 = 1536 poziva). Posle budžeta: G0 1e300, G2 (0, 1e150) (kao I58).

> Nasleđuju se I58 OPF izuzimanja bez zamene; bez scenarija neke primarne mreže nema primarnog zaključivanja.

> Koriste se isključivo I58 reference svih pet metoda (p = 7, s = 1, 2, po 30.000 poziva); njihov SHA-256 i manifest vezuju se za I60 pre testiranja. I58 test rezultati ne menjaju reference, instance ni protokol. Cilj: V = 0 i f ≤ L*(1 + 0,01) + 0,01 MW; bez izvodljive reference samo izvodljivost.

> Seju se svi RNG-ovi; identičnost početnih G0/G2 populacija proverava se asercijom.

### 2. Potpunost i primarni ishod

Putanje pripadaju `i60_analysis.json.gz`.

| Ćelija | JSON putanja → placeholder |
|---|---|
| Potpuni primarni parovi | `complete` → `{{complete}}` |
| Izuzeti primarni parovi | `excluded` → `{{excluded}}` |
| OPF izuzimanja | `excluded_instances` → `{{excluded_instances}}` |
| θ | `H60.estimate` → `{{H60.estimate}}` |
| 95% interval | `H60.ci[0]`, `H60.ci[1]` → `[{{H60.ci[0]}}; {{H60.ci[1]}}]` |
| Podržana | `H60.supported` → `{{H60.supported}}` |

> T = min(prvi poziv dostizanja / 3000, 1), uz nedostizanje = 1. θ prosečava T(G2) − T(G0), jednako po mrežama i preostalim scenarijima. Bootstrap uparenih vektora unutar mreža × scenario: 20.000, seme 60, percentilni 95% interval.

> **H60 je podržana samo ako je ceo interval ispod nule.**

- **Gornja granica <0:** „H60 je podržana: G2 skraćuje ograničeno vreme do cilja prema G0 na ovom skupu, sa ε rasporedom za budžet 3000.“
- **Interval obuhvata nulu:** „H60 nije podržana; interval obuhvata nulu i ne dokazuje odsustvo efekta.“
- **Donja granica >0:** „H60 nije podržana; interval označava duže ograničeno vreme G2 prema G0.“
- **`H60=null`:** „Primarni zaključak nije izračunat; proveriti zastupljenost mreža i izuzete parove.“
- **Izuzimanja >5%:** „Zaključivanje je blokirano: nasleđena analiza osetljivosti nije implementirana.“
- **STOP/neuspeh provere:** „Zaključivanje je blokirano; statistička potvrda se ne izriče.“

### 3. Opisno, provera i ograničenja

Za svaki `k="<mreža>|<grana>"`, grane `G0/G2`:

| Ćelija | JSON putanja → placeholder |
|---|---|
| n | `descriptive[k].runs` → `{{descriptive[k].runs}}` |
| Srednje T | `descriptive[k].mean_T` → `{{descriptive[k].mean_T}}` |
| Dostizanje prema kodu, T<1 | `descriptive[k].attained` → `{{descriptive[k].attained}}` |
| Izvodljivost | `descriptive[k].feasible` → `{{descriptive[k].feasible}}` |
| Medijana najboljeg izvodljivog gubitka | `descriptive[k].median_best` → `{{descriptive[k].median_best}}` |

`attained` izostavlja dostizanje tačno na pozivu 3000; medijane su uslovne na nađeno izvodljivo rešenje.

> Nasleđuju se I58 pravila grešaka, ponavljanja i osetljivosti, uz potpune G0/G2 parove. Nezavisna provera (I58 proverivač) obuhvata obe grane i sve svedoke cilja; neuspeh blokira zaključak. Arhiviraju se kompletna podešavanja, kod, okruženje i manifesti; drugi istraživač ponavlja paket ili se navodi ograničenje.

## Blokirajući nalazi i granica audita

1. **I60 menja pravilo izuzimanja:** [analiza](/Users/danijel/Desktop/gadapt/research/iteration60_epsilon.py:178) zahteva nula izuzetih parova i nema osetljivost; I58 dozvoljava preostale potpune jedinice uz navedene uslove i aktivira osetljivost iznad 5%/pri praznoj ćeliji.
2. **I60 ne vezuje I58 referentni manifest niti zahteva uspešnu proveru referentnih svedoka:** [test](/Users/danijel/Desktop/gadapt/research/iteration60_epsilon.py:95) beleži heš referenci; [check](/Users/danijel/Desktop/gadapt/research/iteration60_epsilon.py:124) proverava samo I60 test zapise. Heš referenci ne zamenjuje proveru L*.
3. **I60 poređenje manifesta preskače sopstvene podatke:** `i60_sha256`, `i60_protocol_sha256`, `i60_settings` se beleže, ali ih [same_provenance](/Users/danijel/Desktop/gadapt/research/iteration58_validation.py:251) ne poredi.

Nasleđena I56 pravila i implementacija `bootstrap`/`make_target` nisu među dozvoljenim izvorima. Njihovu potpunu usklađenost, uključujući stvarnih 20.000 resampliranja, ovaj audit zato ne potvrđuje.