import math
import random

import numpy as np


class CompensatoryMutation:
    """
    Compensatory mutation (opt-in, GA parameter compensatory_mutation).

    After the usual mutation of a candidate solution, each mutated decision variable i may drag ONE partner decision variable j
    along the elite correlation: delta_j = clip(C_ji / (C_ii + eps), -2, 2) * delta_i, in range-normalised coordinates. C is
    the covariance of the best evaluated candidate solutions of the population (the share given by keep_elitism_percentage).
    No additional cost function evaluations are made. The "gated" mode accepts a pair only if two interleaved halves of the elite
    agree on the sign of the correlation and both have |rho| >= 0.5.

    Modes: "gated" (the feature); experimental controls for studies: "ungated" (partner by largest |rho|, no gate),
    "permuted" (the same shift is applied to a random unused partner), "resample" (partner value re-drawn from the Gaussian
    conditional on the mutated value, as in linkage-model optimizers).
    """

    MODES = ("gated", "ungated", "permuted", "resample")
    RHO_MIN = 0.5
    EPS = 1e-12
    CLIP = 2.0

    def __init__(self, mode: str):
        if mode not in self.MODES:
            raise ValueError("compensatory_mutation must be None or one of " + ", ".join(self.MODES))
        self.mode = mode

    @staticmethod
    def _bounds(c):
        lo = np.array([v.decision_variable.min_value for v in c], float)
        hi = np.array([v.decision_variable.max_value for v in c], float)
        return lo, hi

    def _elite(self, population, c, d):
        evaluated = [x for x in population.candidate_solutions
                     if x is not c and len(x) == d and not math.isnan(x.cost_value)]
        if len(evaluated) < d + 2:
            return None
        evaluated.sort(key=lambda x: x.cost_value)
        k = max(d + 2, min(len(evaluated), int(math.ceil(population.options.keep_elitism_percentage / 100.0 * population.options.population_size))))
        return evaluated[:k]

    @staticmethod
    def _fit(dv, value):
        low, high = dv.min_value, dv.max_value
        if high > low:
            span = high - low
            value = (value - low) % (2 * span)
            value = low + (value if value <= span else 2 * span - value)
        step = getattr(dv, "step", None)
        if step is not None and step > 0:
            k_max = math.floor((high - low) / step + 1e-9)
            k = min(max(int(round((value - low) / step)), 0), k_max)
            value = round(low + k * step, max(0, getattr(dv, "decimal_places", 0)))
        return value

    def apply(self, population, c, before):
        """before: list of the candidate's variable values before the mutation."""
        d = len(c)
        mutated = [i for i in range(d) if c[i].value != before[i]]
        if not mutated:
            return
        elite = self._elite(population, c, d)
        if elite is None:
            return
        lo, hi = self._bounds(c)
        rng_ = np.where(hi > lo, hi - lo, 1.0)
        X = (np.array([[v.value for v in e] for e in elite], float) - lo) / rng_
        C = np.cov(X.T)
        if C.ndim == 0:
            return
        sd = np.sqrt(np.maximum(np.diag(C), 0.0))
        denom = np.outer(sd, sd)
        R = np.where(denom > self.EPS, C / np.where(denom > self.EPS, denom, 1.0), 0.0)
        np.fill_diagonal(R, 0.0)
        if self.mode == "gated":
            h1, h2 = X[0::2], X[1::2]
            if len(h1) < 3 or len(h2) < 3:
                return
            R1, R2 = np.corrcoef(h1.T), np.corrcoef(h2.T)
            np.fill_diagonal(R1, 0.0); np.fill_diagonal(R2, 0.0)
            R1, R2 = np.nan_to_num(R1), np.nan_to_num(R2)
            gate = (np.sign(R1) == np.sign(R2)) & (np.abs(R1) >= self.RHO_MIN) & (np.abs(R2) >= self.RHO_MIN)
        else:
            gate = np.ones((d, d), bool)
        used = set(mutated)
        mu = X.mean(axis=0)
        order = list(mutated)
        random.shuffle(order)
        for i in order:
            delta_i = (c[i].value - before[i]) / rng_[i]
            cand = [j for j in range(d) if j not in used and gate[i, j] and abs(R[i, j]) > 0.0]
            if not cand:
                continue
            j = max(cand, key=lambda t: abs(R[i, t]))
            b = float(np.clip(C[j, i] / (C[i, i] + self.EPS), -self.CLIP, self.CLIP))
            if self.mode == "permuted":
                free = [t for t in range(d) if t not in used]
                tgt = random.choice(free)
                new_norm = (c[tgt].value - lo[tgt]) / rng_[tgt] + b * delta_i
                c[tgt].value = self._fit(c[tgt].decision_variable, lo[tgt] + new_norm * rng_[tgt]); used.add(tgt)
            elif self.mode == "resample":
                xi_new = (c[i].value - lo[i]) / rng_[i]
                var_c = max(C[j, j] - C[j, i] ** 2 / (C[i, i] + self.EPS), 0.0)
                new_norm = mu[j] + b * (xi_new - mu[i]) + math.sqrt(var_c) * random.gauss(0.0, 1.0)
                c[j].value = self._fit(c[j].decision_variable, lo[j] + new_norm * rng_[j]); used.add(j)
            else:
                new_norm = (c[j].value - lo[j]) / rng_[j] + b * delta_i
                c[j].value = self._fit(c[j].decision_variable, lo[j] + new_norm * rng_[j]); used.add(j)
            used.add(i)
        c.set_candidate_solution_string_none()
        c.reset_hash_cache()
