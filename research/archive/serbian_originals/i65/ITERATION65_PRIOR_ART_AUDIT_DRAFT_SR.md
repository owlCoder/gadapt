# I65 — audit postojećih dokaza i prior art (DRAFT; 2026-11-01)

**Status:** samostalni radni audit; `novelty not established`; bez izmene GitHub repozitorijuma, bez nove optimizacione serije. Repozitorijum: `owlCoder/gadapt:main`; `bpzoran/gadapt` i `bpzoran/gadapt_experiments` samo za čitanje. Pregledani: `AGENTS.md`, `PHD_PROGRESS.md` (poslednji deo do 2026-10-30), `MENTOR_MEETING_NOTES_SR.md`, `MENTOR_SUMMARY_2026-10-28_SR.md`, `ITERATION64_PROTOCOL.md`, `ITERATION64_S0_REPORT_SR.md`, izveštaji I64-E/E3/A/R/I/I2, specifikacije E/E3 i izvorni I64 E/E3 benchmark moduli. Nije revidirana svaka stara sirova arhiva, niti se tvrdi ponavljanje njihovih analiza.

## 1. Matrica postojećih nalaza — zašto se eksperimenti ne ponavljaju

| Studija | Šta je dokazano u njenom fiksnom dizajnu | Negativno, kontradiktorno ili otvoreno |
|---|---|---|
| I64-S0 | Mentorova replika: 21 ćelija, 4 metode, 20 semena, 1.680 pokretanja. GAdapt-M ima A=0,698; DE A=0,651. | DE ima bolju završnu ćelijsku medijanu u 14/21 ćelija; izvorni broj generacija nije uporediv sa pozivima; S0 nije BBOB. |
| I64-E | 12.000 stvarnih poziva, pomeraj/rotacije, 63 ćelije, devet metoda. GAdapt-M A=0,6732; IPOP=0,7699; BIPOP=0,7688; DE=0,6396. | Originalni H64a suprotan; CMA porodica je agregatno efikasnija, bez opšteg dokaza o infrastrukturnoj superiornosti. |
| I64-E3 | 30% budžeta GAdapt, 70% CMA; na rotaciji A hibrida 0,7196 prema M 0,6167. | H64g2 suprotna zbog lošijeg ne-rotiranog repa; H64g3 neodlučna prema IPOP; hibrid nije nova metoda. |
| I64-A | Zamena prve 30% faze slučajnim uzorkovanjem smanjuje A za 0,131 rot / 0,178 nonrot. | Efekat je uslovan na fiksni CMA start `sigma0=0.05`; nije izolovana univerzalna prednost GAdapt-a. |
| I64-R | Uparen isti pomeraj; dodatna Q smanjuje GAdapt A za 0,0809 [0,0721; 0,0897], IPOP za 0,0101 [0,0036; 0,0166]. | Ne generalizovati sa 21 fiksnog Q i jednog skupa funkcija. Mehanizam nije ustanovljen. |
| I64-I | Diskretni ORPD, 8 ćelija × 30 semena, 12k PF: GAdapt feasibility 0,746; IPOP 0,771. | GAdapt vs CMA/IPOP/BIPOP: intervali obuhvataju 0; 2 ćelije skoro neizvodljive; reference nisu sertifikovani diskretni optimumi. |
| I64-I2 | ORPD hibrid feasibility 0,742; CVaR 0,3772. | Nije potvrđen bolji rep od GAdapt-M; rep lošiji od IPOP (0,2518). Provenance caveat: `i_run_sha256` prazan u I2 arhivi, naknadna provera. |
| I64-E2/E4/C/N (kontekst) | Diferencijalni crossover i kompenzaciona mutacija nisu dokazano zatvorili jaz; C mehanizam nije potvrđen, N Potts sonda nije pokazala očekivani deficit. | Ne dodavati varijante samo zato što postojeći rezultat nije pozitivan. |

**Aktuelni handoff:** `PHD_PROGRESS.md` završava stanjem 2026-10-30: mentorska odluka o obimu doktorata i dalje se čeka; nova metoda nije potvrđena. Nije korektno iz starijih "SLEDEĆI KORAK" izvući dozvolu za konfirmatorno pokretanje.

## 2. Izvorna instrumentacija koja već postoji

- `research/i64/e_common.py`: `Budget`, `BudgetReached(BaseException)`, najbolji svedok i evaluacioni događaji; potvrđeni Git blob SHA `3aab99773a7e4a95b7972a3c8061c50bd471618d`.
- `research/i64/e_algos.py`: GAdapt-M, DE `best1exp` 64 početnih jedinki, CMA restart, IPOP, BIPOP i ostali; CMA u jediničnom prostoru, GAdapt/DE u nativnim jedinicama (poznata neinvarijantnost GAdapt-a na jedinice).
- `research/i64/e3_algo.py`: već implementiran fiksni GAdapt→CMA hibrid; ne implementirati ponovo pod drugim nazivom.
- GAdapt ima originalni `exit_check="min_cost", max_attempt_no=20`; to nije identično opisanom *significant* kriterijumu sa dva epsilon parametra; SciPy `tol` meri disperziju vrednosti u populaciji (nije stagnacija). Sve metode moraju biti računovodstveno uporedive po fizičkim pozivima, ne generacijama.

