'Estimate the construction and maintenance cost of a low voltage distribution system'
# Import custom modules
from np.lib.variable_store import Variable as V
from np.lib import store
import demographics



# Low voltage distribution cost parameters


class LowVoltageLineCostPerMeter(V):

    section = 'distribution'
    option = 'low voltage line cost per meter'
    aliases = ['di_ll_cm']
    default = 10
    units = 'dollars per meter'


class LowVoltageLineLifetime(V):

    section = 'distribution'
    option = 'low voltage line lifetime'
    aliases = ['di_ll_life']
    c = dict(check=store.assertPositive)
    default = 10
    units = 'years'


class LowVoltageLineOperationsAndMaintenanceCostPerYearAsFractionOfLineCost(V):

    section = 'distribution'
    option = 'low voltage line operations and maintenance cost per year as fraction of line cost'
    aliases = ['di_ll_omf']
    default = 0.01


# Low voltage distribution cost derivatives


class LowVoltageLineLength(V):

    section = 'distribution'
    option = 'low voltage line length'
    aliases = ['di_ll_len']
    dependencies = [
        demographics.MeanInterhouseholdDistance,
        demographics.ProjectedHouseholdCount,
    ]
    units = 'meters'

    def compute(self):
        # Load
        meanInterhouseholdDistance = self.get(demographics.MeanInterhouseholdDistance)
        projectedHouseholdCount = self.get(demographics.ProjectedHouseholdCount)
        # Return
        return meanInterhouseholdDistance * (projectedHouseholdCount - 1) if projectedHouseholdCount > 1 else 0


class LowVoltageLineInitialCost(V):

    section = 'distribution'
    option = 'low voltage line initial cost'
    aliases = ['di_ll_ini']
    dependencies = [
        LowVoltageLineLength,
        LowVoltageLineCostPerMeter,
    ]
    units = 'dollars'

    def compute(self):
        return self.get(LowVoltageLineCostPerMeter) * self.get(LowVoltageLineLength)


class LowVoltageLineOperationsAndMaintenanceCostPerYear(V):

    section = 'distribution'
    option = 'low voltage line operations and maintenance cost per year'
    aliases = ['di_ll_om']
    dependencies = [
        LowVoltageLineOperationsAndMaintenanceCostPerYearAsFractionOfLineCost,
        LowVoltageLineCostPerMeter,
        LowVoltageLineLength,
    ]
    units = 'dollars per year'

    def compute(self):
        return self.get(LowVoltageLineOperationsAndMaintenanceCostPerYearAsFractionOfLineCost) * self.get(LowVoltageLineCostPerMeter) * self.get(LowVoltageLineLength)


class LowVoltageLineReplacementCostPerYear(V):

    section = 'distribution'
    option = 'low voltage line replacement cost per year'
    aliases = ['di_ll_rep']
    dependencies = [
        LowVoltageLineInitialCost,
        LowVoltageLineLifetime,
    ]
    units = 'dollars per year'

    def compute(self):
        return self.get(LowVoltageLineInitialCost) / float(self.get(LowVoltageLineLifetime))


class LowVoltageLineRecurringCostPerYear(V):

    section = 'distribution'
    option = 'low voltage line recurring cost per year'
    aliases = ['di_ll_rec']
    dependencies = [
        LowVoltageLineOperationsAndMaintenanceCostPerYear,
        LowVoltageLineReplacementCostPerYear,
    ]
    units = 'dollars per year'

    def compute(self):
        return sum([
            self.get(LowVoltageLineOperationsAndMaintenanceCostPerYear),
            self.get(LowVoltageLineReplacementCostPerYear),
        ])
