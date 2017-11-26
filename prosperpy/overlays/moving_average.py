import collections
import decimal


class SimpleMovingAverage:
    def __init__(self, values):
        self.period = len(values)
        self.values = collections.deque(values, maxlen=self.period)
        self.value = self.simple_moving_average()

    def simple_moving_average(self):
        return sum(self.values) / len(self.values)

    def add(self, value):
        self.values.append(value)
        self.value = self.simple_moving_average()

    def __call__(self, value):
        self.add(value)
        return self.value


class ExponentialMovingAverage(SimpleMovingAverage):
    def __init__(self, values):
        super().__init__(values)
        self.multiplier = decimal.Decimal(2 / (self.period + 1))

    def add(self, value):
        super().add(value)
        self.value = ((value - self.value) * self.multiplier) + self.value
