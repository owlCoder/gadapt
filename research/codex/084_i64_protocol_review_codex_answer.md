**FREEZE AFTER FIXES.** Nacrt je održiv, ali sada dopušta različite rezultate zavisno od tumačenja metrike, konfiguracije i prekida. Pregled je bio read-only; ništa nije menjano niti pokretano. Sledeći pasusi su predloženi zamenski tekst za blokirajuće stavke [protokola](/Users/danijel/Desktop/gadapt/research/ITERATION64_PROTOCOL.md:14).

1. **Konfiguracije i vernost replikacije.** „GAdapt podrazumevano“ nije mentorova konfiguracija. Postoji i konkretna zamka: `saturation_criterias=[15]` prepisuje skalarno podešavanje 20.

   > „R koristi klon `0e388356ba954d17a8d78941bd18a4580cc9d210`, originalni GAdapt 0.5.0 i zaključano kompatibilno okruženje. Eksplicitno postavljamo `saturation_criterias=[20]`, populaciju 64, elitizam 50%, limit 600 i četiri uključene konfiguracije. Zadržavamo originalne razlike zaustavljanja, uključujući DE toleranciju i callback. PyGAD koristi mentorovu selekciju prema rangu bez vraćanja, BLX-α=0,5 i mutacione verovatnoće 0,1 odnosno [0,6;0,1]. GAdapt koristi originalne operatore, mutacione procente 60/60, imigraciju 0 i isključenu jedinstvenost. Manifest beleži sva razrešena podešavanja. E koristi dve jasno imenovane grane istog zamrznutog izvora: GAdapt-M i identičnu konfiguraciju sa presetom. Eventualna razlika prema istorijskoj biblioteci posebno se prijavljuje.“

2. **Normalizacija i transformacije.** Neodređeni `scale` može promeniti rangiranje.

   > „Za funkciju/dimenziju i definišemo \(s_i=\operatorname{median}_{k=1}^{4096}[f_i(U_k)-f_i^\*]>0\), gde su \(U_k\) unapred generisane uniformne tačke originalnog domena. Uzorci i numeričke vrednosti normalizatora arhiviraju se pre optimizacije; isti \(s_i\) važi za sve algoritme i transformacije. Definišemo \(g=\max(0,(f-f^\*)/s_i)\). Vrednost ispod \(f^\*-10^{-12}s_i\) blokira instrument.
   >
   > Minimum je 0 za sve funkcije osim Styblinski–Tang: \(f^\*=D(a^4-16a^2+5a)/2\), gde je a negativni globalno minimizujući koren \(4a^3-32a+5=0\); koristimo visoku preciznost, ne zaokruženo −39,16617D.
   >
   > U E optimizatori rade na \(y\in[0,1]^D\). Original je \(f(l+wy)\); pomerena/rotirana funkcija je \(f(x^\*+wQ^\top(y-o))\), gde je \(w=u-l\), \(o\in[0,25;0,75]^D\), a Q ortogonalna; za samo pomeranje Q=I. Arhiviramo o, Q i odabrani \(x^\*\). Minimum ostaje dostižan. Rosenbrock zadržava originalni uzak opseg [0,5;1,5]; zaključak ne obuhvata standardni širi domen. Pomerena i rotirana Sphere moraju biti jednake do numeričke tolerancije.“

