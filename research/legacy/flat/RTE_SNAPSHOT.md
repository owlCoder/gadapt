# RTE-origin offline grid snapshot: stronger external validity

Public `case1888rte` benchmark, published with MATPOWER and imported by
pandapower. The case models the scale/complexity of a French transmission
network and includes data sampled from the iTesla offline platform.

**Important source limitation:** The publishers expressly state these
datasets are for validation of mathematical methods, NOT for operation or
planning of real French or European networks. This is not live operational
telemetry and does not replace a field dataset, hardware-in-the-loop tests,
or utility approval.

Primary source: https://matpower.org/docs/ref/matpower6.0/case1888rte.html
Cite: C. Josz et al., AC Power Flow Data in MATPOWER and QCQP Format:
iTesla, RTE Snapshots, and PEGASE (2016), arXiv:1603.01533.

The one-seed, four-generation run is a **connectivity/convergence smoke
test only**. It cannot establish accuracy or robustness. Replicate with
more seeds and budgets after measuring computational cost.
