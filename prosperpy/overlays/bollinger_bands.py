from . import moving_average
from .. import indicators


class BollingerBands:
    def __init__(self, values, multiplier=2, moving_average_class=moving_average.SimpleMovingAverage):
        self.moving_average_class = moving_average_class
        self.multiplier = multiplier
        self.moving_average = self.moving_average_class(values)
        self.standard_deviation = indicators.StandardDeviation(values)

    def add(self, value):
        self.moving_average.add(value)
        self.standard_deviation.add(value)

    @property
    def upper(self):
        return self.moving_average.value + (self.standard_deviation.value * self.multiplier)

    @property
    def lower(self):
        return self.moving_average.value - (self.standard_deviation.value * self.multiplier)

    @property
    def bandwidth(self):
        return self.upper - self.lower
