# Posle I41 — nezavisni audit originalnosti, matematička recenzija i GO/NO-GO

**22. oktobar 2026.** Samo `owlCoder/gadapt:main`; upstream nije diran. **Nijedan novi stvarni eksperiment nije izvršen**:
korišćeni su samo postojeći kod, sintetički property testovi i literatura. Svi DOI-ji ispod su provereni na Crossref-u
(naslov, autori i godina se poklapaju). Gde je pročitan samo sažetak, to je naznačeno.

## 1. Zaključak u pet rečenica

1. **I41 teorema je tačna** (nezavisno proverena; 0 kontraprimera u 2.300 nasumičnih instanci, iscrpno po svim izborima ruta).
2. **I41 nije originalna metoda.** To je trivijalan specijalan slučaj (a) poznatog MIP presolve testa redundantnosti dva reda
   i (b) „totalne dominacije“ saobraćajnih matrica za fiksni skup putanja, primenjene na jedan link.
3. Najjača postojeća konkurentska metoda (Ben-Ameur, Pavón-Mariño, Pióro 2011, Prop. 1) je **strogo jača** od I41:
   uklanja i redove koje I41 zadržava (naš kontraprimer iz §3.3).
4. I41 **ne menja GAdapt genetski algoritam**: ubrzava samo odvojenu MILP referencu; GA fitness ostaje bit-identičan.
5. **NO-GO** za I41 kao centralni doktorski doprinos. Za sam GAdapt preporučujem jednu hipotezu (H1) sa statusom
   *novost nije utvrđena* — GO samo za literaturni gate i jeftin strukturni pretest, **ne** za implementaciju.

## 2. Mapa originalnosti (najbliži prior art)

