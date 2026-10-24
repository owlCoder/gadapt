**Verdict: READY TO APPLY.** Read-only; nothing applied or written. All **71 tests passed** using an in-memory import overlay; targeted boundary checks also passed.

- **Penalty key collapse — FIXED within the revised input domain.** `parse_pair` rejects objective magnitudes and violations above `1e150`. Combined with the maximum adaptive weight of `1e106`, penalties remain finite; survivor keys use the unclipped penalized value.

- **Parent selection/immigration on scalars — FIXED as a documentation issue.** README now limits exact ordering to survivors and explicitly identifies parent selection, immigration and adaptation as scalar consumers. Their behavior remains unchanged, as documented.

- **Overflow fallback reversing penalty ordering — FIXED.** The fallback is removed, and permitted inputs cannot overflow the penalty calculation. Targeted ordering checks passed; the original overflowing examples are now rejected.

- **Initial-scale overflow — FIXED.** Initial objective magnitudes are bounded by `1e150`, so the median’s intermediate sum remains finite. Initial objectives `−1e150` and `1e150` produce `f_ref=1e150` and distinct scalar costs.

**New bugs:** None found in this review. “Exact” penalty ordering remains subject to ordinary floating-point rounding; the overflow-specific defects from 030 are resolved.