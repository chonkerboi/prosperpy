import math
import decimal

from .. import overlays


class StandardDeviation(overlays.SimpleMovingAverage):
    @property
    def value(self):
        average = super().value
        return decimal.Decimal(math.sqrt(sum([(value - average)**2 for value in self.values]) / len(self.values)))
