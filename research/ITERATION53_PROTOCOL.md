# ITERATION53 — oracle test uzroka: da li kontrola koraka mutacije objašnjava zaostatak GAdapt-a na AC dispečingu

**Status: ZAMRZNUTO pre ikakvog merenja** (recenzija Codex 002 uneta). Datum: 2026-10-23. Bez tvrdnje o novini: ovo je dijagnostički (uzročni) eksperiment.

## 1. Polazište

- I47: na AC ekonomskom dispečingu (5 MATPOWER slučajeva, 3000 evaluacija) CMA-ES je 3–5 redova veličine bolji od GAdapt-a.
  Ispravka invarijantnosti (`linear`) ne pomaže (B1 0/5).
- Mehanizam (kod): Gausova mutacija GAdapt-a ima σ = σ_min + (σ_max − σ_min)·ρ (relativno opsegu promenljive),
  gde je ρ kolonska raznovrsnost (rasipanje populacije po promenljivoj u odnosu na generaciju 0), σ_min = 1e-3.
  To je procena rasipanja populacije, kao u Gausovim EDA. Za EDA je poznato da takva procena ne prati udaljenost
  od optimuma (Shapiro 2005, 10.1162/1063656053583414; Bosman i Thierens 2007, 10.1145/1276958.1277067).
- Eksplorativno (kvadratna f, 10D, 6 semena, `research/results/iteration53_exploratory/probe.json`): u podrazumevanom
  GAdapt-u nove tačke su u poslednjoj četvrtini 5–1500× dalje od x* nego najbolje rešenje (donja granica σ dominira);
  sa opt-in decay korak se urušava (odnos ≈ 1,01) i gap je gori. Translacija f* = 0 / 1e4 bez primetnog efekta.

## 2. Pitanje i hipoteza

**Pitanje:** da li je kontrola koraka (σ koji ne prati udaljenost od optimuma) glavni uzrok zaostatka GAdapt-a za CMA-ES
na stvarnom AC dispečingu, ili je uzrok drugde (kondicioniranje/korelacije, selekcija, mutacija koja nije centrirana na
najboljem rešenju)?

**Dodatni mehanizam (Codex, nezavisna analiza `research/codex/001_*`, provereno u kodu):** podrazumevano
`decision_variable_mutation="variable_columnar_diversity,random"` za SVAKU mutiranu koordinatu nasumično (50/50,
`ComposedDecisionVariableMutator`: `random.shuffle`, pa prvi) bira Gausov pomak ili uniformni reset na ceo opseg.
Kandidat sa k mutiranih koordinata dobija samo Gausove pomake sa verovatnoćom 2^-k. Zato je dizajn faktorski 2×2.

**Faktori (sve ostale opcije podrazumevane, kao I47 `gadapt:log_relative:mw`):**
- Korak: podrazumevani (σ iz kolonske raznovrsnosti) ili **oracle**: columnar-diversity Gausov mutator dobija
  σ_rel = clip(κ · r / √N, 1e-12, 0.6), gde je r normalizovana euklidska udaljenost (koordinate podeljene opsegom)
  najboljeg do sada evaluiranog rešenja od referentne tačke x_ref, a N broj promenljivih; κ = 1.
- Reset: sa `random` komponentom (podrazumevano) ili bez nje (`decision_variable_mutation="variable_columnar_diversity"`).

Grane: **G0** (podrazumevano), **GN** (bez reseta), **OR1** (oracle, sa resetom), **ORN** (oracle, bez reseta),
**ORN01** (oracle κ = 0,1, bez reseta; sekundarno, ne ulazi u odluku), **CMA**. Zakrpa važi samo u procesu oracle
grane i vraća se posle pokretanja; biblioteka se ne menja.

**H53 (primarna):** mutacioni operator (korak + reset) objašnjava najveći deo jaza između GAdapt-a i CMA-ES.

Mera po slučaju: C(X) = (m_G0 − m_X) / (m_G0 − m_CMA), gde je m medijana log10(max(score − best_known, 1e-12)) preko
semena, a best_known = score_ref (referenca fiksirana pre svih grana, §3; ne zavisi od grana). Pokretanja bolja od
reference dobijaju gap 1e-12 i prijavljuju se (broj po grani).
- **PODRŽANO:** C(ORN) ≥ 0,9 i ORN bolji od G0 (upareni jednostrani Wilcoxon, Holm preko 5 slučajeva, α = 0,05)
  na ≥ 4/5 slučajeva.
- **OPOVRGNUTO:** C(ORN) < 0,5 na ≥ 3/5 slučajeva → OVA intervencija (izotropni korak skaliran udaljenošću najboljeg,
  κ = 1, bez reseta) nije dovoljna da zatvori jaz. To NE isključuje mutaciju kao uzrok (mutiraju se potomci, ne najbolje
  rešenje; κ fiksno; kondicioniranje; broj mutiranih koordinata); tumači se samo kao uska negacija (Codex review 002).
