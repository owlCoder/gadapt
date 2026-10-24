**Verdict: revise before acceptance.** The numerical core is sound, but several statements overreach the frozen descriptive protocol. No files were changed.

1. **Independent numerical audit.** My read-only, single-process `python -B` reader imported no study modules and reproduced all six archived bootstrap intervals exactly; estimates agree within floating-point rounding. Confirmed: 2,100 records, 300 complete units, 30 instances, 3,000 calls each, 6.3 million total; zero recorded failures, reruns or exclusions; all references and manifest hashes match. Pooled percentages, feasibility counts and the 9/12 conditional-median comparison check out.

   Concrete corrections in [the report](/Users/danijel/Desktop/gadapt/research/ITERATION57_REPORT_SR.md:43):

   - Random, case14/R33: **0.9916 → 0.992**, not 0.993.
   - The merged case118 row has **120 runs per configuration**, not 40.
   - Scenario-2/R17 CMAwM medians are **9.028 SP / 9.027 FR**; specify which accompanies GAdapt’s 9.204/9.323.
   - Block-level GAdapt/CMAwM mean-T ratios span **2.4–3.1**, not uniformly 2.5–3.
   - Execution times **17:06–18:11** and actual use of **eight workers** cannot be established from these artifacts; cite an execution log or remove them.

2. **Correct the concentration and attainment claims.**

   > “Ceo kontrast T potiče sa case14 (R = 17, 33).”

   Replace with: **“Najveći doprinos kontrastima T dolazi iz case14/R17 i R33; nenulti doprinosi postoje i u case14/R9 i case57/R17/R33.”**

   > “U ostalih 7 blokova … neinformativno”

   Replace with: **“Tačno četiri bloka imaju T=1 za sva pokretanja svih konfiguracija; u ostalima je dostizanje često retko.”**

   > “Na jedinoj mreži gde su ciljevi dostižni … (case14)”

   False: case57 has two attainments—CMAwM/FR/R17 at call **2593**, GAdapt/FR/R33 at **1714**. Replace with: **“Na case14/R17 i R33, gde je dostizanje često, CMAwM ima niži opaženi srednji T.”**

3. **Keep interpretation descriptive.**

   > “DE se od GAdapt-a ne razlikuje jasno”

   Replace with: **“Procene DE−GAdapt su +0,012/SP i +0,008/FR; oba opisna intervala obuhvataju nulu. Ekvivalencija nije ispitana.”**

   > “Izbor tehnike … ne menja sliku”

   Replace with: **“Znaci šest agregatnih procena isti su pod SP i FR; odsustvo interakcije nije utvrđeno.”**

   > “činjenica da je CMAwM ipak brži … zato je konzervativna”

   Replace with: **“Reference potiču samo iz GAdapt-a; smer i veličina mogućeg uticaja na poređenje nisu utvrđeni.”**

   Also remove the untested mechanism “učenje korelacija.” The assertion that I56’s “efekti CHT … su mali” needs qualification: its descriptive EC contrasts on case14 are substantial.

4. **DE explanation: population sizes correct, generation accounting wrong.** I checked installed SciPy **1.18.1**, the driver and [versioned SciPy source](https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_differentialevolution.py). Here all bounds vary, so population size is 15d. Initialization consumes one population’s evaluations before evolution. Replace “~7 odnosno ~2,6 generacija” with:

   **“case57: 405 inicijalnih evaluacija + 6 punih evolucionih generacija + 165 kandidata sedme; case118: 1155 inicijalnih evaluacija + 1 puna generacija + 690 kandidata druge.”**

   Cheap synthetic calls using the driver’s settings confirmed these counts. The wrapper blocks evaluation 3001; polishing is disabled.

5. **Case57 feasibility is robust within this sample.** GAdapt achieves **10/10 in every scenario × R × CHT cell**, hence 60/60 per CHT. CMAwM ranges **1–10/10** per cell; FR/R17 also achieves 10/10 in both scenarios. Replace “uvek”/“najpouzdaniji” with those observed counts.

   None of GAdapt’s case57 runs becomes feasible within its initial 32 evaluations; first feasibility occurs at **183–910**. Initialization is therefore not directly supplying feasible solutions. Shared snapping, grid-index checks and initial genotypes reveal no decoding defect. Nevertheless, GAdapt’s population/operator distribution and CMAwM’s midpoint mean with sigma=(R−1)/3 remain confounded with method. GAdapt-derived targets cannot explain feasibility counts: targets only determine attainment.

6. **Add threats:** only two retained case57 scenarios after OPF exclusions; extensive censoring; bootstrap uncertainty conditional on fixed instances/references; pointwise intervals; configuration-specific initialization; and benchmark-specific grid/range assumptions. Conditional feasible-loss medians compare selected subsets and cannot establish paired loss superiority.