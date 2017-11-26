import decimal

from . import average_true_range


class AverageDirectionalMovement:
    def __init__(self, candles, true_range=None):
        self.period = len(candles)
        self.value = sum([self.directional_movement(candle) for candle in candles])
        self.true_range = true_range

    @staticmethod
    def _directional_movement(candle):
        plus = candle.high - candle.previous.high
        if plus < 0:
            plus = decimal.Decimal('0')

        minus = candle.previous.low - candle.low
        if minus < 0:
            minus = decimal.Decimal('0')

        return minus, plus

    @classmethod
    def directional_movement(cls, candle):
        raise NotImplementedError()

    def smooth(self, candle):
        return self.value - (self.value / self.period) + self.directional_movement(candle)

    def add(self, candle):
        self.value = self.smooth(candle)

    @property
    def indicator(self):
        return 100 * (self.value / self.true_range.value)


class MinusDirectionalMovement(AverageDirectionalMovement):
    @classmethod
    def directional_movement(cls, candle):
        minus, plus = cls._directional_movement(candle)

        if minus > plus:
            return minus
        else:
            return decimal.Decimal('0')


class PlusDirectionalMovement(AverageDirectionalMovement):
    @classmethod
    def directional_movement(cls, candle):
        minus, plus = cls._directional_movement(candle)

        if plus > minus:
            return plus
        else:
            return decimal.Decimal('0')


class TrueRange(average_true_range.AverageTrueRange):
    def __init__(self, candles):
        super(TrueRange, self).__init__(candles)
        self.period = len(candles)
        data = [average_true_range.true_range(candle) for candle in candles]
        self.value = sum(data)

    def smooth(self, candle):
        return self.value - (self.value / self.period) + average_true_range.true_range(candle)


class DirectionalIndex:
    def __init__(self, candles):
        self.true_range = TrueRange(candles)
        self.minus = MinusDirectionalMovement(candles, self.true_range)
        self.plus = PlusDirectionalMovement(candles, self.true_range)

    def add(self, candle):
        """Add a new candle to the index.

        It is important to add the the true range before the directional movements because the DM uses TR internally.
        Args:
            candle (prosperpy.Candle): the candle to add.
        """
        self.true_range.add(candle)
        self.minus.add(candle)
        self.plus.add(candle)

    @property
    def value(self):
        return 100 * (abs(self.plus.indicator - self.minus.indicator) / self.plus.indicator + self.minus.indicator)


class AverageDirectionalIndex(object):
    def __init__(self, candles):
        self.period = int(len(candles) / 2)
        self.index = DirectionalIndex(candles[:self.period])

        data = [self.index.value]
        for candle in candles[self.period:]:
            self.index.add(candle)
            data.append(self.index.value)
        self.value = sum(data) / len(data)

    def smooth(self):
        return ((self.value * (self.period - 1)) + self.index.value) / self.period

    def add(self, candle):
        self.index.add(candle)
        self.value = self.smooth()
