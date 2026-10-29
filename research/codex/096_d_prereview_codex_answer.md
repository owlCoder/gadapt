## Zaključak

Računska definicija estimanda je **MATCH**: nema FR/SP niti AD-N/FX-T zamene, neizvodljivi ishodi i veze obrađeni su po protokolu, težine ćelija/mreža i bootstrap su ispravni.

Međutim, postoje **tri infrastrukturna BUG-a** koji mogu dozvoliti da pogrešan ili izmenjen ulaz prođe do izveštaja, kao i dve obmanjujuće formulacije u generatoru izveštaja.

Nisam menjao nijedan fajl niti pisao u `research/results`.

## 1. Pregled koda

### MATCH — estimand i mapiranje grana

- `task63` pravilno prenosi CHT, arm, seme i FX-T vektor: [iteration63_replication.py:72](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:72).
- `run63` zahteva tačno 12.000 poziva i odsustvo grešaka: [iteration63_replication.py:184](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:184).
- `gap(None) → None`, odnosno algoritamska neizvodljivost nije izbačena iz estimanda: [iteration63_replication.py:272](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:272).
- `win2(FX-T, AD-N)` pravilno daje:

  - oba neizvodljiva: vezu;
  - samo FX-T izvodljiv: pobedu;
  - samo AD-N izvodljiv: poraz;
  - prag veze uključuje `|Δ| ≤ 0,001`.

  Videti [iteration63_replication.py:278](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:278).

- `d = W_FR − W_SP`; nema zamene FR/SP: [iteration63_replication.py:294](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:294).
- `stage_analyse` koristi FX-T kao kandidata, AD-N kao komparator: [d_study.py:179](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:179).
- Negativni jazovi ostaju dozvoljeni; `None` se izbacuje samo iz opisne medijane, ne iz `d`: [d_study.py:181](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:181).

### MATCH — težine, bootstrap i intervali

- θ je prosek scenarija unutar mreže, pa jednak prosek tri mreže: [iteration63_replication.py:658](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:658).
- Mreža sa dva scenarija ne dobija manju težinu od mreža sa tri scenarija.
- Bootstrap nezavisno resampluje semena unutar svake ćelije. Resamplovanje skalara `d` je za θ ekvivalentno resamplovanju pripadajućeg četvorovektora, jer je `d` njegova deterministička funkcija.
- Koriste se 20.000 ponavljanja, jedan `default_rng(63)`, isti niz za oba intervala, percentili 2,5/97,5 i 5/95: [iteration63_replication.py:658](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:658).
- Network means i leave-one-network-out su pravilno definisani: [d_study.py:173](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:173).

### BUG — `chosen_n` nije vezan hešom

`source_state()` čita `power["chosen_n"]`, ali `provenance()` ne hešira `power.json.gz`: [d_study.py:70](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:70), [d_study.py:80](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:80).

Dodatno, ako `power` ne postoji, dozvoljen je proizvoljan `D_N` iz okruženja. `stage_analyse` ponovo čita trenutni `power`, umesto da proveri `run["n"]`: [d_study.py:162](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:162).

Posledica: tvrdnja da je korišćen zamrznuti I63 `n` nije kriptografski dokazana. Potrebno je vezati najmanje SHA-256 `power.json.gz` i proveriti `run["n"] == source chosen_n`.

### BUG — postojeći `run_part_*` nije validiran

Postojeći part se bezuslovno učitava samo zato što mu postoji ime: [d_study.py:118](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:118).

Kasnija provera potvrđuje samo:

- ključeve `(network, j, s)`;
- prisustvo četiri arma;
- `ok=True`.

Ne proverava `seed`, `budget`, `calls`, `purpose`, `fixed`, izabrani FX-T niti tačnu jednakost sa planiranim taskom: [d_study.py:165](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:165). `units_of` takođe prepisuje duplirani arm poslednjim zapisom: [iteration63_replication.py:304](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:304).

Aktuelnih sedam partova je ručno provereno: svih 4.480 zapisa ima očekivani task, seme, FX-T, budžet, 12.000 poziva i `ok=True`. Dakle, nema uočene posledice na ovih sedam ćelija, ali je kodna zaštita nedovoljna.

### BUG — `check` nije vezan za provereni `run`

`stage_check` čuva samo broj redova i neuspeha: [d_study.py:142](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:142). Ne čuva SHA-256 `run.json.gz`. `stage_analyse` zato može analizirati drugi/izmenjeni `run` nakon uspešne provere: [d_study.py:157](/Users/danijel/Desktop/gadapt/research/i63tools/d_study.py:157).

