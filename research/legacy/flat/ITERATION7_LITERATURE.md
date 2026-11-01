# Iteracija 7 — prior art i evidencija da hipoteza nije nova sama po sebi
**Ažurirano 21.10.2026.** Ovo je preliminarna, a ne iscrpna sistematska
bibliografska revizija. Provereni su izdavački izvori, a radovi ne
predstavljaju dokaz da nijedan srodan mehanizam nije objavljen.

## Ograničenja i restauracija izvodljivosti
- **Deb, K. (2000).** *An efficient constraint handling method for
  genetic algorithms*. Computer Methods in Applied Mechanics and
  Engineering 186, 311–338. DOI
  [10.1016/S0045-7825(99)00389-8](https://doi.org/10.1016/S0045-7825(99)00389-8).
  Relacije između izvodljivih i neizvodljivih jedinki i rangiranje
  ne mogu biti samostalna doktorска novost GAdapt-a.
- **Runarsson, T. P.; Yao, X. (2000).** *Stochastic ranking for constrained
  evolutionary optimization*. IEEE Transactions on Evolutionary
  Computation 4(3), 284–294.
  [DOI 10.1109/4235.873238](https://doi.org/10.1109/4235.873238).
  Podešavanje ranga između cilja i ograničenja je poznato,
  uključujući rizike penalizacionih funkcija.
- **Coello Coello, C. A. (2002).** *Theoretical and numerical
  constraint-handling techniques used with evolutionary algorithms:
  a survey of the state of the art*. CMAME 191, 1245–1287.
  [DOI 10.1016/S0045-7825(01)00323-1](https://doi.org/10.1016/S0045-7825(01)00323-1).
  Obuhvata penalitete, izvodljivost, popravku, specijalne
  reprezentacije, dekodere, hibridizaciju, domination i multipravila.
  Pre formulacije novog constraint-handling mehanizma obavezno
  uporediti sa ovom literaturom i novijim radovima.

## Memetika, budžet i skupe fizičke evaluacije
- **Neri, F.; Cotta, C.; Moscato, P. (ur., 2012).**
  *Handbook of Memetic Algorithms*. Springer, Studies in
  Computational Intelligence 379.
  [DOI 10.1007/978-3-642-23247-3](https://doi.org/10.1007/978-3-642-23247-3).
  GA + lokalno usavršavanje, kao i fiksno ili adaptivno prebacivanje
  na lokalnu pretragu, nisu automatski originalni.
- **Constraint-handling techniques in surrogate-assisted evolutionary
  optimization: An empirical study** (2018), *Applied Soft Computing*
  73, 215–229.
  [DOI 10.1016/j.asoc.2018.08.016](https://doi.org/10.1016/j.asoc.2018.08.016).
  Optimizacija uz skupe simulacije i aproksimacija ukupnog kršenja
  već su istraživani. Treba izmeriti cenu obuke surogata i stvarnih
  validacionih PF poziva.
- **Li, K.; Li, F. (2026).** *Multi-Fidelity Methods for Optimization:
  A Survey*. ACM Computing Surveys 58(12).
  [DOI 10.1145/3801959](https://doi.org/10.1145/3801959).
  Multi-fidelity alokacija već ima široku teorijsku/primenjenu
  literaturu; jeftin model mora biti fizički kalibrisan i
  sistematski validiran na skupoj istini.
- **Liang, J. i saradnici (2025).** *A survey of surrogate-assisted
  evolutionary algorithms for expensive optimization*.
  Journal of Membrane Computing 7, 108–127.
  [DOI 10.1007/s41965-024-00165-w](https://doi.org/10.1007/s41965-024-00165-w).
  Sama zamena AC solvera surogatom nije dovoljna za doprinos.

## AC-OPF, podaci i ograničenja
- **Frank, S.; Steponavičė, I.; Rebennack, S. (2012).**
  *Optimal power flow: a bibliographic survey I — Formulations
  and deterministic methods*. Energy Systems 3, 221–258.
  [DOI 10.1007/s12667-012-0056-y](https://doi.org/10.1007/s12667-012-0056-y).
  Naziv AC-OPF ima precizno značenje uključujući generator P/Q
  dispečing, napone, fizičke tokove i zadate kontrole.
  Samo osam fiksnih generatorskih naponskih setpointa nije isti problem.
- **Josz, C.; Fliscounakis, S.; Maeght, J.; Panciatici, P. (2016).**
  *AC Power Flow Data in MATPOWER and QCQP Format: iTesla, RTE
  Snapshots, and PEGASE*. [arXiv:1603.01533](https://arxiv.org/abs/1603.01533).
  `case1888rte` ne sme se koristiti za stvarno
  operativno planiranje RTE mreže.
- **MATPOWER case format**, [Branch Data, RATE_A=0 for unlimited](https://matpower.app/manual/matpower/DataFileFormat.html).
  Ovaj primarni semantički podatak je ključna validaciona kontrola
  našeg eksperimenta: 455/2531 RATE_A=0 ne predstavlja
  455 fizičkih prekoračenja kada dođe do konverzije.

## Granice novosti / konkretni falsifikabilni uslovi
**Nije originalno:** feasibility-first (Deb), stohastičko rangiranje
(Runarsson/Yao), popravka jedinke, GA→SLSQP, adaptivni budžet
bez novog principa, sam izvorno veran proračun RATE_A.
Ovo su relevantni standardni kontrolni baselines.

**Još nevalidirana hipoteza za sledeće eksperimente:**
postoji li algoritamski mehanizam sa istovremeno kontrolisanim
troškom stvarnih AC evaluacija i mogućnošću fizičke
restauracije pod ispravno validiranim OPF ograničenjima,
koji nadmašuje dobro podešen domenski solver i standardne
evolutivne/budžetske pristupe **na unapred sakrivenim
nezavisnim instancama**, uključujući visoke kvantile neuspeha?
Moraju postojati teorijsko objašnjenje ili dokaziva osobina
novog mehanizma i ozbiljno poređenje sa navedenim radovima.

Pre implementacije novog kandidata potrebno je otvoriti
dokumentovan pretraživački protokol: upiti i datum,
identifikacija radova o feasibility restoration AC-OPF,
projekciji/popravci, adaptivnoj lokalnoj pretrazi,
surrogate and evaluation-cost-aware optimization,
kao i razlikovanje konkretno istražene novosti od poznatih
komponenti. Trenutna iteracija 7 nije potvrda takve novosti.
