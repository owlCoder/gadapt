**FIX FIRST.** Diff i oba fajla pročitani direktno. Izolovane AST/mock provere potvrđuju nalaze ispod; fajlovi nisu menjani, gate i optimizacija nisu pokretani.

1. **TESTING ne curi u produkcione parametre.** Bez `I63_TESTING` dobijaju se B=12000, SIM=1000/2000/20000, pragovi 10/8/8/0.02 i 0.8/0.05, 27 konfiguracija, N_GRID=(80,160,240,320,480), semena 1..20, ESS≥N/2 i stroga dostižnost bez uniformnog fallback-a. Za stvarni izlazni direktorijum mora izostati i `I63_TEMP`. Vrednost `"0"` takođe aktivira TESTING jer se koristi `bool(string)`.

2. **Crash može naknadno postati terminalan.** CLI običan `RuntimeError` pravilno propušta bez STOP markera. Međutim, prekid posle snimanja rostera ostavlja fajl zbog kog sledeći `gate` podiže protokolarni STOP. Analogno važi za prekid između snimanja `manifest_frozen` i objavljivanja `freeze`. Dodatno, nasleđeni `i61.gate_run` pretvara svaki `Exception` u neuspešan gate, koji I63 zatim proglašava terminalnim.

   U [stage_gate](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:316) zameniti poziv:

   ```python
   if not i61._gate_run("current", workers):
   ```

   Postojeća poruka unutar tog `if` ostaje protokolarni STOP. U guard-u na redu 319 zameniti izuzetak:

   ```python
   raise SystemExit("EXISTS: gate artifacts exist; recovery required")
   ```

   U guard-u na redu 590:

   ```python
   raise SystemExit("EXISTS: frozen artifact exists; recovery required")
   ```

   Time nepotpuna faza zahteva kontrolisan oporavak, bez pogrešnog terminalnog markera.

   **Protokolarni neuspeh nezavisne provere trenutno izbegava STOP wrapper:** [red 650](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:650) koristi `SystemExit(1)`. Analiza kasnije blokira zaključak, ali eksperiment odmah ne postaje terminalan. Zameniti:

   ```python
   raise SystemExit("STOP: independent check failed (§7)")
   ```

3. **Neuspeli prvi pokušaji i ponavljanja jesu sačuvani pre normalnog ponovljenog-failure STOP-a u sva tri stadijuma.** `assert_paired` može ranije izazvati drugi STOP, ali su ti pokušaji već snimljeni.

   **Arhiva ipak nije trajna pri restartu:** nazivi se ponovo koriste i prepisuju. Svi prvi rezultati najpre ostaju u memoriji; uspešni pokušaji iz neuspelog `fxt/rehearsal` nisu objavljeni.

   U [execute](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:193), početni Pool blok zameniti:

   ```python
   import uuid
   invocation = uuid.uuid4().hex
   records = []
   with Pool(workers, maxtasksperchild=1) as pool:
       for k, r in enumerate(pool.imap(run63, tasks)):
           save(f"attempt_{purpose}_{invocation}_{k}_1.json", r)
           records.append(r)
   ```

   U petlji ponavljanja ukloniti postojeći `save(..._1...)`, a snimanje ponavljanja zameniti:

   ```python
   save(f"attempt_{purpose}_{invocation}_{k}_2.json", again)
   ```

   Ostatak funkcije ostaje isti.

4. **Gate nema fallback; provera provenijencije pre/posle postoji.** Završni manifest vezuje roster heš. Međutim, [signature63](/Users/danijel/Desktop/gadapt/research/iteration63_replication.py:105) ne uključuje stvarne scenarijske podatke `p.base`. Mock potvrđuje da promena podataka sabirnice ostavlja isti potpis. Zameniti `data`:

   ```python
   data = [p.base, p.resolution, p.opf_losses,
           p.lo, p.hi, p.step, p.bus_groups]
   ```

   Za proveru nepromenjenosti rostera tokom gate-a, odmah posle `preflight63()` dodati:

   ```python
   roster_sha = sha256(path("roster.json.gz"))
   ```

   Neposredno pre `select_gate`:

   ```python
   if sha256(path("roster.json.gz")) != roster_sha:
       raise SystemExit("STOP: roster changed during gate")
   ```

5. **`require_provenance("normalizers")` radi.** Njegov `INPUTS` je prazan, pa novi `verify_chain63` tada ne proverava gate kao običnog proizvođača. Manifest normalizatora dobija gate/roster identitet; naredne faze ga pravilno proveravaju, uključujući rekurzivne pretke.