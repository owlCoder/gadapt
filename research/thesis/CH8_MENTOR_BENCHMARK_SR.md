# Poglavlje 8. Replikacija i proširenje mentorovog benchmarka: stabilnost, tačnost i stvarni troškovi

*Nacrt, 28. oktobar 2026. Merodavni su zamrznuti protokoli i generisani izveštaji: `ITERATION64_PROTOCOL.md`, `ITERATION64_S0_REPORT_SR.md`, `ITERATION64_E_SPEC.md` i (kada postoji) `ITERATION64_E_REPORT_SR.md`. Odeljci 8.4 i 8.5 popunjavaju se tek posle završetka studije E i ne sadrže nikakav unapred pretpostavljen ishod.*

## 8.1 Pitanje i poreklo

Mentor je ocenio da GAdapt nadmašuje sve upoređene algoritme osim jednog, ali da je tačniji, i traži da biblioteka bude stabilna i primenljiva u industriji. Ovo poglavlje proverava tu ocenu na njegovom sopstvenom eksperimentu (`bpzoran/gadapt_experiments`, komit `0e388356`): GAdapt sa mutacijom vođenom raznovrsnošću naspram PyGAD slučajne i PyGAD adaptivne mutacije i SciPy diferencijalne evolucije, na devet klasičnih funkcija. Doprinos je replikacija, proširenje i karakterizacija pouzdanosti. Ne tvrdi se nova metoda niti teorema; poređenje adaptivnih mutacija na klasičnim funkcijama ima dugu istoriju (Srinivas i Patnaik 1994, DOI: 10.1109/21.286385; Marsili Libelli i Alba 2000, DOI: 10.1007/s005000000042).

## 8.2 Šta mentorov dizajn omogućava, a šta ne

Mentorov eksperiment zaustavlja svaku konfiguraciju pravilom stagnacije od 20 generacija i meri brzinu u generacijama. Generacija, međutim, nije jedinica troška. Nezavisno brojanje stvarnih poziva funkcije cilja (S0, svih 1.680 pokretanja) pokazalo je da PyGAD u mentorovom kodu po generaciji troši ≈ 2× više poziva od GAdapt-a zbog ponovnih računanja u `best_solution()`, da PyGAD adaptivna mutacija zahteva još 2×, i da DE na 20 dimenzija troši ≈ 36.000 poziva naspram ≈ 19.000 kod GAdapt-a. Poređenje po generacijama zato pristrasno favorizuje DE po brzini i opterećuje PyGAD po preciznosti. Funkcije nisu pomerene ni rotirane, a četiri od devet imaju optimum u ishodištu.

## 8.3 Studija S0: replikacija sa stvarnim brojanjem

S0 pokreće mentorove funkcije bez izmene (jedine intervencije su brojač poziva i seme za SciPy DE), 21 ćeliju (funkcija × dimenzija), četiri originalne konfiguracije i 20 semena. Protokol je zamrznut pre merenja; sve brojke je nezavisno reprodukovala recenzija.

**Zamrznuto pravilo (H64a)** zahteva da GAdapt ima veću ponderisanu ECDF-površinu do 12.000 stvarnih poziva od svakog konkurenta, prema simultanim bootstrap intervalima. Ono je ispunjeno: ΔA = 0,164 (PyGAD random), 0,204 (PyGAD adaptive), 0,047 (DE), sve donje granice > 0. GAdapt je dakle efikasniji u uslovima ovog benchmarka.

**Završna preciznost je složenija slika.** Agregatni medijalni jaz GAdapt-a je manji od svih konkurenata, ali to potiče uglavnom iz dve ćelije (Rastrigin-20 i Griewank-7). Po ćelijama, SciPy DE ima manju završnu grešku u 14 od 21 ćelija (na glatkim funkcijama DE stiže ≈ 10⁻¹⁴, GAdapt ≈ 10⁻⁵–10⁻⁸), dok GAdapt ima veću ECDF-površinu u 17 od 21. Pri jednakih 12.000 poziva odnos GAdapt : DE po medijanama je 10 : 10 (jedna veza). Preciznost nije poređena pri jednakom budžetu u izvornom dizajnu: GAdapt troši u proseku ≈ 10.200, DE ≈ 11.900, PyGAD random ≈ 16.500, PyGAD adaptive ≈ 25.200 poziva.

Zaključak S0 sme biti samo operacionalizovan: veća efikasnost do 12.000 poziva među četiri konfiguracije, na neokrenutim klasičnim funkcijama, sa 20 semena. Ne sme se tvrditi opšta veća preciznost, prednost u većini ćelija, industrijska pouzdanost niti uzročna uloga mutacionog operatora. Obelodanjeno je da su tri od dvadeset semena bila viđena u probnoj seriji pre glavnog pokretanja.

## 8.4 Studija E: pomerene i rotirane funkcije, jednak budžet, jači konkurenti (rezultati čekaju)

E koristi 63 ćelije (21 funkcija/dimenzija × {original, pomereno, pomereno i rotirano}), tačno 12.000 stvarnih poziva po pokretanju, 100 semena, i devet konfiguracija: GAdapt, GAdapt sa opcionim presetom stabilnosti, PyGAD random i adaptive, SciPy DE, CMA-ES, IPOP-CMA-ES, BIPOP-CMA-ES i (1+1)-ES sa restartima. Mere stabilnosti su raspodela greške, prosek najgorih 10% ishoda (CVaR), verovatnoća dostizanja ciljeva i ECDF. Hipoteze su unapred zadate u oba smera: H64a (mentorova tvrdnja, pri jednakom budžetu i rotaciji) i H64b (preset smanjuje CVaR najmanje 20% bez pada uspešnosti većeg od 5 procentnih poena).

*[Rezultati se upisuju iz `ITERATION64_E_REPORT_SR.md` posle analize; nijedan ishod nije pretpostavljen.]*

## 8.5 Infrastrukturna faza (nije zamrznuta)

Faza I64-I proverava iste mere na diskretnom ORPD-u pod jednakim budžetom stvarnih proračuna toka snage. Dok nije zamrznuta i izvršena, poglavlje ne sadrži nikakvu tvrdnju o industrijskoj primeni.

## 8.6 Šta poglavlje doprinosi

Doprinos je u tri stvari: (1) replikacija mentorovog benchmarka sa nezavisnim brojanjem stvarnih poziva i preregistrovanim pravilima odlučivanja, sa obelodanjenim odstupanjima; (2) karakterizacija pouzdanosti (rep raspodele, verovatnoća dostizanja) umesto samo srednje vrednosti i SD-a; (3) proverljiv opcioni preset stabilnosti u biblioteci. Poglavlje ne ustanovljava novu optimizacionu metodu.
