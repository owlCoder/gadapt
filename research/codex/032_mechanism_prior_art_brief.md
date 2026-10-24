# Brief for Codex #32 — prior art for the MECHANISM claim of I56, beyond power systems (read-only, web search on)

I56 (research/ITERATION56_PROTOCOL.md, H5_PROPOSAL_SR.md §10–11) asks whether the effect of GAdapt's diversity-driven
self-adaptation depends on the constraint-handling technique, and whether part of it runs through adaptation signals
that read cost VALUES (static penalty) vs a common scalar. OPF-specific prior art is in H5 (Biswas 2018, Mallipeddi
2012, Premkumar 2023, ...). Now search the general EC literature, try to refute novelty of the mechanism:
- theory/empirics of self-adaptation (step size, mutation rate, CMA) interacting with constraint handling: e.g.
  Arnold (2011–2013) (1,λ)-σSA-ES / cumulative step-size adaptation on constrained linear problems; Hellwig & Arnold
  2016 comparison of constraint-handling mechanisms for the (1,λ)-ES (ECJ); Arnold & Hansen 2012 (1+1)-CMA-ES with
  constraints; Atamna, Auger, Hansen (augmented Lagrangian CMA-ES, 2016–2020) where penalty adaptation interacts with
  step size; Spettel & Beyer (2018–2020) on constrained ES dynamics; DE: "constraint handling × parameter adaptation"
  (e.g. Tanabe & Fukunaga on SHADE with constraints, CEC constrained competition analyses, Polakova 2017);
  diversity measurement under penalties / infeasible populations.
- any study that separates the "ordering" path from the "value-in-the-adaptation-signal" path of a CHT.
Give: closest works with VERIFIED DOIs, what they establish, and the precise remaining difference of I56 (if any);
a paragraph for the I56 report's related work; impact on the novelty statement. Max ~700 words. Read-only.
