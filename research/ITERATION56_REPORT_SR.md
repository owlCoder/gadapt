# ITERATION56: tehnike za ograničenja × samoadaptacija GAdapt-a na diskretnom ORPD-u (IZVEŠTAJ)

**Status: IZVEŠTAJ** (2026-10-24; kostur napisan pre rezultata, brojevi upisani posle analize). Test zaključivanje i sažeci:
`analysis.json.gz`; pokretanja, ponavljanja i tragovi: `test.json.gz`; kalibracija i snaga: razvojni izlazi i
`rehearsal.json.gz`. Tumačenje prati unapred zadata pravila protokola.

- Protokol: [ITERATION56_PROTOCOL.md](ITERATION56_PROTOCOL.md) (zamrznut `3f09eb9`); pojašnjenja P1–P5:
  [ITERATION56_CLARIFICATIONS.md](ITERATION56_CLARIFICATIONS.md).
- Kod: [iteration56_cht_study.py](iteration56_cht_study.py), merilo [iteration56_orpd.py](iteration56_orpd.py),
  testovi [test_iteration56_cht_study.py](test_iteration56_cht_study.py) (9/9). Recenzije: Codex 021–025.
- Sirovi izlazi: [results/iteration56/](results/iteration56/) (`.json.gz`).

## 1. Pitanje i šta je novo
Da li efekat samoadaptivne politike mutacije GAdapt-a na vreme do izvodljivog cilja zavisi od tehnike za
rukovanje ograničenjima (CHT), i menja li se efekat pod statičkom kaznom kad signali adaptacije koji čitaju
vrednost troška dobiju zajednički skalar? Uska novina (H5 §10): ablacija cele adaptivne politike sa istim
operatorima × CHT × rezolucija diskretnih kontrola. Rizik R1 (Mallipeddi 2012): i dalje neproveren (Codex 026).

**Srodni radovi (Codex 032, H5 §12):** Interakcija rukovanja ograničenjima i adaptacije parametara već je teorijski i
empirijski proučavana u evolutivnim strategijama, naročito za CSA i popravku neizvodljivih rešenja (Arnold 2013;
Hellwig i Arnold 2016). Numerički prekršaji ulaze i u adaptaciju istorije uspeha CAL-SHADE-a (Zamuda 2017), dok
Atamna i sar. (2020) analiziraju invarijantnost adaptivnog augmented-Lagrangian pristupa. I56 ispituje užu,
konkretnu intervenciju: promenu numeričkih signala GAdapt-ove politike mutacije uz zadržavanje pravila selekcije,
uključujući transformaciju statičke kazne koja čuva poredak. Doprinos je kontrolisana dijagnostička studija na
diskretnom ORPD-u; prioritet te tačne kombinacije nije dokazan.

## 2. Instance i izvršavanje
- case14 / case57 / case118 (9 / 27 / 77 kontrola), R ∈ {9, 17, 33}; test scenariji 0,90 / 1,00 / 1,10 / 1,15.
- Izuzeto po §2: case57 (1,10) i (1,15) — OPF ne uspeva.
- Izvršeno jednom: test reference 240/240 ok; test 4800/4800 ok (300 jedinica × 16 grana), 0 ponavljanja, 0
  grešaka omotača; nijedna jedinica izuzeta, nijedna prazna ćelija → primarno zaključivanje dostupno, analiza
  osetljivosti nije bila potrebna.
- Bez izvodljive reference (cilj = samo izvodljivost, §6): case14 R = 9 (scenariji 4, 5) i case118 R = 9 (3, 5).

## 3. Kalibracija (razvojni scenariji)
- Razvojne reference: 72/72 ok. Bez izvodljivog i pri 30.000 poziva: case14 R=9 i case118 R=9 (oba scenarija).
- FX-M vektori (a, b, σ), medijana medijana preko 54 razvojna AD-N pokretanja po CHT-u: SP (0,571; 0,111; 0,001),
  AP (0,533; 0,111; 0,001), FR (0,500; 0,111; 0,001), EC (0,533; 0,111; 0,001). **σ = 0,001 je donja granica
  GAdapt-a:** kolonska raznovrsnost na diskretnim mrežama brzo kolabira, pa Gausova mutacija radi sa minimalnim σ
  (na mreži to je pomak od jednog koraka, zbog „mutiraj dok se ne promeni“).
- FX-T izbor (a, b, σ) iz mreže 27 konfiguracija: SP (0,75; 0,2; 0,05), AP (0,5; 0,4; 0,05), FR (0,75; 0,4; 0,05),
  EC (0,75; 0,4; 0,15).
- Proba (360 razvojnih pokretanja) i snaga: simulirana snaga 0,968 ≥ 0,8 → 10 semena po instanci (bez odstupanja).
  **Ograničenje simulacije:** u 4 od 9 razvojnih blokova (case118 svi R, case57 R = 33) nijedna od četiri grane
  probe ne dostiže cilj (T = 1 svuda, d = 0, sd = 0). Simulacija svaki takav blok pretvara u konstantno d = 0,05,
  što θ_a doprinosi 0,0222 bez varijabilnosti. Snaga 0,968 je uslovna na nametnutu alternativu; može precenjivati
  snagu testa i ne utvrđuje snagu ako ti blokovi ostanu degenerisani. Izvršavanje se ne menja (pravilo je zamrznuto).