## 3. Prior-art: tačna podudaranja i granica tvrdnje

| Izvor i DOI | Šta već postoji | Odnos prema kandidatu |
|---|---|---|
| Auger & Hansen (2005), `10.1109/CEC.2005.1554902` | Restarti CMA-ES sa rastućom populacijom (IPOP). | Restart kao takav: **poznat**, nema novine. |
| Hansen (2009), `10.1145/1570256.1570333` | BIPOP: dva režima populacija/budžetsko prebacivanje. | Portfolio restart politika: **poznata**. |
| Wineberg & Opawale (2018), `10.13164/mendel.2018.1.017` | Stagnacioni kriterijumi za IPOP-slične DE restarte, `EqualFunValHist`. | Konkretnija potvrda da sama detekcija stagnacije/restart nema prvenstvo. |
| Zhang et al. (2023), `10.1109/MCI.2022.3222057` | Kontrolisano vreme prelaska između metaheuristika pomoću (deep) Q-learning; uključuje HSES univarijatno → CMA. | Sekvencijalno switching vreme: **poznato**; zadato pravilo 20 generacija je jednostavniji inženjerski slučaj. |
| Scientific Reports (2021), `10.1038/s41598-021-04549-1` | IR-CMA-ES prelazi na DE redistribuciju kad stagnira CMA. | Srodna politika zastoja i promene algoritma (suprotan smer); novost kandidata nije ustanovljena. |
| Muñoz, Sun, Kirley & Halgamuge (2015), `10.1016/j.ins.2015.05.010` | Pregled izbora algoritma, portfolio, hibrida i procene pejzaža za black-box optimizaciju. | Izbor algoritma po osobinama zadatka: poznat. |
| Krasnogor & Smith (2005), `10.1109/TEVC.2005.850260` | Memetičke/hibridne metode; već citirano u I64-E3. | GAdapt→CMA kao obrazac globalno/lokalno: poznat. |

**Provenijencija DOI:** provereno preko indeksnih/izdavačkih strana navedenih ispod (za Science Reports originalni izdavač). Direktni Crossref API upiti u ovoj sesiji nisu bili dostupni; zato ovo nije tvrdnja o dodatnoj nezavisnoj Crossref verifikaciji. Ne tvrdi se iscrpan sistematski pregled literature.

**Izvori:**
- https://dblp.org/rec/conf/cec/AugerH05.html
- https://cma-es.github.io/index.html
- https://explore.metascienceobservatory.org/papers/W2097263684
- https://ib-b2b.test.infv.eu/index.php/mendel/article/view/14
- https://scholarlypublications.universiteitleiden.nl/handle/1887/3721895
- https://www.nature.com/articles/s41598-021-04549-1
- https://research.monash.edu/en/publications/algorithm-selection-for-black-box-continuous-optimization-problem/
- https://github.com/owlCoder/gadapt/blob/main/research/ITERATION64_E3_SPEC.md

## 4. Naučni gate

- **Istraživačko pitanje:** može li jednostavna, unapred definisana stagnaciona politika dati bolji rep rezultata pod 12k poziva na f21/f24 nego fiksni E3 i IPOP?
- **Precizna novina metode:** `novelty not established`. Sama promene algoritma/restart nije novo; nema osnova za claim o novom doktoratskom algoritmu.
- **Formalne pretpostavke:** f: X→R∪{nonfinite} deterministička na fiksnoj instanci; sekvencijalni brojač poziva; svaki attempted call rezerviše jednu jedinicu B; evaluacioni budget i seed logovi verni.
- **Teorema za proveru instrumentacije, NE naučni doprinos:** ako se brojač uveća *pre* svakog poziva evaluatoru i proveri `n < B` pre rezervacije, onda indukcijom `n ≤ B`, a nijedan evaluator nije pozvan nakon B-te rezervacije. Za paralelizam/vektorizaciju moraju se atomarno rezervisati stavke svake serije; ne pretpostavljati primenu ove tvrdnje na njih bez dokaza.
- **Falsifikacija:** nema prednosti ili se rep pogorša u odnosu na IPOP/E3, neuspešna verifikacija svedoka, nefer brojanje, prebacivanje pre 20 kompletnih generacija, ili nezavisne instance ponište prednost.
- **GO/NO-GO:** GO samo za jeftin instrumentacioni gate i recenziju uskog *empirijskog* protokola. **NO-GO za tvrdnju o novoj metodi**; STOP pre implementacije algoritamske intervencije prema `AGENTS.md` dok istraživačka kapija nije posebno razrešena. Ne zamrzavati i ne pokretati skup eksperiment samo radi pozitivnog ishoda.