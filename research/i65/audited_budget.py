"""Audited *research-only* sequential evaluator, no changes to GAdapt defaults.

Physical attempts are reserved BEFORE invocation; failed and nonfinite calls
count. The best *input* is snapshotted BEFORE the callback can mutate arrays.
One slot can be reserved for an independent final witness, inside total B.

This is a candidate instrument for external review, not a frozen protocol or
a production-ready/power-flow-certified evaluator. Parallel and vectorized
objectives are deliberately unsupported.
"""
from __future__ import annotations
import copy
from dataclasses import dataclass
import hashlib
import json
import math
from typing import Callable
import numpy as np

class BudgetReached(BaseException):
    """Internal control signal for deterministic budget boundary."""

@dataclass(frozen=True)
class Record:
    n: int
    phase: str
    x: tuple[float, ...]
    outcome: str
    value: float | None
    error_type: str | None

class AuditedBudget:
    ALLOWED = frozenset({"init", "search", "probe", "callback", "restart",
                         "polish", "recheck"})
    def __init__(self, objective: Callable, budget: int, *, reserve_witness: bool = True):
        if type(budget) is not int or budget < (2 if reserve_witness else 1):
            raise ValueError("invalid B or too small for witness reservation")
        if not callable(objective):
            raise ValueError("objective must be callable")
        self.objective = objective
        self.budget = budget
        self.reserve_witness = reserve_witness
        self.search_cap = budget - int(reserve_witness)
        self.attempts = 0
        self.best = math.inf
        self.best_x: tuple[float, ...] | None = None
        self.best_at: int | None = None
        self.records: list[Record] = []
        self.checked = False

    def __deepcopy__(self, memo):
        """Compatible with GAdapt GA.execute() copying its callback."""
        return self

    @staticmethod
    def _snapshot(x) -> tuple[float, ...]:
        a = np.array(x, dtype=float, copy=True)
        if a.ndim != 1 or len(a) < 1:
            raise ValueError("expected 1D nonempty candidate")
        if not np.all(np.isfinite(a)):
            raise ValueError("expected finite candidate coordinates")
        return tuple(float(t) for t in a.tolist())

    def evaluate(self, x, *, phase: str = "search", evaluator=None) -> float:
        if phase not in self.ALLOWED:
            raise ValueError(f"unknown phase {phase}")
        if phase == "recheck":
            if not self.reserve_witness or self.checked:
                raise RuntimeError("invalid/duplicate recheck")
            if evaluator is None or evaluator is self.objective:
                raise ValueError("independent witness evaluator required")
            cap = self.budget
        else:
            if evaluator is not None:
                raise ValueError("independent evaluator only for recheck")
            # A witness is terminal even when evaluated before search_cap.
            # Never permit a newer incumbent after it was independently checked.
            if self.checked:
                raise BudgetReached()
            cap = self.search_cap
        if self.attempts >= cap:
            raise BudgetReached()
        # Snapshot and objective input are separate objects. Input coercion is
        # not a physical objective call; do not increment on invalid vector.
        before = self._snapshot(x)
        self.attempts += 1  # reserve BEFORE physical invocation
        if phase == "recheck":
            self.checked = True
        obj = evaluator if phase == "recheck" else self.objective
        try:
            # A separate mutable copy prevents user callback from modifying x.
            v = float(obj(np.array(before, dtype=float)))
        except BaseException as ex:
            self.records.append(Record(self.attempts, phase, before,
                                       "exception", None, type(ex).__name__))
            raise
        if math.isfinite(v):
            outcome = "finite"
            # Recheck must not modify the optimizer's search incumbent or
            # time-to-target trace even when it returns a different value.
            if phase != "recheck" and v < self.best:
                self.best, self.best_x, self.best_at = v, before, self.attempts
        else:
            outcome = "nonfinite"
        self.records.append(Record(self.attempts, phase, before,
                                   outcome, v if math.isfinite(v) else None, None))
        return v

    def __call__(self, x):
        return self.evaluate(x, phase="search")

    def verify(self, independent: Callable, *, atol=1e-12, rtol=1e-10,
               bounds=None) -> dict:
        """Consumes one reserved physical attempt; fails closed."""
        if not self.reserve_witness:
            raise RuntimeError("no witness slot reserved")
        if self.checked:
            raise RuntimeError("witness already checked")
        if independent is self.objective or not callable(independent):
            raise ValueError("independent witness evaluator required")
        # Never certify under an invalid tolerance: infinity would make every
        # finite discrepancy pass math.isclose, including an incorrect oracle.
        try:
            atol, rtol = float(atol), float(rtol)
        except (TypeError, ValueError, OverflowError) as ex:
            raise ValueError("invalid witness tolerances") from ex
        if not (math.isfinite(atol) and math.isfinite(rtol)
                and atol >= 0 and rtol >= 0):
            raise ValueError("invalid witness tolerances")
        if self.best_x is None:
            return {"status": "NOT_SOLVED", "reason": "no_finite_search_result",
                    "attempts": self.attempts}
        x = np.asarray(self.best_x, dtype=float)
        if bounds is not None:
            try:
                lo, hi = (np.asarray(z, dtype=float) for z in bounds)
            except (TypeError, ValueError, OverflowError) as ex:
                raise ValueError("invalid witness bounds") from ex
            # A wrong shape can broadcast silently, and NaN comparisons are
            # False. Neither must ever produce VALIDATED_WITNESS.
            if (lo.shape != x.shape or hi.shape != x.shape
                    or not np.all(np.isfinite(lo))
                    or not np.all(np.isfinite(hi)) or np.any(lo > hi)):
                return {"status": "INVALID_RESULT", "reason": "invalid_bounds",
                        "attempts": self.attempts}
            if np.any(x < lo) or np.any(x > hi):
                return {"status": "INVALID_RESULT", "reason": "out_of_bounds",
                        "attempts": self.attempts}
        try:
            v = self.evaluate(x, phase="recheck", evaluator=independent)
        except (Exception, BudgetReached) as ex:
            # BudgetReached inherits BaseException so drivers cannot swallow the
            # outer budget boundary. Inside a witness callback it is an actual
            # failed, charged recheck, not an unclassified escaped sentinel.
            return {"status": "INVALID_RESULT", "reason": "recheck_exception",
                    "error_type": type(ex).__name__, "attempts": self.attempts}
        if not math.isfinite(v):
            return {"status": "INVALID_RESULT", "reason": "recheck_nonfinite",
                    "attempts": self.attempts}
        if not math.isclose(v, self.best, rel_tol=rtol, abs_tol=atol):
            return {"status": "INVALID_RESULT", "reason": "objective_mismatch",
                    "reported": self.best, "observed": v,
                    "attempts": self.attempts}
        return {"status": "VALIDATED_WITNESS", "best": self.best,
                "x": list(self.best_x), "attempts": self.attempts}

    def trace_hash(self) -> str:
        # Canonical typed deterministic trace, no wall-clock timestamps.
        payload = [r.__dict__ for r in self.records]
        s = json.dumps(payload, allow_nan=False, sort_keys=True,
                       separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(s.encode("ascii")).hexdigest()