## 4. Primarni ishod (H56a)
**H56a je podržana prema unapred zadatom pravilu:** θ_a = +0,0205, 95% interval [0,0020; 0,0396], p = 0,03.
Pozitivan znak znači da je razlika „podrazumevana adaptacija − podešena fiksna politika“ u vremenu do cilja
VEĆA (lošija za adaptaciju) pod pravilima izvodljivosti nego pod statičkom kaznom.

**Tumačenje mora biti usko** (opisno, van protokola; slika `results/iteration56/fig56_interaction.png`):
- U 6 od 9 blokova (case57 i case118, sve rezolucije) nijedna od četiri grane kontrasta ne dostiže cilj u 3000
  proračuna (T = 1 svuda, d = 0). Ti blokovi ne nose informaciju; procena je u praksi zasnovana na case14.
- Na case14 R = 17: podešena fiksna politika dostiže cilj u 85% pokretanja pod FR, podrazumevani GAdapt u 40%;
  pod SP 57% naspram 42%. Fiksna politika je bolja pod obe tehnike, ali znatno više pod FR.
- Bez bloka case14 R = 17 (opisna provera osetljivosti, nije deo protokola) procena je 0,012, interval
  [−0,005; 0,029].
- Efekat je mali (≈ 2% budžeta), a donja granica intervala je blizu nule.

Zaključak koji podaci podržavaju: na mreži gde su ciljevi dostižni (case14), podrazumevana samoadaptacija GAdapt-a
pod pravilima izvodljivosti gubi od podešene fiksne politike više nego pod statičkom kaznom. Za veće mreže (case57,
case118) pri budžetu od 3000 proračuna studija nema informaciju.

## 5. Sekundarni ishodi (Holm preko 5)
Nijedna sekundarna procena nije različita od nule (Holm preko pet; `ci` nekorigovani):

| Kontrast | Procena | 95% interval | p | p_holm |
|---|---|---|---|---|
| H56b: signal pod SP (AD-N − AD-C) | +0,0015 | [−0,013; 0,016] | 0,85 | 1,00 |
| AP naspram SP (interakcija) | +0,0093 | [−0,013; 0,031] | 0,40 | 1,00 |
| EC naspram SP (interakcija) | +0,0030 | [−0,019; 0,025] | 0,79 | 1,00 |
| θ_a sa FX-M umesto FX-T | −0,0070 | [−0,025; 0,011] | 0,46 | 1,00 |
| Kodiranje SP naspram SP-T | +0,0035 | [−0,010; 0,016] | 0,60 | 1,00 |

Posebno: **H56b nije podržana** — zamena vrednosti u signalima zajedničkim FR skalarom pod statičkom kaznom ne
menja vreme do cilja, a ni transformacija kazne koja čuva poredak (SP-T). Interakcija iz H56a zato nije
objašnjena putem „vrednost troška u signalu“; verovatniji su put redosleda i sama politika mutacije. Obrasci po blokovima, rangovi na toplotnoj mapi, razdvajanje krivih i tragovi su
OPISNI.

## 6. Opisno (H56c, per-arm, tragovi)
- **H56c:** medijana d po bloku je 0 svuda osim case14 R = 17 (0,12); sa tri mreže i šest degenerisanih blokova
  nema osnove za tvrdnju o rezoluciji.
- **ε-ograničenje (EC) je opisno najbrže** (slika `fig56_mean_T.png`): na case14 R = 17 / 33 srednje T 0,28 / 0,39
  uz podrazumevani GAdapt, naspram 0,77 / 0,82 (FR) i 0,81 / 0,81 (SP); EC je jedina tehnika koja povremeno
  dostiže cilj na case57 (T 0,95–0,99). Udeo dostizanja po grani (sve jedinice): EC 0,20–0,26, AP 0,17–0,24,
  SP 0,11–0,15, FR sličan SP. **Ovo nije bila hipoteza I56** i ne sme se tumačiti konfirmatorno; to je kandidat za
  buduću preregistrovanu proveru (I58 je zamrznut sa FR pre ovih rezultata i ostaje takav).
- Udeo pokretanja koja su ikad našla izvodljivo rešenje je ≈ 0,47–0,51 u svim granama: razlike su u dostizanju
  cilja kvaliteta, ne u izvodljivosti.

## 7. Pretnje validnosti
- Mreže vrednosti, opsezi šantova i scenariji su naše pretpostavke (merilo); termički pritisak slab (9900 MVA).
- Referenca L* je najbolje poznata, ne optimum; ciljevi zavise od nje.
- Tri mreže: nema tvrdnje o „veličini mreže“.
- R1: pun tekst Mallipeddi i sar. 2012 nije dostupan; novina formulisana uslovno.

## 8. Zaključak i posledice za GAdapt
1. Prema preregistrovanom pravilu postoji interakcija tehnike za ograničenja i GAdapt-ove samoadaptacije, ali je
   mala i u praksi zasnovana na jednoj mreži (case14); za case57 i case118 budžet od 3000 proračuna je premali da bi
   studija išta rekla.
2. Mehanizam nije „vrednost troška u signalu“ (H56b nulta, SP-T nulto).
3. Praktično važniji je opisni glavni efekat tehnike: ε-ograničenje višestruko skraćuje vreme do cilja. Za
   biblioteku: `constraint_handling="epsilon"` je već u patch-u v4; preporuka korisnicima čeka konfirmatornu
   proveru (predlog sledeće preregistracije).
4. Za buduće studije: budžete birati tako da blokovi nisu degenerisani (pouka primenjena u I59 izboru (B, ε)).
