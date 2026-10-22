# H1 — sistematski prior-art audit (gray-box partition crossover za mrežni dizajn)

**22. oktobar 2026.** Gate odobren od korisnika. Bez koda i bez eksperimenata. Pretragu je uradio read-only
`literature-auditor` agent. Ja sam potom **lično** proverio sve DOI-je u tabeli na Crossref-u (13/13: naslov, prvi autor
i godina se poklapaju) i lično pročitao ključne delove dva rada (Chicano i sar. 2024, str. 3–7; Jordán i sar. 2025, §1–4).
Kontekst: [POST_I41_NOVELTY_AUDIT_SR.md](POST_I41_NOVELTY_AUDIT_SR.md) §5–6.

## 1. Zaključak

1. **Ekvivalentan rad nije nađen.** Nijedan rad ne primenjuje PX ni VIG izveden iz deljenja linkova na dimenzionisanje
   mreže sa fiksnim kandidatskim putanjama. Zato nema STOP-a zbog ekvivalencije.
2. **Pretpostavljeni matematički diferencijator je opovrgnut.** Diferencijator je bio „visoka arnost, van k-ograničenih
   funkcija“. Chicano, Whitley, Ochoa, Tinós (2024), Teorema 1 i §3.2 (lično pročitano), dokazuju dekompoziciju delta
   funkcije i optimalnost PX-a („najbolji od 2^q“) za **proizvoljno** `f : X → ℝ`, ako su potezi međusobno neinteragujući.
   Arnost i max/ceil oblik `g_e` ne ulaze u teoremu. Oni samo čine VIG gušćim i parcijalnu evaluaciju skupljom.
   H1 operator je zato **specijalan slučaj** poznate teorije.
3. **„PX kao opt-in operator u GA“ nije novo.** Hibridi GA+PX postoje (Tinós 2015; Przewoźniczek i sar. 2022, 2026).
4. **Novost metode: NIJE UTVRĐENA.** Prema `CLAUDE.md`, implementacija PX-a u GAdapt-u ostaje **zabranjena**.
5. **Najuža odbranjiva tvrdnja** (primena i merenje, ne metoda): *prvo merenje broja PX komponenti na VIG-ovima
   dvoputnog modularnog mrežnog dizajna nad arhiviranim stvarnim topologijama i, ako to prođe, prvi test PX-a unutar
   samoadaptivnog GA-a na ovoj klasi pri istom broju evaluacija.* To je empirijski doprinos, ne doktorska metoda.
   Važi samo ako Faza 0 prođe.
6. **Faza 0 je i dalje opravdana**, jer je to jeftina falsifikacija preostale (empirijske) tvrdnje, a korisnik ju je
   odobrio. Literatura nema nijedno merenje broja PX komponenti `k` na telekom topologijama, ali ima jasne indikacije
   da gusti realni VIG-ovi daju `k ≈ 1` (§4).

## 2. Najbliži radovi (DOI lično provereni na Crossref-u)

