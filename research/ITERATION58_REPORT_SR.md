# ITERATION58: ugrađena FR opcija GAdapt-a na svežim elektroenergetskim mrežama (IZVEŠTAJ)

**Status: IZVEŠTAJ** (2026-10-24). Kostur pisan pre rezultata (Codex 051); brojevi upisani posle analize. Merodavan je
zamrznuti protokol [ITERATION58_PROTOCOL.md](ITERATION58_PROTOCOL.md) (zamrznut `3f915db`, pre ijednog I56 test
rezultata), koji zamenjuje pravilo izbora iz predloga.

- Kod: [iteration58_validation.py](iteration58_validation.py) (nepromenjen od zamrzavanja manifesta), dopuna provere
  [iteration58_check_amendment.py](iteration58_check_amendment.py) (odstupanje D1, §5). Biblioteka: patch v4 (`08a5b75`).
- Sirovi izlazi: `results/iteration56/i58_refs.json.gz`, `i58_test.json.gz`, `i58_check_v1.json.gz` (originalna provera),
  `i58_check.json.gz` (dopunjena), `i58_analysis.json.gz`, manifesti `i58_refs_manifest`, `i58_manifest`.

## 1. Pitanje, instance i izvršavanje
Da li integrisana FR opcija G1 (`constraint_handling="feasibility_rules"`) skraćuje ograničeno vreme do cilja prema G0
(skalar f + 1000·V, `constraint_handling=None`)?

Primarno: case30, case39, case24_ieee_rts; case300 opisno. R = 17, scenariji 301–303, jedna VG kontrola po generatorskoj
sabirnici; 15 semena, p = 6. Kontekst: CMAwM/FR, DE/FR, nasumična. Svaka metoda: jedna putanja od 10.000 stvarnih PF
poziva; prvih 3000 određuje primarni ishod. Reference: svih pet metoda, po 30.000 poziva, dva semena (p = 7).

Izvršeno jednom: reference 18:12–19:15, test 19:15–21:47 (8 radnika). OPF izuzimanje: case300 scenario j = 2 (bez
zamene). Jedinice: 165 ukupno; primarnih potpunih **134**; izuzeta 1 primarna jedinica (case30, j = 0, seme 60017006:
CMAwM pokretanje neuspešno i posle ponavljanja → cela uparena jedinica izuzeta, 1/135 = 0,7% < 5% → analiza osetljivosti
nije aktivirana). Prazne ćelije mreža × scenario: nema. Početne populacije G0/G1 identične (asercija prošla).

## 2. Primarni ishod (H58)
> T = min(prvi poziv dostizanja / 3000, 1), uz T = 1 za nedostizanje. θ je prosek razlika T(G1) − T(G0), jednako po
> mrežama i preostalim scenarijima. Bootstrap 20.000, seme 58, percentilni 95% interval. **H58: θ < 0; podržana ako je
> ceo interval ispod nule.**

| θ | 95% interval | Podržana |
|---|---|---|
| **−0,0143** | [−0,0345; +0,0061] | **ne** |

**H58 nije podržana: interval obuhvata nulu; rezultat ne dokazuje odsustvo efekta.** Tačkasta procena je negativna
(G1 brže), ali je nesigurnost veća od procene.

## 3. Opisno (van zaključivanja)
Srednja razlika T(G1) − T(G0) po ćeliji (T3000 / T10000), broj dostizanja do 3000 poziva (G0 / G1 / CMAwM):

| Ćelija | n | d (3000) | d (10.000) | dostizanje ≤ 3000 |
|---|---|---|---|---|
| case30, j=0 | 14 | 0,000 | 0,000 | 0 / 0 / 0 (cilj = izvodljivost; niko izvodljiv) |
| case30, j=1 | 15 | +0,016 | +0,045 | 6 / 5 / 15 |
| case30, j=2 | 15 | 0,000 | 0,000 | 0 / 0 / 0 (cilj = izvodljivost; niko izvodljiv) |
| case39, j=0 | 15 | −0,099 | −0,055 | 5 / 7 / 4 |
| case39, j=1 | 15 | −0,004 | −0,016 | 1 / 1 / 0 |
| case39, j=2 | 15 | −0,023 | +0,025 | 5 / 2 / 0 |
| case24_ieee_rts, j=0 | 15 | 0,000 | −0,040 | 0 / 0 / 6 |
| case24_ieee_rts, j=1 | 15 | −0,018 | −0,015 | 1 / 1 / 3 |
| case24_ieee_rts, j=2 | 15 | 0,000 | +0,017 | 0 / 0 / 4 |

Po mreži (sve ćelije, uključujući izuzetu jedinicu za kontekstne metode): srednji T3000 / T10000 / udeo pokretanja sa
izvodljivim rešenjem do 10.000 / medijana najboljeg izvodljivog gubitka (MW):

