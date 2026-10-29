# Poglavlje 8. Replikacija i proširenje mentorovog benchmarka: stabilnost, tačnost i stvarni troškovi

*Nacrt, 29. oktobar 2026. Merodavni su zamrznuti protokoli i generisani izveštaji: `ITERATION64_PROTOCOL.md`, `ITERATION64_S0_REPORT_SR.md`, `ITERATION64_E_SPEC.md`/`_REPORT_SR.md`, `ITERATION64_E2_SPEC.md`/`_REPORT_SR.md`. Odeljak 8.5 (infrastruktura) se popunjava tek posle završetka I64-I.*

## 8.1 Pitanje i poreklo

Mentor je ocenio da GAdapt nadmašuje sve upoređene algoritme osim jednog, ali da je tačniji, i traži da biblioteka bude stabilna i primenljiva u industriji. Ovo poglavlje proverava tu ocenu na njegovom sopstvenom eksperimentu (`bpzoran/gadapt_experiments`, komit `0e388356`): GAdapt sa mutacijom vođenom raznovrsnošću naspram PyGAD slučajne i PyGAD adaptivne mutacije i SciPy diferencijalne evolucije, na devet klasičnih funkcija. Doprinos je replikacija, proširenje i karakterizacija pouzdanosti. Ne tvrdi se nova metoda niti teorema; poređenje adaptivnih mutacija na klasičnim funkcijama ima dugu istoriju (Srinivas i Patnaik 1994, DOI: 10.1109/21.286385; Marsili Libelli i Alba 2000, DOI: 10.1007/s005000000042).

## 8.2 Šta mentorov dizajn omogućava, a šta ne

Mentorov eksperiment zaustavlja svaku konfiguraciju pravilom stagnacije od 20 generacija i meri brzinu u generacijama. Generacija, međutim, nije jedinica troška. Nezavisno brojanje stvarnih poziva funkcije cilja (S0, svih 1.680 pokretanja) pokazalo je da PyGAD u mentorovom kodu po generaciji troši ≈ 2× više poziva od GAdapt-a zbog ponovnih računanja u `best_solution()`, da PyGAD adaptivna mutacija zahteva još 2×, i da DE na 20 dimenzija troši ≈ 36.000 poziva naspram ≈ 19.000 kod GAdapt-a. Poređenje po generacijama zato pristrasno favorizuje DE po brzini i opterećuje PyGAD po preciznosti. Funkcije nisu pomerene ni rotirane, a četiri od devet imaju optimum u ishodištu.

## 8.3 Studija S0: replikacija sa stvarnim brojanjem

S0 pokreće mentorove funkcije bez izmene (jedine intervencije su brojač poziva i seme za SciPy DE), 21 ćeliju (funkcija × dimenzija), četiri originalne konfiguracije i 20 semena. Protokol je zamrznut pre merenja; sve brojke je nezavisno reprodukovala recenzija.

**Zamrznuto pravilo (H64a)** zahteva da GAdapt ima veću ponderisanu ECDF-površinu do 12.000 stvarnih poziva od svakog konkurenta, prema simultanim bootstrap intervalima. Ono je ispunjeno: ΔA = 0,164 (PyGAD random), 0,204 (PyGAD adaptive), 0,047 (DE), sve donje granice > 0. GAdapt je dakle efikasniji u uslovima ovog benchmarka.

**Završna preciznost je složenija slika.** Agregatni medijalni jaz GAdapt-a je manji od svih konkurenata, ali to potiče uglavnom iz dve ćelije (Rastrigin-20 i Griewank-7). Po ćelijama, SciPy DE ima manju završnu grešku u 14 od 21 ćelija (na glatkim funkcijama DE stiže ≈ 10⁻¹⁴, GAdapt ≈ 10⁻⁵–10⁻⁸), dok GAdapt ima veću ECDF-površinu u 17 od 21. Pri jednakih 12.000 poziva odnos GAdapt : DE po medijanama je 10 : 10 (jedna veza). Preciznost nije poređena pri jednakom budžetu u izvornom dizajnu: GAdapt troši u proseku ≈ 10.200, DE ≈ 11.900, PyGAD random ≈ 16.500, PyGAD adaptive ≈ 25.200 poziva.

Zaključak S0 sme biti samo operacionalizovan: veća efikasnost do 12.000 poziva među četiri konfiguracije, na neokrenutim klasičnim funkcijama, sa 20 semena. Ne sme se tvrditi opšta veća preciznost, prednost u većini ćelija, industrijska pouzdanost niti uzročna uloga mutacionog operatora. Obelodanjeno je da su tri od dvadeset semena bila viđena u probnoj seriji pre glavnog pokretanja.

## 8.4 Studija E: pomerene i rotirane funkcije, jednak budžet, jači konkurenti

E koristi 63 ćelije (21 funkcija/dimenzija × {original, pomereno, pomereno i rotirano}), tačno 12.000 stvarnih poziva po pokretanju, 100 semena i devet konfiguracija: GAdapt, GAdapt sa opcionim presetom stabilnosti, PyGAD random i adaptive, SciPy DE, CMA-ES, IPOP-CMA-ES, BIPOP-CMA-ES i (1+1)-ES sa restartima. Zamrznute hipoteze su H64a (mentorova tvrdnja pri jednakom budžetu i rotaciji) i H64b (preset smanjuje CVaR najmanje 20% bez pada uspešnosti većeg od 5 procentnih poena). Svi brojevi dolaze iz generisanog izveštaja `ITERATION64_E_REPORT_SR.md`.