Takođe se proverava samo završni pokušaj; ugnježdeni `first_attempt` s eventualnim prijavljenim izvodljivim svedokom nije proveren. U sedam testiranih partova nije bilo rerunova.

### BUG/MISMATCH — izveštaj

- [report_d.py:7](/Users/danijel/Desktop/gadapt/research/i63tools/report_d.py:7) kaže da kriterijum „nije dostižan ni za test tačne veličine 5%“. To je previše kategorično. Protokol navodi da takav test prolazi približno 2,1% simulacionih serija; kriterijum je veoma konzervativan, ali nije matematički nedostižan.
- [report_d.py:9](/Users/danijel/Desktop/gadapt/research/i63tools/report_d.py:9) prikazuje `positive/negative/equivalent` kao rezultate odluke. Uz početni disclaimer to nije formalna potvrda, ali treba ih eksplicitno nazvati „deskriptivnim dijagnosticima zamrznutih pragova, bez inferencijalne odluke“.
- Analiza računa medijane jazova, ali ih izveštaj uopšte ne prikazuje: [report_d.py:10](/Users/danijel/Desktop/gadapt/research/i63tools/report_d.py:10). To je nepotpuno u odnosu na opisne rezultate zahtevane protokolom.

## 2. Nezavisna reprodukcija sedam ćelija

Redosled u kolonama je: `FR/AD-N, FR/FX-T, SP/AD-N, SP/FX-T`.

| ćelija | d_mean | izvodljivost | medijana G među izvodljivim |
|---|---:|---|---|
| case30/2 | -0.012500 | 1, 1, 1, 1 | .006570, .006570, .006570, .006570 |
| case30/3 | 0.000000 | 0, 0, 0, 0 | —, —, —, — |
| case39/2 | -0.015625 | 1, 1, 1, 1 | -.006252, -.007323, -.006824, -.006987 |
| case39/3 | 0.115625 | .96875, .95625, .975, .96875 | -.007160, -.008395, -.008315, -.007320 |
| case39/4 | 0.003125 | 0, .00625, 0, 0 | —, -.001976, —, — |
| case24_ieee_rts/2 | -0.021875 | 1, 1, 1, 1 | .002756, .002756, .002756, .002756 |
| case24_ieee_rts/3 | 0.068750 | 1, 1, 1, 1 | .007195, .003199, .007195, .005922 |

**Poređenje sa projektnim kodom, jedini korak koji ga je importovao:** svih sedam `d_mean` vrednosti je **MATCH**, bez numeričke razlike.

θ₆₃, network means i leave-one-out nisu računati na ovom nepotpunom preseku. Tokom pregleda se pozadinski završio osmi part; nisam ga uključio u navedeni pre-result test.

## Nezavisni skript

