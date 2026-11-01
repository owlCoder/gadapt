# Iteracija 5 — potraga za boljom preciznošću GAdapt-a (21. oktobar 2026)

**Status:** završena eksperimentalna iteracija na `owlCoder/gadapt:main`.
**Naučni rezultat:** jasno identifikovana slabost u iskorišćavanju lokalne strukture
petodimenzionog IEEE14 modela. **Nije razvijen niti dokazan nov
globalno optimalan GAdapt algoritam.** Negativni rezultati ostaju sastavni deo izveštaja.

## Urađeno i zašto

Prethodni UCB i upareno nagrađivanje mutacija nisu imali konzistentnu prednost.
Zato je unapred definisana kontrolisana studija postojećih memetičkih algoritama
i lokalnih optimizatora, ne pokušaj da se poznata tehnika proglasi originalnom.
Krasnogor i Smith (2005), DOI 10.1109/TEVC.2005.850260, već su opisali
kombinovanje evolucije i lokalne pretrage, a SLSQP i CMA-ES su standardne metode.

Dodati su:
- `research/ITERATION5_PROTOCOL.md` — metode, semena, fizički budžeti,
  ograničenja, unapred fiksirana primarna poređenja i jasno razdvojena
  kasnija GÉANT provera.
- `research/ieee14_local_refinement.py` — stvarni GAdapt, PYPOWER,
  SLSQP, DE, strogo brojanje fizičkih simulacija, nezavisni pokazatelji
  izvodljivosti i dvostepeni hibrid GAdapt→SLSQP.
- `research/geant_local_refinement.py` — pravi GAdapt sa diskretnom
  koordinatnom lokalnom pretragom, uz 12+32 već pregledane istorijske matrice.
- `research/ieee14_best_known_reference.py` — nezavisno potvrđena
  najbolja ostvarena, ali **ne globalno sertifikovana**, referenca.
- `research/ieee14_cma_es.py` — zasebni pravi CMA-ES kao snažan
  nepristrasno budžetiran referentni metod.
- `research/analyze_ieee14_local_refinement.py`,
  `research/analyze_geant_local_refinement.py`,
  `research/analyze_ieee14_six_method_pilot.py` —
  upareni testovi, intervali, najgori kvantili, Holm-korekcija,
  eksplicitno uključivanje neuspeha.
- Četiri CI workflow-a, provereni sirovi CSV zapisi,
  statistički logovi i SVG grafikoni.

Sve izmene izvršene su direktno na korisnikovom `main`.
Izvorni `bpzoran/gadapt` nije izmenjen.

## IEEE14 — 360 stvarnih AC proračuna po pokretanju

Izvor prvobitnog izvođenja (120 pokretanja, 5 metoda):
https://github.com/owlCoder/gadapt/actions/runs/39576882485

CMA-ES dodatno (24 pokretanja):
https://github.com/owlCoder/gadapt/actions/runs/39578032233

Kompletna 6-metodna statistika uključujući CMA-ES:
https://github.com/owlCoder/gadapt/actions/runs/39578970309

12 unapred fiksiranih semena 100–111, 360 fizičkih poziva PYPOWER
`runpf` po metodi i faktoru opterećenja. Svih 144/144 metoda–seme–opterećenje
pokretanja ima tačno 360 fizičkih evaluacija; svih šest metoda našlo
je izvodljivo rešenje u svakom od 12 pokretanja pri oba opterećenja.
Interval Wilson 95% za 12/12 je [0,7575,1], što **ne potvrđuje
pouzdanost na nivou industrijske eksploatacije**.

| Metod | Medijana gubitaka 100% (MW) | Najgore 100% (MW) | Medijana 110% (MW) | Najgore 110% (MW) |
|---|---:|---:|---:|---:|
| Originalni GAdapt | 14,318710 | 15,010315 | 17,735386 | 18,618137 |
| Affine GAdapt | 14,458830 | 14,940665 | 17,875307 | 18,735743 |
| SLSQP sa višestrukim startovima | **13,497284** | **13,497310** | **16,792139** | **16,792301** |
| GAdapt(180 evaluacija) + SLSQP(180) | 13,497333 | 13,497440 | 16,792250 | 16,792303 |
| SciPy DE | 13,651538 | 13,879374 | 17,529568 | 18,408660 |
| CMA-ES, sigma=0,035 | 13,498865 | 13,501995 | 16,794541 | 16,805509 |

