# Nezavisna (slepa) lista kandidata — Claude, 2026-10-24

Zapisano i komitovano PRE čitanja Codex 016 odgovora, da bi poređenje bilo nezavisno. Procene novine su moje,
pre sistematske provere prior art-a; većina verovatno pada na gate-u.

| # | Pitanje | Skica | Najbliži poznati prior art (za proveru) | Moja procena novine |
|---|---|---|---|---|
| K1 | Može li populacioni GA na N-1 sigurnosnom dispečingu (max preko K kontingencija) da donese **iste odluke selekcije** kao uz punu evaluaciju, uz delić AC poziva? | lenja evaluacija: delimičan max je donja granica; elitni skup se određuje bez pune evaluacije onih čija donja granica već premašuje prag; redosled kontingencija uči se iz populacije; teorema: elitni skup i najbolji trošak identični punoj evaluaciji | racing (Hoeffding racing za CMA-ES, Heidrich-Meisner i Igel 2009), filtriranje kontingencija u SCOPF (Capitanescu i sar.), coevolutivna worst-case optimizacija (Branke i Rosenbusch 2008); postojeći `sequential_scenario_budget_cost.py` (rani prekid po izvodljivosti, sam sebe označava kao poznat) | 15–25% (tačnost selekcije uz rang-rulet zahteva pune rangove → garancija samo za elitni skup) |
| K2 | Mreža kao struktura genoma: ukrštanje koje razmenjuje električno koherentne zone (PTDF / električna udaljenost) | FOS / particija promenljivih iz mreže, zonsko ukrštanje u GAdapt-u | GOMEA sa datim modelom povezanosti (gray-box), partition crossover (I42 H1 NO-GO) | 5–10% |
| K3 | Usmeravanje mutacije prema promenljivim povezanim sa prekršenim ograničenjima (kovarijansa vrednost–prekršaj iz populacije) | „raznovrsnost prekršaja“ kao novi GAdapt signal | constraint consensus (Chinneck; Hamza i sar. 2016), gradijentna popravka (Chootinan i Chen 2006) | 10% |
| K4 | Promena fidelnosti DC→AC vođena GAdapt-ovom raznovrsnošću troškova | DC tok dok je raznovrsnost velika, AC kad populacija konvergira | multi-fidelity EA (adaptivna fidelnost po konvergenciji) | 5–10% |
| K5 | Retke promene (operater želi malo izmenjenih zadatih vrednosti u odnosu na trenutno stanje) | trošak + λ·broj promenjenih promenljivih; GAdapt kolonska raznovrsnost bira koje se menjaju | SparseEA (Tian i sar. 2019), L0 regularizacija | 5–10% |
| K6 | Teorija: vreme izvršavanja GAdapt-ovog pravila „stopa mutacije iz raznovrsnosti troškova“ na OneMax/LeadingOnes/Jump | dokaz očekivanog vremena; poređenje sa 1/5 pravilom i (1+(λ,λ)) GA | teorija kontrole parametara (Doerr i Doerr 2020), DGEA (Ursem 2002) | 20–30% za novinu, ali daleko od infrastrukture i visok rizik izvodljivosti dokaza |
| K7 | Postepeno usitnjavanje mreže vrednosti (korak) kad kolonska raznovrsnost promenljive kolabira | adaptivna rezolucija po promenljivoj | Dynamic Parameter Encoding (Schraudolph i Belew 1992), ARGOT (Shaefer 1987) | < 5% |
| K8 | Toplo pokretanje između uzastopnih perioda dispečinga | prenos populacije + imigracija | dinamička EA (memorija, imigranti) | < 5% |

**Moj izbor pre poređenja:** K1 (najveća praktična vrednost za infrastrukturu i jasna matematička tvrdnja), zatim K6
(najverovatnija formalna novina, ali rizična). Ostali verovatno padaju.

## Ishod gate-a (posle čitanja Codex 016)
- **K1: NO-GO kao originalna metoda** (Codex 017, 2–5%): Rosete-Suárez, Ochoa, Sebag 1999 (rani prekid evaluacije uz
  granicu i redosled iz prethodne generacije; DOI nije proveren), Bongard i Hornby 2010
  ([10.1145/1830483.1830504](https://doi.org/10.1145/1830483.1830504)), Knuth i Moore 1975 (alfa-beta). Korisno:
  GAdapt odseca na elitni skup pre statistike (`ElitismCostFinder`), pa je tačna lenja evaluacija max-po-scenarijima
  moguća kao **opt-in ubrzanje bez promene putanje** (praktično, ne za tezu).
- **Codex 016 #1 (samoadaptacija svesna jedinstvenosti): NO-GO** (literature-auditor, 10–15%): Biedrzycki 2020
  „darvinovska“ popravka ([10.1016/j.swevo.2019.100627](https://doi.org/10.1016/j.swevo.2019.100627)), Hansen
  arXiv:1110.4181 (ubačena rešenja kvare adaptaciju), Yuen i Chow 2009
  ([10.1109/TEVC.2008.2003008](https://doi.org/10.1109/TEVC.2008.2003008)), Raidl i Hu 2010
  ([10.1007/978-3-642-12139-5_21](https://doi.org/10.1007/978-3-642-12139-5_21)), Wang i Gao 2013 (NrGA na
  distributivnoj mreži, [10.1109/tpwrs.2013.2238259](https://doi.org/10.1109/tpwrs.2013.2238259)). Moguće samo
  kao ablacija (jedinstvenost+popravka / memoizacija / signal bez popravljenih).
- Sledeći krug: K6 (Codex 018) i Codex 016 #2 (literature-auditor).
- **Codex 016 #2 (DC + AC provere za signal adaptacije): NO-GO** (literature-auditor, 10–15%): Horvitz–Thompson 1952,
  uopšteni diferencni procenjivač (Cassel, Särndal, Wretman 1976, [10.1093/biomet/63.3.615](https://doi.org/10.1093/biomet/63.3.615)),
  MFMC (Peherstorfer i sar. 2016; Qian i sar. 2018), prediction-powered inference (Angelopoulos i sar. 2023,
  [10.1126/science.adi6000](https://doi.org/10.1126/science.adi6000)); evolution control (Jin i sar. 2002).
- **K6 (teorija pravila raznovrsnosti troškova): NO-GO kao glavni doprinos** (Codex 018): Srinivas i Patnaik 1994
  ([10.1109/21.286385](https://doi.org/10.1109/21.286385)), DGEA (Ursem 2002), stagnation detection (Rajabi i Witt;
  Doerr i Rajabi). Na platou Jump_k pravilo daje Θ(n^k) kao statička mutacija → nema priče o ubrzanju.
- **Nalaz o biblioteci (oba revizora):** `average_difference` = (max − min)/(n − 1) → podrazumevana raznovrsnost
  troškova je normalizovan log-RASPON preživelih (unet u CLAUDE.md).
- Ukupno odbačeno: 7 (23. okt.) + 4 danas = 11.
