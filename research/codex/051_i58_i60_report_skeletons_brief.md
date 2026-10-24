# Brief for Codex #51 — I58 and I60 report skeletons written BEFORE their results (read-only)
I58 test stage and then I60 are running now. Do NOT open any research/results/iteration56/i58_* or i60_* file or any
log: the skeletons must be result-blind. Sources: research/ITERATION58_PROTOCOL.md, ITERATION58_PROPOSAL_SR.md,
research/iteration58_validation.py (stages check, analyse: exact output keys), research/ITERATION60_PROTOCOL.md,
ITERATION60_PROPOSAL_SR.md, research/iteration60_epsilon.py, and the I56 report research/ITERATION56_REPORT_SR.md as the
style template (Serbian, Latin script). For EACH of I58 and I60 produce a Markdown report skeleton: sections; every
decision rule quoted verbatim from the frozen protocol; tables with placeholders named after the exact JSON keys the
analyse stage writes (key path -> table cell); and the pre-written interpretation sentence for every outcome branch
(confirmed / not confirmed / interval spans 0 / stop rule or check failure / exclusions above threshold), so that
writing the report is mechanical and cannot drift from the protocol. Flag any protocol rule that the analyse code does
NOT implement, or implements differently (that would be a blocking finding). Max ~1500 words total.
