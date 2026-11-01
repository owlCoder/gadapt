# I52 post hoc analiza osetljivosti prenosa (PLAN, zamrznut pre računanja)

**Status:** ZAMRZNUTO 2026-10-24, pre ijednog izračunavanja. Post hoc, opisno; **nije test hipoteze**.
Originalni rezultat H52 (19/21, protokol `32bac01`) ostaje nepromenjen i primaran.
Izvor plana: Codex 013 (`research/codex/013_transfer_sensitivity_codex_answer.md`); povod: recenzije 011/012
(„matched-exposure and incomplete-library sensitivity analyses remain absent“).
**Otkrivanje:** autor zna ishod H52 i neslaganja (Nevergrad, SciPy DE) pre ovog plana. Nema novih pokretanja,
nema rekonstrukcije nedostajućih podataka. Objavljuju se SVI izlazi navedeni ovde.

## Definicije
- K = {C3, C4, C5, R1, R2, R3, D2, D3, D3x}. C1 i C2 isključeni (kao u H52). Ćelija je pozitivna ako je bar jedna
  dostupna zastavica iz K > 0. Nedostupna provera nije potvrđeno negativna (ne beleži se kao nalaz).
- Uspešna ćelija: `error` je null. GAdapt se ne broji.
- Sintetički, arhiva A (originalna, kao H52): uzorak 1 = I49 `cells` (zastavice bez D3x) spojeno sa I51 `cells`
  (samo D3x) po (library, function, d, seed); zadržavaju se ćelije uspešne u oba. Uzorak 2 = I50 `cells_<lib>.json`.
- Sintetički, arhiva B (I55): važeće ćelije (`error` null i `manipulation_ok` true); D3 = polje `D3`, D3x =
  `D3x_diff`. Arhive se ne spajaju.
- Dispečing: I52 `cells_<lib>.json`, uspešne ćelije; D_l = bar jedna pozitivna ćelija.
- Za biblioteku l: n_l uspešne sintetičke ćelije, k_l pozitivne sintetičke ćelije, S_l = 1(k_l > 0),
  m_l uspešne dispečing ćelije (od 15).

## Kontrola pre analiza
Iz arhive A i I52 izračunati broj poklapanja Σ 1(S_l = D_l). Mora biti **19/21** sa neslaganjima Nevergrad i
SciPy DE. Ako nije: STOP, prijaviti razliku, ne podešavati definicije.

## Analize (za arhivu A, pa posebno za arhivu B)
1. **Izjednačena izloženost:** podskup od m_l sintetičkih ćelija, uniformno bez vraćanja, nezavisno po biblioteci.
   Tačno (analitički, bez semena): q_l = C(n_l − k_l, m_l) / C(n_l, m_l) = P(podskup bez nalaza).
   P(poklapanje_l) = q_l ako D_l = 0, inače 1 − q_l. Konvolucija 21 Bernulijeve raspodele → raspodela A = 0..21.
   Prijaviti: celu raspodelu, nosač, očekivanje, P(A ≥ 17) (opisno).
2. **Samo potpune biblioteke:** S_l iz cele arhive; poklapanje među bibliotekama sa m_l = 15, sa matricom
   konfuzije i ponavljanjem pozitivnih (imenilac Σ S_l među potpunim).
3. **Granice za nedostajuće ćelije:** D_l^- = D_l, D_l^+ = D_l ∨ (m_l < 15). Donja/gornja granica poklapanja =
   Σ_l min/max_{d ∈ {D_l^-, D_l^+}} 1(S_l = d), imenilac 21; plus scenariji „sve nedostajuće negativne“ (= opaženo)
   i „sve nedostajuće pozitivne“.

## Pravilo za tekst rada (unapred)
Ako nosač raspodele iz (1) sadrži vrednosti < 17, ili je donja granica iz (3) < 17 (u bilo kojoj arhivi), rad kaže:
„≥ 80% agreement is not uniformly robust to this sensitivity analysis“. U svakom slučaju zadržava se formulacija
„poklapanje detekcije“ i odvojeno ponavljanje pozitivnih; bez tvrdnji o značajnosti. Podskup ne dokazuje
zamenljivost ćelija niti otklanja informativne greške (navesti).

## Izlazi
`research/iteration52_sensitivity.py` → `research/results/iteration52/sensitivity.json` (uz SHA-256 ulaznih fajlova).
