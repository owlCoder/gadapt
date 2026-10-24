Predlažem **I61 kao replikaciju interakcije uz očuvan I56 instrument**, sa razvojnim izborom informativnih uslova. I56 nalaz je mali: θₐ = 0,0205, dok šest blokova ima T = 1 u svim granama. Zato novi test treba planirati za efekat oko 0,02, bez pretpostavljanja da neinformativni blokovi nose pozitivan efekat. Izvori: [I56 protokol](research/ITERATION56_PROTOCOL.md), [pojašnjenja](research/ITERATION56_CLARIFICATIONS.md), [izveštaj](research/ITERATION56_REPORT_SR.md).

Ponovna upotreba I58 mreža jeste legitimna: H61 proverava drugi kontrast, a nove realizacije opterećenja i nezavisna semena omogućavaju novo testiranje. Prigovor je da poznati I58 rezultati mogu usmeriti izbor mreža, budžeta ili instrumenta; iste topologije ne daju potpuno nezavisnu spoljašnju validaciju. **Preporučujem sva tri I58 primarna sistema, bez izbora prema njihovim rezultatima**, uz eksplicitnu oznaku „replikacija na mrežama odvojenim od I56, uz ponovljene I58 topologije“. Za tvrdnju o potpuno neviđenim mrežama potrebna je naredna studija.

Sledi predloženi tačan tekst protokola. Status je **nacrt za zamrzavanje**, bez izvršenog razvoja ili testa.

1. **Pitanje i skup.** I61 proverava da li se pozitivna interakcija adaptivne politike mutacije i FR naspram statičke kazne ponavlja na `case30`, `case39`, `case24_ieee_rts`, tim redom. Koristi se `BusORPD`: jedna VG kontrola po generatorskoj sabirnici, primenjena na sve aktivne generatore na njoj; ostali model, granice i PF podešavanja nasleđuju I56. Razvojni scenariji su **(0,97; 6101), (1,03; 6102)**; test scenariji **(0,92; 6201), (1,02; 6202), (1,08; 6203)**, gde par označava faktor opterećenja i seme scenarija; `spread=0,1`. Razvoj i test ne koriste I58 scenarije 301–303, reference ili ishode. OPF neuspeh znači izuzimanje bez zamene, pre optimizacije odgovarajuće faze. Razvoj zahteva oba scenarija svake mreže; test zahteva najmanje jedan preostali scenario svake mreže.

2. **Instrument i četiri grane.** Grane su `AD-N/SP`, `AD-N/FR`, `FX-T/SP`, `FX-T/FR`. Koriste se I56 `CHT`, `CHTCostFinder`, `StudyFactory` i fiksni selektori, uz biblioteku iz commita `17e9ce7`; podudaranje sa arhiviranim I56 instrumentom proverava se pre razvoja. Bibliotečki FR/ε nije aktiviran. Važi:
   \[
   SP=f+1000V;\quad
   FR=\begin{cases}
   1+f/(f+f_{\rm ref}),&V=0\\
   2+V/(1+V),&V>0\\
   3,&\text{neuspeo PF}.
   \end{cases}
   \]
   `f_ref` su gubici kontinualnog OPF-a scenarija. \(V=\sum_k\max(0,c_k-10^{-6})\); neuspeo ili nekonačan PF ima \(f=2f_{\rm ref}, V=10\), nikada nije izvodljiv i troši poziv. AD-N oba adaptivna signala čita iz odgovarajućeg CHT skalara. AD-C i FX-M nisu test grane.

3. **Reference i cilj.** Pre razvojnog izbora izvršavaju se razvojne reference: svaki scenario × R∈{9,17,33} × I56 {SP,AP,FR,EC}/AD-N × jedno seme, po 30.000 PF poziva. Test reference nastaju tek posle konačnog zamrzavanja, za izabrani R svake mreže, iste četiri referentne grane i dva semena, po 30.000 poziva. L* je najmanji izvodljiv gubitak među uspešnim referentnim pokretanjima; cilj je \(V=0\) i \(f\le1,01L^*+0,01\) MW. Ako uspešne reference nemaju izvodljivo rešenje, cilj je samo izvodljivost. Ako nema nijedne uspešne reference za instancu, faza staje. L* nije optimum.

