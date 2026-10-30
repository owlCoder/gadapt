Ukupan ishod: **MATCH u sve četiri tačke**. Proračun je urađen nezavisnim kodom koristeći samo `gzip/json`, NumPy i sirove događaje; projektni analizatori nisu uvezeni i fajlovi nisu menjani.

## 1. Metrike, kontrasti i agregati — MATCH

Izračunato je per-run \(A,g,L\) za svih 6.300 uparenih H/R zadataka. CVaR po ćeliji je prosek 10 najvećih od 100 vrednosti \(L\).

Sirove težine su \(1/81\) za funkcije sa tri dimenzije, odnosno \(1/27\) za funkcije sa jednom dimenzijom, pre renormalizacije u `rot` i `orig+shift`.

| Kontrast | Nezavisni rezultat | `analysis.json.gz` | \(|\Delta|\) |
|---|---:|---:|---:|
| c1 A_rot(H−R) | 0.13125542181069957 | 0.13125542181069957 | 0 |
| c2 A_nonrot(H−R) | 0.17786820987654323 | 0.17786820987654323 | 0 |
| c3 CVaR_rot(R−H) | 0.005510165520888415 | 0.005510165520888415 | 0 |
| c4 CVaR_nonrot(R−H) | 0.013415389117766657 | 0.013415389117766654 | \(3.47\times10^{-18}\) |

Maksimalna apsolutna razlika kontrasta: **\(3.47\times10^{-18}\)**.

Agregati po varijanti:

| Varijanta | Konf. | A | CVaR₀․₉ | medijana jaza |
|---|---|---:|---:|---:|
| orig | H | 0.7628009670781892 | 0.004771194868098625 | 0.0021636598292582394 |
| orig | R | 0.5875884053497942 | 0.018367118210008680 | 0.011317462511590028 |
| shift | H | 0.7707763580246914 | 0.004320262140456046 | 0.0021865290068182634 |
| shift | R | 0.5902525000000000 | 0.017555117034079304 | 0.008907075711523254 |
| rot | H | 0.7196330246913579 | 0.011916067967877472 | 0.004433321282439508 |
| rot | R | 0.5883776028806584 | 0.017426233488765888 | 0.009113523294050307 |

Maksimalna apsolutna razlika svih agregata: **\(2.22\times10^{-16}\)**.

## 2. Simultani max-studentizovani bootstrap — MATCH

Reimplementirano je 20.000 ponavljanja sa `default_rng(71)`, redosledom ćelija 0–62 i jednim zajedničkim uzorkom indeksa po ćeliji za H i R.

Standardne greške:

- c1: 0.0030385494825614784
- c2: 0.0017275552591979647
- c3: 0.0005779064282224863
- c4: 0.0004117810274564945

Dobijeno je:

- \(t^*=2.5027541906927815\)
- arhiva: 2.502754190692769
- razlika: **\(1.24\times10^{-14}\)**

| Kontrast | Donja granica | Gornja granica |
|---|---:|---:|
| c1 | 0.12365067935959145 | 0.13886016426180770 |
| c2 | 0.17354456371193216 | 0.18219185604115430 |
| c3 | 0.004063807785826290 | 0.006956523255950540 |
| c4 | 0.012384802425652137 | 0.014445975809881178 |

Maksimalna razlika granica prema arhivi: **\(4.16\times10^{-17}\)**.

- **H64a1: supported**, jer je LB = 0.1236506794 > 0.02.
- **H64a2: supported**, jer je LB = 0.1735445637 > 0.02.
- `contribution_supported = true`.

## 3. Struktura i provenijencija — MATCH

R zapisi:

- 6.300 zapisa i **6.300 jedinstvenih `(cell, seed)` zadataka**
- 63 ćelije × 100 semena
- formula semena tačna za sve: `67_000_000 + 1000*c + s`, \(s=1,\ldots,100\)
- `config = hyb_rand` i `purpose = run` u svih 6.300
- `ok = true` i `calls = 12000` u svih 6.300
- sva vremena događaja su u `[1,12000]` i strogo rastu
- svih 6.300 zadataka tačno je upareno sa H zapisima
- vrednosti best-so-far su strogo opadajuće između zabeleženih poboljšanja

Random faza:

- prvi događaj je na pozivu **1 u svih 6.300 zapisa**, dakle unutar random faze do poziva 3.600
- ukupno je 55.337 zabeleženih poboljšanja do poziva 3.600
- arhiva ne čuva evaluirane tačke, pa se njihova uniformnost ili tačan RNG niz ne mogu nezavisno proveriti; može se potvrditi samo vremenska pripadnost fazi i monotonost best-so-far zapisa

Metapodaci:

- `check_repro` i `run` imaju identičan manifest
- sva tri artefakta imaju identične `inputs`
- `freeze_commit = 3e107a161696ae072d61f99c27c997f650c69934`
- u `check_repro`/`run` commit je u manifestu; u `analysis` je direktno polje
- sva četiri ulazna SHA-256 heša odgovaraju stvarnim fajlovima
- sadržaj specifikacije ima isti SHA-256 kao verzija na commitu `3e107a1`: `264761bc…1701e7`

`check_repro` sadrži preflight `{calls: 12000, random_calls: 3600}`. Tri E3 provere — ćelije 2, 29 i 28 — označene su kao identične.

## 4. Tvrdnje i ograničenja — MATCH

Nisam našao prekoračenje dozvoljene tvrdnje. Specifikacija eksplicitno ograničava atribuciju na zamenu prve faze u fiksiranom hibridu i izričito navodi šta se ne tvrdi u [ITERATION64_A_SPEC.md](/Users/danijel/Desktop/gadapt/research/ITERATION64_A_SPEC.md:15).

Izveštaj takođe eksplicitno navodi traženi weak-start konfaund: CMA kreće iz najbolje slučajne tačke sa `σ₀=0,05`, što može biti nepovoljan start, i zato rezultat nije „čista mera kvaliteta GAdapt faze“ — [ITERATION64_A_REPORT_SR.md](/Users/danijel/Desktop/gadapt/research/ITERATION64_A_REPORT_SR.md:29).

Dakle, opravdana formulacija je upravo: **efekat zamene GAdapt prve faze od 30% uniformnim uzorkovanjem u ovom konkretnom, fiksiranom hibridu**.