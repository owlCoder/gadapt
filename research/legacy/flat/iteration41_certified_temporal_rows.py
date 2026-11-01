"""I41 mathematically safe route-aware redundancy of edge x scenario rows.

Only for the EXACT I38/I39 one fixed binary choice between TWO original
paths per demand. This module makes NO network or physical solver calls.
The minimum route-wise load difference is computed analytically.

Theorem: For every e,s,t,
  min_z [load(e,s,z)-load(e,t,z)]
   = sum_{d: both routes use e} (q[s,d]-q[t,d])
     + sum_{d: exactly one route uses e} min(0,q[s,d]-q[t,d]).
Thus if the RHS >= 0, (e,s) implies (e,t) for ALL possible binary route
vectors and ALL admissible static capacity-module installations.
This is a presolve certificate, NOT original robust-optimization theory.
"""
import math
import numpy as np


def _physical_masks(problem, edge):
    a0 = np.asarray(problem.incidence[0, :, edge])
    a1 = np.asarray(problem.incidence[1, :, edge])
    if (a0.shape != (problem.n,) or a1.shape != (problem.n,) or
            not np.all((a0 == 0) | (a0 == 1)) or
            not np.all((a1 == 0) | (a1 == 1))):
        raise ValueError("I41 requires exact two binary unsplittable route incidence")
    use0, use1 = a0 == 1, a1 == 1
    return use0 & use1, use0 ^ use1


def _dominance_margin(q, both, xor, s, t):
    """Return conservative float-certified min_z(load_s - load_t) or zero-tie."""
    mask = both | xor
    if np.array_equal(q[s, mask], q[t, mask]):
        return (0., 0., True)
    delta_both = q[s, both] - q[t, both]
    delta_xor = q[s, xor] - q[t, xor]
    # Use a conservative roundoff guard; near-zero ambiguous cases stay in MILP.
    margin = math.fsum(float(v) for v in delta_both) + math.fsum(
        min(0., float(v)) for v in delta_xor)
    scale = math.fsum(abs(float(v)) for v in delta_both) + math.fsum(
        abs(float(v)) for v in delta_xor)
    # includes input subtraction and sum rounding, roughly 64 ULP envelope.
    guard = 64.0 * np.finfo(float).eps * max(1., scale)
    return (float(margin), float(guard), False)


def _certifies(q, both, xor, s, t):
    # First prove elementwise domination over every demand that MAY use
    # this edge. This also certifies equality M=0 when a demand may
    # choose a route avoiding the edge, with no cancellation/roundoff.
    active = both | xor
    if np.all(q[s, active] >= q[t, active]):
        return True
    margin, guard, identical = _dominance_margin(q, both, xor, s, t)
    return identical or margin > guard


def certified_route_aware_rows(problem):
    """Compute exact-for-model dominance witnesses and kept rows per edge.

    Consequence: reducing ONLY certified dominated link-time rows retains the
    same feasible (z,y) set for I39 MILP, not just the same one candidate.
    The complete original demand array is still retained for independent
    incumbent re-verification and for holdout checks.
    """
    q = np.asarray(problem.q, dtype=float)
    if (q.ndim != 2 or q.shape[1] != problem.n or not len(q)
            or not np.all(np.isfinite(q)) or np.any(q < 0)):
        raise ValueError("Invalid source traffic matrix; cannot certify dominance")
    n_time, n_edge = len(q), len(problem.links)
    result = []
    for e in range(n_edge):
        both, xor = _physical_masks(problem, e)
        kept = []
        for t in range(n_time):
            # If any *currently retained* frame dominates this frame,
            # there is no need to add it.
            if any(_certifies(q, both, xor, s, t) for s in kept):
                continue
            # A new time may dominate previously kept frames. Dropping them
            # is logically safe; every removed row gets a direct FINAL witness
            # below (not an unverified transitivity chain).
            kept = [s for s in kept if not _certifies(q, both, xor, t, s)]
            kept.append(t)
        # Directly construct/verify a live retained witness for EACH removed row.
        kept_set = set(kept)
        removed = []
        for t in range(n_time):
            if t in kept_set:
                continue
            found = next((s for s in kept if _certifies(q, both, xor, s, t)), None)
            if found is None:
                # Usually indicates a floating-point transitivity anomaly.
                # Fail CLOSED rather than dropping an unverified original row.
                raise ValueError("No direct source traffic dominance witness")
            margin, guard, identical = _dominance_margin(q, both, xor, found, t)
            removed.append(dict(time=t, dominated_by=found,
                                min_route_load_difference=margin,
                                roundoff_guard=guard, identical_inputs=identical))
        result.append(dict(edge=e, kept_times=sorted(kept), removed=removed))
    certificate=dict(
        kind="I41_route_aware_two_unsplittable_paths_exact_row_implication",
        original_rows=n_time*n_edge,
        kept_rows=sum(len(item["kept_times"]) for item in result),
        removed_rows=sum(len(item["removed"]) for item in result),
        edge_time_rows=result)
    verify_certified_rows(problem, certificate)
    return certificate


