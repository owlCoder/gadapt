# ITERATION64-C: koeficijentni potpis gubitka GAdapt-a pod ortogonalnom transformacijom — izveštaj (generisan iz arhive)

Specifikacija: [ITERATION64_C_SPEC.md](ITERATION64_C_SPEC.md). 21 par (funkcija, dimenzija), `shift` naspram `rotm` (isti pomeraj, Q iz E `rot`), GAdapt-M, prvih 1.200 poziva, 30 semena; koeficijenti kolonske raznovrsnosti (log-relative) snimani pasivno po generaciji.

- Ponderisana srednja Δ (pad CV koeficijenata, shift − rotm): **0.0132** [-0.0466; 0.0709] (Bonferroni α/3 = 0.0167); Δ_k > 0 u 14 od 21 nenultih parova (binomni p = 0.0946)
- Spearman ρ(Δ_k, ΔA_k) = **0.274** [-0.085; 0.618]; osnovna linija ρ(E_k, ΔA_k) = 0.578; razlika = -0.304 [-0.721; 0.148]

- **H64c1** (homogenizacija koeficijenata): **undecided**
- **H64c2** (asocijacija sa padom A): **undecided**
- **H64c3** (jača marginalna rang-asocijacija od osnovne linije): **undecided**
- predviđeni koeficijentni potpis podržan: **False**; jača marginalna asocijacija od osnovne linije: **False**

Spearman ρ(Δ_k, ΔA_k) uz izostavljanje jedne funkcije (opisno):

| izostavljena funkcija | ρ |
|---|---|
| sphere | 0.230 |
| rosenbrock | 0.257 |
| rastrigin | 0.342 |
| ackley | 0.298 |
| griewank | 0.288 |
| styblinski_tang | 0.329 |
| beale | 0.247 |
| himmelblau | 0.236 |
| booth | 0.208 |

Po parovima:

| par | Δ_k | ΔA_k | E_k |
|---|---|---|---|
| sphere|2 | -0.0165 | -0.0002 | -0.0387 |
| sphere|7 | 0.0007 | 0.0034 | 0.1774 |
| sphere|20 | 0.0068 | -0.0008 | 0.0203 |
| rosenbrock|2 | -0.1985 | -0.0872 | -0.5757 |
| rosenbrock|7 | 0.1358 | -0.0029 | 0.1129 |
| rosenbrock|20 | 0.0382 | 0.0472 | 0.1381 |
| rastrigin|2 | -0.0178 | 0.3857 | 3.1824 |
| rastrigin|7 | 0.1014 | 0.5259 | 0.3654 |
| rastrigin|20 | 0.1150 | 0.0132 | 0.2650 |
| ackley|2 | 0.0363 | 0.0009 | -0.0431 |
| ackley|7 | 0.0156 | 0.0270 | 0.1792 |
| ackley|20 | 0.0264 | 0.1298 | 0.0942 |
| griewank|2 | 0.0276 | 0.0320 | -0.1166 |
| griewank|7 | 0.0967 | 0.0188 | 0.1578 |
| griewank|20 | 0.0011 | 0.0950 | -0.0003 |
| styblinski_tang|2 | -0.0844 | 0.0146 | 0.5078 |
| styblinski_tang|7 | -0.0715 | 0.5057 | 1.3865 |
| styblinski_tang|20 | 0.1449 | 0.2709 | 0.1668 |
| beale|2 | 0.1676 | 0.0693 | 1.2414 |
| himmelblau|2 | -0.1449 | 0.0037 | 0.4426 |
| booth|2 | -0.0234 | -0.0047 | -1.4315 |

## Ograničenja
Korelaciona studija na 21 fiksnu ćeliju iz 9 funkcija; meri se samo log-relative koeficijent (ne dijagonala kovarijanse); nema intervencije ni medijacije, pa se ne tvrdi uzrok; ne tvrdi se inkrementalna prediktivna vrednost; važi za GAdapt-M, native domen, b = 1.200 i ove ćelije; ne važi za diskretne probleme (ORPD se ne rotira). Bootstrap obuhvata semena i izbor funkcija, ne izbor Q i pomeraja.
