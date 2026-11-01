# I65 — konačni GO/NO-GO i preporuka (2026-11-01)

## Finalni status ove sesije

U `owlCoder/gadapt:main` je proveren `AGENTS.md`, `PHD_PROGRESS.md` i glavni I64 protokoli/rezultati. GitHub nije menjan, upstream je samo čitan. Novi I65 **nije** zamrznut, konfirmatorni broj pokretanja je 0, nema novih COCO uspeha/neuspeha, nema novog CVaR/ECDF poređenja. Izveštaji ne smeju označavati DRAFT kao preregistraciju.

## Postojeći dokazi (prethodne studije, ne nove serije)

| Tvrdnja | Stanje u ranijim dokumentima |
|---|---|
| Brza rana efikasnost GAdapt-a na originalnom mentorovom testu | I64-S0 GAdapt A=0,698, SciPy DE A=0,651. DE ima bolju završnu ćelijsku medijanu na 14/21 ćelija. |
| Osetljivost na ortogonalnu transformaciju | I64-R, isti pomeraj: pad GAdapt A=0,0809 [0,0721;0,0897], IPOP A=0,0101 [0,0036;0,0166]. |
| Fiksni GAdapt→CMA na sintetici | I64-E3: rotirano A_hybrid=0,7196 prema A_G=0,6167, ali ukupni unapred utvrđen kriterijum hibrida nije prošao. |
| Zaseban doprinos GAdapt faze | I64-A: zamena 30% GAdapt faze slučajnim uzorkovanjem u konkretnom hibridu pogoršava A; nije dokaz nove metode. |
| Industrijska izvodljivost | I64-I/I2: ORPD GAdapt feasibility 0,746, IPOP 0,771, hybrid 0,742; prednost hibrida na ORPD-u nije potvrđena, a CVaR IPOP=0,2518 < hybrid=0,3772 sa statistički podržanom razlikom u I2. |

## Pravila izbora za praksu

1. Za novo, snažno spregnuto, rotirano kontinualno okruženje: **IPOP-CMA-ES kao jaka podrazumevana referenca za evaluaciju**, uz BIPOP i DE kao kontrolu. To nije univerzalni dokaz da će dati najbolji rezultat; korisno je za konzervativan početni shortlist.
2. GAdapt-M je opravdan konkurent kada prethodno testirana struktura problema i budžet pokazuju dobru ranu efikasnost, ali zbog I64-R nema opšte preporuke za nepoznate rotirane funkcije.
3. GAdapt→CMA fiksni hibrid je legitimna inženjerska opcija za pilot, **ne** bezuslovan industrijski izbor: I64-I2 nije potvrdio prenos sintetičke koristi na ORPD.
4. Stagnacijom okinut GAdapt→CMA iz I65 (kandidat C) nema merenja: status **UNTESTED / NOT_RECOMMENDED** za radni sistem. Za svaki infrastrukturni run: proveriti granice, ograničenja, realan vraćen cost i fallback; ako kvalitet/feasibility nisu dokazani, `NOT_SOLVED`.

## Odluke

| Gate | Odluka |
|---|---|
| Prior-art naučne metode | **NO-GO**: `novelty not established` (IPOP/BIPOP, restarti, portfolio, memetičke/algorithm switching strategije već postoje) |
| I65 sandbox testovi | **GO** za slanje na nezavisnu recenziju; 54 uspešna i 3 očekivana negativna testa |
| Integracija GAdapt/CMA/COCO | **BLOCKED / NOT_TESTED** u ovom okruženju |
| FREEZE I65 | **NO-FREEZE**: nedostaju nezavisan review, environment lock i validirane COCO instance/optimizer adapteri |
| Confirmatory I65 (18 COCO ćelija, 9 algoritama) | **NOT_RUN**; nema osnova za GO C niti za NO-GO empirijskom kvalitetu C |
| Industrijska pouzdanost | **NO-GO** za tvrdnju o spremnosti ili univerzalnom uspehu |

### Koliko 30 semena mogu dokazati o retkim otkazima?

Čak i pri **nula opaženih otkaza** u 30 nezavisnih pokretanja iste raspodele, egzaktna jednostrana 95% gornja granica verovatnoće otkaza je `1 - 0.05**(1/30)` ≈ **9,50%**. Ako bi svih 90 pokretanja na 3 instance moglo da se opravdano tretira kao i.i.d., odgovarajuća granica je ≈ **3,27%**, što je i dalje daleko od industrijski retkog otkaza. U ovom protokolu su instance različite, tako da 90 nije automatski i.i.d. uzorak za jednu ciljnu funkciju. Bez zajedničkog modela raspodele nije dozvoljeno naivno pool-ovati.

**Krajnji zaključak:** ovo je uska, reproduktibilna empirijska hipoteza sa validiranim laboratorijskim podskupom instrumentacije; ne postoji potvrda nove optimizacione metode. Sadašnji najbolji konzervativni izbor za sledeći pravi eksperiment je IPOP kao snažna kontrola, a ne neprovereni stagnacioni hibrid. Nije opravdano tvrditi empirijski inferiornost kandidata C koji nije ni pokrenut.