def _binary64_exact_integer_matrix(q):
    """Losslessly encode each finite IEEE-754 float as an integer on ONE
    common power-of-two denominator; Python arbitrary integers avoid
    every arithmetic cancellation/roundoff issue in the final proof.

    This is exact for the numbers ACTUALLY loaded by numpy. It does not
    claim recovery of original unparsed decimal-text precision.
    """
    values = np.asarray(q, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("Exact certificate cannot represent NaN/inf")
    ratios = [float(v).as_integer_ratio() for v in values.flat]
    common_exp = max((den.bit_length()-1 for _,den in ratios), default=0)
    integers = [num << (common_exp-(den.bit_length()-1))
                for num,den in ratios]
    return np.asarray(integers,dtype=object).reshape(values.shape)


def verify_certified_rows(problem, certificate):
    """Fail closed on tampered/partial certificates (no silent missing rows)."""
    q=np.asarray(problem.q,dtype=float)
    if not np.all(np.isfinite(q)) or np.any(q<0):
        raise ValueError("Cannot certify invalid original source demand")
    # Slow exact verification is applied ONLY to proposed removed rows;
    # the O(T^2 D) screening above still uses conservative fast floats.
    q_exact=_binary64_exact_integer_matrix(q)
    n_time,n_edge=len(q),len(problem.links)
    if (not isinstance(certificate,dict) or
            certificate.get("kind") !=
            "I41_route_aware_two_unsplittable_paths_exact_row_implication" or
            type(certificate.get("original_rows")) is not int or
            certificate["original_rows"] != n_time*n_edge or
            not isinstance(certificate.get("edge_time_rows"),list) or
            len(certificate["edge_time_rows"]) != n_edge):
        raise ValueError("Unrecognized or wrong-sized I41 certificate")
    covered=0
    removed_count=0
    for e,entry in enumerate(certificate["edge_time_rows"]):
        if not isinstance(entry,dict) or entry.get("edge") != e:
            raise ValueError("I41 certification edge mismatch")
        kept=entry.get("kept_times")
        rem=entry.get("removed")
        if (not isinstance(kept,list) or not isinstance(rem,list) or
                not kept or any(type(x) is not int for x in kept) or
                any(not 0<=x<n_time for x in kept) or
                len(set(kept))!=len(kept) or kept!=sorted(kept)):
            raise ValueError("I41 has invalid kept scenario indices")
        both,xor=_physical_masks(problem,e)
        both_ids=np.flatnonzero(both)
        xor_ids=np.flatnonzero(xor)
        dropped=[]
        for witness in rem:
            if not isinstance(witness,dict):
                raise ValueError("I41 missing witness")
            t=witness.get("time")
            s=witness.get("dominated_by")
            if (type(t) is not int or type(s) is not int or
                    not 0<=t<n_time or s not in kept or t in kept):
                raise ValueError("I41 forged or out-of-range witness")
            if not _certifies(q,both,xor,s,t):
                raise ValueError("I41 non-implying witness, cannot omit constraint")
            # This is an EXACT min over every permitted binary routing vector,
            # with no floating-point rounding, as an integer numerator.
            exact_min=sum((q_exact[s,d]-q_exact[t,d] for d in both_ids),0)
            exact_min+=sum((min(0,q_exact[s,d]-q_exact[t,d])
                           for d in xor_ids),0)
            if exact_min<0:
                raise ValueError("I41 EXACT binary64 rational witness is negative")
            margin,guard,identical=_dominance_margin(q,both,xor,s,t)
            if (witness.get("min_route_load_difference")!=margin or
                    witness.get("roundoff_guard")!=guard or
                    witness.get("identical_inputs") is not identical):
                raise ValueError("I41 source witness details mismatch")
            dropped.append(t)
        if set(kept)|set(dropped)!=set(range(n_time)) or (
                set(kept)&set(dropped)) or len(set(dropped))!=len(dropped):
            raise ValueError("I41 every original edge-time row needs exact coverage")
        covered+=len(kept)
        removed_count+=len(dropped)
    if (certificate.get("kept_rows")!=covered or
            certificate.get("removed_rows")!=removed_count or
            covered+removed_count!=n_time*n_edge):
        raise ValueError("I41 corrupted global row count")
    return True
