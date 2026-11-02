"""Independent, research-only I56-style ORPD constraint aggregation.

Operates exclusively on a supplied already-solved MATPOWER case, using NumPy
and the separately written AC-equation residual checker. Never imports or
runs PYPOWER, GAdapt, COCO, or any nonlinear solver. The four metrics follow
historical I56 definitions exactly, NOT a full OPF-feasibility certificate.
"""
from __future__ import annotations

import numpy as np

from ac_residual_witness import InvalidACCase, evaluate_ac_point

COMPONENTS = ("voltage", "reactive", "slack", "thermal")


def calculate_constraint_components(case):
    """Unqualified numeric I56-style components; do not infer feasibility.

    Historical I56: voltage excursions in p.u.; on-generator reactive/slack
    PG violations in MW/MVAr divided by baseMVA; max apparent flow at each
    branch end minus positive RATE_A, summed and divided by baseMVA.
    """
    try:
        base = float(case["baseMVA"])
        bus = np.asarray(case["bus"], dtype=float)
        gen = np.asarray(case["gen"], dtype=float)
        branch = np.asarray(case["branch"], dtype=float)
    except (KeyError, ValueError, TypeError) as exc:
        raise InvalidACCase("invalid constraint input") from exc
    if (not np.isfinite(base) or base <= 0 or
        bus.ndim != 2 or bus.shape[1] < 13 or
        gen.ndim != 2 or gen.shape[1] < 10 or
        branch.ndim != 2 or branch.shape[1] < 17 or
        any(not np.isfinite(x).all() for x in (bus, gen, branch))):
        raise InvalidACCase("incomplete/nonfinite solved case or invalid baseMVA")
    if np.any(bus[:, 11] < bus[:, 12]) or np.any(gen[:, 3] < gen[:, 4]) or np.any(gen[:, 8] < gen[:, 9]):
        raise InvalidACCase("inverted voltage, reactive or active generator limits")
    if np.any(branch[:, 5] < 0):
        raise InvalidACCase("negative branch thermal rating")
    if np.any((bus[:, 1] != np.rint(bus[:, 1]))):
        raise InvalidACCase("invalid bus types")
    active = gen[gen[:, 7] > 0]
    reference_ids = set(bus[bus[:, 1] == 3, 0].astype(int))
    if not reference_ids or not np.any(np.isin(active[:, 0].astype(int), list(reference_ids))):
        raise InvalidACCase("no online reference generator")
    slack_generators = active[np.isin(active[:, 0].astype(int), list(reference_ids))]
    voltage = np.maximum(bus[:, 7] - bus[:, 11], 0) + np.maximum(bus[:, 12] - bus[:, 7], 0)
    reactive = np.maximum(active[:, 2] - active[:, 3], 0) + np.maximum(active[:, 4] - active[:, 2], 0)
    slack = np.maximum(slack_generators[:, 1] - slack_generators[:, 8], 0) + np.maximum(slack_generators[:, 9] - slack_generators[:, 1], 0)
    apparent_from = np.hypot(branch[:, 13], branch[:, 14])
    apparent_to = np.hypot(branch[:, 15], branch[:, 16])
    thermal = np.where(branch[:, 5] > 0, np.maximum(np.maximum(apparent_from, apparent_to) - branch[:, 5], 0), 0)
    return {
        "voltage": float(np.sum(voltage)),
        "reactive": float(np.sum(reactive) / base),
        "slack": float(np.sum(slack) / base),
        "thermal": float(np.sum(thermal) / base),
    }


def validate_constraint_components(case, *, residual_balance_tolerance_mva=1e-3,
                                   residual_flow_tolerance_mva=1e-5,
                                   i56_component_tolerance=1e-6):
    """Report I56-compatible metrics only when an independent AC residual passes.

    The caller must separately establish that inputs are a genuine solved
    operating point; no second numerical AC solver is implemented here.
    """
    if not np.isfinite(i56_component_tolerance) or i56_component_tolerance < 0:
        raise InvalidACCase("invalid I56 feasibility tolerance")
    residual = evaluate_ac_point(case, balance_tolerance_mva=residual_balance_tolerance_mva,
                                 flow_tolerance_mva=residual_flow_tolerance_mva)
    if residual["status"] != "AC_RESIDUAL_PASS":
        return {"status": "AC_RESIDUAL_FAIL", "residual": residual,
                "components": None, "i56_compatible_feasible": None}
    values = calculate_constraint_components(case)
    feasible = all(value <= i56_component_tolerance for value in values.values())
    return {"status": "AC_CONSISTENT_CONSTRAINT_CHECK",
            "residual": residual,
            "components": values,
            "i56_compatible_feasible": bool(feasible),
            "i56_component_tolerance": i56_component_tolerance,
            "scope": "I56 four-component constraints on solver-supplied state, not independent numerical AC PF"}