4. **Izbor B i R.** Referentna grana za izbor težine zadatka je **AD-N/SP**, nezavisno od znaka interakcije. Na oba razvojna scenarija, svakom R i pet semena izvršava se putanja od 24.000 poziva. Iz prvog dostizanja izračunava se \(T_B=\min(h/B,1)\) za B∈{3000,6000,12000,24000}; nedostizanje daje 1. Par prolazi ako je medijana \(T_B\) **na svakom razvojnom scenariju** u [0,3;0,8]. Po mreži se bira najmanji prolazni B; veze rešava redosled R=17,9,33. Bez prolaznog para bilo koje mreže: STOP, bez testiranja i bez naknadnog proširivanja mreže kandidata.

5. **FX-T kalibracija.** Zadržava se I56 postupak: R=17, oba razvojna scenarija, sve tri mreže, tri semena; svaka mreža koristi svoj izabrani B. Za SP i FR zasebno ispituje se
   \[
   a\in\{0,25;0,5;0,75\},\
   b\in\{0,1;0,2;0,4\},\
   \sigma\in\{0,02;0,05;0,15\}.
   \]
   Bira se **jedan globalni vektor po CHT-u**, najmanjeg srednjeg T preko razvojnih pokretanja; veze → prvi indeks `FXT_GRID`. Nepotpuna kalibraciona mreža znači STOP. Važe I56 formule za tačne k i v, uniformni izbor bez vraćanja, fiksni σ, isti Gaus/reset operatori i postojeće popravke duplikata. Kalibracija na R=17 prenosi se na izabrani R, kao u I56. Test podaci nikada ne podešavaju FX-T.

6. **Nezavisna razvojna proba i snaga.** Sa izabranim B/R i FX-T izvršavaju se četiri grane na deset novih semena po razvojnom scenariju. Svaka mreža mora imati: medijanu AD-N/SP u [0,3;0,8] na oba scenarija; najmanje 20% dostizanja u svakoj grani preko dva scenarija; pozitivnu empirijsku varijansu uparenog kontrasta d. Neprolaz znači STOP, bez ponovnog izbora B/R.

   Za snagu se po mreži udružuju kompletni upareni četvorovektori razvojne probe; pretpostavlja se prenos te raspodele na test scenarije. Alternativa θₐ=0,02 konstruiše se eksponencijalnim težinama \(w_\lambda(u)\propto\exp(\lambda d_u)\), normalizovanim unutar mreže, sa zajedničkim λ koji daje jednako ponderisan prosek 0,02. Čuvaju se stvarni četvorovektori, granice i cenzura. **Degenerisan blok ostaje degenerisan; ne dodaje mu se efekat.** Ako alternativa nije dostižna postojećom podrškom, snaga je neprocenjiva i test ne počinje.

   Za n∈{20,40,60,80} simulira se 1000 eksperimenata, sa konačnom analizom iz tačke 8. Bira se najmanji n čija donja 95% Wilsonova granica simulirane snage iznosi ≥0,80; inače STOP. Snaga je uslovna planska procena, ne garancija.

7. **Semena i zamrzavanje.** Koristi se
   \[
   seed=10^7p+10^5i+10^3R+100j+s.
   \]
   i=0..2; razvoj j=0,1, test j=2..4. Namene p=61 razvojne reference, 62 izbor B/R, 63 FX-T, 64 proba, 65 test reference, 66 test. s=1 za razvojne reference; 1..5 za izbor; 1..3 za kalibraciju; 1..10 za probu; 1,2 za test reference; 1..n za test. Iste početne populacije četiri grane proveravaju se asercijom. Seju se Python i NumPy RNG. Simulacija koristi seme 61023; bootstrap 61. B/R, FX-T, n, protokol, kod, zavisnosti i biblioteka heširaju se **pre test referenci**; reference dodatno pre testa.

