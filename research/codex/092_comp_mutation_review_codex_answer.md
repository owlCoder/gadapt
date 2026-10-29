**Verdikt: INVALID za planiranu Gausovu `resample` kontrolu i zaključak H64k4.** Nalaz ne obara samostalno `gated`/`ungated` rezultate. Pregled je bio read-only; numeričke reprodukcije izvršene su u memoriji.

1. **`resample` ne uzorkuje uslovnu raspodelu elitnog Gausovog modela kada regresioni nagib pređe ±2.** U [compensatory_mutation.py:100](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/compensatory_mutation.py:100), `b` se klipuje pre grananja. Zatim uslovna sredina koristi taj klipovani `b`, dok varijansa koristi izvorni `C[j,i]²/(C[i,i]+ε)`. `mu` jeste pravilno izračunat iz normalizovane elite, a standardna devijacija jeste kvadratni koren nenegativnog Schurovog izraza; problem je sredina.

   Reprodukcija sa elitnim nagibom 4 i isključenim slučajnim članom daje **0,425**, dok odgovarajuća uslovna sredina iznosi približno **0,500**. Ovo je razlika pre refleksije/granica. Bouterova uslovna konstrukcija polazi od uslovne raspodele procenjenog multivarijantnog Gausovog modela ([rad, §4.2](https://ir.cwi.nl/pub/30061/30061.pdf)).

   **Tačna minimalna ispravka:** u `resample` grani koristiti neklipovani `a=C[j,i]/(C[i,i]+EPS)` za `mu[j]+a*(xi_new-mu[i])`; zadržati postojeću uslovnu varijansu, uz eksplicitno deklarisanu ε regularizaciju. Klip ±2 ostaje za kompenzacione pomake ostalih režima.

2. **`_fit` ima dva reprodukovana defekta korektnosti van E4 domena.** [Linija 48](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/compensatory_mutation.py:48):

   - Za `low=0.05`, `high=0.95`, `step=0.1`, ulaz `0.05` postaje `0.1`: rezultat nije na mreži `low+k·step`. `decimal_places` opisuje preciznost koraka, ali zanemaruje preciznost početka mreže. Zaokruživanje može prekršiti i granice.
   - Za `low==high` nema povratka na `low`. `permuted` može izabrati takvu slobodnu koordinatu i pomeriti je: reprodukovano **0,3** za fiksnu granicu **[0,2; 0,2]**.

   Ispravka: za degenerisan opseg odmah vratiti `low`; preciznost mreže izvesti iz **oba** broja, `low` i `step`, uz završnu proveru granica/mreže. Refleksija za konačne vrednosti i pozitivan opseg radi pravilno. **E4 nije pogođen:** koristi strogo pozitivne opsege i `step=None`.

3. **Elita, normalizacija i kapija odgovaraju zamrznutom opisu.** [Izbor elite](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/compensatory_mutation.py:38) isključuje `c` po identitetu, pogrešnu dimenziju i `NaN` troškove; sortira rastuće i uzima propisani udeo, najmanje `d+2`, odnosno odustaje ako ih nema dovoljno. Normalizacija koristi `(x−lo)/(hi−lo)`.

   Nulta varijansa daje nultu punu korelaciju; `NaN` korelacije polovina pretvaraju se u nule. Interleaved podele, slaganje znaka i oba praga `|ρ|≥0,5` pravilno su implementirani. Manje od tri tačke u bilo kojoj polovini blokira `gated`; jednodimenzionalna kovarijansa bezbedno završava bez kompenzacije. `_elite` sam ne odbacuje beskonačne troškove, ali standardni E4 cost-finder već odbacuje nekonačne evaluacije.

4. **Delta, disjunktnost i keševi su ispravni u E4 putanji.** Delta je stvarna neto promena posle osnovne mutacije, normalizovana opsegom. Početni `used` sadrži sve promenjene koordinate; partneri se ne ponavljaju i ne postaju izvori novih pomaka. Izbor je maksimum `|ρ|` među slobodnim, prihvatljivim partnerima.

   [Hook:74](/Users/danijel/Desktop/gadapt/gadapt/operations/mutation/population_mutation/base_candidate_solution_mutation_selector.py:74) pravilno snima stanje pre mutacije. Oba keša se poništavaju posle kompenzacije, pa sledi registracija konačnog kandidata. `VariableValue.value` je obična dodela bez skrivenih efekata; bezbednost granica zavisi od `_fit`. U ovoj putanji mutiraju se neevaluirani potomci, pa nema zadržavanja zastarele cene.

5. **`permuted` zahteva ograničeno tumačenje.** Za svaki korak zaista prenosi isti predloženi **normalizovani** `b·δ_i` na slučajnu slobodnu koordinatu, pre refleksije/mreže. Međutim, nije stroga permutacija celog skupa `ungated` pomaka: slučajni cilj menja `used`, pa naredni izvori mogu dobiti druge donorske partnere i nagibe. Reprodukovani skupovi pomaka bili su `{0,03; 0,01}` naspram `{0,03; 0,03}`. U D=2 postoji najviše jedan slobodan partner, pa prostorna randomizacija nema efekta.

   Takođe, `permuted` nema kapiju, dok je poređeni G ima. Zato H64k3 meri razliku kompletnih režima, a ne izolovano tačnost koordinatnog povezivanja. Strogo očuvanje pomaka zahtevalo bi prethodno formiranje svih parova/pomaka, pa tek onda raspoređivanje ciljeva.

6. **Zaobilaženja hooka i RNG ne kompromituju E4.** Crossover mutacija protiv duplikata, direktni `mutate_candidate_solution` i imigracija zaobilaze kompenzaciju. Međutim, [E4 konfiguracija:41](/Users/danijel/Desktop/gadapt/research/i64/e4_study.py:41) postavlja `ensure_unique_individuals=False`, `immigration_number=0`, a adaptivna imigracija ostaje isključena. Sa `mode=None` novi hook ne poziva kompenzator niti dodatni RNG; potvrđeno diffom i izolovanom proverom.

7. **Trošak i poređenje kapije:** računanje matrica je `O(kd²)` po mutiranom kandidatu, uz izbor/sortiranje elite `O(n log n)` i memoriju `O(kd+d²)`. Nema dodatnih evaluacija. `gated`/`ungated` nemaju dodatnu konfiguracionu konfuziju; kapija uključuje i izbor najboljeg prolaznog partnera, ne samo odbacivanje unapred izabranog para.

**Potrebno ponavljanje:** za ispravljenu obećanu kontrolu ponoviti svih **6.300 `gadapt_cr` pokretanja** i ponovo izračunati simultane intervale svih sedam kontrasta. Postojeće `cg`, `cu`, `cp` i arhivirane E rezultate zadržati. Zamrznute artefakte sačuvati; korekciju voditi kao novu verziju protokola. Stroža `permuted` kontrola iz tačke 5 zahtevala bi zasebno novih 6.300 `cp` pokretanja.