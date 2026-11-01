# I33 Korak 5/5 — audit literature i odluka o stvarnoj doktorskoj hipotezi

**Datum:** 22. oktobar 2026. **Status:** I33 literatura/gap audit; ovo samo po sebi nije potvrda originalnosti. Numerički GÉANT eksperimenti se moraju posebno prikazati u [I33_REPORT_SR.md](ITERATION33_REPORT_SR.md) tek nakon izvršenja i audita svih sirovih podataka. Originalni GAdapt upstream nije menjan.

## Relevantni prethodni radovi (linkovi provereni prema javnim stranicama)

1. **Nathan Sankary i Avi Ostfeld (2018), _Stochastic Scenario Evaluation in Evolutionary Algorithms Used for Robust Scenario-Based Optimization_, Water Resources Research, DOI 10.1002/2017WR022068.** [Izdavačev rad](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017WR022068). Eksplicitno problematizuje broj obrađenih rešenja prema broju scenario evaluacija pri fiksnom budžetu, stohastičko menjanje skupa scenarija i robusnost u infrastrukturnim problemima. **Ne smemo tvrditi da je scenario subsampling, early-stop/racing ili budžet kao fenomen izmišljen u I29–I33.** Ovaj rad ne smemo bez detaljnog poređenja predstavljati kao identičan našem determinističkom first-fail, niti kao dokaz da je naš rezultat nov.
2. **Adaptive Operator Selection With Bandits for a Multiobjective Evolutionary Algorithm Based on Decomposition**, IEEE Transactions on Evolutionary Computation (2013), DOI [10.1109/TEVC.2013.2239648](https://doi.org/10.1109/TEVC.2013.2239648). Adaptivni izbor operatora pomoću bandita i istorije poboljšanja **već postoji**; prosti UCB ili promena skalarne reward funkcije u GAdapt nije automatska naučna inovacija. Slično i stariji Fialho i saradnici, _Adaptive Operator Selection with Dynamic Multi-Armed Bandits_.
3. **Liang i saradnici, _A survey of surrogate-assisted evolutionary algorithms for expensive optimization_**, online 2024, Journal of Membrane Computing (2025), DOI [10.1007/s41965-024-00165-w](https://doi.org/10.1007/s41965-024-00165-w). Izuzetno obimna literatura već obuhvata optimizaciju resursno skupih funkcija, surrogate predviđanje i adaptivno smanjivanje broja skupih evaluacija. Nije dovoljno reći da imamo `budget-aware` ili `fewer evaluations`.
4. **DRL-AEOSF, _A deep reinforcement learning-assisted evolutionary operator selection framework for constrained optimization problems_**, Swarm and Evolutionary Computation 107 (2026), DOI [10.1016/j.swevo.2026.102453](https://doi.org/10.1016/j.swevo.2026.102453). Postoji nov rad koji kombinuje stanje populacije i feasibility informacije sa učenim izborom operatora, pa ni RL + constraints nije nužno novo.
5. **Ledford i Regli (IJCAI 2026), _Cost of Structural Learning Under Censored Feedback: A Threshold-Bandit Approach_**, DOI [10.24963/ijcai.2026/495](https://doi.org/10.24963/ijcai.2026/495). Cenzurisani feedback u bandit učenju i identifikabilnost su postojeća naučna tema — taj rad koristi **drugu (cooperative threshold-bandit)** formulaciju i ne treba neosnovano tvrditi da pokriva naš konkretan genetic-operator/scenario-racing problem. Njegovo postojanje je razlog da se preciznije proveri originalnost bilo koje censored-credit ideje.

## Konkretna otvorena istraživačka praznina (hipoteza, NE potvrđena novina)

Umesto generičkog `first-failure screening`, testirati sistematski **troškovno normalizovanu i cenzurom svesnu atribuciju korisnosti mutacionim operatorima u pravom GAdapt-u**, uz:

- Vidljive `(prvi prekršeni scenario, stvarno plaćen broj evaluacija, fizičko kršenje, potpuna ili delimična opservacija)`. *Neizvršeni scenariji nisu nule ili automatski uspehi.*
- **Odvojenu** metriku `(1) verifikovana robust-feasible poboljšanja` i `(2) poboljšanja stvarno izmerenog rezidualnog constraint stanja`, sa eksplicitnom cenom/rasponom nesigurnosti `c` i pažljivom obradom `unknown`. Smanjenje broja AC nije samo po sebi reward, jer inače nagrađuje operator koji stalno generiše očigledno neuspešne jedinke.
- Regulator koji ne uči iz potencijalno pristrasnih `censored_score` kao da je puni source mean economic cost; jedinke koje završe sa nepotpunim evaluacijama nemaju punu ekonomsku cenu.
- Poređenje ne samo prema originalnom legacy GAdapt-u, nego i prema **I26 UCB scalar feasibility**, **I26 scenario feasibility UCB (neuspešan na IEEE118 I28 6/12 prema originalnom 8/12)**, statičkom `stop_fixed`, `full_censored`, DE i domenski jakim lokalnim baseline-ovima, sve na **istom source fizičkom problemu i zaista plaćenom budžetu**.
- **Nezavisan train/test** između mreža/topologija i realnih industrijskih profila, a ne samo umetnuti 1/2/8% veštački stres. Bez unapred zamrznutih primarnih metrika, n≥30–50 novih seedova i korekcije za višestruka poređenja nema generalnih naučnih tvrdnji.

Predložena matematička forma za dalji rad (ne finalni doprinos):
`reward(a,t) = (verified_robust_improvement(a,t) + beta * measured_constraint_progress(a,t)) / genuinely_paid_scenario_calls(a,t)`, gde je **`measured_constraint_progress` definisan samo nad odgovarajućim istinski izmerenim scenarijima** uz dokumentovanu selekcionu pristrasnost; zato gornja prosta formula sama po sebi nije spremna za publikaciju. Ne treba računati nedostajuće `scenario t` kao nula, ni zaključivati da su isti kandidati upoređeni ako su različite evolutivne trajektorije.

## Naučna go/no-go pravila posle I33

**Go** samo ako postoje različite topologije i stvarno različiti infrastrukturni evaluatori gde poznata rana selekcija pokazuje jasno opisiv **mehanizam** i imamo realan razlog da operator-level izbor donese dodatnu korist u odnosu na najjače već postojeće metode.

**No-go / pivot** ako se signal gubi na telekom domenu, ima nula validnih rezultata ili je ograničenje samo veštački cost cap. U tom slučaju sledeći legitimni predmet disertacije može biti *negativna analiza pristrasnosti i korektna procena troškova feasibility-aware GA za infrastrukturu*, ali originalni doktorski doprinos i dalje zahteva mentorovu naučnu saglasnost. **Ne praviti pet novih heuristika da bi se sakrio negativan rezultat.**

**Napomena:** svi navedeni izvori su *relevantni predmeti poređenja*, ne potpun sistematski pregled literature, a radovi o decoupled constrained Bayesian optimization, racing, censored-cost bandits i network robust planning tek zahtevaju dopunski ekspertski pregled.