| Izvor (DOI proveren) | Šta već sadrži | Odnos prema I41 |
|---|---|---|
| Gemander, Chen, Weninger, Gottwald, Gleixner, Martin, *Two-row and two-column mixed-integer presolve using hashing-based pairing methods*, EURO J. Comput. Optim. 8 (2020), [10.1007/s13675-020-00129-6](https://doi.org/10.1007/s13675-020-00129-6) — pun tekst | §3.3, jedn. (17): red je redundantan ako minimum aktivnosti njegovog dela, uz drugi red i granice promenljivih, pokriva desnu stranu | **Obuhvata I41** (slučaj kada su sve promenljive zajedničke, a LP množilac fiksiran na 1) |
| Achterberg, Bixby, Gu, Rothberg, Weninger, *Presolve Reductions in MIP*, INFORMS JoC (2020), [10.1287/ijoc.2018.0857](https://doi.org/10.1287/ijoc.2018.0857) — samo sažetak | Gemander i sar. mu pripisuju ideju redundantnosti dva reda | Verovatno obuhvata I41 (sekcija nije lično pročitana) |
| Ben-Ameur, Pavón-Mariño, Pióro, *On Traffic Domination in Communication Networks*, LNCS 6821 (2011), [10.1007/978-3-642-25575-5_16](https://doi.org/10.1007/978-3-642-25575-5_16) — pun tekst | Def. 1: totalna dominacija za skup putanja i jedno statičko rutiranje; Prop. 1: ako neko ĥ ∈ conv(H) zadovoljava ĥ ≥ h, onda H totalno dominira h | **Najbliži mrežni prior art.** I41 = Def. 1 za jedan link, jedan dominirajući okvir i dve putanje. Prop. 1 po linku je **jača** |
| Pavón-Mariño, García-Manrubia, Aparicio-Pardo, *Multi-hour network planning based on domination between sets of traffic matrices*, Computer Networks 55 (2011), [10.1016/j.comnet.2010.10.013](https://doi.org/10.1016/j.comnet.2010.10.013) — pun tekst | §VII: pre rešavanja multi-hour statičkog modela uklanja dominirane matrice „bez promene skupa dopustivih rešenja i bez suboptimalnosti“ | Isti cilj (egzaktno uklanjanje vremenskih okvira); razlika je samo u tome što I41 radi po linku, a ne po celoj matrici |
| Oriolo, *Domination Between Traffic Matrices*, Math. Oper. Res. 33 (2008), [10.1287/moor.1070.0280](https://doi.org/10.1287/moor.1070.0280) — sažetak | Formalna dominacija saobraćajnih matrica | Teorijska pozadina |
| Hoen, Oertel, Gleixner, Nordström, *Certifying MIP-Based Presolve Reductions for 0–1 ILPs* (2024), [10.1007/978-3-031-60597-0_20](https://doi.org/10.1007/978-3-031-60597-0_20) — metapodaci | Sertifikovani presolve | Slabi tvrdnju o novini sertifikata i egzaktne aritmetike |
| SCIP `cons_linear.c`, `preprocessConstraintPairs` (izvorni kod pročitan) | Dominacija para redova, koeficijent po koeficijent | Slabiji od I41 (ne dozvoljava kompenzaciju među zahtevima) |
| HiGHS `HPresolve.cpp` (izvorni kod pročitan) | Dominirane kolone, paralelni redovi | Nije nađen parni test za neparalelne redove → HiGHS verovatno **ne** nalazi I41 redukcije |

**Ranije citirani radovi su stvarni, ali nisu prior art za I41:**
- Goerigk & Khosravi 2023 ([10.1016/j.ejor.2023.03.019](https://doi.org/10.1016/j.ejor.2023.03.019)) radi aproksimativnu redukciju scenarija u funkciji cilja;
- Zagorowska i sar. 2024 ([10.1002/rnc.7038](https://doi.org/10.1002/rnc.7038)) generiše scenarije za robusno upravljanje;
- Chen & Wu 2026 ([10.2139/ssrn.7428860](https://doi.org/10.2139/ssrn.7428860)) pruning unutar CCG.

**Šta eventualno ostaje (skromno, nije doktorska metoda):**
- primena testa **po (link, vreme)** umesto po celoj matrici — nije nađen rad koji radi baš to, ali to direktno sledi iz obe linije;
- empirijska činjenica da SCIP/HiGHS ove redukcije propuštaju — **još nije izmerena**;
- sertifikacioni pipeline kao inženjerski artefakt.

Pošteno uokvirenje: *„egzaktna, sertifikovana primena poznatih testova redundantnosti dva reda i totalne dominacije
na multi-period modularni dizajn“*.

## 3. Nezavisna matematička recenzija I41

### 3.1 Šta je tačno
Neka je Δ_d = q[s,d] − q[t,d]. Tada `M[e;s,t] = Σ_d min_j Δ_d·a[e,d,j]` jeste minimum razlike `L[e,s](z) − L[e,t](z)`
po `z ∈ {0,1}^D`, jer je izraz separabilan po `z_d`.

Dokaz u [I41 izveštaju](ITERATION41_ALGORITHM_PROOF_AND_RESEARCH_DECISION_SR.md) je ispravan. Zato što je izraz linearan
po svakom `z_d`, isti minimum važi i nad kockom `[0,1]^D`. Posledica: i **LP relaksacija** redukovanog modela je
identična punoj, pa I41 ne menja korensku donju granicu; moguće ubrzanje dolazi samo od manjeg LP-a.

### 3.2 Struktura relacije
U egzaktnoj aritmetici `M` je superaditivan: `M(a,c) ≥ M(a,b) + M(b,c)`. Zato je relacija „s dominira t na linku e“
preuređenje (refleksivno i tranzitivno), a pohlepni algoritam vraća skup njegovih maksimalnih elemenata (antilanac).

U kodu `_certifies` koristi konzervativnu float zaštitu, pa tranzitivnost u retkim skoro-jednakim slučajevima može da
otkaže. Tada kod baca izuzetak („No direct … witness“) umesto da zadrži red. To je bezbedno, ali krhko — sitna
inženjerska napomena, ne greška u dokazu.

### 3.3 Sertifikat je dovoljan, ali NIJE potpun (novi nalaz)
Primer: jedan link, dva zahteva čija ruta 0 koristi link, a ruta 1 ga zaobilazi, i okviri s1=(10,0), s2=(0,10), t=(5,5).
- Za svako `z` važi `L_t(z) ≤ max(L_s1(z), L_s2(z))`, pa je red t suvišan.
- Ipak je `M(s1,t) = M(s2,t) = −5`, pa ga I41 zadržava.

Ovo je tačno slučaj koji hvata Prop. 1 iz Ben-Ameur i sar. 2011, jer je t = ½·s1 + ½·s2. Primer je zaključan testom
`test_pairwise_certificate_is_sufficient_but_not_complete`.

Potpuna (zajednička) redundantnost pita da li postoji z za koje je `L_t(z) > max_{s∈S} L_s(z)`. Za |S| ≥ 2 to je problem
sa dve linearne nejednakosti nad binarnim promenljivima. **Skica (nije potpun dokaz):** redukcija iz PARTITION pokazuje
slabu NP-teškoću. To je u skladu sa opšte poznatom NP-teškoćom provere redundantnosti u celobrojnom programiranju —
dakle ni to nije novo.

### 3.4 Opseg važenja (potvrđen)
Teorema traži:
- tačno dve fiksne, nedeljive putanje po zahtevu;
- isti (neanticipativni) izbor ruta u svim vremenskim okvirima;
- kapacitet linka nezavisan od vremena, sa istom desnom stranom za sve t.

Ne važi za scenario-zavisno rutiranje, deljiv tok sa recourse-om, otkaze linkova ni nelinearne (AC) modele.

### 3.5 Falsifikacioni testovi (sintetički, bez stvarnih podataka)
[test_iteration41_property_falsification.py](test_iteration41_property_falsification.py) sadrži dva Hypothesis testa i
jedan dokumentovani primer:
- **1.500 instanci:** maksimum opterećenja po linku nad zadržanim redovima jednak je maksimumu nad svim redovima, za svako `z ∈ {0,1}^D`;
- **800 instanci:** formula `M` jednaka je brute-force minimumu u racionalnoj aritmetici (`Fraction`);
- primer nepotpunosti iz §3.3.

Rezultat: 3/3 prolaze; postojećih 12 I39/I41 testova i dalje prolazi.

## 4. Da li je I41 doprinos samom GAdapt-u? — Ne.

U I39 GAdapt je imao 272 binarna gena (izbor rute), budžet od **360** evaluacija (populacija 24, oko 15 generacija) i
jeftinu numpy evaluaciju (`ModularCommonPlan.evaluate`). I41 menja samo skup redova MILP reference.

Pošto su vršna opterećenja po linku očuvana, GA fitness bi i sa I41 okvirima bio **identičan**. Uštedeo bi se samo
zanemarljiv numpy račun, a putanja pretrage se ne bi promenila. I41 je, dakle, unapređenje referentnog solvera, ne GA-a.

Empirijski problem samog GAdapt-a koji I39 zaista pokazuje: u **11/12** semena GA nije popravio trivijalno početno rešenje
(1.614.560), a najbolji je 4,08% iznad MILP plana. To može biti posledica premalog budžeta, a ne samo slabosti operatora;
uzrok nije identifikovan.

## 5. Hipoteze za sam GAdapt (najviše dve)

### H1 (preporučena za gate, NE za implementaciju): gray-box partition crossover za troškove dekomponovane po linkovima

**Struktura.** Trošak I39 modela je aditivno dekomponovan: `f(z) = Σ_e g_e(z_{D_e})`. Ovde je D_e skup zahteva čije se
dve putanje razlikuju na linku e; zahtevi koje obe putanje vode kroz e daju konstantu.
- Graf interakcije promenljivih (VIG) spaja d i d' ako dele neki link u D_e.
- **Partition crossover (PX)** razbija promenljive po kojima se roditelji razlikuju na povezane komponente VIG-a i za
  svaku komponentu nezavisno bira bolji roditelj.
- Poznata teorema (Tinós, Whitley, Chicano 2015, [10.1145/2725494.2725497](https://doi.org/10.1145/2725494.2725497);
  Whitley, Chicano, Goldman 2016, [10.1162/EVCO_a_00184](https://doi.org/10.1162/EVCO_a_00184)): PX vraća najboljeg od
  2^k potomaka, gde je k broj komponenti, po ceni linearnoj u k.

**Hipoteza.** Na multi-period modularnim mrežnim modelima, GAdapt sa opt-in PX operatorom postiže manji relativni
razmak do MILP donje granice od legacy GAdapt-a pri **istom broju stvarnih evaluacija**.

**Novost: NIJE utvrđena.** PX je poznat. Eventualna razlika: podfunkcije su ovde visoke arnosti (max po vremenu +
modularna stepenasta cena), van uobičajene k-ograničene pretpostavke. Plitka OpenAlex pretraga nije našla PX primenjen
na dizajn kapaciteta mreža, ali to nije sistematski audit.

**Glavni rizik.** Na gustoj mreži VIG može biti skoro potpun. Tada je k ≈ 1 i PX se svodi na izbor celog roditelja —
H1 pada.

### H2 (NE preporučujem): I41 frontier kao egzaktna redukcija scenarija u GA evaluaciji
Za linearne modele ušteda je trivijalna (vidi §4). Za skupe AC modele (IEEE14/118) monotonost opterećenja ne važi, pa
egzaktna dominacija nema osnov. **NO-GO.**

## 6. Plan prvog falsifikacionog eksperimenta (za H1) — preregistrovati PRE izvršenja

**Faza 0 — strukturni pretest, bez saobraćajnih podataka i bez GA.**
- Na topologijama trajno arhiviranim pod DOI-jem ([topohub v1.5.1, 10.5281/zenodo.19154525](https://doi.org/10.5281/zenodo.19154525),
  SNDlib skup; to su konvertovane topologije, *ne* SHA-identični native fajlovi) generisati iste dve determinističke
  najkraće putanje kao I38.
- Za svaku instancu izračunati VIG i broj PX komponenti k za nasumične parove roditelja koji se razlikuju u 5%, 10% i 20% gena.
- **Kriterijum odbacivanja:** ako je medijana k ≤ 2 (pri 10%) na najmanje 2/3 instanci → **H1 NO-GO**, kraj.
- Budžet: samo grafovski račun, nula optimizacionih i solver poziva.

**Faza 1 — samo ako Faza 0 prođe i postoje stvarni vremenski podaci sa trajnom arhivom.**
- Metode (isti budžet stvarnih evaluacija, uparena semena): legacy GAdapt, GAdapt+PX, samostalni PX hill-climber
  (kontrola da je efekat od GA-a), first-shortest baseline i MILP referenca (dual bound).
- Primarni ishod: relativni razmak do MILP donje granice pri budžetu B.
- Više instanci, Holm korekcija, bez ponavljanja dok ne postane pozitivno.

**Data-gate:** originalni I39 bajtovi su i dalje nedostupni (vidi [PHD_PROGRESS.md](PHD_PROGRESS.md)). Fazu 1 ne pokretati
dok se ne nađe javni, arhivirani skup vremenskih matrica sa zabeleženim SHA-256.

## 7. Šta je dokazano, a šta nije

| Tvrdnja | Status |
|---|---|
| I41 teorema (dva puta, statičko rutiranje, zajednički kapacitet) | **Dokazano** (dokaz + egzaktna provera + property testovi) |
| Identičan skup dopustivih rešenja i identična LP relaksacija | **Dokazano** |
| Sertifikat je potpun (minimalan skup redova) | **Opovrgnuto** (§3.3) |
| I41 je originalna naučna metoda | **Opovrgnuto** (§2) |
| I41 ubrzava stvarni I39 MILP | **Nije testirano** (nema podataka) |
| HiGHS/SCIP ne nalaze ove redukcije | **Nije izmereno** (samo čitanje koda) |
| I41 poboljšava GAdapt | **Ne** (§4) |
| H1 je originalna i korisna | **Nije utvrđeno** — sledi gate |
