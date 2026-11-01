# ITERATION54 — oracle geometrija: da li učenje korelacija/skala objašnjava zaostatak GAdapt-a na AC dispečingu

**Status: NACRT — NIJE ZAMRZNUT, POVUČEN 2026-10-23 posle Codex recenzije 007 (dve blokirajuće greške: okvir za y poništava sopstvene vrednosti jer GAdapt normalizuje opsegom; odsecanje meša geometriju sa granicom). Nijedno merenje nije pokrenuto. Redizajn tek uz zasebnu odluku.** Datum: 2026-10-23. Dijagnostički (uzročni) eksperiment, bez tvrdnje o novini.

## 1. Polazište

- I53 (`e9d0024`): oracle korak mutacije zatvara najviše 29% jaza G0–CMA na dispečingu (H53 opovrgnuto u uskom smislu);
  sintetički obrazac (sfera 61%, dijagonalni elipsoid 23%, rotirani 9%) liči na elipsoide. Kandidat-uzrok (nije utvrđen):
  GAdapt radi po koordinatama i ne uči korelacije ni relativne skale promenljivih.
- Uzročni test kandidata: dati GAdapt-u ispravnu geometriju bez ikakve druge promene algoritma.

## 2. Intervencija

- Geometrija iz reference: po slučaju se ponovo pokreće najbolje referentno CMA-ES pokretanje iz I53
  (`research/results/iteration53/reference.json`, isto seme, isti budžet 60.000, deterministički) i čuva se njegova
  završna matrica kovarijanse C (u normalizovanim koordinatama u = (x − lo)/(hi − lo)). Koristi se samo OBLIK:
  C = B·diag(d²)·Bᵀ, d normalizovano na max(d) = 1 (veličina koraka CMA-ES se odbacuje).
- **Transformacija bez informacije o lokaciji:** u = 0,5·1 + A·y, A = B·diag(d). Centar je sredina opsega, ne optimum.
  Opseg za y: najmanji kvadar koji sadrži sliku celog kvadra [0, 1]^N pod A⁻¹ (y_i ∈ [−h_i, h_i],
  h_i = 0,5·Σ_j |(A⁻¹)_ij|). Tačke u van [0, 1]^N se odsecaju na granicu (clip) pre evaluacije; to se broji i prijavljuje.
- Grane:
  * **G0:** podrazumevani GAdapt u originalnim koordinatama (kao I53 G0).
  * **W:** podrazumevani GAdapt nad y (izbeljene koordinate), isti cost (preko u → x), sve opcije podrazumevane.
  * **WD:** kontrola — isto kao W, ali A = diag(d_i^diag) gde je d^diag koren dijagonale C (samo skale, bez rotacije).
  * **CMA:** kao I53 (originalne koordinate).
- Semena 5500–5511 (nova). Budžet 3000 `runpf`, `probe_cost_function=False`, slučajevi kao I53.

## 3. Hipoteza i odluka

Mera kao I53: C(X) = (m_G0 − m_X)/(m_G0 − m_CMA), m = medijana log10(max(score − score_ref, 1e-12)), score_ref iz I53
reference (zamrznuta). Odlučujući slučajevi: m_G0 − m_CMA ≥ 0,5.

**H54:** ispravna geometrija zatvara veći deo jaza.
- **PODRŽANO:** C(W) ≥ 0,5 i W bolji od G0 (upareni jednostrani Wilcoxon, Holm preko 5 slučajeva, α = 0,05) na ≥ 3/4
  odlučujuća slučaja.
- **OPOVRGNUTO:** C(W) < 0,2 na ≥ 3/4 odlučujuća slučaja → ni oracle geometrija ne objašnjava jaz.
- Inače **DELIMIČNO**.
- Sekundarno (atribucija): W bolji od WD (rotacija povrh skala), WD bolji od G0 (samo skale); Holm preko 5 po testu.
- Opisno: izvodljivost po grani (posebno case118), broj odsecanja.

## 4. Pretnje validnosti

- C potiče od CMA-ES koji je video optimum: geometrija je lokalna informacija oko optimuma (oracle), ne metoda.
  Lokacija se ne prenosi (centar = sredina opsega), ali uski oblik C usmerava pretragu ka pravcima doline.
- Odsecanje na granicu menja pejzaž kod aktivnih ograničenja promenljivih; prijavljuje se.
- Pragovi 0,5 i 0,2 niži su nego u I53 (0,9 / 0,5), jer je pitanje da li geometrija objašnjava *veći deo*, a I53 je
  već pokazao da korak objašnjava najviše 29%. Fiksirani su pre merenja.
- Budžet: ponavljanje 5 referentnih pokretanja (300.000 `runpf`) + 4 × 5 × 12 × 3000 = 720.000 `runpf`.

## 5. Arhiva

Kod `research/iteration54_oracle_geometry.py`, testovi `research/test_iteration54_oracle_geometry.py`,
izlazi `research/results/iteration54/` (geometrija po slučaju, pokretanja, analiza, verzije, SHA-256).
