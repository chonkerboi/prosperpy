import collections
import decimal
import math


class SimpleMovingAverage:
    def __init__(self, values):
        self.period = len(values)
        self.values = collections.deque(values, maxlen=self.period)

    @property
    def value(self):
        return sum(self.values) / len(self.values)

    def add(self, value):
        self.values.append(value)

    def __call__(self, value):
        self.add(value)
        return self.value


class ExponentialMovingAverage(SimpleMovingAverage):
    def __init__(self, values):
        super().__init__(values)
        self.multiplier = decimal.Decimal(2 / (self.period + 1))
        self._value = super().value

    @property
    def value(self):
        return self._value

    def add(self, value):
        self.values.append(value)
        self._value = ((value - self.value) * self.multiplier) + self.value
        return self.value


class WeightedMovingAverage(SimpleMovingAverage):
    def __init__(self, values):
        super().__init__(values)
        self.denominator = decimal.Decimal(sum(range(1, self.period+1)))

    @property
    def value(self):
        return sum([value * ((index + 1) / self.denominator) for index, value in enumerate(self.values)])


class VolumeWeightedMovingAverage(WeightedMovingAverage):
    def __init__(self, candles):
        super().__init__(candles)
        self.volume = self.sum_volumes()

    def sum_volumes(self):
        return sum([candle.volume for candle in self.values])

    def add(self, value):
        super().add(value)
        self.volume = self.sum_volumes()

    def weight(self, candle, index):
        return (((index + 1) / self.denominator) + (candle.volume / self.volume)) / 2

    @property
    def value(self):
        return sum([candle.close * self.weight(candle, index) for index, candle in enumerate(self.values)])


class HullMovingAverage(SimpleMovingAverage):
    def __init__(self, values, moving_average_class=WeightedMovingAverage):
        super().__init__(values)
        self.period = int(math.sqrt(self.period))
        self.moving_average_class = moving_average_class
        self.half = self.moving_average_class(list(self.values)[:int(len(self.values) / 2)])
        self.full = self.moving_average_class(self.values)
        self.values = collections.deque(maxlen=self.period)
        self.moving_average = None

    @property
    def value(self):
        try:
            return self.moving_average.value
        except AttributeError:
            return None

    def add(self, value):
        self.half.add(value)
        self.full.add(value)
        value = (self.half.value * 2) - self.full.value

        try:
            self.moving_average.add(value)
            return
        except AttributeError:
            self.values.append(value)
            if len(self.values) == self.values.maxlen:
                self.moving_average = WeightedMovingAverage(self.values)
