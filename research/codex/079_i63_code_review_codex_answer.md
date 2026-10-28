**FIX FIRST.** Protokol odgovara zamrznutom `7c1f698`; pronađeni su blokatori u gate-u, provenijenciji i arhiviranju. Trinaest čistih testova prolazi. Nisam pokretao optimizaciju, gate niti menjao fajlove.

1. **BLOCKING: pogrešan redosled RNG toka.** [I63, red 56](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:56) definiše `0,+0,05,−0,05`, a §6 zahteva `+0,05,0,−0,05`. `wanted` to ne ispravlja: `series` prolazi kroz `TARGETS`. Zamena:

```python
TARGETS = (THETA, 0.0, -THETA)
```

2. **BLOCKING: I61 preflight dopušta samo jedan potvrdni scenario; nema zamrznutih scenarijskih podataka.** Mock potvrđuje prihvatanje jednog scenarija po mreži i nekonačnog `r`. Kasniji `make_problem` ponavlja OPF bez poređenja sa zamrznutim scenarijem/normalizatorom.

U I63 dodati sledeće; postojeći `stage_gate` zameniti prema tački 3:

```python
import hashlib

_make63 = i61.make_problem

def signature63(p):
    if not math.isfinite(p.opf_losses) or p.opf_losses <= 0:
        raise RuntimeError("invalid OPF normalizer")
    data = [p.base, p.resolution, p.opf_losses,
            p.lo, p.hi, p.step, p.bus_groups]
    raw = json.dumps(data, sort_keys=True,
                     default=lambda x: x.tolist()).encode()
    return hashlib.sha256(raw).hexdigest()

def preflight63():
    from iteration56_orpd import ScenarioError
    roster = dict(dev=[], test=[], excluded=[], scenario_hashes={})
    for n in NETWORKS:
        for j in range(5):
            try:
                p = _make63(n, j)
            except ScenarioError:
                roster["excluded"].append([n, j])
                continue
            roster["scenario_hashes"][f"{n}|{j}"] = signature63(p)
            roster["dev" if j < 2 else "test"].append([n, j])
    save("roster.json", roster)
    if any(j < 2 for _, j in roster["excluded"]) or any(
        sum(nn == n for nn, _ in roster["test"]) < 2
        for n in NETWORKS
    ):
        raise SystemExit("STOP: insufficient eligible scenarios")
    return roster

def make_problem63(n, j):
    p = _make63(n, j)
    expected = load("roster.json")["scenario_hashes"][f"{n}|{j}"]
    if signature63(p) != expected:
        raise RuntimeError("scenario or normalizer changed")
    return p

i61.make_problem = make_problem63
```

`RuntimeError` je nameran: `SystemExit` unutar Pool radnika može ugasiti radnika umesto vratiti neuspešan zapis.

3. **BLOCKING: fallback izlazi iz I63; gate nema proveru provenijencije pre/posle.** [I61, red 477](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:477) pokreće I61 skriptu: nestaju I63 scenariji, prošireni `CODE` i dopuna manifesta. Kasnije faze odbijaju takav gate. Biblioteku izabrati pre gate-a; ukloniti automatski fallback:

```python
def stage_gate(workers):
    if any(os.path.exists(path(f)) for f in (
        "roster.json.gz", "gate_current.json.gz", "gate.json.gz",
        "manifest_gate.json.gz"
    )):
        raise SystemExit("STOP: gate already attempted")
    before = build_manifest("gate-before")
    save("manifest_gate_before.json", before)
    preflight63()
    if not i61.gate_run("current", workers):
        raise SystemExit("STOP: frozen instrument gate failed")
    attempt = load("gate_current.json")
    if not (
        i61.same_provenance(before, attempt["manifest"])
        and i61.same_provenance(before, build_manifest("gate-after"))
    ):
        raise SystemExit("STOP: provenance changed during gate")
    i61.select_gate("current")
```

Dopuniti `CODE`:

```python
i61.CODE += ("iteration57_external.py",
             "test_iteration56_cht_study.py")
```

U `build_manifest`, pre `return m`, dodati vezivanje arhive i proverenu evidenciju zavisnosti:

```python
import subprocess
m["settings"]["i63"]["i56_archive_sha256"] = sha256(
    i56.path("test.json.gz"))
m["pip_freeze"] = subprocess.check_output(
    [sys.executable, "-m", "pip", "freeze"], text=True).split()
```

4. **BLOCKING: `verify_chain` ne proverava gate/roster identitet proizvođača.** Rekurzivni heševi izlaza rade, ali istorijski manifest može pripadati drugom rosteru iste provenijencije. Dopuna u I63:

```python
_chain63 = i61.verify_chain

def verify_chain63(stage, current):
    _chain63(stage, current)
    m = load(f"manifest_{stage}.json")
    gate = i61.verify_gate()
    if any(m.get(k) != gate[k]
           for k in ("gate_sha256", "roster_sha256")):
        raise SystemExit("STOP: producer used another gate/roster")
    if "frozen_sha256" in m and m["frozen_sha256"] != sha256(
        path("manifest_frozen.json.gz")
    ):
        raise SystemExit("STOP: producer used another freeze")

i61.verify_chain = verify_chain63
```