**H64a po zamrznutom pravilu: suprotan ishod.** Tri CMA varijante (CMA, IPOP, BIPOP) imaju dokazano veću ECDF-površinu od GAdapt-a (ΔA između −0,097 i −0,089, simultani intervali potpuno negativni). GAdapt je dokazano efikasniji od oba PyGAD-a, od DE-a i od (1+1)-ES. Naknadno (post hoc, bez statusa potvrde): obrazac „GAdapt nadmašuje sve osim CMA porodice“ liči na mentorov opis, ali grupisanje CMA varijanti u jedan algoritam nije bilo unapred zadato i ne potvrđuje H64a.

**Presudna zavisnost od rotacije.** GAdapt-ov rep raspodele (CVaR₀,₉ normalizovanog gubitka) iznosi 0,0033 na originalnim i pomerenim funkcijama, što je najbolje od svih devet konfiguracija, ali 0,0386 pod rotacijom, gde CMA porodica ima oko 0,019. ECDF-površina GAdapt-a pada sa 0,63 na 0,52, dok je CMA porodice oko 0,70 u sve tri varijante. Medijana jaza raste za red veličine (0,0013 na 0,014). Agregatni CVaR GAdapt-a (0,0117) je najniži od svih zato što većina ćelija nije okrenuta. Pomereno i rotirano koriste različite pomeraje, pa razlika među varijantama nije izolovan efekat rotacije. Ne sme se tvrditi da je krosover uzrok.

**H64b: nije podržana.** Preset ne menja CVaR (0,0117 naspram 0,0121); nema dokaza da stabilizuje GAdapt.

## 8.4b Studija E2: opcioni diferencijalni krosover (negativan preregistrovan rezultat)

Da bi se proverilo da li koordinatni krosover objašnjava rotacijski jaz, u biblioteku je dodat opcioni `crossover="differential"` (roditelj plus skalirana razlika dva člana populacije, svi parametri zajedno; podrazumevano ponašanje bit-identično, proveren heš niza poziva). Operator je rotaciono ekvivarijantan samo kao neograničen korak predloga; refleksija na granice, diskretizacija i mutacioni operatori ostaju koordinatni. E2 je zamrznut pre merenja i koristi iste ćelije i semena kao E, uparene sa arhiviranim zapisima (arhivirani E tragovi GAdapt-a reprodukovani su bit-tačno, 126 od 126).

Ishod (jedna simultana porodica od pet kontrasta): **opcija ne zatvara jaz**. Pod rotacijom ΔA(D − M) = −0,036 (interval od −0,047 do −0,025), a CVaR se pogoršava; na osno-poravnatim ćelijama ΔA = −0,042; prema IPOP-u ΔA = −0,18. H64e1 i H64e3 su suprotni, H64e2 neodlučena. Opcija ostaje u biblioteci dokumentovana, podrazumevano isključena i bez preporuke; nije ponavljana sa drugim parametrima.

## 8.4c Studija E3: hibrid GAdapt → CMA-ES (industrijski recept)

Pošto ni opcioni krosover ni jednokratno učenje koordinata nisu pomogli, testiran je uobičajeni recept „globalna pretraga, pa lokalno doterivanje“: GAdapt troši prvih 30% budžeta (udeo izabran na razvoju među 0,3/0,5/0,7), zatim CMA-ES startuje iz najboljeg rešenja sa malim korakom. Hibridi su poznati (npr. Krasnogor i Smith 2005); ovo je empirijska provera, ne nova metoda, i hibrid nije GAdapt sam. Isti 63 ćelije i semena kao E, uparene sa arhiviranim zapisima.

Zamrznuta pravila daju mešan ishod: **H64g1 podržana** (pod rotacijom ΔA = +0,103, CVaR se smanjuje više od 20%), **H64g2 suprotno** (na osno-poravnatim ćelijama rep je 1,8× veći od GAdapt-M, iznad tolerisanih 1,5×, uz ΔA = +0,065), **H64g3 neodlučeno** (neinferiornost prema IPOP-u pod rotacijom: −0,043, interval [−0,052; −0,035] seče granicu −0,05). Opisno, u proseku tri varijante hibrid ima najniži CVaR (0,0070 naspram 0,0117 za GAdapt-M i 0,0142 za IPOP) i najnižu medijanu jaza (0,0029), uz ECDF-površinu 0,751 (IPOP 0,770, GAdapt-M 0,673). Slika je konzistentna sa tim da GAdapt doprinosi pouzdanom globalnom istraživanju, a CMA brzim lokalnim usavršavanjem na spregnutim problemima.

## 8.5 Infrastrukturna faza (nije zamrznuta)

Faza I64-I proverava iste mere na diskretnom ORPD-u pod jednakim budžetom stvarnih proračuna toka snage. Dok nije zamrznuta i izvršena, poglavlje ne sadrži nikakvu tvrdnju o industrijskoj primeni.

## 8.6 Šta poglavlje doprinosi

Doprinos je u tri stvari: (1) replikacija mentorovog benchmarka sa nezavisnim brojanjem stvarnih poziva i preregistrovanim pravilima odlučivanja, sa obelodanjenim odstupanjima; (2) karakterizacija pouzdanosti (rep raspodele, verovatnoća dostizanja) umesto samo srednje vrednosti i SD-a; (3) proverljiv opcioni preset stabilnosti u biblioteci. Poglavlje ne ustanovljava novu optimizacionu metodu.
