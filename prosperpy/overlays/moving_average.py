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


class HullMovingAverage(SimpleMovingAverage):
    def __init__(self, values):
        super().__init__(values)
        self.period = int(math.sqrt(self.period))
        self.half = WeightedMovingAverage(list(self.values)[:int(len(self.values) / 2)])
        self.full = WeightedMovingAverage(self.values)
        self.values = collections.deque(maxlen=self.period)
        self.wma = None

    @property
    def value(self):
        try:
            return self.wma.value
        except AttributeError:
            return None

    def add(self, value):
        self.half.add(value)
        self.full.add(value)
        value = (self.half.value * 2) - self.full.value

        try:
            self.wma.add(value)
            return
        except AttributeError:
            self.values.append(value)
            if len(self.values) == self.values.maxlen:
                self.wma = WeightedMovingAverage(self.values)


if __name__ == '__main__':
    prices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 8, 7, 6, 7, 8, 9, 10, 11, 12, 13, 14, 13, 12, 11, 10, 9, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    hma = HullMovingAverage(prices[:20])

    print(hma.value)
    for price in prices[20:]:
        print(price, hma(price))
