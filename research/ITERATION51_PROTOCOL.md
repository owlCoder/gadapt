# ITERATION51: reproduktivnost između procesa (D3x) na I49 uzorku (PREREGISTRACIJA)

**Status: ZAMRZNUTO pre koda i pre pokretanja.** Datum: 2026-10-23.

## Obavezni elementi (CLAUDE.md)
- **Pitanje:** da li neka od 9 biblioteka iz I49 (plus GAdapt kao kontrola) daje različit niz poziva sa istim semenom
  u dva sveža procesa? D3x je uveden u I50 posle I49.
- **Prior art i novina:** kao u H4 i I50. Nema nove tvrdnje; ovo samo dopunjava meru za ceo uzorak od 21 biblioteke.
- **Hipoteza:** nema je. Ovo je deskriptivno merenje sa jednim unapred zadatim ishodom.
- **Kontrole:** I50 validacija D3x (`hash_seeded` daje samo D3x, `time_seeded` daje D3 i D3x, čista referenca daje
  ništa) ponavlja se pre pokretanja i mora proći.
- **Budžet:** CPU. 30 ćelija po biblioteci, timeout 600 s po pokretanju.
- **GO.**

## Dizajn (zamrznuto)
- **Biblioteke i adapteri:** tačno I49 adapteri iz `research/iteration49_integrity_audit.py`, bez izmene: budžet 1000,
  iste konfiguracije i semena 6000–6004, sfera, Rastrigin i plato, N ∈ {2, 10}.
- **Okruženje:** novi venv iz `research/h4_requirements_lock.txt`, uz repozitorijum na putanji za GAdapt kontrolu.
- **Mera:** za svaku ćeliju dva sveža procesa (`python -I`), sa `PYTHONHASHSEED=1` i `=2`. D3x = različit heš niza
  poziva. Beleži se i D3 iz istih procesa (ponovljeno pokretanje u procesu 1).
- **BLAS/OpenMP:** 1 nit po procesu, kao u I50.
- **Ishod:** broj biblioteka (od 9) sa D3x u bar jednoj ćeliji. Lista se poredi sa I49 D3 (samo Nevergrad).
- **Razvrstavanje:** D3x je protivrečnost dokumentaciji ako biblioteka dokumentuje seme. Svih 9 imaju mehanizam
  semena naveden u I49 protokolu, tabela §2.
- **Prijava:** po I50 §7, samo nov i neprijavljen nalaz koji protivreči dokumentaciji, potvrđen na najnovijoj verziji.
- **Jedno pokretanje.** Izlaz `research/results/iteration51/d3x.json` i `ITERATION51_REPORT_SR.md`.
