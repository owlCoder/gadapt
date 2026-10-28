**GO za replikaciju i proširenje benchmarka; NO-GO za opštu tvrdnju da je GAdapt precizniji i stabilniji od vodećih optimizatora.** Mentorov cilj je opravdan, ali zahteva odvojeno merenje preciznosti, potrošnje evaluacija i rizika lošeg ishoda.

Pregledana verzija benchmarka je `0e388356`. Ispod je predlog protokola za preregistraciju: u ovom read-only pregledu ništa nije menjano, zamrznuto commit-om niti pokretano.

**1. Šta postojeći benchmark može da podrži**

Može da utvrdi kako se **četiri konkretne konfiguracije** ponašaju na izabranim klasičnim funkcijama, pod zadatim pravilima stagnacije. Uz sirove rezultate može da podrži ograničene tvrdnje o njihovoj završnoj preciznosti i rasipanju. Sam kod ne potvrđuje mentorovo rangiranje.

Ne može da utvrdi opštu superiornost GAdapt-a, industrijsku pouzdanost ili da razliku uzrokuje isključivo mutaciona strategija. Konkretne pretnje validnosti su:

- **Generacije nisu jednak računarski budžet.** GAdapt zadržava evaluirane preživele, DE evaluira probne kandidate za celu populaciju, a PyGAD ima dodatne evaluacije. Jednaka stagnaciona tolerancija zato daje različitu izloženost funkciji troška.
- **Pravila zaustavljanja nisu identična.** DE callback priznaje poboljšanje tek preko `1e-12`, dok SciPy dodatno koristi `tol=1e-7`. PyGAD koristi sopstveni `saturate_N`. Treba proveriti i indeksiranje početne generacije i efektivni generacijski limit.
- **DE populacija je približno poravnata.** Kod koristi `max(1, 64 // D)`: pri D=2/7/20 dobija 64/63/60 jedinki. Nije napravljen čest propust `popsize=64`, koji bi značio približno `64D` jedinki. Međutim, DE i dalje uglavnom evaluira više kandidata po generaciji od elitističkog GA. Značenje množitelja potvrđuje [SciPy dokumentacija](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.differential_evolution.html).
- **Postoje dodatni pozivi.** DE callback ponovo evaluira najbolje rešenje. PyGAD ručno evaluira početnu populaciju i poziva `best_solution()` bez prosleđenih fitnesa tokom svake generacije. I49 pokazuje zašto takav pristup može ponovo računati fitnes. GAdapt-ove validacione probe takođe treba uračunati. Tačne brojeve po pokretanju i konfiguraciji mora dati omotač funkcije, uz označavanje faze i generacije.
- **Porede se konfiguracije biblioteka.** PyGAD koristi namensku selekciju po rangu i BLX-α ukrštanje. Naziv „blend“ sam po sebi ne dokazuje jednak operator kao u GAdapt-u. Razlikuju se i zamena populacije, popravke i ponovno korišćenje fitnesa. Za uzročnu tvrdnju o mutaciji potrebna je ablacija unutar istog implementacionog okvira.
- **Klasične funkcije ograničavaju generalizaciju.** Sphere, Rastrigin, Ackley i Griewank imaju optimum u ishodištu; ostale nemaju. Funkcije nisu rotirane, a Rosenbrock je ograničen na uzak opseg `[0.5,1.5]`. Osetljivost na pomeranje, rotaciju i položaj optimuma zahteva nove eksperimente.
- **REC/AUCC mere drugačije nego što sugeriše README.** U kodu je REC  
  \((f_t-f_{\mathrm{final}})/(f_0-f_{\mathrm{final}})\): preostali deo ostvarenog poboljšanja. Prozor zavisi od najkraće prosečne putanje među konfiguracijama. AUCC je normalizovana površina odsečene krive, sa početkom i završetkom normalizovanim posebno po pokretanju. Obe mere koriste generacije; nijedna neposredno ne meri cenu dostizanja apsolutnog cilja.
