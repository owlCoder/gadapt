# Iteracija 10 — kontrolisan slack/reference scenario RTE1888

**Pre-registracija:** 21.10.2026, pre prvog AC izvršavanja ove iteracije. Polazna činjenica iteracije 9: originalna MATPOWER 2019 slack BUS 1320, pandapower ext_grid BUS 1268. Sve promene samo u lokalnoj testnoj kopiji modela; upstream i GAdapt algoritam ne dirati.

## Primarno pitanje

Da li promena referentne/slack sabirnice na originalni BUS 1320 menja konvergenciju, napone i izvorna MVA ograničenja? Ovo NIJE rekonstrukcija izvorno identičnog AC-OPF modela, operativna preporuka, niti algoritamsko poređenje.

## Unapred fiksirana dva fizička AC poziva

1. Proveriti originalne izvore iteracije 9: MATPOWER jedina referentna sabirnica 1320, originalni aktivni generator red 298 na BUS1320 sa PG=0, PMIN=0, PMAX=1000, QMIN=-1, QMAX=1, VG=1.0588; na BUS1268 dva jednaka online generatora po PG=44.5, QMIN=-9, QMAX=27, VG=1.027. Ako nije tako, ne menjati AC model.
2. Prvi AC: SourceRatedRTEGrid(load_factor=1.0) nepromenjeni pandapower primer, prvih osam generatorskih napona na referentnim vrednostima, stvarni runpp: DC inicijalizacija, NR, 40 iteracija, tol 1e-8 MVA, enforce_q_lims=True, bez numba. RATE_A=0 znači bez granice; pozitivne originalne RATE_A MVA granice mere se na oba kraja grane.
3. Drugi AC: nakon prvog poziva, jedini ext_grid preseliti na pandapower bus čije je originalno ime BUS1320; postaviti VG=1.0588, Pmin=0, Pmax=1000, Qmin=-1, Qmax=1 prema izvornom redu 298. Na BUS1268 dodati jedan stvarni pandapower.gen sa PG=44.5, VG=1.027, PMIN=44, PMAX=45, QMIN=-9, QMAX=27 prema izvornom redu 1. Postojeći aktivan sgen na BUS1268 mora imati PG=44.5, kao drugi originalni generator; ako nema tog sgen uslova, prekinuti pre drugog AC. Sve druge grane, loads, šantove, ostale gen setpointove ostaviti iste.
4. Tačno 2 fizička AC poziva ako su preduslovi ispunjeni. Brojati svakog runpp pokušaja. Sačuvati za oba: konvergenciju, sabirničke i source-rated MVA povrede, gubitke samo uz konvergenciju, slobodni slack P/Q i eksplicitne min/max povrede P/Q na ext_grid prema izvoru, Q zasićenja i Q prekoračenja svih gen. Ako proračun ne konvergira, odgovarajući brojčani rezultati moraju biti JSON null.
5. Sirovi CSV i JSON u main, testovi, GitHub Actions, srpski izveštaj. Bez optimizacije, statističke superiornosti, novog algoritma ili zaključka matematičke neizvodljivosti.
6. Pinovano Python 3.12, pandapower==2.14.11, scipy==1.13.1, pandas==2.2.3, PYTHONHASHSEED=0, jednonitni BLAS/OMP/MKL, source MATPOWER commit 80b6e16... sa CC BY 4.0.

## Ograničenja

Preostala odstupanja 75 trafo impedansi, nepotpuna reaktivna semantika jednog sgen u BUS1268 i druge promene konverzije nisu razrešene. Dva AC PF scenarija **nisu** izvorno identičan MATPOWER AC-OPF niti dokaz originalne algoritamske novine. Originalni podaci nisu za operativno upravljanje ili planiranje francuske ili evropske mreže.