3. **Tačno brojanje i prekid.** Običan `Exception` GAdapt hvata; `exit_function` proverava granice generacija. Nijedan samostalno ne rešava tačan budžet.

   > „Jednonitni omotač broji svaki fizički poziv, uključujući duplikate, validacione all-min/all-max probe, PyGAD ručnu početnu evaluaciju, dodatne adaptive evaluacije, `best_solution()` ponovna računanja i DE callback. Keširani fitnes nije novi poziv. CMA brojači, `maxfevals`, restarti i završne evaluacije ne zamenjuju omotač. [PyGAD dokumentacija](https://pygad.readthedocs.io/en/latest/pygad.html) potvrđuje mogućnost dodatnih evaluacija kroz `best_solution()`.
   >
   > Pre zahteva B+1 omotač podiže namenski `BudgetReached(BaseException)`, uhvaćen isključivo u spoljašnjem drajveru. Poziv B se potpuno izvršava, zapisuje i vraća algoritmu. Nema lažnog fitnesa posle budžeta. Proveravamo da svaka zaključana biblioteka propušta signal.
   >
   > Primarni rezultat je najmanji konačan f među prvim B pozivima, uključujući probe; pri jednakosti uzimamo prvi vektor. Čuvamo kopiju vektora i fazu. Izvorni povratni rezultat beležimo odvojeno; pri nasilnom prekidu označavamo ga kao nedostupan, bez konstruisanja prividnog `GAResults`. Njegova semantika ne može istovremeno ostati očuvana i garantovati proizvoljan prekid usred generacije.“

   Nezavisna naknadna provera svedoka ima zaseban brojač i ne poboljšava rezultat. Iz I63 preuzeti provenijenciju, a ne automatski njegov način završavanja generacije.

4. **Prerano završavanje i rizik.**

   > „U E uklanjamo spoljašnju stagnaciju. Pri izvornom završetku pre B sledi unapred definisan restart sa zajedničkim preostalim budžetom. Obična CMA grana zato se imenuje CMA sa restartima iste populacije; IPOP/BIPOP zadržavaju svoje rasporede. Restart pravila važe i za DE. `tol=0` sam ne garantuje nastavak na potpuno konstantnoj populaciji; kriterijum je opisan u [SciPy dokumentaciji](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.differential_evolution.html).
   >
   > Za n=100 sortiramo L rastuće: \(\widehat{\mathrm{CVaR}}_{0,9}=10^{-1}\sum_{r=91}^{100}L_{(r)}\). Veze zadržavaju multiplicitet; ne prosečujemo sve vrednosti iznad empirijskog kvantila. Koristimo \(L=g/(1+g)\), a algoritamski otkaz L=1. Greška instrumenta znači STOP, ne loš algoritamski ishod. Agregat je ponderisani prosek ćelijskih CVaR.“

5. **ECDF, izuzetak i višestruko testiranje.** Wilcoxon sam ne testira razliku očekivanih ECDF površina.

   > „Za svaki cilj τ, \(T_\tau\) je prvi stvarni poziv sa \(g\le\tau\), ili ∞. Površina pokretanja je
   > \[
   > A=\frac1{3B}\sum_{\tau\in\{10^{-2},10^{-4},10^{-6}\}}\sum_{b=1}^{B}1(T_\tau\le b).
   > \]
   > Nedostizanje daje nulu. U R/S0 B=12.000 služi analizi putanje: posle izvornog završetka najbolje ostaje konstantno, bez dodatnih poziva; završna preciznost koristi izvorni kraj.
   >
   > Funkcije imaju težinu 1/9, njihove dimenzije jednake unutrašnje težine, a E varijante 1/3. Definišemo \(\Delta A_j=E_w[A_G-A_j]\) i \(\Delta M_j=M_j-M_G\), gde je M ponderisani prosek ćelijskih završnih medijana g. Neodređene razlike beskonačnosti blokiraju odgovarajući zaključak.
   >
   > H64a prolazi ako svi konkurenti imaju donju simultanu granicu ΔA>0, ili postoji jedan e za koji to važi za sve j≠e i donja granica ΔMₑ>0. E obuhvata svih deset konkurenata, uključujući preset; fokalni GAdapt se ne bira naknadno. Veze nisu pobede. Suprotan ishod zahteva dva dokazano efikasnija konkurenta, ili jednog dokazano efikasnijeg i preciznijeg; ostalo je neodlučeno.
   >
   > Primarni testovi koriste 20.000 stratifikovanih bootstrap uzoraka celih uparenih vektora i simultane intervale preko maksimalnog standardizovanog odstupanja. Porodice su S0: šest kontrasta, α=0,01; R: šest, α=0,01; E-H64a: dvadeset, α=0,02; H64b: četiri, α=0,01. Ukupni nominalni FWER je 0,05; bootstrap nije konačnouzoračka garancija. Nulta procenjena varijansa blokira potvrdu. Snimak 3.000 je opisni.
   >
   > H64b zahteva \(R_0>0\), donju granicu \(0,8R_0-R_{\rm preset}\ge0\) i donje granice razlika uspešnosti ≥−0,05 za sva tri cilja. Dva nulta rizika nisu poboljšanje.“

6. **Razvoj i zamrzavanje.**

   > „Sada zamrzavamo estimande, težine, ciljeve, budžete, roster i pravila odlučivanja. Samo razvoj bira CMA σ₀, populacije, tolerancije, granice i IPOP/BIPOP raspored, odnosno korak, adaptaciju i restart (1+1)-ES, iz unapred navedenih kandidata uz jednak kalibracioni budžet. [Pycma dokumentacija](https://cma-es.github.io/apidocs-pycma/cma.evolution_strategy.html) razlikuje te restart mehanizme. PyGAD operatori ostaju originalni; nema automatskog preslikavanja njihovih verovatnoća na GAdapt procente.
   >
   > Za sortiranu ćeliju c=3i+v koristimo seme \(64.000.000+1.000.000p+1.000c+s\): p=0/1/2/3 za S0/razvoj/R/E; s=1…20/5/100/100. Odvojena semena transformacija i normalizatora ulaze u manifest. Postavljamo Python, NumPy i bibliotečke RNG; isto seme ne znači identičnu početnu populaciju. Preset-off mora dati bit-identičan trag odgovarajuće kontrolne grane.“

7. **Najjeftiniji S0 i CPU.**

   > „S0 obuhvata svih 21 originalnih ćelija, četiri originalne konfiguracije i prvih 20 semena p=0: 1.680 pokretanja, jedno jezgro, originalna stagnacija i bez dodatnog evaluacionog limita. Objavljujemo originalne proseke/generacije, stvarne pozive i navedene kontraste. Ishod može biti podržano, suprotno ili neodlučeno. GO zavisi od ispravnosti instrumenta i troška, ne od pozitivnog rangiranja.“

   Nijedan mali dizajn ne garantuje odlučan odgovor za nepoznatu veličinu efekta u dva sata.

   Procena je
   \[
   T_{\rm CPU}=\bigl[N_ft_f+\sum_aN_{{gen},a}h_a+T_{\rm start}+T_{\rm zapis}+T_{\rm analiza}\bigr]/3600,
   \]
   uz početnu aproksimaciju \(h_G=0,001(P/32)(D/10)\) sekundi. S0 planirati 1–2 sata; R približno 5–10; razvoj 0,5–2 po kompletnom kandidatskom rosteru; E okvirno 10–40, sve uslovno na razvojno merenje. Sam GAdapt generacijski overhead iznosi približno 0,12/0,60/2,25 sati za S0/R/E. E sa 11 konfiguracija ima **831,6 miliona**, sa devet 680,4 miliona poziva. I64-I ostaje zaseban: 528 miliona AC poziva daje 293–2.347 sati pri 2–16 ms, pre režije.

Pre potvrde zahtevati create-once identitet, heševe svih tranzitivnih izvora i gateove brojanja, transformacija, prekida i svedoka. S0 nije deo potvrdnog uzorka.