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
                # 3-4. Standard deviation relative to the range of the decision variable
                current_log_stdev = stat.stdev(values) / (g.max_value - g.min_value)
            else:
                # 3. Logarithmic Transformation
                # Shift values by min_value and add 1.0 to ensure values are > 0 for log
                # This measures variety relative to the decision variable's search space range
                log_values = []
                for v in values:
                    # Distance from min_value + 1.0 (to avoid log(0))
                    shifted_v = (v - g.min_value) + 1.0
                    log_values.append(math.log(shifted_v))

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