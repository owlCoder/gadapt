# ITERATION47 — invarijantnost GAdapt-a na jedinice; AC ekonomski dispečing: izveštaj

**23. oktobar 2026.** Protokol: [ITERATION47_PROTOCOL.md](ITERATION47_PROTOCOL.md) (`6588731`). Kod `6dda81c`. Biblioteka
`cc2f357`. Izvršeno je **jedno** pokretanje oba dela: sintetički (384 pokretanja, 12 s) i dispečing (360 pokretanja,
1.080.000 stvarnih `runpf`, 558 s). Sirovi izlazi: [synthetic.json](results/iteration47/synthetic.json),
[dispatch.json](results/iteration47/dispatch.json).

Transparentno: pre pokretanja je urađen smoke test cevovoda na `case14` sa semenom 1 i budžetom 120 (nije protokolarno
seme ni budžet); videle su se samo vrednosti tog smoke testa. Nijedan parametar nije menjan posle toga.

## 1. Deo A (sintetika): A1 **NIJE PODRŽANO** (1/4); linearna mera je tačno invarijantna

Medijana najboljeg rezultata, optimum na 0,999 opsega, budžet 3000, 12 semena:

| Ćelija | R=1, log | R=1000, log | R=1, linear | R=1000, linear | Holm p (A1) |
|---|---|---|---|---|---|
| sfera, D=5 | 3,3e-9 | **6,8e-5** | 5,2e-9 | **5,2e-9** | **0,002** |
| elipsoid, D=5 | 4,2e-6 | 2,2e-4 | 3,5e-7 | 3,5e-7 | 0,68 |
| sfera, D=20 | 6,8e-2 | 7,6e-2 | 7,4e-2 | 7,2e-2 | 0,68 |
| elipsoid, D=20 | 3,0 | 3,8 | 3,1 | 3,1 | 0,19 |

- **A1:** linearna mera je značajno bolja samo na sferi u 5D. Elipsoid u 5D ima razliku medijana od oko 600 puta, ali
  varijansa među semenima je prevelika za Holm prag. U 20D nijedan krak ne konvergira sa 3000 evaluacija, pa efekat
  preciznosti tu nije merljiv.
- **A2:** za `linear` su rezultati pri R=1 i R=1000 **identični** u 5D (isti medijani do svih cifara). To je
  invarijantnost po konstrukciji, potvrđena. Za `log_relative` je zavisnost od jedinica značajna samo na sferi u 5D
  (Holm p = 0,008).
- Optimum u sredini opsega: obe mere su ekvivalentne, kao što je i predviđeno.

## 2. Deo B (AC ekonomski dispečing, MATPOWER): B1 **OPOVRGNUTO** (0/5)

| Slučaj | Promenljive | med score log-MW | med score lin-MW | Holm p (B1) | rel. jaz GAdapt (log-MW) | rel. jaz CMA-ES | rel. jaz DE |
|---|---|---|---|---|---|---|---|
| case14 | 4 | 12476,7 | 12494,4 | 0,80 | 6,0e-3 | **4,8e-7** | 2,8e-4 |
| case30 | 5 | 1156,1 | 1131,1 | 1,00 | 1,4e-1 | **1,0e-5** | 4,1e-3 |
| case39 | 9 | 44195,7 | 43310,8 | 0,31 | 4,6e-2 | **3,8e-7** | 1,5e-2 |
| case57 | 6 | 42811,1 | 42760,5 | 0,26 | 1,3e-3 | **2,7e-7** | 5,1e-4 |
| case118 | 53 | 146847,5 | 146318,4 | 1,00 | 5,7e-2 | **1,4e-2** | 6,3e-1 |

Relativni jaz se meri u odnosu na najbolji score svih metoda na tom slučaju.

- **B1:** ispravka ne donosi značajno poboljšanje ni na jednom slučaju. Medijana je bolja na 4/5, ali razlike su
  male u odnosu na rasipanje.
- **B2:** jedina značajna zavisnost od jedinica je `log` MW vs p.u. na case39 (Holm p = 0,024). Sa `linear` nijedna
  razlika nije značajna.
- **Izvodljivost:** na case14–case57 **nijedan metod, pa ni CMA-ES**, nije našao izvodljivo rešenje. Sa fiksnim
  naponima iz slučaja i bez Q-limita u NR-u, Q i/ili V granice su prekršene nezavisno od PG. Problem je zato
  penalizovan dispečing, a poređenje važi za penalizovani score. Na case118: CMA-ES 11/12 semena izvodljivo, GAdapt
  1–3/12, DE 0/12.

## 3. Glavni nalaz (opisno, ali veoma veliki efekat)

Pri istom budžetu (3000 stvarnih AC proračuna) **CMA-ES je 3–5 redova veličine bliži najboljem rešenju od GAdapt-a**
na 4 od 5 stvarnih sistema. Na case118 (53 promenljive) razlika je oko 4 puta. Zajedno sa I5 (IEEE14 naponi: CMA-ES
12/12) i I43–I46 (binarno: (1+1)-EA i udžbenički GA bolji): **GAdapt-ova slabost nije u jedinicama ni u pojedinačnim
opcijama, već u brzini konvergencije (intenzifikaciji)**. Invarijantna mera je ispravna, ali tu slabost ne rešava.

## 4. Zaključak i status
| Tvrdnja | Status |
|---|---|
| Podrazumevana kolonska raznovrsnost zavisi od jedinica | **Potvrđeno**, ali značajno samo u delu ćelija (sfera 5D, case39) |
| `linear` je invarijantna | **Potvrđeno** (identični rezultati) |
| `linear` praktično poboljšava GAdapt na dispečingu | **Opovrgnuto** (0/5) |
| GAdapt je konkurentan CMA-ES-u na kontinualnim infra problemima | **Ne**: 3–5 redova veličine lošiji pri istom budžetu |

Opt-in `columnar_diversity_metric="linear"` ostaje u biblioteci kao ispravka invarijantnosti (bez štete, podrazumevano
ponašanje nepromenjeno), ali **ne** kao dokazano poboljšanje performansi.
