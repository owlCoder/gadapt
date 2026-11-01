# I65 — instrumentacija i testovi (research-only; UNFROZEN)

**Status 2026-11-01:** `novelty not established`, `FREEZE=NO`,
`COCO f21/f24 = NOT_RUN`, `GAdapt/CMA integration = NOT_TESTED`.

Devet Python fajlova u ovom direktorijumu su **sandbox-only**, bez promena
u `gadapt/` ili GAdapt podrazumevanim parametrima:

- `audited_budget.py`: sekvencijalni brojač fizičkih poziva i nezavisni witness.
- `stagnation_checked.py`: provereno pravilo 20 završenih generacija.
- `e_common_snapshot.py`, `stagnation_reference.py`: lokalni poredbni izvori.
- `make_gate_fixtures.py` i `test_*.py`: testne fixtures, regresioni i DE smoke test.

## Lokalno pokretanje

Iz korena repozitorijuma, uz instalirane NumPy/SciPy/pytest:

```bash
python -m pytest -q -rx research/i65
python research/i65/make_gate_fixtures.py
```

Pri pripremi arhive: **54 passed, 3 xfailed**; log:
[../I65_GATE_TEST_LOG.txt](../I65_GATE_TEST_LOG.txt).
Tri očekivana neuspeha odnose se na prethodne reference, ne na COCO ishod.
I65 tests `!=` GAdapt/CMA/COCO integration; nijedan held-out run nije izvršen.

- [DRAFT protokol](../ITERATION65_DRAFT_PROTOCOL_SR.md)
- [Prior-art](../ITERATION65_PRIOR_ART_AUDIT_DRAFT_SR.md)
- [Gate izveštaj](../ITERATION65_INSTRUMENTATION_GATE_REPORT_SR.md)
- [Sirove **testne** fixtures](../I65_INSTRUMENTATION_FIXTURES.json)
- [Provenijencija GitHub arhive](../ITERATION65_GITHUB_PROVENANCE_ADDENDUM_SR.md)
