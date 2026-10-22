# I38 — stvarna SNDlib Nobel-Germany zajednička mreža: **dokazana neizvodljivost izabrane EXPLICIT formulacije**

**Završeno 22.10.2026.** [Preregistracija](ITERATION38_PROTOCOL.md) komitovana pre bilo kakve I38 fizičke domenske/mrežne optimizacije. [Originalni uspešni CI sa izvornim merenjima i optimizacionim stdout-om](https://github.com/owlCoder/gadapt/actions/runs/39788866777); [originalni sirovi JSON+source manifest artifact](https://github.com/owlCoder/gadapt/actions/runs/39788866777/artifacts/12430875549) (`sha256:c4343a347a03f76da0f41b12ed3fd657e76ef7b731260dc2ad9842fd49d8d851`); [sačuvani svih 12 raw GAdapt stdout događaja i MILP status](results/iteration38_original_source_stdout_audit_4320.json). **Nijedno rešenje nije post-hoc 'ispravljano'.**

## Izvor i nezavisnost

- Izvorna mreža: [SNDlib Nobel-Germany native](https://sndlib.put.poznan.pl/download/sndlib-networks-native/nobel-germany.txt), SHA256 `35e58a3799d78d2ebfd2a557be2ba4a221ca17fc704cfdd13df56bb90c12a796`.
- Izvorni DFN 2005-02-15 hronološki saobraćaj: [288 originalnih petominutnih native matrica](https://sndlib.put.poznan.pl/download/directed-nobel-germany-DFN-aggregated-5min-over-1day-native.tgz), SHA256 `2c3ca706a8d5c9601eb4d144651816dfd956257c20f60111a8aceb5f07ab0100`; **272 usmerena demand para**, 17 čvorova, 26 linkova. TRAIN prvih 192 matrica i HOLDOUT narednih 96. To je istorijski agregiran dataset, ne savremena industrijska validacija.
- Model je eksplicitno NAŠA ograničena *EXPLICIT single-option* mrežna varijanta: jedan trajni plan po linku; kapacitet instalacije sa izvornog spiska može imati NAJVIŠE jedan izvorni kapacitetni element po linku (maksimalno 800 po linku), oba smera koriste zajedničku kapacitetnu granicu; svi originalni vremenski treninzi, bez recourse kupovine. Samo dve najkraće putanje za svaki par. Pretpostavljena je kompatibilnost jedinica izvornog kapaciteta i izvorno prijavljenog Mbit/s — nije nezavisno fizički sertifikovana.
- Ovaj test razlikuje se od GÉANT I33/I34 hipotetičkog cap-a i zasebne recourse kupovine.

## Svi unapred fiksirani I38 rezultati — negativni bez skrivanja

**HiGHS MILP `status=2` INFEASIBLE**, sa 1.312 binarnih promenljivih, 5.018 ograničenja i oko 0,45 s solver vremena. Dakle nije objavljen izmišljeni optimum niti "loš" GAdapt rezultat. Originalni GAdapt 12 semena **3800–3811 × 360** stvarno izvršenih kompletnog izvornog TRAIN-panel-cost evaluation attempts: ukupno **4.320**, svi pokazali neizvodljiv plan; **0/12** semena sa makar jednim train-feasible trajnim kapacitetnim planom; zabeleženo **0 numeričkih/ulaznih grešaka**. Sva 12 nezavisna GA pokretanja (ali isti poznati source model), ne 4.320 nezavisnih dokaza o superiornosti. GA `result.success` ne znači mrežnu fizičku izvodljivost.

## Nezavisan matematički dokaz uzroka — cut capacity certificate

**Odvojeni post-result source-only CI** [#39789612415](https://github.com/owlCoder/gadapt/actions/runs/39789612415) izvršio je proveru nužnog uslova preseka samo nad originalnim 288 matrica i originalnim link-capacity listama; NULA GAdapt, HiGHS, Dijkstra, AC i domain route evaluacija. Prošao je i test nužnog uslova na sintetičkoj mreži.

Za svaki skup čvorova `S` i vreme `t` svaki usmereni zahtev `(u,v)` sa tačno jednim krajem u `S` mora preko najmanje jednog izvornog linka koji seče `δ(S)`. Prema tome je **neophodno**:

```
sum_{d: exactly one endpoint in S} q[d,t]
    <= sum_{e in delta(S)} max_allowed_installed_capacity[e].
```

Ako se ova nejednakost prekrši, **NEMA izvodljivog plana ni sa proizvoljnim splittable/nesplittable routingom**, ne samo sa GAdapt-ovim dvema putanjama. Ovaj zaključak važi u precizno definisanom I38 *EXPLICIT-single-option shared-undirected* modelu i pretpostavljenim kapacitetnim jedinicama, ne za pravo stanje DFN mreže.

Za **singleton S={Frankfurt}** izvorna TRAIN matrica indeks **154** zahteva **5.093,309166**, a zbir svih maksimalnih dozvoljenih originalnih jednokratnih instalacija preko njegovog preseka iznosi **4.000,000000**: nedostaje **1.093,309166**, nezavisno od izbora putanja, GA-a i MILP-a. Čak **80 TRAIN vremenskih slotova** krši taj nužni cut uslov. U 96 HOLDOUT intervala najveće odstupanje na istom preseku je **656,006986** (0. indeks), uz **21 prekršen slot**. Otkriveno ukupno **9 TRAIN** i **3 HOLDOUT** prekršena pregleda preseka među veličinama 1–3 čvora. Ovo objašnjava why MILP infeasible: prethodna sposobnost GA-a nije pitanje.

## Tačan sledeći korak, NE posthoc popravljanje ovog eksperimenta

Novi, odvojeni [I39 PREREGISTERED PROTOCOL](ITERATION39_PROTOCOL.md) zamrznut je POSLE I38 negativnog nalaza ali PRE ijednog I39 domen optimizacionog poziva. Umesto jedne instalacije po linku koristi dokumentovan SNDlib **MODULAR_LINK_CAPACITIES** model (mogućnost višestrukih izvornih modula, jedan trajni plan kroz svih 192 trening stanja); pre bilo kog solvera proverava se izvorna matematička ekvivalentnost svih 26×40 izvornih opcija kapacitetnim modulima 20 i 40 uz identičnu izvornu cenu. Nema proizvoljnog cap-a niti per-scenario recourse. Nove uparene GA semene 3900..3911, ista skrivena poslednja 96 vremenska stanja i MILP dual bound. **Ovo je opravdana promena modela, a ne ponavljanje I38 uz druga semena da dobije pozitivan p.**

Naučna originalnost I39 NIJE dokaziva samim time: SNDlib robust/modular network design i MILP već postoje. Doktorski značaj dosad je pošteno otkrivanje *infeasible-by-construction* formulacije i izrada uporedivog realnog modela.