I63 `INPUTS` se inače pravilno prenosi kroz `before`; preuzeti `finish/publish` ne koriste pogrešan I61 graf.

5. **BLOCKING: tehnički STOP gubi pokušaje i dozvoljava ponovno odlučivanje.** `fxt/rehearsal` pozivaju `require_all_ok` pre objavljivanja; I61 odbacuje `generated` prvog pokušaja. Manifest postoji samo posle završetka, a promena `I63_OUT` zaobilazi identitet.

Zameniti `execute`:

```python
def execute(tasks, workers):
    from multiprocessing import Pool
    records = []
    purpose = tasks[0]["purpose"]
    with Pool(workers, maxtasksperchild=1) as pool:
        for k, r in enumerate(pool.imap(run63, tasks)):
            save(f"attempt_{purpose}_{k}_1.json", r)
            records.append(r)
    for k, r in enumerate(records):
        if not r.get("ok"):
            with Pool(1, maxtasksperchild=1) as pool:
                again = pool.apply(run63, (tasks[k],))
            save(f"attempt_{purpose}_{k}_2.json", again)
            again.update(rerun=True, first_attempt=r)
            records[k] = again
    return records
```

Fiksirati identitet zamenom definicije `OUT`:

```python
OUT = os.path.join(HERE, "results", "iteration63")
```

Zameniti završni CLI blok:

```python
if __name__ == "__main__":
    actions = dict(
        STAGES, power=lambda _: stage_power(),
        freeze=lambda _: stage_freeze(), analyse=lambda _: analyse())
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    if stage not in actions:
        raise SystemExit(__doc__)
    if os.path.exists(path("STOP.json.gz")):
        raise SystemExit("STOP: experiment is terminal")
    marker = path(f"started_{stage}")
    if os.path.exists(marker):
        raise SystemExit("stage already attempted")
    with open(path("RUNNING"), "x"):
        pass
    try:
        with open(marker, "x"):
            pass
        actions[stage](workers)
    except BaseException as exc:
        save("STOP.json", dict(stage=stage, reason=repr(exc)))
        raise
    else:
        os.unlink(path("RUNNING"))
```

Proveriti i svedoke neuspelih/prvih pokušaja. Dodati:

```python
def all_attempts(records):
    for r in records:
        if "first_attempt" in r:
            yield r["first_attempt"]
        yield r
```

U `stage_check` zameniti odgovarajuće dve linije:

```python
for r in all_attempts(load(f"{source}.json")["records"]):
    if r.get("best_feasible") is not None:
```

6. **BLOCKING: test pokreće stvarnu I63 optimizaciju pre gate-a.** [SmokeRun](/Users/danijel/Desktop/gadapt/research/test_iteration63_replication.py:134) koristi novi scenario i I63 seme. Ako komitno „15/15“ označava celu datoteku, već izvršeni smoke zahteva obelodanjivanje; zamena koda ne popravlja istoriju zamrzavanja.

Zameniti metod čistim testom omotača:

```python
def test_instrument_record_fields(self):
    from unittest.mock import patch
    t = m.task63("case30", 0, "FR", "AD-N", "rehearsal", 1)
    for calls, errors in ((m.B, 0), (m.B - 1, 0), (m.B, 1)):
        rec = dict(ok=True, calls=calls, errors=errors)
        with patch.object(m.i61, "run", return_value=rec):
            self.assertEqual(m.run63(t)["ok"],
                             calls == m.B and errors == 0)
```

7. **Odstupanje izveštavanja:** analiza objavljuje normalizovane, ne sirove MW jazove. U petlju `for c,a in ARMS` dodati:

```python
row[f"MW|{c}|{a}"] = [
    None if u[(c, a)]["best_feasible"] is None
    else u[(c, a)]["best_feasible"] - rr for u in us]
```

Ostale proverene komponente odgovaraju protokolu: `run` koristi trenutno `scenario(j)`; `run63/check_item/normalizer_item` pri `spawn` uvoze I63. `seed63` određuje optimizaciona semena, ne I61 `seed_of`. Kalibracija koristi uparene celobrojne zbirove; kriterijumi probe (i)–(iv), stroga dostižnost, ESS, Wilson, multinomijalni bootstrap, odvojene odluke, jednake težine, izostavljanje mreža i proširenje tvrdnje su ispravni. Projekcija sa sačuvanih četvorovektora na `d` dovoljna je za ove odluke.

Tehnički: roster ključevi `dev/test/excluded` odgovaraju; svi postojeći `CODE` fajlovi postoje, kao i arhiva sa 54 zadatka i I56 testovi. `archive_seeds` preširoko skenira rezultate i prećutkuje nečitljive arhive; ograničiti skeniranje na I56/I58–I61 i greške prijaviti. Plafoni 230 M PF/400 CPU-sati nemaju automatski nadzor; pri izvođenju moraju obuhvatiti i ponavljanja.