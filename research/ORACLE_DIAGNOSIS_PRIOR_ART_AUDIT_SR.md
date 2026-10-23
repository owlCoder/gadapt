# Prior-art provera: validirani protokol uzročne dijagnoze zaostatka optimizatora (oracle intervencije)

**23. oktobar 2026.** Kandidat: Codex 010 §1 (jedini ograničeni GO, procena ~40%). Nezavisna adversarijalna provera:
`literature-auditor` agent (OpenAlex, Crossref, arXiv, web; Semantic Scholar delimično ograničen sa HTTP 429).
DOI-je sam proverio na Crossref-u (svih 12 sa DOI-jem; Kostovska 2025 preko pretrage).

## Odluka: **NO-GO kao originalna metoda (novost nije utvrđena)**

| Deo kandidata | Već postoji u |
|---|---|
| Oracle/optimalni korak kao referenca za ocenu jednog mehanizma | Hansen, Atamna, Auger 2014, [10.1007/978-3-319-10762-2_6](https://doi.org/10.1007/978-3-319-10762-2_6); Krause, Glasmachers, Igel 2017, [10.1145/3040718.3040725](https://doi.org/10.1145/3040718.3040725) |
| Dijagnostički alat za optimizatore validiran na generisanim (podmetnutim) scenarijima | BIAS: Vermetten i sar. 2022, [10.1109/TEVC.2022.3189848](https://doi.org/10.1109/TEVC.2022.3189848) |
| Poznata tačna politika kao ground truth za analizu/kontrolu optimizatora | Biedenkapp i sar. 2022, [10.1145/3512290.3528846](https://doi.org/10.1145/3512290.3528846) |
| Pripisivanje performansi komponentama | Fawcett, Hoos 2015/16, [10.1007/s10732-014-9275-9](https://doi.org/10.1007/s10732-014-9275-9); Kostovska i sar. 2025, [10.1162/evco_a_00356](https://doi.org/10.1162/evco_a_00356); IOHxplainer arXiv:2401.17842 |
| Uzročna (interventna) dijagnoza performansi | Unicorn: Iqbal i sar. 2022, [10.1145/3492321.3519575](https://doi.org/10.1145/3492321.3519575) |
| Validacija metoda atribucije na podmetnutim mehanizmima, sa lažnim kontrolama | Zhou i sar. 2022, [10.1609/aaai.v36i9.21196](https://doi.org/10.1609/aaai.v36i9.21196); InterpBench arXiv:2407.14494; Jones, Harrold 2005, [10.1145/1101908.1101949](https://doi.org/10.1145/1101908.1101949); Just i sar. 2014, [10.1145/2635868.2635929](https://doi.org/10.1145/2635868.2635929) |

- Ostaje samo **kombinacija** poznatih delova primenjena na nov objekat (zaostatak optimizatora A za B); nema teoreme;
  pragovi (90% / 5%) su izbor dizajna.
- **Kružnost:** ako se podmetnu mehanizmi iz istih porodica koje oracle popravlja, visoka tačnost je skoro zagarantovana.
- **Pristrasno poređenje:** oracle koristi znanje o optimumu, ablacija ne.
- Procene agenta: ~55% da niko nije objavio tačno ovu kombinaciju; ~20% da je recenzent prihvati kao nov metod.

## Posledica
- Po `CLAUDE.md`: STOP pre implementacije kao PhD metode.
- Prihvatljivo kao **empirijsko poglavlje** (prenos validacije sa podmetnutim ground truth-om na objašnjavanje
  zaostatka optimizatora, I53 kao studija slučaja), uz eksplicitno oslanjanje na gornje radove i obaveznu ispravku
  kružnosti (podmetnuti mehanizmi van porodica koje oracle popravlja; slepo podmetanje treće strane).
