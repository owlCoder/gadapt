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
