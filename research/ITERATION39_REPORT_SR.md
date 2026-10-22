# I39 — zajednički modularni SNDlib kapacitetni plan: originalni GAdapt naspram MILP granice i vremenskog holdout-a

**ZAVRŠENO 22. oktobra 2026.** Ovo je završni izveštaj za *preregistrovanu* I39 seriju. [I39 protokol](ITERATION39_PROTOCOL.md) je komitovan **pre** prvog I39 solver poziva; njegov cilj je numerički proveriti izvodljiv izvorno zasnovan model i dobru optimizacionu referencu. Ovo **nije** potvrda novog doktorskog algoritma. Menjan je isključivo `owlCoder/gadapt:main`, ne `bpzoran/gadapt`.

## Originalni dokaz i reproduktivnost

- [GitHub Actions I39 #39790821143](https://github.com/owlCoder/gadapt/actions/runs/39790821143): sintetički testovi PASS, provera originalnih izvora i modula PASS, zatim **jedan** kompletan MILP + 12 GAdapt runova SUCCESS, originalni job **119866499475**. Ne predstavljati uspeh CI kao dokaz bolje optimizacije.
- [Originalni puni source-data manifest + originalni JSON sa svim GA i MIP odlukama (Actions artifact #12430628680)](https://github.com/owlCoder/gadapt/actions/runs/39790821143/artifacts/12430628680), digest **sha256:a1254c10715fa1801f9de5b6c4a34669df6d5382a220c4587dac7ae97d939967**. Fajlovi unutar arhive: `iteration39_real_272pair_288source_modular_joint_ga12_milp.json` i `iteration39_original_traffic_sha_manifest.json`.
- [Sirovi originalni I39 stdout događaji za 12/12 stvarnih runova](results/iteration39_original_stdout_12seed_4320_fullpanel.json), zajedno sa MILP metapodacima i SHA poreklom. Sačuvano **bez nove simulacije**, a audit potvrđuje 12 različitih preregistrovanih semena i zbir stvarnih domain poziva.
- Nezavisni [I39 original source-only algebra gate CI #39790581601](https://github.com/owlCoder/gadapt/actions/runs/39790581601) prethodio je fizičkoj domen optimizaciji.

## Precizno definisan istorijski *source-based* model

**Izvorna mreža Nobel-Germany:** 17 čvorova, 26 linkova, SHA256 originalni SNDlib native model `35e58a3799d78d2ebfd2a557be2ba4a221ca17fc704cfdd13df56bb90c12a796`. Originalni DFN istorijski 5-min traffic za 15.02.2005: **288 vremenskih matrica i 272 usmerena para**, SHA256 native arhive `2c3ca706a8d5c9601eb4d144651816dfd956257c20f60111a8aceb5f07ab0100`; prvih **192 TRAIN** i narednih **96 HOLDOUT** bez prilagođavanja na holdout.

Jedan statički izbor između dve determinističke najkraće loopless putanje za svaki usmereni demand pair; jedan statički skup modula po **neusmerenom linku sa zbirnim prometom oba smera**. Svaki isti trajni kapacitetni plan ostaje tokom svih 192 TRAIN matrica. Nijedan vremenski scenario ne može da kupi novu opremu — **nema recourse**, nema proizvoljno odabranog investicionog praga/cap-a. Izvorni modularni meni svakog od 26 linkova ima 40 opcija; u odvojenom izvornom algebra gate-u je **svaka od 1.040 opcija** potvrđena ekvivalentnom celobrojnim kombinacijama native modula kapaciteta **20 i 40**, uz **isti izvorni trošak**. Izvorni base/setup/routing cost polja su testirana i nulta za ovu redukciju. To je ekvivalentna reprezentacija **MODULAR** modela, ne nastavak I38 pogrešne *EXPLICIT-one-option* pretpostavke.

**Ključna granica:** preuzeta istorijska saobraćajna matrica je u Mbit/s, a u našem source-based modelu pretpostavljamo numeričku jednakost jednog source kapacitetnog jedinice i jednog Mbit/s. Nema nezavisne telekom kalibracije ni garancije da je plan realno primenljiv. Mreža je javna istorijska, dva puta po paru su naša restrikcija, ne globalni optimum svih mogućih putanja. MILP daje validnu donju granicu **isključivo tog istog restriktivnog modela**.

## Glavna numerička poređenja: ista optimizaciona funkcija i ista TRAIN ograničenja

| Metod, striktno isti source-based problem | Najniži *stvarno train-feasible* source instalacioni trošak | Napomena |
|---|---:|---|
| Deterministički prvi shortest-hop put po svakom paru | **1.614.560** | Bez stohastičke optimizacije, source modul cover |
| Originalni `gadapt.ga.GA` — 12 novih semena 3900–3911 | **1.609.960** | Samo seed 3900 poboljšao shortest-hop baseline; preostalih 11 ima 1.614.560 |
| HiGHS MILP, nezavisno source-capacity revalidiran statički plan | **1.546.850** | Dobijen plan iz MILP ruta, naknadno rekonstruisani minimalno potrebni moduli bez menjanja rute/holdout zahteva |
| HiGHS dokaziva **donja** granica | **1.537.030** | Nije feasible trošak i nije dokaz tačnog optimuma |

Originalni HiGHS prijavio je `status=0` (uspešno završio sa `mip_rel_gap=0.01`), `solver_objective=1.549.850`, `mip_gap≈0,00827`, **dual lower bound 1.537.030**. Ponovnom **determinističkom** izvornom minimalnom kupovinom kapaciteta za ISTU MILP rutnu odluku utvrđen je jeftiniji validni PLAN od **1.546.850**. Dakle nije izmišljeni bolji primal: solver izvorni plan je validiran uz još jeftinije module pri istim ograničenjima. Ne nazivati status=0 dokazom exact optimuma; plan u odnosu na validni dual bound ima najviše **(1.546.850−1.537.030)/1.537.030 = 0,6389%** relativnog optimality-gap upper bound-a. Minimalni GA source plan od 1.609.960 je **63.110** source price jedinica, odnosno **4,08%**, skuplji od validnog najboljeg MILP plana. Njegovo odstupanje od donje granice je **4,7449%**.

**Pozivi i obračun:** 12 metoda×seed runova originalnog GAdapt-a, svaki sa **360 stvarnih kompletnog 192-TRAIN-panel objective evaluations**, ukupno **4.320** provereno izvršenih panel računanja (NE 4.320 različitih topologija i NE pojedinačnih AC). Nema generatora AC; ovo nisu 4.320 `runpf` poziva, već vektorizovana mrežna opterećenja na svih 192 vremenska stanja po kandidatu. GA runovi prosečno oko jedne sekunde, MILP **169,10 s**. Zbog različitih vremena i kvaliteta rešenja ovo **nije pravična jednako-vremenska superiornost** MILP-a; jeste pošteno numeričko poređenje pri dokumentovanim protokolom zamrznutim budžetima.

## HOLDOUT — važna nezavisna negativna validacija

| Prethodno TRAIN-feasible jedinstveni plan | HOLDOUT časovni intervali sa preopterećenjem (od 96) | Najveći source capacity višak |
|---|---:|---:|
| MILP nezavisno verifikovani plan | **34/96** | **1.182,121610** |
| GA seed 3900, jedini bolji od baseline | **39/96** | **1.392,482008** |
| GA ostalih 11 i shortest-path baseline | **31/96** | **1.396,723509** |

**Nijedan plan ne zadovoljava svih 96 holdout vremenskih stanja.** Ovo **nije** statistički dokaz da MILP generalizuje lošije od GAdapt-a (različite aktivne rute i različiti cilj/training balans), niti da je problem matematički nemoguć ako bi se u protokolu unapred dozvolio drugi skup scenarija ili vremenski zaštitni faktor. Planovi su svi **izvodljivi za 192 obučavajuća stanja** samo u definisanom kapacitetnom modelu. Posmatrani HOLDOUT nema pravo da utiče na njihove kapacitete bez novog zasebno preregistrovanog modela.

## Metodološki zaključak za disertaciju i odluka

1. U **I38** je dokazano da je prvobitna eksplicitna *single-option* formulacija strukturno neizvodljiva nezavisno od algoritma: [I38 izveštaj sa Frankfurt cut sertifikatom](ITERATION38_REPORT_SR.md). To nije negativan dokaz protiv GAdapt-a.
2. U **I39** postoji prvi zaista zajednički source modularni plan, potvrđena source-cost ekvivalentnost, referentni MILP dual i 12 ponovljenih stvarnih originalnih core GAdapt runova sa zamrznutim budžetom. GA mnogo slabije pretražuje taj model od MILP-a uz dato vreme/solver budžet, a obična train-only robustna izvodljivost nije dovoljna za izdvojene 96 holdout intervale.
3. **NOVELTY=NOT ESTABLISHED:** modular network planning, MIP, scenario-based capacity planning i GAdapt kombinacija nisu novi sami po sebi. Koristan i falsifikabilan kandidat novog metodskog problema jeste *nezavisno kalibrisana robustnost stvarnog zajedničkog kapacitetnog plana pri vremenskim promenama*, uz formalno opravdane TRAIN-only margin/certification i jake kontrole, ali samo posle duboke literature. Nema pravo post hoc menjati ovaj eksperiment da se dobije 96/96. Ne dodavati novi UCB reward bez novog identifikabilnog algoritamskog doprinosa.

**Doktorska ocena:** I39 je prvi validno uporediv benchmark zajedničke telekom investicije sa proverljivom donjom optimizacionom granicom i stvarnim vremenskim podacima; ovo **jeste opipljiv pomak u istraživačkom osnovu, ali još nije dokaz originalne doktorske metode**.