Uparena poređenja sa originalnim GAdapt-om, po faktoru opterećenja:
- SLSQP: pobeda u svih 12/12 pokretanja pri oba faktora,
  egzaktno sign p=0,00048828125, **Holm-korigovano (5 poređenja)
  p=0,00244140625** po faktoru.
- GAdapt+SLSQP: takođe 12/12 pobeda i ista korekcija, ali NIJE
  pokazao superiornost nad samostalnim SLSQP-om.
- CMA-ES: 12/12 pobeda nad GAdapt-om, ista korigovana p-vrednost.
- SciPy DE: 12/12 pobeda pri 100%; 10/12 pri 110%,
  gde je Holm p=0,0771484375, te nema značajnosti u toj porodici.
- Affine varijanta: 4/12 pobeda, nema potvrđene prednosti.

Medijalna uparena razlika SLSQP − GAdapt na 100%:
−0,821401 MW, 95% percentile bootstrap
[−1,029660; −0,598045] MW.
Na 110%: −0,943376 MW,
95% interval [−1,296830; −0,666024] MW.
Ovo je dokaz prednosti *poznatog lokalnog metoda na ovim pet kontrolnih
promenljivih i ovim parametrima*, a **ne dokaz novog doktorskog doprinosa**.

Sekundarno poređenje SLSQP naspram CMA-ES:
SLSQP je imao niži gubitak u 12/12 pokretanja po faktoru,
ali su medijalne razlike samo −0,001611 MW (100%) i −0,002404 MW
(110%). To nije praktični dokaz veće industrijske pouzdanosti
jer je efekat vrlo mali i ista referentna IEEE14 instanca je mnogo puta
istraživana.

## Nezavisno ponovljena fizička provera najboljeg ostvarenog kandidata

https://github.com/owlCoder/gadapt/actions/runs/39577546304

Za svaki faktor, 3600 pravih AC proračuna tokom optimizacije
(2000 DE + 1600 SLSQP), zatim **još jedan eksplicitno evidentiran**
nezavisan `runpf` poziv za potvrdu najboljeg fizički izvodljivog vektora.

| Faktor opterećenja | Najbolja ostvarena i ponovo potvrđena vrednost (MW) |
|---|---:|
| 100% | **13,497263522715254** |
| 110% | **16,791946841097882** |

Kontrolni setpointi (p.u., redosled PYPOWER `case14.gen`):
- 100%: [1,060000000000; 1,037610890960; 1,005427857706;
  1,060000000000; 1,060000000000].
- 110%: [1,060000000000; 1,035674879741; 1,001241617423;
  1,060000000000; 1,060000000000].

Nakon dodatnog proračuna konstatovani su maksimalni reaktivni viškovi
0,068515 MVAr odnosno 0,094946 MVAr, ispod zadate tolerancije
0,1 MVAr, a višak napona i termičkih granica je nula.
Provera je samo po OGRANIČENJIMA u implementaciji: grane
bez objavljenog RATE_A nemaju pretpostavljenu termičku granicu;
nisu modelovani N-1 kontingencije, pun OPF slobodan aktivni dispečing,
podešavanje tapova, diskretni šantovi ni nesigurnost opterećenja.

Rešenja su ostvaren **gornji ograničavajući rezultat**
za minimizaciju gubitaka: postojanje izvodljivog kandidata
dokazuje da optimum ne može imati VEĆE gubitke,
ali NE dokazuje matematičku donju granicu niti globalnu optimalnost.
Medijana SLSQP sa samo 360 poziva je za ~0,000021 MW (100%)
i ~0,000192 MW (110%) iznad najbolje odvojeno ostvarene reference.
To je veoma malo rastojanje prema postignutoj referenci,
ali nije teoretska garancija optimalnosti.

## Druga domena: GÉANT 44 istorijske matrice (već pregledane)

https://github.com/owlCoder/gadapt/actions/runs/39577336565

