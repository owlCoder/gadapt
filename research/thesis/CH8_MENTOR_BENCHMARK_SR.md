# Poglavlje 8. Replikacija i proširenje mentorovog benchmarka: stabilnost, tačnost i stvarni troškovi

*Nacrt, 29. oktobar 2026. Merodavni su zamrznuti protokoli i generisani izveštaji: `ITERATION64_PROTOCOL.md`, `ITERATION64_S0_REPORT_SR.md`, `ITERATION64_E_SPEC.md`/`_REPORT_SR.md`, `ITERATION64_E2_SPEC.md`/`_REPORT_SR.md`. Odeljak 8.5 (infrastruktura) se popunjava tek posle završetka I64-I.*

## 8.1 Pitanje i poreklo

Mentor je ocenio da GAdapt nadmašuje sve upoređene algoritme osim jednog, ali da je tačniji, i traži da biblioteka bude stabilna i primenljiva u industriji. Ovo poglavlje proverava tu ocenu na njegovom sopstvenom eksperimentu (`bpzoran/gadapt_experiments`, komit `0e388356`): GAdapt sa mutacijom vođenom raznovrsnošću naspram PyGAD slučajne i PyGAD adaptivne mutacije i SciPy diferencijalne evolucije, na devet klasičnih funkcija. Doprinos je replikacija, proširenje i karakterizacija pouzdanosti. Ne tvrdi se nova metoda niti teorema; poređenje adaptivnih mutacija na klasičnim funkcijama ima dugu istoriju (Srinivas i Patnaik 1994, DOI: 10.1109/21.286385; Marsili Libelli i Alba 2000, DOI: 10.1007/s005000000042).

## 8.2 Šta mentorov dizajn omogućava, a šta ne

Mentorov eksperiment zaustavlja svaku konfiguraciju pravilom stagnacije od 20 generacija i meri brzinu u generacijama. Generacija, međutim, nije jedinica troška. Nezavisno brojanje stvarnih poziva (S0, svih 1.680 pokretanja) beleži približno 32/64/96 poziva po generaciji za GAdapt/PyGAD random/PyGAD adaptive (uz ponovna računanja u `best_solution()`); na pojedinim 20D ćelijama DE troši oko 36.000, a GAdapt oko 19.000 poziva. Generacije zato nisu uporediva jedinica troška. Uticaj tog nesklada na preciznost nije posebno proveren. Funkcije nisu pomerene ni rotirane, a četiri od devet imaju optimum u ishodištu.

## 8.3 Studija S0: replikacija sa stvarnim brojanjem

S0 zadržava mentorove funkcije i konfiguracije, uz instrumentaciju (brojač poziva), seedovanje DE-a i obelodanjena odstupanja, 21 ćeliju (funkcija × dimenzija), četiri originalne konfiguracije i 20 semena. Protokol je zamrznut pre merenja; sve brojke je nezavisno reprodukovala recenzija.

**Zamrznuto pravilo (H64a)** prolazi ako su svi ΔA pozitivni prema simultanim granicama, ili uz najviše jedan izuzetak prema kojem je ΔM pozitivan. S0 prolazi prvom granom: ΔA = 0,164 (PyGAD random), 0,204 (PyGAD adaptive), 0,047 (DE), sve donje granice > 0. GAdapt je dakle efikasniji u uslovima ovog benchmarka.

**Završna preciznost je složenija slika.** GAdapt ima niži ponderisani prosek ćelijskih završnih medijana normalizovanog jaza; prednost prema DE-u nose uglavnom dve ćelije (Rastrigin-20 i Griewank-7), ali to objašnjenje ne važi za sva poređenja. Post hoc, opisno: DE ima nižu završnu medijanu u 14 od 21 ćelija, GAdapt veći A u 17 od 21; pri najviše 12.000 poziva odnos medijana je 10 : 10 : 1. Preciznost nije poređena pri jednakom budžetu u izvornom dizajnu: GAdapt troši u proseku ≈ 10.200, DE ≈ 11.900, PyGAD random ≈ 16.500, PyGAD adaptive ≈ 25.200 poziva.

Zaključak S0 sme biti samo operacionalizovan: veća efikasnost do 12.000 poziva među četiri konfiguracije, na neokrenutim klasičnim funkcijama, sa 20 semena. Ne sme se tvrditi opšta veća preciznost, prednost u većini ćelija, industrijska pouzdanost niti uzročna uloga mutacionog operatora. Obelodanjeno je da su tri od dvadeset semena bila viđena u probnoj seriji pre glavnog pokretanja.