| Rad | Sadržaj | Odnos prema H1 | Pročitano |
|---|---|---|---|
| Chicano, Whitley, Ochoa, Tinós, *Generalizing and Unifying Gray-box Combinatorial Optimization Operators*, arXiv:2407.06742 (2024), [arxiv.org/abs/2407.06742](https://arxiv.org/abs/2407.06742); arXiv DOI nije proveren na Crossref-u | Def. 1 (neinteragujući potezi na skupu Y), Teorema 1 (dekompozicija), Kor. 1, §3.2 PX za bilo koje `f` | **Obuhvata** teorijski deo H1 | Pun tekst str. 3–7 (lično) |
| Tinós, Whitley, Chicano, FOGA 2015, [10.1145/2725494.2725497](https://doi.org/10.1145/2725494.2725497) | PX za k-ograničene pseudo-Bulove funkcije | Originalni PX | Sažetak |
| Whitley, Chicano, Goldman, Evol. Comput. 2016, [10.1162/EVCO_a_00184](https://doi.org/10.1162/EVCO_a_00184) | Gray-box za Mk landscapes, hiperravanski proseci | Pozadina. **Sažetak ne pominje PX** → ispravljena atribucija u POST_I41 auditu | Sažetak (lično) |
| Chicano, Ochoa, Whitley, Tinós, *Dynastic Potential Crossover*, Evol. Comput. 2022, [10.1162/evco_a_00305](https://doi.org/10.1162/evco_a_00305) | Najbolji potomak u celoj hiperravni roditelja | Jači od PX-a; prirodna kontrola za Fazu 1 | Sažetak |
| Chicano i sar., APX, GECCO 2018, [10.1145/3205455.3205561](https://doi.org/10.1145/3205455.3205561) | Sečenje u artikulacionim tačkama → više komponenti | Popravka za gust VIG; kontrola za Fazu 1 | Metapodaci |
| Hauschild, Pelikan, *Network crossover*, GECCO 2010, [10.1145/1830483.1830612](https://doi.org/10.1145/1830483.1830612) | Ukrštanje vođeno poznatom mrežom interakcija | Raniji crossover svestan strukture | Metapodaci |
| Jordán, Palanca, Sánchez-Anguix, Julián, Complex Intell. Syst. 2025, [10.1007/s40747-024-01721-8](https://doi.org/10.1007/s40747-024-01721-8) | „Subgraph crossover“: nasumična razmena okolina u grafu za `F = Σ_i f_i(X_i)`. Sintetički grafovi, primena na lokaciju punjača | **Delimično**: ista aditivna struktura, ali nema PX dekompozicije ni garancije optimalnosti; nije mrežni dizajn | Pun tekst §1–4 (lično) |
| Luong, La Poutré, Bosman, Evol. Comput. 2018, [10.1162/evco_a_00209](https://doi.org/10.1162/evco_a_00209) | GOMEA sa naučenim linkage stablom za proširenje distributivne mreže | **Delimično**: infrastruktura + linkage-aware EA, ali naučena (ne egzaktna) veza i drugo kodiranje | Delimičan pun tekst (agent) |
| Przewoźniczek, Komarnicki, ASOC 2021, [10.1016/j.asoc.2021.107864](https://doi.org/10.1016/j.asoc.2021.107864) | Empirijska dekompozicija za velik NP-težak problem preživljivosti mreže | **Delimično**: naučena dekompozicija, ne iz deljenja linkova | Sažetak |
| Przewoźniczek, Tinós, Frej, Komarnicki, GECCO 2022, [10.1145/3512290.3528734](https://doi.org/10.1145/3512290.3528734); Przewoźniczek i sar., GECCO 2026, [10.1145/3795095.3805172](https://doi.org/10.1145/3795095.3805172) | Empirijski VIG + PX unutar GA | PX u opštem GA već postoji | Sažetak |
| Przewoźniczek, Chicano, Tinós i sar., GECCO 2025, [10.1145/3712256.3726410](https://doi.org/10.1145/3712256.3726410) | U realnim problemima „sve promenljive“ mogu biti zavisne → PX maske beskorisne | **Direktno relevantno za rizik Faze 0** | Sažetak |
| Tsuji, Munetomo, Akama, CEC 2007, [10.1109/cec.2007.4424492](https://doi.org/10.1109/cec.2007.4424492) | Linkage identifikacija za problem mrežnog dizajna sa preklapajućim blokovima | **Delimično**: black-box linkage | Sažetak (oštećen) |
| Abdelkafi, Derbel, Liefooghe, Whitley, PPSN 2020, [10.1007/978-3-030-58112-1_21](https://doi.org/10.1007/978-3-030-58112-1_21) | PX za QAP (gusta interakcija) traži redizajn | Presedan: gust problem ubija običan PX | Sažetak |

## 3. Dnevnik pretrage (2026-10-22, agent; brojevi pogodaka su iz njegovog izveštaja)

| # | Upit / izvor | Pogoci | Relevantni |
|---|---|---|---|
| 1 | OpenAlex `search=partition crossover network design` | 30.185 (fuzzy) | 0 u top 25 |
| 2 | OpenAlex `search="partition crossover"` (3 strane) | 230 | ~40 PX porodica; 0 mrežni dizajn |
| 3 | OpenAlex `title_and_abstract="partition crossover"` (svi) | 76 | 0 mreža/telekom/grid; 3 VRP; Jordán 2025 |
| 4 | OpenAlex `"gray box" optimization variable interaction graph` (top 50) | 3.085 | ~15 gray-box; 0 mreža |
| 5 | OpenAlex t&a (PX ∨ gray-box ∨ optimal mixing) ∧ (network design ∨ routing ∨ capacity ∨ telecom ∨ power grid) | 65 | 1 (Luong 2014) |
| 6 | OpenAlex t&a (linkage tree ∨ GOMEA ∨ DSMGA ∨ linkage learning) ∧ (network ∨ routing ∨ path) | 49 | 7 |
| 7 | OpenAlex t&a "variable interaction graph" | 28 | 12 gray-box; 0 na mrežnim topologijama |
| 8 | OpenAlex GA ∧ (multi-hour ∨ multi-period) ∧ (network design ∨ dimensioning) | 97 | 0 |
| 9 | OpenAlex GA ∧ "candidate paths" ∧ crossover ∧ (capacity ∨ modular ∨ dimensioning) | 2 | 0 |
| 10 | OpenAlex crossover ∧ (interaction graph ∨ linkage ∨ decomposition) ∧ (network design ∨ RWA ∨ path selection ∨ multicommodity) | 10 | 1 (Tsuji) |
| 11 | OpenAlex autor Przewoźniczek + „network“ | 17 | 4 |
| 12 | Lista referenci Jordán 2025 | 61 | PX, APX, GPX2 |
| 13 | Web pretraga „partition crossover“ + network design/telecom/capacity/routing | 9 | 0 |
| 14 | Web pretraga „variable interaction graph“ + SNDlib/topologija | 9 | 0 |

**Praznine u pokrivenosti (otvoreno):** Semantic Scholar API je vratio HTTP 429, dblp je blokirao bota, a Google Scholar
nije direktno pretražen. Pun tekst Przewoźniczek 2016/2021 i Tinós 2015 nije pročitan. Pre bilo kakve tvrdnje o novini
u publikaciji ove izvore treba ponovo proveriti.

## 4. Relevantno za Fazu 0

- Nema objavljenog merenja `k` na SNDlib/telekom topologijama, pa je Faza 0 informativna.
- Literatura ukazuje na veliki rizik: gusti realni VIG-ovi (Przewoźniczek 2025, QAP 2020) i postojanje APX/DPX baš da
  bi se ublažio slučaj sa malo komponenti.
- Agentova **gruba procena** (nije dokaz i ne utiče na protokol): na mreži veličine cost266 sa 10% razlike očekuje se
  džinovska komponenta, tj. `k ≈ 1`.
- Ideja „Y-restriktovane“ neinterakcije (ravni delovi stepenaste cene između dva roditelja mogu da razdvoje komponentu
  koju strukturni VIG spaja) već je obuhvaćena Def. 1 Chicano 2024. Eventualno novo bi bio samo efikasan detektor za
  max/ceil. Za to je potreban saobraćaj, pa je van Faze 0 i traži zaseban prior-art audit.

## 5. Odluka

- **H1 kao metoda: NO-GO** (novost nije utvrđena; teorijski deo je specijalan slučaj Chicano 2024).
- **Faza 0 (strukturno merenje): GO**, prema [ITERATION42_PROTOCOL.md](ITERATION42_PROTOCOL.md), zamrznutom pre koda.
- Čak i ako Faza 0 prođe, sledeći korak nije implementacija, nego nova odluka korisnika o tome da li je empirijska
  tvrdnja iz §1.5 vredna Faze 1 (uz data-gate i APX/DPX kao kontrole).
