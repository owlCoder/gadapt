# Iteracija 9 — originalni generatorski limiti RTE1888: ispravan deo konverzije i ključna razlika slack sabirnice

**Datum:** 21.10.2026 · **Repo:** owlCoder/gadapt:main · **Tip:** statički audit 2019 MATPOWER izvora i pandapower konverzije, **0 AC proračuna**. Preregistracija u [ITERATION9_PROTOCOL.md](ITERATION9_PROTOCOL.md), commit [387f299](https://github.com/owlCoder/gadapt/commit/387f29918252e1b244fbb1d0a41227158cdff9ac), nastala pre punog pokretanja poređenja.

**Glavni rezultat:** 264 nedvosmislena aktivna generatora imaju poklopljena **svih šest polja PG, PMIN, PMAX, QMIN, QMAX, VG** (tolerancija 1e-4), i svih 1888 sabirničkih naponskih granica i nominalnih kV je usklađeno (tolerancija 1e-5). Međutim, **izvorna MATPOWER slack sabirnica 1320 nije isto što i pandapower ext_grid na originalnoj sabirnici 1268**. Izvorni aktivni generator na sabirnici 1320 nije pokriven elementom gen/sgen/ext_grid u konvertovanoj mreži. Ovo je materijalno ograničenje dosadašnjih fizičkih evaluacija.

## 1. Poređenje i dokazni materijal

Javni MATPOWER izvor: [case1888rte.m, fiksni commit](https://github.com/MATPOWER/matpower/blob/80b6e16f760f58721ad31221c7287c28259cd4ad/data/case1888rte.m), blob SHA 820bd317167381baf819d67eab7d886013e8b05a; Josz et al. (2016). Licence CC BY 4.0. Podaci služe za proveru metoda; **ne smeju se koristiti za planiranje/operativno upravljanje francuskom ili evropskom mrežom**.

MATPOWER original sadrži 298 generatorskih redova: **291 aktivan i sedam deaktiviranih**, na **281 aktivnoj generatorskoj sabirnici**, sa osam sabirnica koje imaju više aktivnih izvora. Devet aktivnih generatora ima fiksirane izvorne Q granice; 92 aktivna su već na izvornom PMIN u početnom stanju. Ukupno izvorno zadato aktivno proizvođenje je PG = 60090,91 MW, pre balansiranja slack generatora — to nije potvrđen stvarni radni dispečing.

| Provera | Potvrđeni statički rezultat |
|---|---:|
| Poređene originalne sabirnice | 1888/1888 |
| Nepodudarnosti izvornog VMIN/VMAX | **0** |
| Nepodudarnosti izvornog nominalnog kV | **0** |
| Poređeni jednoznačni online generatori | 264 |
| Nepodudarnosti šest generatorskih polja | **0/264** |
| Ostali izvorni online generatorski busovi za posebno mapiranje | 17 |
| Izvorne generatorske sabirnice bez odgovarajućeg aktivnog gen/sgen/ext_grid | **jedna: 1320** |
| Stvarni pozivi AC solvera u ovom auditu | **0** |

Konvertovani pandapower sistem sadrži **271 aktivan gen**, **75 aktivnih sgen od 82 ukupno**, i **1 aktivan ext_grid**. Od 82 sgen, njih 57 nema popunjene kolone minimalnog i maksimalnog P/Q; automatski ne znači da su izvorna ograničenja izgubljena, jer više od 50 sgen sabirnica uopšte nema odgovarajući aktivni izvorni MATPOWER generator. Za preostalih 17 nejednoznačnih izvornih generatorskih sabirnica treba posebno proveriti mnogostruku konverziju i kategorije.

## 2. Kritična razlika u referentnom slack bus-u

Originalni MATPOWER 2019 (sa dodatim generatorom na slack bus-u):
- BUS 1320 ima originalni BUS_TYPE=3 (reference/slack), V = 1,05884172 p.u., VMIN=1,05526 i VMAX=1,10263.
- Poslednji originalni generator, red #298 na BUS 1320: PG=0 MW, PMIN=0 MW, PMAX=1000 MW, QMIN=-1 MVAr, QMAX=1 MVAr, VG=1,0588 p.u. Ne tvrdimo da su te Q granice fizički realistične niti da je izvodljivo u PF.
- Originalna BUS 1268 ima BUS_TYPE=2 (PV), dva generatora sa po PG=44,5 MW, QMIN=-9, QMAX=27 MVAr, VG=1,027 p.u.

Konvertovana pandapower mreža, nasuprot tome, smešta **ext_grid na originalni BUS 1268**, dok originalni BUS 1320 nema aktivni gen, sgen ili ext_grid. Razlog može biti razlika u verzijama izvornog slučaja ili konverziji; uzrok **nije još nezavisno potvrđen**. Kod i CI mere razliku, ne nagađaju uzrok.

**Posledica:** sama činjenica da se 264 generatora i svih 1888 V granica poklapaju ne daje pravo da kažemo da referentni AC PF ili mogući optimum iz iteracija 7/8 predstavlja originalni MATPOWER AC-OPF sa izvornim slack-om. Usklađivanje modela i nezavisna fizička provera moraju prethoditi novom algoritamskom poređenju. Rezultati prethodnih iteracija ostaju tačni kao opažanja **za konvertovani pandapower model**, uz ranije navedene source-rated granice, ali se ne smeju predstavljati kao originalni izvorno identični model.

## 3. Trajni dokazi i ponavljanje

- [Kompletan mašinski JSON: 36 kB](results/rte1888_iteration9_source_generator_conversion_audit_20261021.json)
- [Izvorni redovi 298 generatora](results/rte1888_iteration9_original_matpower_generator_rows_2019.csv)
- [Izvorne redove 1888 sabirnica](results/rte1888_iteration9_original_matpower_bus_rows_2019.csv)
- [Implementacija statičkog audita](iteration9_source_generators.py)
- [Strukturni testovi](test_iteration9_source_generators.py)
- [GitHub Actions — uspešan CI #39624498771](https://github.com/owlCoder/gadapt/actions/runs/39624498771)

Pokretanje sa istim izvorima i pinovanim okruženjem:

    python -m pip install -e . 'pandapower==2.14.11' 'scipy==1.13.1' 'pandas==2.2.3'
    python -m unittest -v research.test_iteration9_source_generators research.test_iteration7_rate_source
    python -m research.iteration9_source_generators --output /tmp/i9.json

CI log jasno navodi **nula** stvarnih AC poziva. Ova iteracija nije ni optimizator ni dokaz inovacije.

## 4. Sledeća obavezna validacija

Najpre uporediti aktuelnu pandapower konverziju sa izvornim v2 MATPOWER slučajem na slack/reference, izvorima i električnim granama; pokušaj promene slack sabirnice sme se izvršiti **samo u kopiji modela, po zasebno unapred definisanom protokolu**, uz prikaz fizičkih poziva, Q/P limita, razlika i konvergencije. Tek nakon validacije modela tražiti stvarni AC-OPF benchmark i novu, literaturom opravdanu adaptaciju GAdapt-a.

**Zaključak:** dokazano dobar prenos šest generatorskih polja na 264 jednoznačna primera, ali i nova, ozbiljna nesaglasnost reference. Nema izvodljivog optimalnog rešenja, dokaza naučne novine, dokaza prednosti GAdapt-a niti industrijske spremnosti.
