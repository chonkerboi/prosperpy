import decimal

from . import volatility


class AverageDirectionalMovement:
    def __init__(self, candles, true_range=None):
        self.period, self.value = self._process_candles(candles)
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

    def _process_candles(self, candles):
        candles = candles[1:]  # The root candle has not previous candle to use
        data = [self.directional_movement(candle) for candle in candles]
        return len(candles), sum(data)

    def smooth(self,  candle):
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


class TrueRange(volatility.AverageTrueRange):
    @staticmethod
    def _process_candles(candles):
        candles = candles[1:]  # The root candle has not previous candle to use
        data = [volatility.true_range(candle) for candle in candles]
        return len(candles), sum(data)

    def smooth(self,  candle):
        return self.value - (self.value / self.period) + volatility.true_range(candle)


class DirectionalIndex:
    def __init__(self, candles):
        self.true_range = TrueRange(candles)
        self.minus = MinusDirectionalMovement(candles, self.true_range)
        self.plus = PlusDirectionalMovement(candles, self.true_range)

    def add(self, candle):
        """Add a new candle to the index.

        It is important to add the the true range before the directional movements because the DM uses TR internally.
        Args:
            candle (autotrade.Candle): the candle to add.
        """
        self.true_range.add(candle)
        self.minus.add(candle)
        self.plus.add(candle)

    @property
    def value(self):
        di_diff = abs(self.plus.indicator - self.minus.indicator)
        di_sum = self.plus.indicator + self.minus.indicator
        return 100 * (di_diff / di_sum)


class AverageDirectionalIndex(object):
    def __init__(self, candles):
        self.period = int(len(candles) / 2)  # 'int' casting rounds down
        # Use period + 1 because the first candle is the root candle
        self.index = DirectionalIndex(candles[0:self.period+1])
        self.value = self._process_candles(candles[self.period+1:])

    def _process_candles(self, candles):
        data = []
        for candle in candles:
            self.index.add(candle)
            data.append(self.index.value)
        return sum(data) / len(data)

    def smooth(self):
        return ((self.value * (self.period - 1)) + self.index.value) / self.period

    def add(self, candle):
        self.index.add(candle)
        self.value = self.smooth()