| Mreža | G0 | G1 | CMAwM | DE | Nasumična |
|---|---|---|---|---|---|
| case30 | 0,947 / 0,776 / 0,33 / 2,293 | 0,953 / 0,791 / 0,33 / 2,293 | 0,716 / 0,676 / 0,34 / 2,293 | 0,898 / 0,736 / 0,33 / 2,293 | 1 / 1 / 0,33 / 2,429 |
| case39 | 0,971 / 0,611 / 0,96 / 43,87 | 0,929 / 0,595 / 0,91 / 43,71 | 0,970 / 0,791 / 0,62 / 43,57 | 1 / 1 / 0 / — | 1 / 1 / 0 / — |
| case24_ieee_rts | 0,997 / 0,864 / 1 / 48,07 | 0,991 / 0,851 / 1 / 48,03 | 0,903 / 0,527 / 1 / 48,27 | 1 / 1 / 1 / 50,19 | 1 / 1 / 0 / — |
| case300 (opisno) | 1 / 1 / 0 / — | 1 / 1 / 0 / — | 1 / 1 / 0 / — | 1 / 1 / 0 / — | 1 / 1 / 0 / — |

Zapažanja (opisno): (1) **slaba informativnost pri 3000 poziva** — u 4 od 9 primarnih ćelija nijedna GAdapt grana ne
dostiže cilj (d = 0 za sve jedinice), na dve od njih (case30 j = 0, 2) nijedna metoda ni referenca nije našla izvodljivo
rešenje (cilj = izvodljivost); (2) jedini veći opisni pomak u korist G1 je case39 j = 0; (3) CMAwM je i ovde najbrži na
case30 j = 1 i case24_ieee_rts, ali sporiji od GAdapt-a na case39 (dostizanje i izvodljivost); (4) case300 bez ijednog
izvodljivog rešenja bilo koje metode.

## 4. Provera i ponovljivost
Nezavisni proverivač (bez koda merila) rekonstruiše kontrole, granice, gubitke i prekršaje: svi svedoci referenci (L*),
prvog cilja i najboljeg izvodljivog rešenja prošli su u originalnoj proveri; vraćena rešenja G0/G1 — vidi D1. Konačna
(dopunjena) provera: 1008 redova, 0 neuspeha, vezana heševima za `i58_refs` i `i58_test`. Analiza je proverila poreklo
(kod, biblioteka, okruženje, podešavanja) prema manifestima referenci i testa. Ponavljanje paketa u čistom okruženju od
strane drugog istraživača nije urađeno (ograničenje).

## 5. Odstupanje D1 — dopuna pravila nezavisne provere vraćenih izlaza
Posle referentnih i test pokretanja, a pre analize i uvida u H58 ishode, originalna provera odbila je 67 od 374 vraćena
izlaza (G0: 33; G1: 34), sve na opisnoj mreži case300. Kontrole su bile validne, ali tokovi snaga nisu konvergirali.
Instrument i nezavisni proverivač bili su saglasni; pravilu je nedostajala grana za konvenciju neuspeha. D1 prihvata
takav izlaz samo uz nezavisno potvrđenu nekonvergenciju i odgovarajuće vrednosti: G0 = 2f_ref + 1000·10; G1: cilj =
2f_ref, prekršaj = 10, feasible = False. f_ref se nezavisno računa kontinualnim AC OPF-om scenarija (poklapa se sa
instrumentom u svih 11 OPF-validnih scenarija, Codex 067). Pravila za konvergirane izlaze i ostale svedoke ostaju ista;
zaštita red po red dozvoljava samo prelaz „neuspeo vraćeni izlaz → prošao“ (promenjeno tačno 67 redova). Original je
sačuvan kao `i58_check_v1.json.gz`; dopunjena provera beleži heševe i broj promenjenih redova. Podaci i H58 analiza nisu
menjani (case300 nije primarna mreža). Prolaz potvrđuje saglasnost evidentiranja neuspeha, ne izvodljivost vraćenog izlaza.
Recenzija: Codex 067 (RUN). Ista praznina ispravljena je u I60 proverivaču pre ijednog I60 pokretanja.

## 6. Ograničenja
- Nije dokaz opšte superiornosti, industrijske koristi, nove metode niti kvaliteta vraćenog rešenja.
- Slaba informativnost pri 3000 poziva (4/9 degenerisanih ćelija); budžet nije biran razvojnim pravilom (pouka unesena u
  I61 protokol pre ovih rezultata).
- Ciljevi iz referenci svih pet metoda (30.000 poziva, dva semena) — najbolje poznato, ne optimum.
- Konfiguracija: kazna 1000 (nepodešena), populacija 32, podrazumevana podešavanja GAdapt-a.

## 7. Zaključak (prema mapi ishoda, Codex 052)
H58 = **N** (validno završena studija bez ispunjenog uslova potvrde). Praktična korist ugrađenog FR naspram kazne 1000
nije potvrđena na svežim elektroenergetskim mrežama pri 3000 poziva; procena je mala i negativna (−0,014), interval
obuhvata nulu. Za biblioteku: `constraint_handling` ostaje opt-in; README ne daje preporuku FR zasnovanu na brzini za ovaj
domen. Konačna centralna tvrdnja teze zavisi i od H60 i H59 (mapa ishoda).
