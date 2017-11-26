import collections
import decimal

from ..indicators import average_true_range


class ChandelierExitLong:
    def __init__(self, candles, multiplier=decimal.Decimal('3')):
        self.candles = collections.deque(candles, maxlen=len(candles))
        self.multiplier = multiplier
        self.period = len(candles)
        self.atr = average_true_range.AverageTrueRange(candles)
        self.value = self.calculate()

    def add(self, candle):
        self.candles.append(candle)
        self.atr.add(candle)
        self.value = self.calculate()

    def calculate(self):
        candle = max(self.candles, key=lambda item: item.high)
        return candle.high - self.atr.value * self.multiplier


class ChandelierExitShort(ChandelierExitLong):
    def calculate(self):
        candle = min(self.candles, key=lambda item: item.low)
        return candle.low + self.atr.value * self.multiplier
