# ITERATION60: ugrađeno ε-ograničenje GAdapt-a naspram kazne (konfirmatorno) (IZVEŠTAJ)

**Status: IZVEŠTAJ** (2026-10-24). Kostur pisan pre rezultata (Codex 051); brojevi upisani posle analize. Merodavan je
zamrznuti protokol [ITERATION60_PROTOCOL.md](ITERATION60_PROTOCOL.md) (zamrznut `be53181`, pre ijednog I58 rezultata);
opisni budžet od 10.000 iz predloga je izostavljen. Motivacija: opisni nalaz I56 (ε na case14, R = 17: T ≈ 0,28 prema FR ≈ 0,77 i kazni SP ≈ 0,81).

- Kod: [iteration60_epsilon.py](iteration60_epsilon.py) — ispravke pre pokretanja: Codex 051 (`df3f8da`), Codex 054
  (`53ee1ab`), grana konvencije neuspeha u proverivaču (kao I58 D1, `08ac7b6`). Biblioteka: patch v4 (`08a5b75`).
- Sirovi izlazi: `results/iteration56/i60_manifest.json.gz`, `i60_test.json.gz`, `i60_check.json.gz`, `i60_analysis.json.gz`.

## 1. Pitanje i izvršavanje
G2 (`constraint_handling="epsilon"`) prema G0 (f + 1000·V, `constraint_handling=None`); iste mreže, scenariji i
reference kao I58 (reference vezane heševima i I58 manifestom; I58 provera referenci prošla), nova semena p = 8, 15 parova.
Obe grane: populacija 32, elitizam 50%, `number_of_generations=188`, budžetsko zaustavljanje; jedna putanja od 3000 stvarnih
PF poziva; ε po rasporedu v4 (20. percentil početne populacije, eksponent 5, nula posle ≈ 1536 poziva).

Izvršeno jednom (prema logu lanca `chain2.log` u scratchpad-u sesije 66e5645f: test 21:59–22:23, provera 22:23–22:25,
analiza 22:25; komanda sa 8 radnika; vremena nisu u JSON artefaktima). Artefakti potvrđuju 330 pokretanja, 0 ponavljanja. OPF izuzimanje nasleđeno iz I58:
case300 j = 2. Potpuni primarni parovi: **135/135**, izuzeti: 0, prazne ćelije: nema → analiza osetljivosti nije bila
potrebna. Početne populacije G0/G2 identične (asercija).

## 2. Primarni ishod (H60)
> T = min(prvi poziv dostizanja / 3000, 1), uz nedostizanje = 1. θ prosečava T(G2) − T(G0), jednako po mrežama i
> preostalim scenarijima. Bootstrap uparenih vektora unutar mreža × scenario: 20.000, seme 60, percentilni 95% interval.
> **H60 je podržana samo ako je ceo interval ispod nule.**

| θ | 95% interval | Podržana |
|---|---|---|
| **−0,0114** | [−0,0350; +0,0117] | **ne** |

**H60 nije podržana; interval obuhvata nulu i ne dokazuje odsustvo efekta.** Opisna prednost ε iz I56 nije
konfirmatorno potvrđena u I60 na svežim mrežama, uz ugrađenu implementaciju v4 i `number_of_generations=188`. Ovo je
provera prenosa koristi, a ne direktna replikacija konfiguracije I56.

## 3. Opisno (van zaključivanja)
Po ćeliji: srednja razlika d = T(G2) − T(G0), dostizanje cilja (G0 / G2), pokretanja sa izvodljivim rešenjem (G0 / G2), od 15:

| Ćelija | d | dostizanje | izvodljivo |
|---|---|---|---|
| case30, j=0 | 0,000 | 0 / 0 | 0 / 0 (cilj = izvodljivost) |
| case30, j=1 | **+0,114** | 12 / 11 | 15 / 15 |
| case30, j=2 | 0,000 | 0 / 0 | 0 / 0 (cilj = izvodljivost) |
| case39, j=0 | −0,049 | 3 / 5 | 9 / 8 |
| case39, j=1 | −0,059 | 2 / 3 | 12 / 12 |
| case39, j=2 | −0,038 | 6 / 6 | 8 / 10 |
| case24_ieee_rts, j=0 | −0,048 | 1 / 3 | 15 / 15 |
| case24_ieee_rts, j=1 | −0,022 | 0 / 1 | 15 / 15 |
| case24_ieee_rts, j=2 | 0,000 | 0 / 0 | 15 / 15 |

