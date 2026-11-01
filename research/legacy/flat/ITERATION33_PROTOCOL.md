# Iteracija 33 — PRE-REGISTRACIJA transfera GAdapt scenario screeninga na GÉANT telekom model (korak 2/5)

**Datum i status:** 22.10.2026 PRE prvog novog I33 routinga. Model audit PRE ovoga: [I33_GEANT_MODEL_AUDIT_SR.md](ITERATION33_GEANT_MODEL_AUDIT_SR.md). Sve izmene samo u `owlCoder/gadapt:main`, upstream `bpzoran/gadapt` nedirnut.

## Hipoteza, fizički / domenski opseg

Treći infrastrukturni test posle I31 IEEE118 i I32 IEEE14: javni originalni **SNDlib GÉANT**, 22 čvora, 36 linkova, 462 zahteva, **36 celobrojnih OSPF-like weight promenljivih 1–25**. Originalni javni `geant.txt` SHA256 `ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed4b4f4ff` obavezno proveriti pre ikakvog routinga. Original `GeantCapacity.evaluate()` trošak je modularno zaokružen po linku. Svaka pozvana scena podrazumeva **jednu stvarno izvršenu Dijkstra + unsplittable-routing + module-cost evaluaciju**. Ovo nisu električne AC, matematički OPF, nezavisni realni field podaci, niti puna telekom QoS/ECMP/availability evaluacija.

**Posebna, hipotetička (NOT SOURCE) pretpostavka**: investicioni cap **145.000 planskih SNDlib price-units ZA SVAKI SCENARIO**. Nije originalna oprema ili uslov operatera, već namerno transparentno postavljen istraživački scenario. Pošto originalni GeantCapacity dozvoljava neograničenu kupovinu modula, bez hipotetičkog cap-a sve bi bilo trivijalno capacity-coverable. Zato se ni jedna nova GÉANT 'feasible' tačka ne sme nazvati *original source physically feasible*, već **izvodljivom samo pod hipotetičkim troškovnim cap-om**. Izvorne module-size/cost strukture ipak ostaju po originalnom javnom modelu.

Tri unapred fiksirane **sintetičke** prostorne tražnje: `nominal` originalni demand; `odd_source_heavy` izvorni demand koji polazi iz 1-based neparnog čvora u **leksikografski sortiranom spisku 22 izvorna imena** ×1,08, iz parnog ×0,92; `even_source_heavy` obrnuto. Sva tri koriste istu topologiju, 36 izvornih module-size/cost, 462 originalnih demand parova i jedan zajednički vektor težina rutiranja. **Objektiv** je prosta srednja vrednost tri potpuno plaćena, odvojena scenario-specific modularna plana (model *scenario recourse*, ne cena jednog zajedničkog trajnog fizičkog plana). Nominalno u svim metodama svi 36 source weights ostaju [1,25] celobrojni. Svaka cena scenarija konačna nenegativna, feasible iff `cost <=145000`. Normalizovano hipotetičko kršenje `max(0,(cost-145000)/145000)`; score pen `1e5*sum(violation)`, censored score `1e9+1e5*v_first_measured_failure`.

## Zamrznuti metodi i budžeti

- `ga_full_true` — 3× stvarno plaćena routinga za svaki kandidat, rangiraj stvarni mean scenario module cost + pen.
- `ga_full_censored` — **3× plaćeno** ali fitnes rangiran kao first-failure za svakog kršioca, *isti* kao `ga_stop_fixed`. Broj ruta isti kao u punom metodu; kontrola razdvaja score i budget.
- `ga_stop_fixed` — PREREG prvom potvrđenom hipotetičkom budget prekršaju prekini preostale neizmerene scene.
- `ga_stop_adaptive` — poznata empirijska beta-smoothed failure-rate ređanja, inače isto.
- `de_full_true` i `de_stop_fixed` — SciPy differential_evolution, `popsize=5,maxiter=12,tol=0,atol=0,polish=False,seed=seed,updating='immediate',integrality=True`, različita samo strategija cena / screeninga.
- Svaka GA uses **originalni pravi `gadapt.ga.GA`**: `population_size=24, log_relative, exit_check=generations, number_of_generations=128, population_mutation='cost_diversity,parent_diversity',timeout=240`, exit when less than 3 stvarna routinga mogu biti finansirana. Originalni GAdapt default NEMENJAN; `FullPaidFirstFailureScore` kontrola deljena sa I32 kao postojeća istraživačka kontrola. Bez novih optimizatorskih hiperparametara na osnovu I33 rezultatâ.

