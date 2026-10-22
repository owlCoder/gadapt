# H3 — prior-art audit: prelaz GAdapt → lokalni intenzifikator vođen raznovrsnošću

**23. oktobar 2026.** Pretragu je uradio `literature-auditor` agent (OpenAlex, Crossref, arXiv, web; Semantic Scholar
delimično ograničen sa HTTP 429, dblp nije pokriven). Ključne DOI-je sam lično proverio na Crossref-u (EMDE, MA-LS-Chains,
HSES, Q-HSES). Bez koda i bez eksperimenata.

## H3 (kandidat)
Kada GAdapt-ovi sopstveni signali raznovrsnosti (koeficijent raznovrsnosti troškova, kolonski koeficijenti) ili
stagnacija pokažu konvergenciju:
- pokreće se lokalni intenzifikator (CMA-ES ili (1+1)-ES), iz elite, sa dijagonalnim početnim korakom iz disperzije
  populacije po promenljivoj;
- intenzifikator dobija udeo budžeta;
- posle njegove stagnacije pretraga se vraća u GA, sa ubačenim poboljšanim elitnim rešenjem.

## Odluka: **NO-GO kao PhD metoda (novost nije utvrđena)**

| Deo H3 | Već postoji u |
|---|---|
| Lokalna pretraga iz najboljeg, okinuta raznovrsnošću, Lamarckov povratak | EMDE: Tirronen, Neri, Kärkkäinen, Majava, Rossi 2008, [10.1162/evco.2008.16.4.529](https://doi.org/10.1162/evco.2008.16.4.529); FAMA: Caponio i sar. 2007, [10.1109/TSMCB.2006.883271](https://doi.org/10.1109/TSMCB.2006.883271) |
| Početni korak intenzifikatora izveden iz mere raznovrsnosti | EMDE (σ0 = ν/2 · opseg promenljive) |
| CMA-ES kao intenzifikator u GA, start u eliti, σ0 iz disperzije populacije, udeo budžeta, povratak u GA | MA-LS-Chains: Molina, Lozano, García-Martínez, Herrera 2010, [10.1162/evco.2010.18.1.18102](https://doi.org/10.1162/evco.2010.18.1.18102) |
| Istraživanje → CMA-ES inicijalizovan iz populacije → istraživanje; prelaz vođen stagnacijom | HSES: Zhang, Shi 2018, [10.1109/CEC.2018.8477908](https://doi.org/10.1109/CEC.2018.8477908); Q-HSES: Zhang i sar. 2023, [10.1109/MCI.2022.3222057](https://doi.org/10.1109/MCI.2022.3222057) |
| Topli start CMA-ES posle prelaza | Schröder i sar. 2022, arXiv:2204.06539; Kostovska i sar. 2022, [10.1007/978-3-031-14714-2_4](https://doi.org/10.1007/978-3-031-14714-2_4) |
| Restart pri stagnaciji | IPOP: Auger, Hansen 2005, [10.1109/CEC.2005.1554902](https://doi.org/10.1109/CEC.2005.1554902); BIPOP: Hansen 2009, [10.1145/1570256.1570333](https://doi.org/10.1145/1570256.1570333) |

- **Preostaje samo uska instanca specifična za GAdapt:** GAdapt-ovi koeficijenti kao prag i dijagonalno C0 iz
  disperzije po promenljivoj. To je standardna procena momenata (EMNA, UMDA_c) i manja varijanta MA-LS-Chains i
  Schröderovog toplog starta.
- **Empirijski deo:** nije nađen CMA-ES hibrid na valve-point dispečingu. To je empirijska, a ne metodološka praznina.

## Posledica
- Po `CLAUDE.md`: STOP pre implementacije za PhD.
- H3 može postojati samo kao **opt-in praktična funkcija** (opcija B), uz obavezno citiranje EMDE i MA-LS-Chains.
- Fer eksperiment bi tada morao da uključi kontrole: IPOP/BIPOP-CMA-ES, MA-LS-Chains, memetski algoritam po EMDE
  pravilu, fiksni prelaz (HSES), ablacije okidača i σ0, L-SHADE i plain GAdapt.