Po mreži (srednji T / dostizanje / izvodljivost / medijana najboljeg izvodljivog gubitka, MW):

| Mreža | G0 | G2 |
|---|---|---|
| case30 | 0,873 / 0,27 / 0,33 / 2,2927 | 0,911 / 0,24 / 0,33 / 2,2929 |
| case39 | 0,945 / 0,24 / 0,64 / 43,92 | 0,896 / 0,31 / 0,67 / 43,87 |
| case24_ieee_rts | 0,995 / 0,02 / 1,00 / 49,47 | 0,972 / 0,09 / 1,00 / 48,85 |
| case300 (opisno) | 1 / 0 / 0 / — | 1 / 0 / 0 / — |

Zapažanja (opisno): znak razlike nije ujednačen — G2 je brži u 5 ćelija case39/case24_ieee_rts, a sporiji na jedinoj ćeliji
case30 sa čestim dostizanjem (+0,114), koja nosi 1/9 težine i umanjuje zbir negativnih doprinosa za oko 53% (+0,0127 naspram −0,0241); 3/9 ćelija je degenerisano
(d = 0 za sve parove; na dve nijedna grana nije našla izvodljivo rešenje). Medijana najboljeg izvodljivog gubitka je pod G2
neznatno niža na case39 i case24_ieee_rts (uslovna na izvodljiva pokretanja, nije upareno poređenje).

## 4. Provera
Nezavisni proverivač (I58, bez koda merila): 562 reda (prvi cilj 53, najbolje izvodljivo 179, vraćena rešenja G0 165 i G2
165), 0 neuspeha, vezano heševima za `i60_test` i `i58_refs`; 44 reda vraćenih rešenja na case300 prošla su granom
konvencije neuspelog PF-a (nekonvergencija nezavisno potvrđena, instrument zabeležio tačno konvenciju; ugrađeno pre I60
pokretanja, kao I58 D1; G0/G2: case300 j = 0 15/6, j = 1 15/8). Prolaz ove grane potvrđuje pravilno evidentiranje
neuspeha, ne izvodljivost vraćenog rešenja. Poreklo (kod, biblioteka, okruženje, podešavanja, reference i I58 manifest referenci) provereno
pri testu i analizi. Ponavljanje paketa od strane drugog istraživača nije urađeno (ograničenje).

## 5. Ograničenja
- Tvrdnja važi samo za ovu konfiguraciju (ε raspored vezan za budžet 3000 preko `number_of_generations=188`) i instance.
- I60 ne testira ε naspram FR direktno; H58 i H60 dele mreže i reference (različita semena) — nisu nezavisne replikacije.
- Bootstrap uslovan na fiksne mreže, scenarije i reference; 3/9 degenerisanih ćelija ne dokazuje jednakost grana.
- Kazna 1000 nepodešena; populacija 32; reference = najbolje poznato (I58), ne optimum.
- T je ograničen na 3000 poziva; retko dostizanje i tri degenerisane ćelije ograničavaju informativnost. Nedostizanje ne
  dokazuje neizvodljivost. Reference imaju 104/110 uspešnih pokretanja; šest CMAwM grešaka zahvata četiri ćelije.
  Izvodljivost u tabelama znači da je izvodljivo rešenje ikada evaluirano, ne nužno vraćeno. Nezavisni proverivač koristi
  isti PYPOWER solver. Kontrast opcija obuhvata i različite skalarne signale adaptacije; ne identifikuje mehanizam koristi.
- Nezavisna ponovna analiza: Codex 071 (θ = −2299/202500 tačno, interval i tabele reprodukovani).

## 6. Zaključak (mapa ishoda, Codex 052)
H60 = **N**. Uz H58 = N: korist ugrađenog FR i ε naspram kazne 1000 nije potvrđena na svežim elektroenergetskim mrežama pri
3000 poziva; obe tačkaste procene su male i negativne (−0,014; −0,011), oba intervala obuhvataju nulu. Opisni I56 ε nalaz
ostaje opisni, vezan za case14. Za biblioteku: `constraint_handling` ostaje opt-in, bez preporuke ε zasnovane na brzini.
H59 određuje da li praktična tvrdnja ostaje ograničena na telekom (N/N/P) ili ubrzanje nije potvrđeno ni u jednoj
naknadnoj studiji (N/N/N). Nijedan ishod ne zamenjuje nezavisnu replikaciju H56 interakcije (I61).
