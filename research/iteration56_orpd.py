"""Discrete optimal reactive power dispatch (ORPD) on pypower cases, the instrument for the H5 study.

Controls (all on a nested value grid of R positions): generator voltage set-points VG, tap ratios of in-service
transformers, and bus shunt susceptances BS at buses with a nonzero shunt in the case. Objective: active power losses
(MW). Constraints: bus voltage limits, generator reactive limits, slack active limits, branch MVA ratings (> 0).
One evaluation = one Newton-Raphson power flow (pypower `runpf`), counted by the caller.

The grids are modelling assumptions (documented in research/H5_PROPOSAL_SR.md), not equipment specifications:
VG in [VMIN, VMAX] of the generator bus, taps in [0.9, 1.1], a shunt with case value b in [0, 2b] (b > 0) or [2b, 0]
(reactor, b < 0). An operating scenario scales all loads by `load_factor` and perturbs each bus load by a fixed
seeded factor in [1 - spread, 1 + spread]; the active dispatch PG is then fixed to the continuous AC OPF (`runopf`)
solution of that scenario, so the study optimizes only the voltage/reactive controls. A scenario whose OPF fails is
invalid (`ScenarioError`).
"""
import contextlib
import io

import numpy as np

TAP_RANGE = (0.9, 1.1)
CASES = ("case14", "case57", "case118")


class ScenarioError(RuntimeError):
    pass
PF_OPTIONS = dict(VERBOSE=0, OUT_ALL=0, ENFORCE_Q_LIMS=0, PF_TOL=1e-8, PF_MAX_IT=30)


class ORPD:
    def __init__(self, case_name, resolution, load_factor=1.0, spread=0.0, scenario_seed=0):
        from pypower import api
        from pypower.idx_brch import BR_STATUS, TAP
        from pypower.idx_bus import BS, PD, QD, VMAX, VMIN
        from pypower.idx_gen import GEN_BUS, GEN_STATUS
        self.case_name, self.resolution = case_name, int(resolution)
        base = getattr(api, case_name)()
        bus = base["bus"]
        rng = np.random.RandomState(scenario_seed)
        scale = load_factor * (1 + spread * (2 * rng.random_sample(len(bus)) - 1))
        bus[:, PD] *= scale
        bus[:, QD] *= scale
        from pypower.idx_gen import PG
        with contextlib.redirect_stdout(io.StringIO()):
            opf = api.runopf({k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in base.items()},
                             api.ppoption(VERBOSE=0, OUT_ALL=0))
        if not opf["success"]:
            raise ScenarioError(f"{case_name}: OPF failed for load_factor={load_factor}, seed={scenario_seed}")
        base["gen"][:, PG] = opf["gen"][:, PG]
        self.opf_losses = float(np.sum(opf["branch"][:, 13] + opf["branch"][:, 15]))
        self.base = base
        self.options = api.ppoption(**PF_OPTIONS)
        gen = base["gen"]
        self.online = np.flatnonzero(gen[:, GEN_STATUS] > 0)
        index = {int(b): i for i, b in enumerate(bus[:, 0])}
        self.gen_rows = list(self.online)
        self.tap_rows = list(np.flatnonzero((base["branch"][:, TAP] != 0) & (base["branch"][:, BR_STATUS] > 0)))
        self.shunt_rows = list(np.flatnonzero(bus[:, BS] != 0))
        lo, hi = [], []
        for g in self.gen_rows:
            b = index[int(gen[g, GEN_BUS])]
            lo.append(bus[b, VMIN])
            hi.append(bus[b, VMAX])
        for _ in self.tap_rows:
            lo.append(TAP_RANGE[0])
            hi.append(TAP_RANGE[1])
        for s in self.shunt_rows:
            b = bus[s, BS]
            lo.append(min(0.0, 2 * b))
            hi.append(max(0.0, 2 * b))
        self.lo, self.hi = np.array(lo, float), np.array(hi, float)
        self.d = len(lo)
        self.step = (self.hi - self.lo) / (self.resolution - 1)

    def snap(self, x):
        """Nearest grid point (the controls are discrete)."""
        k = np.clip(np.rint((np.asarray(x, float) - self.lo) / self.step), 0, self.resolution - 1)
        return self.lo + k * self.step

    def evaluate(self, x):
        """dict(losses, violations (dimensionless components), feasible, converged); x is snapped first."""
        from pypower.api import runpf
        from pypower.idx_brch import PF, PT, QF, QT, RATE_A, TAP
        from pypower.idx_bus import BS, BUS_TYPE, VM, VMAX, VMIN
        from pypower.idx_gen import GEN_BUS, PG, PMAX, PMIN, QG, QMAX, QMIN, VG
        x = self.snap(x)
        case = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in self.base.items()}
        n_g, n_t = len(self.gen_rows), len(self.tap_rows)
        case["gen"][self.gen_rows, VG] = x[:n_g]
        case["branch"][self.tap_rows, TAP] = x[n_g:n_g + n_t]
        case["bus"][self.shunt_rows, BS] = x[n_g + n_t:]
        try:
            solved, converged = runpf(case, self.options)
        except (ValueError, ArithmeticError, RuntimeError, IndexError, np.linalg.LinAlgError):
            converged = False
        if not converged or not all(np.isfinite(solved[k]).all() for k in ("bus", "gen", "branch")):
            return dict(losses=None, violations=None, feasible=False, converged=False)
        bus, gen, branch = solved["bus"], solved["gen"], solved["branch"]
        base_mva = float(case["baseMVA"])
        losses = float(np.sum(branch[:, PF] + branch[:, PT]))
        g = gen[self.online]
        ref = set(bus[bus[:, BUS_TYPE] == 3, 0].astype(int))
        is_slack = np.array([int(r[GEN_BUS]) in ref for r in g])
        s = g[is_slack]
        rating = branch[:, RATE_A]
        flow = np.maximum(np.hypot(branch[:, PF], branch[:, QF]), np.hypot(branch[:, PT], branch[:, QT]))
        violations = dict(
            voltage=float(np.sum(np.maximum(bus[:, VM] - bus[:, VMAX], 0) + np.maximum(bus[:, VMIN] - bus[:, VM], 0))),
            reactive=float(np.sum(np.maximum(g[:, QG] - g[:, QMAX], 0) + np.maximum(g[:, QMIN] - g[:, QG], 0)))
            / base_mva,
            slack=float(np.sum(np.maximum(s[:, PG] - s[:, PMAX], 0) + np.maximum(s[:, PMIN] - s[:, PG], 0))) / base_mva,
            thermal=float(np.sum(np.where(rating > 0, np.maximum(flow - rating, 0), 0))) / base_mva,
        )
        feasible = all(v <= 1e-6 for v in violations.values())
        return dict(losses=losses, violations=violations, feasible=feasible, converged=True)