8 semena 100–107, budžet po metodi 360 pravih evaluacija
SNDlib inženjerskog modela, bez skrivene evaluacije. Trošak iz
anonimizovanih i treningom skaliranih zahteva, NIJE račun stvarnog operatora.
Avgust je već pregledan u iteracijama 3/4: NEMA nezavisnog holdout-a.

| Metod | Medijalni trošak svih 44 perioda | Najlošiji opaženi |
|---|---:|---:|
| Originalni GAdapt | 197526 | 206526 |
| Samostalna koordinatna pretraga | 211479,5 | 263369 |
| GAdapt+koordinatna pretraga | 194553 | 219202 |
| SciPy DE | 201017,5 | 218846 |

Hibrid naspram originalnog GAdapt-a: 5 pobeda i 3 poraza,
egzaktno p=0,7265625 (Holm p=0,7265625).
Medijalna uparena razlika −1862,
bootstrap 95% [−3144, +1065].
Dakle NIJE dokazana superiornost; najlošiji opaženi rezultat hibrida
je gori nego kod originala. Koordinatna pretraga sama za sebe
bila je mnogo manje pouzdana po kvalitetu plana.

## Reproduktivnost i pronađeni kvar

U procesu premeštanja CSV podataka iz potpunih logova u GitHub
JavaScript je konvertovao bool stringove `True`/`False` u
`true`/`false`. Numerička merenja nisu izmenjena, ali
analizator koji očekuje Python tekst nije prepoznavao
izvodljiva rešenja; jedno prolazno CI izvršavanje je čak bilo
zeleno sa praznom petljom i bez statističkih poređenja!
Sve repozitorijumske CSV kopije iz ranijih iteracija
normalizovane su u originalni Python format.
Šestometodni analizator sada **ne dozvoljava**
prazne nezavisne reference, duplirane ključeve, neočekivani
broj redova ili različit fizički budžet.
Kasnije provereno izvršavanje:
https://github.com/owlCoder/gadapt/actions/runs/39578970309
štampalo je sve očekivane metode, oba faktora i uparene testove.
Ovo je važno za naučnu mogućnost nezavisne reprodukcije.

## Sačuvani sirovi podaci i grafikoni u `main`

- `research/results/ieee14_local_refinement_20261021.csv` (120 redova).
- `research/results/ieee14_cma_es_20261021.csv` (24 reda).
- `research/results/ieee14_reference_3600_20261021.csv` (2 verifikovane reference).
- `research/results/geant_local_refinement_20261021.csv` (32 reda).
- `research/figures/ieee14_local_refinement_load100.svg`.
- `research/figures/ieee14_local_refinement_load110.svg`.
- Detaljni originalni GH Actions artefakti sadrže izvorni CSV,
  izvođački log i testove: linkovi iznad.

## Zaključak i precizna sledeća hipoteza

SLSQP pokazuje da petodimenziona IEEE14 formulacija ima lako
iskoristivu lokalnu strukturu, koju GAdapt pri ovom budžetu propušta.
Samo dodavanje SLSQP faze nije nov algoritam i ne daje očiglednu
prednost u odnosu na sam SLSQP. CMA-ES dodatno potvrđuje da
postoji vrlo kvalitetan standardni ne-GA referentni algoritam.

**Ne treba dalje nuditi jednostavan UCB, slepu uparenu evaluaciju ili
prosto dodavanje lokalnog optimizatora kao gotov doktorski rezultat.**
Potrebna je nova hipoteza o tome *kada, kome i koliko* računarskog
budžeta dati za lokalno usavršavanje: prediktor očekivane koristi
uslovljen izvodljivošću, dimenzionalnošću, napretkom i cenom solvera,
sa stabilnim ograničenjem rizika od neuspeha. Ovaj koncept treba
uporediti sa postojećim memetičkim, multimodalnim,
success-history i constraint-aware algoritmima pre tvrdnje o novosti.

Sledeći tvrd test: IEEE118/RTE pod striktno jednakim pravim budžetima,
nove nezavisne vremenske matrice i treća domena, širi pokretački uzorak,
mereni procesorski trošak i domenski AC-OPF algoritmi. Tek tada je
moguće odlučivati o naučnoj originalnosti i generalizaciji.