## 8.4 Studija E: pomerene i rotirane funkcije, jednak budžet, jači konkurenti

E koristi 63 ćelije (21 funkcija/dimenzija × {original, pomereno, pomereno i rotirano}), tačno 12.000 stvarnih poziva po pokretanju, 100 semena i devet konfiguracija: GAdapt, GAdapt sa opcionim presetom stabilnosti, PyGAD random i adaptive, SciPy DE, CMA-ES, IPOP-CMA-ES, BIPOP-CMA-ES i (1+1)-ES sa restartima. Zamrznute hipoteze su H64a (mentorova tvrdnja pri jednakom budžetu i rotaciji) i H64b (preset smanjuje CVaR najmanje 20% bez pada uspešnosti većeg od 5 procentnih poena). Svi brojevi dolaze iz generisanog izveštaja `ITERATION64_E_REPORT_SR.md`.

**H64a po zamrznutom pravilu: suprotan ishod.** Prema simultanim intervalima E, CMA, IPOP i BIPOP imaju veći ponderisani A od GAdapt-M (ΔA između −0,097 i −0,089, intervali potpuno negativni); GAdapt-M ima veći A od oba PyGAD-a, DE-a i (1+1)-ES. Naknadno (post hoc, bez statusa potvrde): obrazac „GAdapt nadmašuje sve osim CMA porodice“ liči na mentorov opis, ali grupisanje CMA varijanti u jedan algoritam nije bilo unapred zadato i ne potvrđuje H64a.

**Zavisnost od transformacije (post hoc, opisno).** Uz jednake težine ćelija, GAdapt-M ima CVaR₀,₉ 0,0033 na originalnim i pomerenim funkcijama i 0,0386 pod rotacijom, gde CMA porodica ima oko 0,019 (preset ima niže orig/shift vrednosti, 0,0031/0,0032). ECDF-površina GAdapt-a pada sa 0,63 na 0,52, dok je CMA porodice oko 0,70 u sve tri varijante. Ponderisani prosek ćelijskih medijana jaza raste za red veličine (0,0013 na 0,014). Ponderisani agregatni CVaR GAdapt-a (0,0117) najniži je među devet konfiguracija; dve trećine težine pripadaju orig/shift varijantama. Pomereno i rotirano koriste različite pomeraje, pa razlika među varijantama ne izoluje efekat rotacije, a osno poravnanje ne podrazumeva separabilnost. Nalaz ne ustanovljava prednost na klasama infrastrukturnih problema.

**H64b: nije podržana.** Procenjeni CVaR raste sa 0,0117 na 0,0121.

## 8.4b Studija E2: opcioni diferencijalni krosover (negativan preregistrovan rezultat)

E2 proverava da li zamena krosovera poboljšava unapred definisane ishode, u biblioteku je dodat opcioni `crossover="differential"` (roditelj plus skalirana razlika dva člana populacije, svi parametri zajedno; podrazumevano ponašanje bit-identično, proveren heš niza poziva). Operator je rotaciono ekvivarijantan samo kao neograničen korak predloga; refleksija na granice, diskretizacija i mutacioni operatori ostaju koordinatni. E2 je zamrznut pre merenja i koristi iste ćelije i semena kao E, uparene sa arhiviranim zapisima (arhivirani E tragovi GAdapt-a reprodukovani su bit-tačno, 126 od 126).

Ishod (jedna simultana porodica od pet kontrasta): **opcija ne zatvara jaz**; A je niži pod rotacijom i na objedinjenom orig+shift podskupu, uz simultane intervale ispod nule. Uzrok neuspeha nije izolovan. Pod rotacijom ΔA(D − M) = −0,036 (interval od −0,047 do −0,025), a CVaR se pogoršava; na osno-poravnatim ćelijama ΔA = −0,042; prema IPOP-u ΔA = −0,18. H64e1 i H64e3 su suprotni, H64e2 neodlučena. Opcija ostaje u biblioteci dokumentovana, podrazumevano isključena i bez preporuke; nije ponavljana sa drugim parametrima.

## 8.4c Studija E3: hibrid GAdapt → CMA-ES (empirijska provera na klasičnim funkcijama)

