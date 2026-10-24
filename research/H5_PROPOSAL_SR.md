# H5: tehnike za ograničenja × samoadaptacija GAdapt-a na diskretnim kontrolama OPF-a (PREDLOG, pre protokola)

**Status:** predlog 2026-10-24, pre ikakvog koda i merenja. Nastao iz pristupa „prvo praznina“ (Codex 019), posle
12 odbačenih kandidata za metodu (`IDEATION_2026-10-24_CLAUDE_BLIND_SR.md`). Adversarijalna provera prior art-a
(literature-auditor, 2026-10-24): **GO samo za punu faktorsku studiju, verovatnoća originalnosti ≈ 0,6.**

## 1. Istraživačko pitanje
Na problemima optimalnog toka snage / Volt-VAR upravljanja sa **stvarno diskretnim** kontrolama (položaji
regulacionih transformatora, stepeni šant kompenzacije; zadati naponi generatora na mreži vrednosti), da li efekat
tehnike za rukovanje ograničenjima (CHT) na dostizanje izvodljivog cilja pri fiksnom broju AC proračuna zavisi od
toga da li GAdapt koristi svoju samoadaptaciju vođenu raznovrsnošću ili usklađene fiksne parametre, i kako se ta
interakcija menja sa rezolucijom mreže vrednosti i veličinom mreže?

