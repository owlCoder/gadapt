# Istraživački pravac za disertaciju: GAdapt za skupe infrastrukturne simulacije

**Status 21.10.2026: radna hipoteza, NIJE razvijen ni potvrđen naučno nov algoritam.** Mentorov cilj je unapređenje **stvarnog GAdapt-a**, ne zamena paketom koji samo menja ime GA. Industrijska relevantnost podrazumeva validirane fizičke granice i merljiv resursni budžet; nije isto što i dokaz operativne bezbednosti.

## Šta literatura već poznaje (i šta ne smemo nazvati svojim izumom)

- **Adaptive operator selection, multi-armed bandit i credit assignment** su razvijeni mnogo pre ovog projekta: Fialho, da Costa, Schoenauer, Sebag, *Adaptive Operator Selection with Dynamic Multi-Armed Bandits* (GECCO 2008), https://inria.hal.science/inria-00278542v1/document ; Maturana, Lardeux, Saubion, *Autonomous Operator Management for Evolutionary Algorithms*, Journal of Heuristics 16 (2010) 881–909, https://link.springer.com/chapter/10.1007/978-3-642-21434-9_7 .
- **Rangiranje ograničenja nije novo**: Runarsson & Yao (2000), *Stochastic Ranking for Constrained Evolutionary Optimization*, IEEE TEC, DOI:10.1109/4235.873238; i Deb (2000), *An Efficient Constraint Handling Method for Genetic Algorithms*, Computer Methods in Applied Mechanics and Engineering (poznato pravilo izvodljivosti).
- **Surrogate-assisted optimization** je dobro istražena: Liang et al., *A survey of surrogate-assisted evolutionary algorithms for expensive optimization* (2024/2025), DOI:10.1007/s41965-024-00165-w; Liu et al. (2024), *Surrogate-assisted evolutionary algorithms for expensive combinatorial optimization: a survey*, DOI:10.1007/s40747-024-01465-5.
- **GAdapt originalni paket** i dosadašnji dodaci nude cost-diversity/parent-diversity mutacije, opt-in bandit izbor, feasibility credit i strogo upareno merenje pre-posle. Postojanje takvog koda **ne dokazuje** novu metodološku ideju ili superiornost.

## Potencijalna ispitiva, falsifikabilna hipoteza

U problemima s realnim granicama, zasićenim reaktivnim resursima, skupim AC solverom i povremenim neuspehom, kvalitet varijacionog operatora može biti različit u fazi pronalaženja izvodljivosti i kasnije fazi optimizacije. Moguće je da GAdapt modul koji *resursno svesno* prilagođava operatore prema fizičkom napretku bolje koristi ograničeni broj simulacija nego neadaptivni izbor — **ali nije poznato da li je taj spoj originalan ili koristan**.

Minimalan korektan eksperimentalni okvir:
1. Prvo nezavisno rešiti ili proveriti **isti** fizički problem i ograničenja domenskim referentnim solverom. U RTE1888 trenutno postoji neusaglašena originalna i konvertovana slack sabirnica; dok se to ne razreši, ne porediti izvorni AC-OPF sa konvertovanim PF heuristikama.
2. Mera izvodljivosti mora biti zajednička, normalizovana i povezana sa originalnom verifikacijom: V, generator P/Q, slack P/Q i termički izvorno ocenjene MVA granice. Razdvojiti *neuspeh solvera* od pravog fizičkog kršenja. Optimizaciona funkcija ne sme vratiti navodno ostvareni optimalni MW rezultat kada nije izvodljivo.
3. Originalni GAdapt, fiksni AOS, UCB, nasumični izbor operatora, feasibility-first bez AOS, SLSQP, domain AC-OPF i napredna stohastička metoda moraju koristiti identičnu fizičku formulaciju gde su primereni. Brojati **svaki** stvarni simulator poziv, uključujući ponovljene pre/post, neuspehe i finalnu verifikaciju zasebno. Ne izjednačavati wrapper cost_function pozive sa simulatorom.
4. Nove hipoteze naspram prethodno poznatog AOS-a oblikovati samo nakon pregleda konkretnih radova, ne dodavati proizvoljno više pragova i zvati ih inovacijom. Treba ispitati napredovanje kroz faze, efekat skupo plaćene informacije o korisnosti operatora i trošak prikupljanja kredita.
5. Zabeležiti: stopu izvodljivosti, vreme i pozive do prvog izvodljivog rešenja, medijanu i najgori kvantil među svim pokretanjima, gubitke *samo za izvodljive* uz iskreno tretiranje neuspeha, budžetsku efikasnost, raspodelu selekcije i operatora, greške solvera, više nezavisnih semena i ispravljene višestruke statističke testove.
6. Dva javna infrastrukturna domena (elektroenergetski AC i telekomunikacioni planovi) potrebna su za preliminarnu prenosivost. Nijedan javni istorijski podatak nije dokaz rada u pravoj industrijskoj proizvodnji; posebno MATPOWER RTE scenario izričito zabranjuje upotrebu za upravljanje/planiranje stvarne mreže.

## Kako ćemo prepoznati da ideja ne uspeva

Ako obično pravilo izvodljivosti bez adaptacije operatora daje iste ili bolje rezultate, a adaptivni credit troši više AC poziva ili povećava najgori slučaj, **hipoteza pada**. Tada je naučno vrednije objaviti negativan metodološki rezultat nego tvrditi da je algoritam revolucionaran.

## Naredni tehnički koraci

Završiti slack/reference provenijenciju iz iteracije 9 i ograničeni eksperiment iteracije 10. Tek zatim, u zasebno fiksiranom protokolu, postaviti zaista isti verified AC-OPF zadatak i domenski solver, pa razvijati i testirati originalnu modifikaciju GAdapt-a. Ovo je program istraživanja, ne potvrđen doprinos doktoratu.
