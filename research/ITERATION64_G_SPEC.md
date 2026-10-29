# ITERATION64-G: indeks sprege κ kao jeftina dijagnostika „kada GAdapt, kada CMA“ — specifikacija predikcije (zamrznuta PRE uvida u rezultate I64-I)

Motivacija (mentor: stabilan, tačan, primenljiv): E je pokazao da GAdapt-ova prednost zavisi od orijentacije osa. Industrijski korisnik treba jeftin test pre izbora algoritma.
**Definicija**: κ = medijana (20–30 tačaka) od ‖H − diag(H)‖_F / ‖H‖_F, H = Hesijan cilja procenjen centralnim konačnim razlikama (jedinična kocka, h = 10⁻³; na diskretnoj mreži h = 2 koraka mreže, unutrašnje tačke mreže). κ = 0: Hesijan dijagonalan (osno-separabilno u drugom redu); κ → 1: jaka sprega. Cena ≈ 2D² + 1 poziva cilja po tački. Nije novo svojstvo (spregnutost/separabilnost je poznata); ovo je operativna provera za bibliotečke korisnike.

## Razvojni nalaz (POST HOC, na E arhivi, 63 ćelije; `research/i64/g_kappa.py`, `kappa_cells.json`, `kappa_vs_outcome.json`)
Spearman ρ(κ, A_GAdapt − A_IPOP) = −0,39 (p = 0,0016); ρ(κ, CVaR_IPOP − CVaR_GAdapt) = −0,52 (p = 1·10⁻⁵). κ < 0,01 (21 ćelija): srednje ΔA = +0,093 u korist GAdapt-a, GAdapt bolji po A u 57% ćelija, po CVaR u 38%;
κ ≥ 0,01: GAdapt bolji po A u 8–23% ćelija i po CVaR u 0–31%. Ovo je razvojni uvid (isti podaci su generisali hipotezu), ne potvrda; funkcije su klasične.

## Predikcija van uzorka (ORPD, I64-I) — upisana pre uvida u I64-I
κ je izračunat na 8 ORPD ćelija PRE uvida u bilo koji I64-I rezultat (`research/results/iteration64_i/kappa_cells.json`, `g_kappa_infra.py`): case30 j2/j3: 0,598/0,617; case39 j2/j3/j4: 0,802/0,745/0,723; case24_ieee_rts j2/j3/j4: 0,661/0,660/0,666. Sve ćelije su jako spregnute (κ ≥ 0,6).
- **Predikcija P-G1**: u ≥ 6 od 8 ćelija IPOP ima niži (bolji) ćelijski CVaR₀,₉(L) od GAdapt-M pri B = 12.000 (E-razvojni udeo „GAdapt bolji po CVaR“ za κ ≥ 0,3 bio je 6–31%).
- **Predikcija P-G2**: u ≥ 6 od 8 ćelija IPOP ima nižu ćelijsku medijanu G (ili jednaku) od GAdapt-M.
- Ishod: „potvrđeno“ ako su obe ≥ 6/8; „opovrgnuto“ ako je GAdapt-M bolji u ≥ 6/8 po obe; inače „neodlučeno“. Sa 8 ćelija test nije snažan (6/8 jednostrani sign-test p = 0,145); koristi se kao provera konzistentnosti, ne kao dokaz. Izuzetak: izvodljivost (P(izvodljivo)) se ne predviđa; I57 je pokazao da GAdapt ume biti jedini koji uvek nalazi izvodljivo na case57.
- Posledica za tezu: ako je potvrđeno i opovrgnuto nije, κ ide u literaturu kao praktična dijagnostika sa jasnim ograničenjem (klasične funkcije + 8 ORPD ćelija); ako je opovrgnuto, κ se odbacuje.