**NOVA uparena semena 2200...2211 = 12 × 6 metoda × 120 najviše stvarnih evaluacija = MAX **8.640** originalnih Dijkstra/module routing evaluacija**. Uvek rezervisati 3 kompletna eval mesta pre početka kandidata čak i kada metoda screen-uje (0,1,2 AC analogni neplaćeni slotovi ostaju neiskorišćeni). Instrument counter se menja **jednom samo neposredno pre `base.evaluate`**, svaki neuspeh računa kao pokušaj, bez fiktivnih slobodnih merenja ili ponovnog računanja kandidata za vreme rezimea. `not converged` / Python exception status numerical unknown nije dokaz da cap nije zadovoljen. `feasible` robust zahteva sva tri ZAISTA izmerena domen-solvera, sva tri cena ≤145.000.

## Statistika i disclosure

**Primarno**: paired seed binary success `>=1` kandidata izmerenog sva tri scenarija, sa kapom 145.000 po svakoj scenariji; 5 unapred navedenih primary comparisons: GA true/full-censored (score), GA full-censored/GA stop_fixed (budget), GA stop_fixed/GA adaptive (ranking), GA fixed/DE fixed (optimizer) i GA true/DE true (optimizer). Koristiti **egzaktni dvostrani binomial/McNemar**, a 5 kontrasta sa *Holm-korekcijom*, ne prećutati nula diskordantnih.

**Sekundarno**: true Dijkstra/module evaluations, broj samo empirijski rano cenzurisanih, kompletno verifikovanih izvodljivih kandidata, broj stvarno neizmerenih scena, originalni modularni mean cost među verified only, median/worst po uparenom semenu i originalne individualne scenario cene za najbolji verificirani plan, post-budget requests; NA za sve metode koje nisu ostvarile nijedan feasible. Sve merenje je **u veštačkoj recourse formulaciji**, ne globalna optimizacija telekom mreže. Izbor cap-a je **a priori** i ne podešava se da „uspemo“. Ukoliko sva tri profila imaju 0 feasible, to je legitiman negativan rezultat.

## Redosled rada i zaštite

1. Originalni source audit već komitovan; ovaj protokol takođe komitovati **PRE** bilo kojih I33 numerical routing poziva.
2. Implementacija, sintetički no-real-routing unit testovi, workflow sa strict SHA preflight.
3. Tek zatim run 72 preregistrovana physical-domain routing eksperimenta u Actions; svaki `I33_TRUE_ROUTE` stdout JSON, summary, archive kao Actions artifact; prihvatiti samo 72/72.
4. Arhivirati **identične originalne** individualne runove u main JSON/CSV sa CI URL i digestom; izvoz sa unijom kolona.
5. Izvesti uparenu Holm statistiku i uporediti negativne/pozitivne IEEE I31/I32 signale, bez preuveličavanja novosti i bez ponovljenih „independent“ seedova ako se CI fizički rerun kasnije tehnički ponovi.

**Sledeća doktoratska hipoteza i dalje otvorena:** novi, originalno proverljiv adaptivni mehanizam za resource-aware operator izbor pod troškom realne evaluacije, prethodno detaljno proveriti literaturu AOS, budgeted optimization, constraint repair, scenario racing. U I33 testiramo *poznatu* politiku screeninga, ne dokazujemo novu metodu.