```python
#!/usr/bin/env python3
"""
Nezavisna reprodukcija I63-D opisnih rezultata.

Ne importuje projektne module. Jedina nestandardna zavisnost je numpy.

Primeri:
  python3 reproduce_i63d.py

  # Eksplicitni parcijalni presek:
  python3 reproduce_i63d.py \
      research/results/iteration63d/run_part_case30_2.json.gz \
      research/results/iteration63d/run_part_case30_3.json.gz
"""

import argparse
import gzip
import glob
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np


NETWORKS = ("case30", "case39", "case24_ieee_rts")
ARMS = (
    ("FR", "AD-N"),
    ("FR", "FX-T"),
    ("SP", "AD-N"),
    ("SP", "FX-T"),
)
TIE = 0.001
BUDGET = 12000
SEED_BASE = 1_700_000_000
TEST_PURPOSE = 3


def read_gz(path):
    with gzip.open(path, "rt") as fh:
        return json.load(fh)


def win_fx_over_ad(f_fx, f_ad, normalizer):
    """Frozen W_c definition from ITERATION63_PROTOCOL.md §3."""
    if f_fx is None and f_ad is None:
        return 0.5
    if f_fx is None:
        return 0.0
    if f_ad is None:
        return 1.0

    delta = (float(f_ad) - float(f_fx)) / normalizer
    if delta > TIE:
        return 1.0
    if delta < -TIE:
        return 0.0
    return 0.5


def normalized_gap(value, normalizer):
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Non-finite best_feasible")
    return (value - normalizer) / normalizer


def expected_seed(network, j, s):
    i = NETWORKS.index(network)
    return (
        SEED_BASE
        + 10**7 * TEST_PURPOSE
        + 10**6 * i
        + 10**4 * j
        + s
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "parts",
        nargs="*",
        help="Explicit run_part_*.json.gz files; default is every part in --parts-dir",
    )
    parser.add_argument(
        "--source",
        default="research/results/iteration63",
        help="Directory containing frozen roster, normalizers, fxt and power",
    )
    parser.add_argument(
        "--parts-dir",
        default="research/results/iteration63d",
    )
    args = parser.parse_args()

    source = args.source
    normalizers = read_gz(
        os.path.join(source, "normalizers.json.gz")
    )["r"]
    roster = read_gz(os.path.join(source, "roster.json.gz"))
    expected_cells = {tuple(x) for x in roster["test"]}
    chosen_n = int(
        read_gz(os.path.join(source, "power.json.gz"))["chosen_n"]
    )
    chosen_fxt = read_gz(
        os.path.join(source, "fxt.json.gz")
    )["chosen"]

    paths = args.parts or sorted(
        glob.glob(os.path.join(args.parts_dir, "run_part_*.json.gz"))
    )
    if not paths:
        raise SystemExit("No run_part_*.json.gz files found")

    units = {}
    seen_cells = set()

    for path in paths:
        part = read_gz(path)
        records = part.get("records")
        if not isinstance(records, list):
            raise ValueError(f"{path}: missing records list")

        for rec in records:
            task = rec["task"]
            network = task["network"]
            j = int(task["j"])
            s = int(task["s"])
            arm = (task["cht"], task["arm"])
            cell = (network, j)
            key = (network, j, s)

            if cell not in expected_cells:
                raise ValueError(f"Unexpected cell: {cell}")
            if arm not in ARMS:
                raise ValueError(f"Unexpected arm: {key}, {arm}")
            if rec.get("ok") is not True:
                raise ValueError(f"Technical failure: {key}, {arm}")
            if rec.get("calls") != BUDGET:
                raise ValueError(f"Wrong call count: {key}, {arm}")
            if task.get("budget") != BUDGET:
                raise ValueError(f"Wrong task budget: {key}, {arm}")
            if task.get("purpose") != "test":
                raise ValueError(f"Wrong purpose: {key}, {arm}")
            if task.get("seed") != expected_seed(network, j, s):
                raise ValueError(f"Wrong seed: {key}, {arm}")
            if task.get("reference") is not None:
                raise ValueError(f"Unexpected reference: {key}, {arm}")
            if task.get("stop") is not False:
                raise ValueError(f"Unexpected early stop: {key}, {arm}")

            expected_fixed = (
                chosen_fxt[task["cht"]]
                if task["arm"] == "FX-T"
                else None
            )
            if task.get("fixed") != expected_fixed:
                raise ValueError(f"Wrong fixed vector: {key}, {arm}")

            unit = units.setdefault(key, {})
            if arm in unit:
                raise ValueError(f"Duplicate record: {key}, {arm}")
            unit[arm] = rec
            seen_cells.add(cell)

    by_cell = defaultdict(list)
    for key, unit in units.items():
        if set(unit) != set(ARMS):
            missing = set(ARMS) - set(unit)
            raise ValueError(f"Incomplete four-vector {key}: {missing}")
        by_cell[key[:2]].append((key[2], unit))

    expected_seeds = set(range(1, chosen_n + 1))
    for cell, rows in by_cell.items():
        seeds = {s for s, _ in rows}
        if seeds != expected_seeds:
            raise ValueError(
                f"{cell}: expected seeds 1..{chosen_n}; "
                f"missing={sorted(expected_seeds - seeds)[:10]}, "
                f"extra={sorted(seeds - expected_seeds)[:10]}"
            )

    cell_d = {}
    cell_output = {}

    for cell in sorted(by_cell):
        network, j = cell
        normalizer = float(normalizers[f"{network}|{j}"])
        if not math.isfinite(normalizer) or normalizer <= 0:
            raise ValueError(f"Invalid normalizer for {cell}")

        d_values = []
        w_fr_values = []
        w_sp_values = []
        gaps = {arm: [] for arm in ARMS}

        for _, unit in sorted(by_cell[cell]):
            w_fr = win_fx_over_ad(
                unit[("FR", "FX-T")]["best_feasible"],
                unit[("FR", "AD-N")]["best_feasible"],
                normalizer,
            )
            w_sp = win_fx_over_ad(
                unit[("SP", "FX-T")]["best_feasible"],
                unit[("SP", "AD-N")]["best_feasible"],
                normalizer,
            )

            w_fr_values.append(w_fr)
            w_sp_values.append(w_sp)
            d_values.append(w_fr - w_sp)

            for arm in ARMS:
                gaps[arm].append(
                    normalized_gap(
                        unit[arm]["best_feasible"],
                        normalizer,
                    )
                )

        d_array = np.asarray(d_values, dtype=float)
        cell_d[cell] = d_array

        unique, counts = np.unique(d_array, return_counts=True)
        row = {
            "n": int(d_array.size),
            "d_mean": float(np.mean(d_array)),
            "d_counts": {
                f"{value:g}": int(count)
                for value, count in zip(unique, counts)
            },
            "W_FR_mean": float(np.mean(w_fr_values)),
            "W_SP_mean": float(np.mean(w_sp_values)),
            "arms": {},
        }

        for arm in ARMS:
            values = gaps[arm]
            finite = [x for x in values if x is not None]
            row["arms"][f"{arm[0]}|{arm[1]}"] = {
                "feasible": len(finite) / len(values),
                "median_gap": (
                    float(np.median(np.asarray(finite, dtype=float)))
                    if finite
                    else None
                ),
            }

        cell_output[f"{network}|{j}"] = row

    missing_cells = sorted(expected_cells - seen_cells)
    unexpected_cells = sorted(seen_cells - expected_cells)
    if unexpected_cells:
        raise ValueError(f"Unexpected cells: {unexpected_cells}")

    output = {
        "status": "complete" if not missing_cells else "partial",
        "chosen_n": chosen_n,
        "cells": cell_output,
        "missing_cells": [list(x) for x in missing_cells],
    }

    # Global quantities are forbidden for an incomplete roster.
    if not missing_cells:
        network_means = {}
        for network in NETWORKS:
            means = [
                float(np.mean(values))
                for cell, values in cell_d.items()
                if cell[0] == network
            ]
            if not means:
                raise ValueError(f"No cells for network {network}")
            network_means[network] = float(np.mean(means))

        theta_63 = float(
            np.mean([network_means[n] for n in NETWORKS])
        )
        leave_one_out = {
            network: float(
                np.mean([
                    network_means[other]
                    for other in NETWORKS
                    if other != network
                ])
            )
            for network in NETWORKS
        }

        output["theta_63"] = theta_63
        output["network_means"] = network_means
        output["leave_one_network_out"] = leave_one_out
    else:
        output["global_estimates"] = None
        output["note"] = (
            "theta_63, network means and leave-one-network-out "
            "are intentionally omitted for an incomplete roster"
        )

    json.dump(
        output,
        sys.stdout,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

## 3. Šta finalni izveštaj mora dodatno da kaže

- I63-D je post-STOP, deskriptivna analiza; nije nastavak potvrdnog I63 niti ocena H63/H56a.
- `positive`, `negative` i `equivalent` su samo deskriptivni dijagnostici zamrznutih pragova, ne odluke.
- Case30/j4 je unapred izuzet zbog eksplicitnog OPF neuspeha; ostalo je osam ćelija, sa raspodelom scenarija 2/3/3 i jednakim težinama mreža.
- Case30/j3 je potpuno neizvodljiv u sve četiri grane; case39/j4 je gotovo potpuno neizvodljiv. Njihove veze ostaju u estimandu i bitno utiču na tumačenje.
- θ=0,05 znači pet procentnih poena razlike očekivanog skora pobede, ne 5% ubrzanja niti 5% manjeg gubitka.
- `r_ij` je kontinualni OPF normalizator, ne sertifikovani optimum; negativni jazovi su dozvoljeni.
- Prikazati medijane normalizovanih jazova, a idealno i sirove MW jazove zahtevane §8 protokola, uz jasnu napomenu da je medijana uslovna na izvodljivost.
- Navesti bootstrap jedinicu, jednake težine mreža/scenarija, 20.000 ponavljanja, RNG 63 i tačne nivoe intervala.
- Ispraviti tvrdnju „nije dostižno“ u: kriterijum je izrazito konzervativan; pri stvarnoj stopi 5% prolazi približno 2,1% simulacionih serija, a konkretni I63 ga nije prošao.
- Ne tvrditi: podršku H63/H56a, ekvivalenciju, proširenje teze iz §8, opštu prenosivost, kauzalni/numerički mehanizam, novu metodu, superiornost po vremenu dostizanja ili brzini.
- Pre objave vezati i prijaviti SHA-256 za `power`, kompletan `run` i artefakt provere; bez toga tvrdnja o potpuno zamrznutom i proverenom ulazu nije dovoljno potkrepljena.