- **SD nije dovoljna definicija stabilnosti.** Algoritam koji pouzdano vraća loše rešenje može imati mali SD. Potrebni su rep raspodele i učestalost neuspeha. `significance.py` uparuje rezultate samo po indeksu pokretanja, dok runneri ne postavljaju odgovarajuća semena; više stagnacionih postavki dodatno objedinjuje u jedan test.

[I49](/Users/danijel/Desktop/gadapt/research/ITERATION49_REPORT_SR.md) i [rukopis revizije integriteta](/Users/danijel/Desktop/gadapt/research/paper_integrity_audit/manuscript.md) opravdavaju obavezno nezavisno brojanje poziva i proveru vraćenog rezultata. Nalaze iz drugih adaptera ne treba automatski pripisati mentorovim pokretanjima.

**2. Proširenje za preregistraciju**

Predlažem sledeći konačan obim, uz javno arhiviranje protokola, implementacija, parametara i heševa pre testiranja.

| Element | Unapred određeni dizajn |
|---|---|
| Replikacija | Originalne četiri konfiguracije, 21 kombinacija funkcije/dimenzije, stagnacija 20, limit 600 generacija; uz stvarne brojače |
| Sintetika | Istih 21 kombinacija × originalna, pomerena i pomerena+rotirana varijanta: **63 ćelije** |
| Infrastruktura | ORPD case14/30/39/57/118 × R=9/17/33 × dva nova scenarija: 30 ćelija; AC dispatch istih pet mreža × dva scenarija: još 10 |
| Konfiguracije | Originalne četiri; GAdapt preset; CMA-ES, IPOP-CMA-ES, BIPOP-CMA-ES; L-SHADE; jDE; restartovani (1+1)-ES: **11** |
| Ponavljanja | 100 semena po ćeliji; nezavisni procesi |
| Budžet proširenja | Najviše 12.000 stvarnih evaluacija; snimci na 3.000 i 12.000 iz iste putanje |

Pomeranja, ortogonalne matrice i novi scenariji generišu se unapred iz javnih semena. Poznati minimum mora ostati unutar domena; rotacija sfere služi kao negativna kontrola. Za ORPD unapred fiksirati diskretno dekodiranje, a za CMA porodicu koristiti odgovarajuću margin varijantu. Ostalim metodama zamrznuti objavljene preporučene postavke; DE može dobiti eksplicitnu početnu populaciju od 64 jedinke.

U proširenju nema završetka zbog stagnacije: interna pravila restarta pripadaju zamrznutoj konfiguraciji. Spoljni omotač zaustavlja fizičke evaluacije tačno na budžetu, uključujući inicijalizaciju, probe, duplikate i lokalnu pretragu. Ne oslanjati se samo na bibliotečki `maxfevals`. Beležiti i CPU/vreme, granice, izvodljivost i podudarnost vraćenog rešenja sa tragom evaluacija.

Sve promenljive normalizovati na `[0,1]`. Ograničenja, tolerancije i skalarizacija ostaju zajednički svim metodama. I47 dispečing zadržati kao **penalizovani benchmark**, uz odvojenu izvodljivost: na case14–57 tada nijedan metod nije našao izvodljivo rešenje. Referentne vrednosti zamrznuti nezavisnim portfoliom metoda; infrastrukturnu referencu zvati najboljom poznatom, ne optimumom.

Primarne mere:

- završna raspodela normalizovanog jaza: medijana, kvantili 90/95% i svi rezultati;
- **CVaR₀․₉**: prosek najlošijih 10% ishoda;
- verovatnoća izvodljivosti i dostizanja unapred fiksiranih ciljeva;
- ECDF dostizanja ciljeva prema broju evaluacija, sa nedostizanjem zadržanim u imenitelju.

Za zajedničku meru rizika definisati \(L=g/(1+g)\), gde je \(g\) nenegativni normalizovani jaz; bez izvodljivog rešenja ili pri izvršnom neuspehu \(L=1\). Prijaviti i potpisani jaz prema najboljoj poznatoj referenci, uključujući njeno poboljšanje. Ne izbacivati neuspele runove.

