# Iteracija 9 — izvorni generatori i konverzija RTE1888

**Registrovano 21.10.2026 pre punog računarskog poređenja generatorskih podataka sa konvertovanim modelom.** Prethodno javno prebrojavanje: izvorni MATPOWER ima 298 redova generatora (291 aktivan, 7 isključen), dok pandapower iz iteracije 8 prikazuje 271 aktivnih elemenata tipa gen. Različite kategorije ne moraju označavati različite fizičke jedinice.

## Preregistrovano pitanje i izvori

Proveriti da li su izvorne granice P/Q, sabirničke granice V i identiteti preneti u konvertovani pandapower model na način koji dozvoljava definisanje potpunog, fizički vernog AC-OPF problema. Original: MATPOWER/matpower commit 80b6e16f760f58721ad31221c7287c28259cd4ad, data/case1888rte.m, blob 820bd317167381baf819d67eab7d886013e8b05a, CC BY 4.0, Josz et al. 2016. Podaci nisu namenjeni za operaciju ili planiranje francuske ili evropske mreže.

## Metod zamrznut pre poređenja

1. Iz originalnog mpc.gen ekstrahovati svih 298 numeričkih redova sa prvih deset kolona (GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN), uz source-row ID. Iz originalnog mpc.bus ekstrahovati svih 1888 redova sa 13 numeričkih kolona (BUS_I, TYPE, PD, QD, GS, BS, BUS_AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN). Sirove numeričke CSV izvore trajno arhivirati sa licencom i SHA poreklom.
2. Pandapower mreža: networks.case1888rte() u Python 3.12, pandapower==2.14.11, scipy==1.13.1, pandas==2.2.3, jedan BLAS/OMP thread. Ovaj audit je *isključivo statički* — 0 fizičkih AC poziva.
3. Mapiranje sabirnica na izvorni bus ID je int(net.bus.name)+1, uz proveru jedinstvenosti i pokrivenosti svih 1888 sabirnica. Uporediti izvorne VMIN/VMAX, BASE_KV, uz apsolutnu toleranciju 1e-5; referentni VM prikazati samo gde je konvertovani izvor dostupan. Evidentirati slack sabirnice (BUS_TYPE=3) i poziciju ext_grid.
4. Izvorni online/offline generatori: sačuvati broj i skup sabirnica; agregirati PG, QG, PMIN, PMAX, QMIN, QMAX po originalnoj sabirnici; prijaviti slučajeve PMAX manji od PMIN i QMAX manji od QMIN. Pandapower: broj i aktivnost gen, sgen i ext_grid; na izvornoj sabirnici izvesti pokrivenost prema klasama; ne izjednačavati automatski agregat sgen sa izvornim generatorima.
5. Na izvornoj sabirnici sa *tačno jednim aktivnim* MATPOWER generatorom i *tačno jednim aktivnim* pandapower gen, i nijednim sgen/ext_grid, uporediti PG, PMIN/MAX, QMIN/MAX, VG uz apsolutnu toleranciju 1e-4. Ostale slučajeve nazvati nejednoznačnim, ne neuspelom konverzijom. Prijaviti nepodudaranje sa stvarnim brojevima i najmanje deset najvećih odstupanja kad ih ima.
6. Ne sakrivati nedostajuće ili nenumeričke granice. Nepokrivenost izvornih sabirnica, mnogo-na-jedan konverzija i sgen sa drugim semantikama nisu po sebi dokaz izgubljene fizičke generacije — obeležiti kao otvorene slučajeve. Rezultat nije fizička OPF validacija.
7. Verzionski arhivirati originalne CSV, kod i unit testove, CI, JSON i srpski izveštaj na owlCoder/gadapt:main. Bez prepravke bpzoran/gadapt, bez statističkih tvrdnji, p-vrednosti, superiornosti GAdapt ili lažnih AC rezultata.

## Reprodukcija

Python: python -m unittest -v research.test_iteration9_source_generators; python -m research.iteration9_source_generators --output /tmp/iteration9_audit.json

## Naučna ograničenja

Ovo je dijagnostika pred narednu AC-OPF fazu. Naučno nov adaptivni GAdapt još nije razvijen ili potvrđen. Izvorni MATPOWER model i konvertovani pandapower model ne smeju biti proglašeni identičnim bez nezavisne provere njihovih električnih jednačina i OPP ograničenja.
