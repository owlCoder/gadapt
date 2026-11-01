# I62 (PREDLOG, NIJE ZAMRZNUT): spoljna validnost — validirani L-SHADE/jDE i podešena kazna

**Status: PREDLOG 2026-10-24** (posle H58 = N i H60 = N; pre I59 i I61 rezultata). Nacrt: Codex 070 (ispod, doslovno).
Redosled: posle I61 (Codex 052: replikacija H56a ima prioritet). Pre zamrzavanja: adversarijalna recenzija.

## Moje napomene
1. **Okruženje:** NiaPy (i zavisnosti) instalirati u ODVOJENO okruženje (npr. `.venv-i62`), nikako u `.venv`: I61 manifest
   hešira `pip freeze`, pa bi instalacija usred I61 zaustavila svaku narednu I61 fazu.
2. Scenariji (seme 7001xx/7002xx) moraju biti disjunktni i od I61 (61xx/62xx) — proveriti heševima opterećenja.
3. Uloga u tezi: ograničava praktične tvrdnje (spoljni kontekst), ne nosi originalnost.

---

Preporučujem **opisni I62 sa unapred zamrznutim izborima i analizom**. Njegova svrha je spoljna validnost praktičnih tvrdnji teze: poređenje sa validiranim jačim konkurentima i podešenom kaznom. I57 pokazuje prednost CMAwM u vremenu dostizanja na delu instanci; I58 nije potvrdio H58. I62 zato ne treba postaviti kao očekivanu potvrdu konkurentnosti GAdapt-a.

Sledi predlog teksta protokola. Status je **NACRT**, bez menjanja fajlova ili izvršavanja eksperimenata.