8. **Ishod i zaključivanje.** \(T=h/B_i\), odnosno 1 pri nedostizanju. Jedinica je mreža × izabrani R × scenario × seme:
   \[
   d_u=[T_{AD,FR}-T_{FX,FR}]-[T_{AD,SP}-T_{FX,SP}],
   \quad
   \theta_a=\tfrac13\sum_i\operatorname{mean}_{j}
   \operatorname{mean}_{s}d_{ijs}.
   \]
   Koristi se I56 estimator: jednake težine blokova i scenarija, 20.000 stratifikovanih bootstrap ponavljanja celih uparenih vektora unutar ćelija, percentilni 95% interval. **H61 je podržana samo ako je njegova donja granica >0.** Pozitivan znak znači da adaptacija relativno više gubi prema FX-T pod FR nego pod SP.

   Neuspeh tog kriterijuma nije dokaz odsustva interakcije. Unapred određena zona zanemarljivosti je [−0,02;+0,02]: 90% interval potpuno unutar nje podržava praktičnu ekvivalenciju; 95% interval potpuno ispod nule podržava suprotan smer; ostalo je neodlučno. Pozitivna i praktično zanemarljiva interakcija mogu istovremeno biti podržane. Zaključivanje je uslovno na izabrane uslove, scenarije, reference i kalibraciju.

9. **Izvršavanje i zaustavljanje.** Populacija 32, bez sondiranja i imigracije; `exit_check="generations"`, `number_of_generations=10**9`, `timeout=10**6`, prekid po stvarnom PF budžetu, bez prekida pri cilju. Svako pokretanje koristi nov proces. Greška ili nedovoljno poziva → jedno ponavljanje istim semenom; ponovljena greška izuzima celu uparenu jedinicu. Prazna ćelija onemogućava primarno zaključivanje. Svako izuzimanje prati analiza osetljivosti: završeni ishodi ostaju, samo neuspeli dobijaju T=1. Test degenerisani blokovi ostaju sa punom težinom. Nema produžavanja budžeta, dopunjavanja semena ili zaustavljanja prema značajnosti. Nezavisna provera svedoka L*/cilja i izlaza, vezana heševima za podatke, obavezna je; neuspeh znači nedostupan zaključak.

10. **Trošak i implementacija.** Maksimum bez ponavljanja: razvojne reference 2,16 miliona, izbor 2,16, FX-T 23,328, proba 5,76, test reference 2,16, test 69,12: **104,688 miliona PF poziva**. Pri 2,5–3 ms/PF: **72,7–87,2 CPU-sata**, idealno 7,3–8,7 sati na deset jezgara; OPF, provere, Python i simulacija snage dodaju trošak. Jedno ponavljanje svega udvostručuje maksimum. Za B=6000 svuda i n=40 plan je 22,392 miliona PF, odnosno 15,6–18,7 CPU-sati. [I58 kod](research/iteration58_validation.py) nema merenje trajanja PF-a; ove brzine su planska pretpostavka.

   Novi drajver parametrizuje I56 `_run`, `instances`, `make_task`, `stage_dev_fxt`, `contrast_tasks`, `unit_contrasts`, `d_a`, `theta`, `bootstrap`, `execute`; zamenjuje simulaciju `stage_rehearsal`. Iz I58 preuzima `BusORPD`, `WitnessEvaluator` i obrasce `build_manifest`/`same_provenance`; `independent_check` se parametrizuje scenarijem i R. Dodaju se izbor B/R, beleženje vremena i svedoka, provera četiri početne populacije i regresione provere brojača/instrumenta.

V4 koristi početnu medijanu |f|, arctan skalar i tačan ključ za preživele; time menja numeričke signale relevantne za H56. Zato pripada zasebnoj studiji prenosa na biblioteku. Nijedan fajl nije menjan; i58_/i59_/i60_ rezultati i logovi nisu otvarani.