Ciljevi su \(g\le10^{-2},10^{-4},10^{-6}\), uz izvodljivost gde je primenljiva. Koristiti uparene blokove scenarija/semena, Wilcoxon sa rank-biserial efektom i Holm korekcijom; za medijane, CVaR i verovatnoće stratifikovani bootstrap celih uparenih vektora, 20.000 ponavljanja i 95% intervale. Sintetiku i infrastrukturu analizirati odvojeno, uz jednake težine funkcija/mreža. Sto semena ne omogućava jake tvrdnje o veoma retkim otkazima.

**Falsifikabilne hipoteze:**

- **Mentorova tvrdnja:** „bolji“ operacionalizovati kao veću površinu ispod ECDF dostizanja ciljeva; GAdapt nadmašuje sve konkurente osim najviše jednog, a ima niži završni medijalni jaz i od tog izuzetka. Proveriti originalni skup i prošireni skup odvojeno. Istovremeni intervali moraju podržati oba dela; neznačajna razlika nije pobeda.
- **Suprotan ishod:** najmanje dva konkurenta imaju bolju efikasnost ili izuzetak ima i bolju završnu preciznost. Intervali koji ne razrešavaju smer znače „neodlučeno“.
- **Preset:** smanjuje agregatni CVaR gubitka najmanje 20%, bez pada uspešnosti većeg od pet procentnih poena. Obrnuti pragovi predstavljaju praktično pogoršanje.

**CPU budžet:** infrastruktura zahteva najviše **528 miliona AC poziva**; sintetika 831,6 miliona jeftinih evaluacija. Pri zabeleženih 2–16 ms po AC pozivu to je 293–2.347 CPU-sati samo za infrastrukturu, odnosno 29–235 sati idealno na deset jezgara. Predlog ukupnog plafona je **3.000 CPU-sati**, približno 12,5 dana neprekidnog rada, uključujući pripremu i rezerve. Deset procesa, po jedna BLAS nit; prekoračenje znači dokumentovan nepotpun eksperiment, bez selektivnog završavanja.

**3. Opt-in promena za stabilnost**

Vredi testirati preset:

```python
normal_distribution_mutation_min_std_dev=1e-4
normal_distribution_mutation_min_std_dev_decay_generations=2.5
```

Mehanizam već postoji: pri stagnaciji snižava donju granicu Gausovog koraka, vraća je posle poboljšanja i čuva minimum jednog diskretnog koraka. Potrebno je upakovati i proveriti preset, uz podrazumevano isključeno ponašanje i bit-identične tragove evaluacija.

[CLAUDE.md](/Users/danijel/Desktop/gadapt/CLAUDE.md:88) navodi oko **1,8 redova niži medijalni jaz uz 20% više evaluacija**; [README](/Users/danijel/Desktop/gadapt/README.md:264) objašnjava parametre. To opravdava test, ali ne dokazuje bolji najgori decil pri jednakom budžetu. Sitniji koraci mogu i pojačati zarobljavanje u lokalnim minimumima.

**4. Doprinos i odluka**

[I47](/Users/danijel/Desktop/gadapt/research/ITERATION47_REPORT_SR.md:32) već pokazuje znatnu prednost CMA-ES u preciznosti penalizovanog dispečinga. [I57](/Users/danijel/Desktop/gadapt/research/ITERATION57_REPORT_SR.md:101) istovremeno daje zanimljiv opisni nalaz: GAdapt je na case57 nalazio izvodljivost u svih 120 pokretanja, naspram 91/120 za CMAwM. To je konkretan kandidat za potvrdu.

Poređenje adaptivnih mutacija na numeričkim funkcijama ima dugu istoriju: [Srinivas–Patnaik, 1994](https://doi.org/10.1109/21.286385) i [Marsili Libelli–Alba, 2000](https://doi.org/10.1007/s005000000042). Predloženi doprinos je **replikacija, proširenje i karakterizacija pouzdanosti**, bez nove metode ili teoreme.

**GO** za studiju i test preseta. **NO-GO** za unapred proglašenu superiornost, metodološku novinu ili industrijsku spremnost.