- Inače: **DELIMIČNO**.
- Slučaj u kom m_G0 − m_CMA < 0,5 ne ulazi u odluku (prijavljuje se); pragovi „4/5“ i „3/5“ se tada ne menjaju.

**Sekundarne (atribucija, preregistrovane, Holm preko 5 slučajeva po testu):**
- S1 (reset): GN bolji od G0. S2 (korak bez reseta): ORN bolji od GN. S3 (korak uz reset): OR1 bolji od G0.
- Interakcija se prijavljuje opisno: (m_G0 − m_GN) + (m_G0 − m_OR1) naspram (m_G0 − m_ORN).

## 2A. Deo A — sintetički mehanizam (predlog Codex-a, `research/codex/001_*`, skraćen)

Kvadratne funkcije sa poznatim optimumom, N = 10, x ∈ [−5, 5]^N, x* ~ U[−3, 3]^N po semenu, f* = 0:
sfera; elipsoid f = Σ 10^(6(i−1)/(N−1)) z_i²; rotirani elipsoid (ista f na z = Q(x − x*), Q slučajna ortogonalna po semenu).
Grane: korak {**D** podrazumevani, **F** bez donje granice (σ_min = 1e-12, bez decay), **O** oracle κ = 1} ×
reset {**R** sa, **N** bez} = 6 GAdapt grana + **CMA** (I47 konfiguracija, normalizovano [0, 1]). 12 semena (5400–5411),
3000 evaluacija, gap = f(najbolje).
- **A1:** ON (oracle, bez reseta) bolji od DR (podrazumevano) na sva 3 problema (Holm preko 3, α = 0,05).
- **A2 (orijentacija/korelacije):** C(ON) ≥ 0,9 na dijagonalnom elipsoidu, a C(ON) < 0,5 na rotiranom elipsoidu
  (C kao u §2, prema CMA, imenilac ≥ 0,5; inače A2 neodlučeno). Sfera se prijavljuje opisno.
- Ostale razlike (F naspram D, R naspram N, elipsoid naspram rotiranog) prijavljuju se opisno sa Holm p-vrednostima.
- Izostavljeno (zahteva izmenu biblioteke): Codexov faktor „mutacija kopija najboljeg naspram potomaka“.

## 3. Podaci, metode, budžet (deo B — dispečing)

- Slučajevi: case14, case30, case39, case57, case118; problem i kazne identični I47 (`research/iteration47_invariance.py`,
  klasa `Dispatch`), budžet 3000 stvarnih `runpf` evaluacija po pokretanju, validacioni pozivi isključeni
  (`probe_cost_function=False`).
- Grane: G0, GN, OR1, ORN, ORN01, CMA (vidi §2); CMA u konfiguraciji iz I47.
- Semena: 5300–5311 (12, nova, nekorišćena u I47).
- Referenca x_ref, score_ref (fiksira se PRE grana, arhivira se): po slučaju CMA-ES iz I47 konfiguracije sa budžetom
  60.000 evaluacija, semena 7001–7003; uzima se najbolja tačka (900.000 `runpf`). Referenca se arhivira i zamrzava
  pre pokretanja grana; best_known = score_ref (vidi §2).
- Računanje: lokalno, Pool, jedno izvršavanje.

## 4. Pretnje validnosti

- Oracle zna x_ref; to je namerno (dijagnostička intervencija), nije metoda i NIJE gornja granica mogućeg dobitka
  od kontrole koraka (mutiraju se potomci, κ fiksno, izotropno).
- Izotropni oracle ne uči korelacije; ako CMA-ES dobija zbog kovarijanse, OR neće zatvoriti jaz — to je informativan
  ishod, ne neuspeh eksperimenta.
- κ nije podešavan; dve vrednosti su fiksirane unapred.
- Izvodljivost (Codex, provereno u I47 izveštaju): na case14–case57 nijedan metod (ni CMA-ES) nije našao izvodljivo
  rešenje; poređenje važi za **penalizovani score**, ne za sertifikovane OPF optimume. Jaz G0–CMA iz I47 je 3–5 redova
  veličine na 4 slučaja, a na case118 (53 promenljive) samo ~4×. Zaključak o dispečingu se tako i formuliše; izvodljivost
  se prijavljuje po grani.
- Ukupno grane 6 × 5 × 12 = 360 pokretanja × 3000 = 1.080.000 `runpf` + referenca 900.000 = 1.980.000 `runpf`.
  Deo A: 7 × 3 × 12 = 252 pokretanja × 3000 kvadratnih evaluacija.
- Po pokretanju se arhiviraju: best score, izvodljivost, najbolji izvodljivi trošak, najbolja tačka, PF neuspesi.

## 5. Arhiva

Kod `research/iteration53_oracle_step.py`, testovi `research/test_iteration53_oracle_step.py`,
sirovi izlaz `research/results/iteration53/`, verzije paketa i SHA-256 izvora.
