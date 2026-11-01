# H8: zaključak o poređenju optimizatora koji važi za svaki optimum u intervalu [L,U] — prior-art gate (Codex 082, 2026-10-28)

**Zaključak: NIJE USTANOVLJENO; NO-GO za dvonedeljni gate kao samostalni teorijski doprinos.**
- Tražena garancija se dokazuje odmah: E[X_k(r)] = Σ_{t<B} [1 − F_kt(r+ε)], DKW–Massart (10.1214/aop/1176990746) + unija preko algoritama i vremena daje
  P{∀r∈[L,U]: |Δ̂(r) − Δ(r)| ≤ w} ≥ 1 − α, w = B(η_A + η_C), η_k = sqrt(log(4B/α)/(2 n_k)). Pravilo sup_r{Δ̂(r)+w} < 0 potvrđuje prednost za svaki dopušteni optimum.
  Ako je pokriće reference 1−β, ukupno ≥ 1−α−β. Konzervativno; uži bootstrap pojas traži kalibraciju supremuma.
- Prior art: Hansen i sar. 2022 (10.1109/TEVC.2022.3210897), López-Ibáñez i sar. 2024 (10.1109/TEVC.2024.3462758), Hall–Wellner 1980 (10.1093/biomet/67.1.133),
  Nair 1984 (10.1080/00401706.1984.10487964), Teng–Jiang–Chen 2023 (10.1002/sim.9618), maksimalno izabrane log-rank statistike (10.1016/S0167-9473(02)00225-6),
  Zhao–Small–Bhattacharya 2019 (10.1111/rssb.12327), Masten–Poirier–Zhang 2024 (10.1080/07350015.2023.2183212), Bartz-Beielstein 2020 (arXiv:2007.03488).
  Nije nađen identičan rad, ali to ne dokazuje prvenstvo.
- Više od alatne napomene tražilo bi nov rezultat o oštrini, snazi ili optimalnoj širini pojasa; toga nema.
- Korist za tezu: korekcija benchmark protokola (u I63 uporedo: r_ij je normalizator, ne optimum). Ukupno odbačeno: 16.
- Preostalo iz Codex 081 (nije proverano): #3 dinamička granica praćenja uz zakašnjenje signala raznovrsnosti (visok rizik, uslovni GO za gate); #4 vodovod,
  izvršive diskretne komande (domenski gate; NO-GO za tvrdnju da primena GAdapt-a sama po sebi jeste nova metoda). #5 deljenje prefiksa: NO-GO (Santos–Santos 2000).