## 2. Najbliži prior art (DOI provereni na Crossref-u 2026-10-24)
| Rad | Šta pokriva | Šta ne pokriva |
|---|---|---|
| Biswas, Suganthan, Mallipeddi, Amaratunga 2018, [10.1016/j.engappai.2017.10.019](https://doi.org/10.1016/j.engappai.2017.10.019) | DE + pravila izvodljivosti / samoadaptivna kazna / ansambl, IEEE 30/57/118 | adaptacija nije faktor; diskretnost nepotvrđena |
| Mallipeddi, Jeyadevi, Suganthan, Baskar 2012, [10.1016/j.swevo.2012.03.001](https://doi.org/10.1016/j.swevo.2012.03.001) | ORPD sa 5 CHT + ansambl | pun tekst NIJE pročitan (rizik R1) |
| Ali i sar. 2024, [10.1038/s41598-024-56590-5](https://doi.org/10.1038/s41598-024-56590-5) | CoDE + pravila izvodljivosti / ε / hibridi | fiksni parametri; promenljive faktički kontinualne |
| Carvalho i sar. 2015, [10.1109/isap.2015.7325576](https://doi.org/10.1109/isap.2015.7325576); Marcelino i sar. 2018, [10.1007/s10489-018-1167-5](https://doi.org/10.1007/s10489-018-1167-5) | kazne × parametri DEEPSO (ANOVA), SCOPF | samo kazne, offline podešavanje, jedna mreža, bez rezolucije |
| Tanabe 2024, [10.1145/3638529.3654019](https://doi.org/10.1145/3638529.3654019) | parameter control × popravka na bbob-mixint | bez ograničenja, van elektroenergetike |
| Mallipeddi i Suganthan 2010, [10.1109/tevc.2009.2033582](https://doi.org/10.1109/tevc.2009.2033582); Villa-Acevedo i sar. 2018, [10.3390/en11092352](https://doi.org/10.3390/en11092352) | ansambl CHT; nova CHT u GA za ORPD | bez ose adaptacije |
| Ulrich i sar. 2025, [10.3390/electricity6020031](https://doi.org/10.3390/electricity6020031) | pregled: „only a few articles research the effect of different constraint handling techniques or hyper parameter settings“ | slab dokaz praznine (propustio 2012/2015/2024) |
| Kumar i sar. 2020, [10.1016/j.swevo.2020.100693](https://doi.org/10.1016/j.swevo.2020.100693) | CEC2020 realni ograničeni problemi (uklj. elektroenergetske) | verovatno kontinualni (proveriti) |

## 3. Precizna tvrdnja o novini
Nije nova metoda. Novo znanje (ako se potvrdi): **prva preregistrovana faktorska procena interakcije
CHT × samoadaptacija × rezolucija diskretnih kontrola × veličina mreže** u metaheurističkom OPF-u, merena krivama
dostizanja izvodljivog cilja po broju AC proračuna. Uz to, praktičan doprinos samom GAdapt-u: opt-in interfejs za
ograničenja (trošak + vektor prekršaja) sa CHT-ovima i definicijom signala adaptacije pod svakim CHT-om (podrazumevano
ponašanje bit-identično). **Novina NIJE utvrđena dok se ne proveri pun tekst Mallipeddi 2012 (R1).**

## 4. Formalne pretpostavke i očekivanje (ne teorema)
- Kontrole x ∈ G = Π_i {l_i + k·s_i}; jedan poziv = jedan AC proračun (pypower `runpf`); prekršaji g_j(x) ≥ 0
  (napon, Q generatora, termičke granice, balans), cilj f(x) (gubici ili trošak).
- GAdapt-ova adaptacija čita log-raspon troškova preživelih (CLAUDE.md). Pod pravilima izvodljivosti „trošak“ nije
  skalar → signal mora biti definisan (npr. na rangu ili na f samo izvodljivih). Hipoteza mehanizma: pod
  kaznom raspon je dominiran prekršajima, pa adaptacija reaguje na izvodljivost, a ne na konvergenciju cilja.
- Očekivanje (falsifikabilno): interakcija CHT × adaptacija postoji (efekat CHT-a se menja po znaku ili ≥ 2× u
  dostizanju cilja između adaptivnog i fiksnog GAdapt-a) bar na jednoj rezoluciji; nulti ishod je takođe
  rezultat ako je studija dovoljno jaka (analiza snage pre zamrzavanja).

## 5. Najjače poređenje
GAdapt adaptivno i usklađeno fiksno (ista populacija, isti operatori, fiksne stope = medijana adaptivnih trajektorija
iz pilot-skupa koji se NE koristi za procenu); L-SHADE, jDE, CoDE (Tanabeov pobednik), CMA-ES sa marginom (pycma
`integer_variables`/margin), MVMO; referentni cilj iz MINLP/relax-and-round (ili najbolje poznato iz svih
pokretanja, unapred definisano). CHT skup: statička kazna, adaptivna/samoadaptivna kazna, Deb-ova pravila,
stohastičko rangiranje, ε-ograničenje (i popravka gde je definisana).

## 6. Eksperiment za falsifikaciju (skica; zamrzava se u protokolu I56)
Mreže: case14, case30, case57, case118 (pypower) sa dokumentovanim diskretnim mrežama (stepen otcepa 0,0125 p.u.,
±10%; šantovi u koracima; naponi generatora sa korakom); rezolucija kao faktor (npr. 9 / 17 / 33 položaja).
Faktori: CHT (5) × adaptacija (2) × rezolucija (3) × mreža (4) × 15 semena = 1800 GAdapt pokretanja + poredbeni
algoritmi. Budžet: fiksan broj AC proračuna po pokretanju (npr. 3000), broje se SVI pozivi. Ishodi: ECDF dostizanja
cilja (izvodljiv i ≤ (1+ε)·referenca), stopa izvodljivosti, ERT. Analiza: model sa interakcijom (ART-ANOVA ili
mešoviti model), korekcija za višestruka poređenja, unapred definisan prag efekta. Sintetička kontrola (bbob-mixint)
odvojeno od stvarne mreže.

## 7. Budžet
Jedan AC proračun 3–16 ms → 3000 poziva ≈ 10–50 s po pokretanju; ~3000 pokretanja ukupno ≈ 15–40 CPU-sati (lokalno,
paralelno nekoliko sati). Bez CI-a.

## 8. Rizici
- R1: Mallipeddi 2012 možda već varira adaptaciju/korak → pun tekst pre protokola.
- R2: „još jedno poređenje“ → zato interakcija i rezolucija kao glavni faktori, ne rang algoritama.
- R3: definicije diskretnih mreža u pypower slučajevima su naše pretpostavke → objaviti, citirati praksu (PES 2014
  takmičenje ima diskretne kontrole; proveriti dostupnost).

## 9. GO / NO-GO
**USLOVNI GO** za pripremu protokola I56 (Codex recenzija pre zamrzavanja). **STOP** ako R1 pokaže da je
interakcija već izmerena.