Pošto opcioni krosover nije pomogao, a razvojni pokušaj GAdapt-PCA (četiri rotirane ćelije, tri semena) nije dao dovoljnu korist i nije formalno testiran, testiran je uobičajeni recept „globalna pretraga, pa lokalno doterivanje“: GAdapt troši prvih 30% budžeta (udeo izabran na razvoju među 0,3/0,5/0,7), zatim CMA-ES startuje iz najboljeg rešenja sa malim korakom. Hibridi su poznati (npr. Krasnogor i Smith 2005); ovo je empirijska provera, ne nova metoda, i hibrid nije GAdapt sam. Isti 63 ćelije i semena kao E, uparene sa arhiviranim zapisima.

Zamrznuta pravila daju mešan ishod: **H64g1 podržana** (pod rotacijom ΔA = +0,103, CVaR se smanjuje više od 20%), **H64g2 suprotno** (na osno-poravnatim ćelijama rep je 1,8× veći od GAdapt-M, iznad tolerisanih 1,5×, uz ΔA = +0,065), **H64g3 neodlučeno** (neinferiornost prema IPOP-u pod rotacijom: −0,043, interval [−0,052; −0,035] seče granicu −0,05). Post hoc, među šest prikazanih konfiguracija, u proseku tri varijante hibrid ima najniže agregate CVaR/M (0,0070/0,00293; GAdapt-M 0,0117/0,00429; IPOP 0,0142/0,00779); A je 0,7511 prema 0,7699 za IPOP. Neinferiornost prema IPOP-u nije potvrđena. Bez ablacija nije utvrđen zaseban doprinos GAdapt i CMA faze.

## 8.4d Studija E4: opciona kompenzaciona mutacija sa kontrolama (nije podržana)

Poslednja intervencija u samom GAdapt-u: `compensatory_mutation` (posle uobičajene mutacije svaka mutirana promenljiva povlači jednog partnera duž korelacije elite; bez dodatnih evaluacija; podrazumevano isključena). Novost nije ustanovljena (uslovno uzorkovanje iz elitne kovarijanse poznato je iz RV-GOMEA; Bouter i sar. 2020, 10.1145/3377930.3390225), pa je ovo inženjerska opcija sa obaveznim kontrolama: bez kapije, slučajan partner i uslovno uzorkovanje u stilu Boutera. Kontrola uslovnog uzorkovanja ispravljena je posle nezavisne revizije koda i ponovljena (dopuna A1).

Ishod prema zamrznutim pravilima: jezgro (H64k1–k4) **nije podržano**. Pod rotacijom je ΔA prema GAdapt-M +0,014 (interval od 0,005 do 0,023), ali se CVaR ne smanjuje za traženih 20%; šteta na osno-poravnatim ćelijama nije dokazana (H64k2 podržana); razlika prema kontroli sa slučajnim partnerom i prema uslovnom uzorkovanju obuhvata nulu (H64k3/k4 neodlučene), pa dobitak ne možemo pripisati iskorišćavanju veza; prema IPOP-u je ΔA −0,132 (H64k5 suprotno). Zaključak serije E2–E4: nijedna ispitana intervencija u samom GAdapt-u nije zatvorila rotacijski jaz; to je uspeo jedino hibrid sa CMA-om (E3), koji nije GAdapt.

## 8.5 Infrastrukturna faza (nije zamrznuta)

Faza I64-I proverava iste mere na diskretnom ORPD-u pod jednakim budžetom stvarnih proračuna toka snage. Dok nije zamrznuta i izvršena, poglavlje ne sadrži nikakvu tvrdnju o industrijskoj primeni.

## 8.6 Šta poglavlje doprinosi

Doprinos je u tri stvari: (1) replikacija mentorovog benchmarka sa nezavisnim brojanjem stvarnih poziva i preregistrovanim pravilima odlučivanja, sa obelodanjenim odstupanjima; (2) karakterizacija pouzdanosti (rep raspodele, verovatnoća dostizanja) umesto samo srednje vrednosti i SD-a; (3) opcione funkcije sa dokumentovanim proverama (njihova opšta pouzdanost nije ustanovljena; preset i diferencijalni krosover nisu pokazali korist). Poglavlje ne ustanovljava novu optimizacionu metodu; industrijska spremnost nije ustanovljena.
