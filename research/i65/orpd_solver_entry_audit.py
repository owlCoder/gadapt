"""Research-only sequential PYPOWER API-entrypoint tracing; no GA changes.

Counts attempted calls through pypower.api.runopf/runpf, including failures.
Not an instrumentation of PYPOWER's internal Newton steps, nor evidence that
an I58 witness uses a physically independent power-flow solver.

Use only with a single-threaded, pre-reviewed bounded smoke-test. The patch
is in-process and installed at pypower.api; prior ``from ... import ...``
aliases are not intercepted, so import historical modules only after enter.
"""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import importlib
import json
from typing import Callable

KINDS = ("runopf", "runpf")
PHASES = ("setup", "search", "witness")


class SolverEntryAudit:
    def __init__(self) -> None:
        self.events: list[dict] = []
        self._active = False
        self._phase: str | None = None

    def _wrap(self, kind: str, func: Callable) -> Callable:
        def audited(*args, **kwargs):
            if self._phase is None:
                raise RuntimeError("solver entrypoint missing explicit phase")
            record = {"index": len(self.events) + 1,
                      "phase": self._phase, "kind": kind, "outcome": "attempted"}
            # Reserve before calling PYPOWER: exceptions count as attempts.
            self.events.append(record)
            try:
                value = func(*args, **kwargs)
            except BaseException as ex:
                record.update(outcome="exception", error_type=type(ex).__name__)
                raise
            record["outcome"] = "returned"
            return value
        return audited

    @contextmanager
    def trace(self):
        if self._active:
            raise RuntimeError("audit trace already active")
        api = importlib.import_module("pypower.api")
        original = {kind: getattr(api, kind) for kind in KINDS}
        self._active = True
        try:
            for kind in KINDS:
                setattr(api, kind, self._wrap(kind, original[kind]))
            yield self
        finally:
            for kind, func in original.items():
                setattr(api, kind, func)
            self._phase = None
            self._active = False

    @contextmanager
    def phase(self, label: str):
        if label not in PHASES:
            raise ValueError("unknown solver phase")
        if not self._active:
            raise RuntimeError("start audit trace before setting a phase")
        if self._phase is not None:
            raise RuntimeError("nested solver phase is forbidden")
        self._phase = label
        try:
            yield self
        finally:
            self._phase = None

    def count(self, *, phase: str | None = None, kind: str | None = None) -> int:
        if phase is not None and phase not in PHASES:
            raise ValueError("unknown solver phase")
        if kind is not None and kind not in KINDS:
            raise ValueError("unknown solver entrypoint")
        return sum((phase is None or x["phase"] == phase) and
                   (kind is None or x["kind"] == kind) for x in self.events)

    def evidence(self) -> dict:
        data = {"schema": "GADAPT_I65_SOLVER_ENTRYPOINT_V1",
                "scope": "pypower.api.runopf/runpf entrypoint attempts only",
                "events": self.events,
                "totals": {kind: self.count(kind=kind) for kind in KINDS},
                "phases": {phase: {kind: self.count(phase=phase, kind=kind)
                                   for kind in KINDS} for phase in PHASES}}
        blob = json.dumps(data, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
        return {**data, "sha256": sha256(blob).hexdigest()}
