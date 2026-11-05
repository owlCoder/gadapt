import math
import statistics as stat

from gadapt.operations.decision_variable_update.base_decision_variable_updater import BaseDecisionVariableUpdater


class ColumnarDiversityDecisionVariableUpdater(BaseDecisionVariableUpdater):
    """
    Calculates columnar diversity using Logarithmic Scaling to preserve
    sensitivity throughout the convergence curve.
    """

    def __init__(self, metric: str = "log_relative"):
        """
        Args:
            metric: "log_relative" (default) measures the spread of log((value - min_value) + 1),
                which depends on the units of the decision variable and on where the values lie
                in its range. "linear" measures the spread of the values relative to the range,
                which is invariant to the units and to the position in the range.
        """
        super().__init__()
        self._metric = metric

    def _update_decision_variables(self):
        # 1. Group values by decision variable
        values_per_variables = {}
        for c in self.population:
            if c.is_immigrant:
                continue
            for g in c:
                if g.decision_variable not in values_per_variables:
                    values_per_variables[g.decision_variable] = []
                values_per_variables[g.decision_variable].append(g.value)

        # 2. Process each decision variable
        for g, values in values_per_variables.items():
            # Check if population is identical for this decision variable
            if len(set(values)) <= 1:
                g.stacked = True
                g.columnar_diversity_coefficient = 0.0
                continue

            g.stacked = False

            if self._metric == "linear":
                # Scale first in opt-in reliability mode. Even finite bounds
                # [-1e308, 1e308] yield an infinite binary64 range; dividing
                # a finite raw standard deviation by inf silently reports
                # zero diversity for genuinely distinct candidates.
                monitor = getattr(getattr(self.population, "options", None),
                                  "reliability_monitor", None)
                if monitor is not None:
                    low, high = g.min_value, g.max_value
                    span = high - low
                    if math.isfinite(span):
                        normalized = [(v - low) / span for v in values]
                    else:
                        # Halve before subtraction so opposite-signed finite
                        # extremes cannot overflow; the dimensionless ratio
                        # still represents (value - low) / (high - low).
                        half_low = low * 0.5
                        half_span = high * 0.5 - half_low
                        normalized = [(v * 0.5 - half_low) / half_span
                                      for v in values]
                    current_log_stdev = stat.stdev(normalized)
                else:
                    # Keep the historical unmonitored calculation unchanged.
                    current_log_stdev = stat.stdev(values) / (g.max_value - g.min_value)
            else:
                # 3. Logarithmic transformation relative to the lower bound.
                log_values = []
                monitor = getattr(getattr(self.population, "options", None),
                                  "reliability_monitor", None)
                for v in values:
                    if monitor is None:
                        # Preserve the historical default-mode transformation.
                        shifted_v = (v - g.min_value) + 1.0
                        log_values.append(math.log(shifted_v))
                        continue
                    # Reliability mode must also support finite but widely
                    # separated bounds. The subtraction of -1e308 from
                    # +1e308 overflows, and log(inf) makes statistics.stdev
                    # fail even though both coordinates are valid.
                    gap = v - g.min_value
                    if math.isfinite(gap):
                        log_values.append(math.log1p(gap))
                    else:
                        # An overflowing difference between finite, ordered
                        # coordinates requires a negative lower bound and a
                        # positive value. Compute log(1 + value - lower)
                        # without constructing the unrepresentable distance.
                        log_values.append(
                            math.log(-g.min_value) + math.log1p(v / -g.min_value)
                        )

                # 4. Calculate Logarithmic Standard Deviation
                current_log_stdev = stat.stdev(log_values)

            # 5. Capture Benchmark (Initial Log Diversity)
            if g.initial_st_dev < 0:
                # initial_st_dev holds the initial logarithmic standard deviation (negative while not set)
                g.initial_st_dev = current_log_stdev

            # 6. Normalize to 0-1 range
            if g.initial_st_dev == 0:
                g.columnar_diversity_coefficient = 0.0
            else:
                # Ratio of current log-spread to initial log-spread
                normalized_div = current_log_stdev / g.initial_st_dev
                g.columnar_diversity_coefficient = max(0.0, min(1.0, normalized_div))