1. **Pitanje i domet.**  
   I62 opisuje vreme dostizanja, izvodljivost i kvalitet rešenja GAdapt-a naspram L-SHADE, jDE i CMAwM pri jednakom broju stvarnih AC PF poziva. Posebno proverava da li ugrađeni FR i ε ostaju praktično korisni prema razvojno podešenoj statičkoj kazni. Zaključci su uslovni na četiri topologije, model ORPD-a, scenarije, reference i budžete. Studija ne proverava originalnost metode niti zamenjuje I61 replikaciju interakcije.

   Tanabeov nalaz opravdava uključivanje jDE i proveru celobrojnog rukovanja; ne garantuje prednost bilo kog DE-a na ovom zadatku. [Tanabe, 2024](https://arxiv.org/html/2404.03303v1)

2. **Implementacije i obavezna validacija.**  
   Kandidati su NiaPy **2.7.1** L-SHADE i jDE; verzija paketa, zavisnosti, izvorni kod i sve izmene arhiviraju se sa SHA-256. Dostupnost paketa nije dokaz vernosti algoritmu. [Izdanje NiaPy](https://pypi.org/project/niapy/2.7.1/)

   L-SHADE: \(N_0=18D\), \(N_{\min}=4\), \(H=6\), \(p=0,11\), faktor arhive 2,6; proveriti memoriju uspeha, arhivu, selekciju, binomni crossover, granice i redukciju prema stvarnom broju evaluacija. Podešavanja odgovaraju objavljenom eksperimentu. [Izvorni rad](https://ryojitanabe.github.io/pdf/tf-cec2014.pdf)

   jDE: DE/rand/1/bin, populacija 100, početno \(F=0,5\), \(CR=0,9\), \(\tau_1=\tau_2=0,1\), novo \(F=0,1+0,9U\), novo \(CR=U\); parametri se nasleđuju samo sa prihvaćenim potomkom. Proveravaju se originalne jednačine i API: NiaPy oznake parametara i podrazumevane vrednosti ne prihvataju se bez provere. Dostupna dokumentacija starijeg izdanja već pokazuje drugačije defaulte. [Dokumentovani jDE kod](https://niapy.org/en/stable/_modules/niapy/algorithms/modified/jde.html)

3. **CEC provera i kriterijum prolaza.**  
   Pre ORPD razvoja izvršiti CEC2014 F1/F9/F17, \(D=10,30\), 51 nezavisno pokretanje, granice \([-100,100]^D\), tačno \(10^4D\) evaluacija uključujući inicijalizaciju. Koristiti zvanične pomake, rotacije i permutacije; proveriti vrednosti na optimumu i unapred generisanim tačkama. Greška ≤ \(10^{-8}\) prikazuje se kao nula. Objaviti best/worst/median/mean/SD prema tabeli I izvornog rada.

   Za L-SHADE paralelno izvršiti ispravljeni autorov **1.0.1**: autor navodi grešku arhive u 1.0.0, pa odstupanje od objavljene tabele zahteva objašnjenje porekla verzije. [Autorova napomena i kod](https://ryojitanabe.github.io/publication)

   Operativni pragovi prema ispravljenoj referenci, po svih šest ćelija:
   \[
   |\bar e-\bar e_r|\le\max(10^{-8},0,25\max(\bar e_r,s_r)),\quad
   |s-s_r|\le\max(10^{-8},0,5s_r).
   \]
   To su unapred izabrani inženjerski pragovi, ne dokaz statističke ekvivalencije. jDE prolazi audit jednačina, determinističke tragove uz zadate slučajne brojeve i iste pragove prema nezavisno implementiranom jDE-u; ne poredi se sa L-SHADE tabelom kao kriterijumom ispravnosti. Neprolaz blokira ORPD fazu; ispravka zahteva novu verziju i celu validaciju.

4. **Budžet i diskretizacija.**  
   Svaki adapter proveriti na budžetima 3000, **3001**, 10.000, kao i neposredno oko završetka inicijalizacije. Brojati stvarni `runpf`, uključujući duplikate i nekonvergenciju; keš služi evidentiranju, ne besplatnim evaluacijama. Zaštita mora sprečiti poziv \(B+1\). Ishodi dolaze isključivo iz evaluator-a.

   Dekodiranje identično I57:
   `k = clip(rint(x), 0, R−1); values = lo + k*step`.
   Testirati polovine, krajeve i izlazak iz opsega. DE zadržava realne koordinate; zaokruživanje služi evaluaciji, bez upisivanja zaokruženih vrednosti u populaciju. Kontinualnu popravku granica fiksirati prema validiranoj implementaciji.

5. **Instance i razdvajanje podataka.**  
   Redom: case30, case39, case24_ieee_rts, case57; \(R=17\), spread 0,1. Koristiti I58 `BusORPD`, jednu VG kontrolu po generatorskoj sabirnici.

   Razvoj: `(0,97; 700101)`, `(1,03; 700102)`. Test: `(0,92; 700201)`, `(1,02; 700202)`, `(1,08; 700203)`, gde je par faktor opterećenja/seme scenarija. Proveriti disjunktnost semena i heševa stvarnih opterećenja prema I56/I58/I61. Topologije se ponavljaju; novost se odnosi na scenarije.

   OPF neuspeh znači izuzimanje bez zamene, pre optimizacije. Potrebna su oba razvojna i najmanje jedan test scenario svake mreže; inače STOP.

6. **Grane i reference.**  
   Test ima osam grana: GAdapt/SP*, GAdapt/FR, GAdapt/ε; L-SHADE/SP*, L-SHADE/FR; jDE/SP*, jDE/FR; CMAwM/FR. SP* označava zasebno razvojno izabranu kaznu svakog optimizatora. CMAwM čuva važan konkurentski kontekst iz I57/I58.

   GAdapt nasleđuje I58 podešavanja: populacija 32, elitizam 50%, bez sondiranja i imigracije. Za budžet \(B\), sve GAdapt grane koriste \(N=\lceil B/16\rceil\); ε zadržava bibliotečki raspored: početni 20. percentil, eksponent 5, nula na polovini \(N\). Asercijom proveriti iste početne populacije GAdapt grana.

   Razvojne reference obuhvataju svih 17 konfiguracija: četiri kazne po tri optimizatora, njihov FR, GAdapt/ε i CMAwM/FR; jedno seme, 30.000 poziva. Test reference: osam zamrznutih grana, dva semena, 30.000 poziva. Nepotpune reference posle jednog ponavljanja blokiraju fazu.

   Zajednički cilj: \(V=0,\ f\le1,01L^*+0,01\) MW; \(L^*\) je najmanji izvodljiv referentni gubitak. Bez izvodljive reference cilj je izvodljivost. Reference nisu optimum i ne menjaju se test rezultatima.

7. **Razvojni izbor budžeta.**  
   Na oba razvojna scenarija, pet semena, pokrenuti osam grana sa privremenom kaznom 1000, zasebno pri \(B\in\{3000,6000,12000\}\). Prefiksi duže putanje nisu zamena: L-SHADE redukcija populacije i ε zavise od ukupnog budžeta.

   Po mreži izabrati najmanji B sa ukupnom stopom dostizanja 20–80% i bar jednim dostizanjem kod najmanje dva različita optimizatora. Bez prolaza koristiti 12.000 i označiti neuspelu razvojnu informativnost; ne dodavati budžete ili scenarije.

8. **Podešena kazna i izbor CHT-a.**  
   Pri izabranim budžetima koristiti pet novih razvojnih semena. Za svaki od GAdapt/L-SHADE/jDE ispitati \(w\in\{10,100,1000,10000\}\), skalar \(f+wV\). Izabrati jedan globalni w po optimizatoru minimizovanjem srednjeg T, jednako ponderisanog po mrežama i scenarijima; veze rešava manji w.

   GAdapt FR i ε dobijaju isti razvojni obim; „best CHT“ bira se istim kriterijumom, veza → FR. Obe ostaju prikazane. Težine, CHT i budžeti zamrzavaju se pre test referenci. Obavezno promeniti adapterov skalar: I56 `Evaluator` trenutno vraća kaznu 1000.

9. **Semena, ishodi i analiza.**  
   Seme optimizatora:
   \(2.000.000.000+10^6p+10^5i+1000j+100b+s\).
   Faze p=1–5: razvojne reference, izbor B, podešavanje, test reference, test; b je indeks kandidat-budžeta. Proveriti jedinstvenost; ista semena namerno povezuju grane. Sejati sve RNG-ove. Test: **30 semena po ćeliji**.

   Glavni opisni ishod \(T=\min(h/B_i,1)\), nedostizanje=1. Kontrasti: best CHT prema GAdapt/SP*, oba DE-a pod SP*/FR i CMAwM/FR. Jednake težine mreža/scenarija; 20.000 bootstrap ponavljanja celih uparenih vektora unutar ćelija, seme 62; tačkasti 95% intervali.

   Nema konfirmatornih hipoteza, p-vrednosti ili tvrdnje o snazi za superiornost. Trideset ponavljanja određuje obim opisne procene. Posebno prikazati dostizanje, izvodljivost, prvi izvodljiv poziv, najbolji izvodljiv gubitak, nekonvergenciju i vreme. Uslovne gubitke prikazati uz imenilac; degenerisani T ostaje vidljiv.

10. **Izvršavanje, kod i trošak.**  
    Puni budžeti bez prekida pri cilju; svaki posao u novom procesu. Greška izvršavanja → jedno ponavljanje istim semenom; zatim izuzimanje celog uparenog vektora, uz analizu osetljivosti: uspešni ishodi ostaju, nedostupni dobijaju T=1. Prazne ćelije i izuzimanja prijaviti.

    Potrebni su `iteration62_external_validation.py`, CEC drajver i nezavisni proverivač. Ponovo koristiti I57 adaptere i I58 `BusORPD`/`WitnessEvaluator`, parametrizovati scenario, budžet, težinu i ε; proverivač uključuje I58 D1 konvenciju nekonvergencije. Nezavisno proveriti reference, ciljne svedoke, najbolje i vraćene izlaze; neuspeh blokira prihvaćen izveštaj.

    Maksimum bez ponavljanja/provera: razvojne reference **4,08 M**, izbor B **6,72 M**, podešavanje **6,72 M**, test reference **5,76 M**, test **34,56 M** = **57,84 miliona PF**. Pri 3,3–4,5 ms/PF: približno **53–72 CPU-sata**, plus režija i OPF. CEC dodaje 61,2 miliona jeftinijih evaluacija po implementaciji. Zamrznuti manifest pre svake faze i drugi istraživač koji ponavlja paket potrebni su za reproduktivnost.

DOI status: **10.1145/3638529.3654019**, **10.1109/CEC.2014.6900380** i **10.1109/TEVC.2006.872133** ostaju **neprovereni preko Crossref-a**: direktni zahtevi nisu bili dostupni. Ne dodajem nove DOI-je niti predstavljam neuspešnu proveru kao potvrdu.