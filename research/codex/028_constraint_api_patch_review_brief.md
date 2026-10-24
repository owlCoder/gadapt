# Brief for Codex #28 — review of the opt-in constraint_handling library patch (read-only)

Patch: research/patches/constraint_api.patch (unified diff against the current gadapt/, README.md, tests/; developed in a
copy because the I56/I57 study is importing gadapt/ right now — do NOT apply it). Design: research/GADAPT_CONSTRAINT_API_DESIGN_SR.md.
Claims: default behaviour bit-identical (seeded call-sequence hash over 9 runs unchanged), 64 library tests pass incl. 6
new ones. Review for: (1) default bit-identity risks (any code path executed when constraint_handling is None?);
(2) correctness of the four techniques and the event order in ConstraintHandlingCostFinder (it re-implements the
ElitismCostFinder sorting without calling super — anything lost, e.g. operator credit controller, logging, immigrants,
min_cost semantics used by exit checkers / generations_without_improvement?); (3) interaction with GAdapt signals
(cost diversity log-range on merits in (1,3) or penalized costs; sys.float_info.max for failed evaluations under
penalty — does log-range or average_difference break?); (4) validation (pair check, epsilon needing
number_of_generations, setters after construction); (5) CLAUDE.md conventions for a new GA parameter (constructor,
property+setter, GAOptions field?, docstring, README); (6) README accuracy. List BLOCKING / IMPORTANT / MINOR.
Max ~700 words. Read-only.
