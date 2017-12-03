import collections

import prosperpy

from .trader import Trader


class HMATrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hma = None
        self.rsi = None
        self.trend = None
        self.values = None

    def initialize(self):
        prices = [candle.close for candle in self.feed.candles]
        self.hma = prosperpy.overlays.HullMovingAverage(prices)
        self.trend = self.feed.candle.trend
        self.values = collections.deque(maxlen=len(self.feed.candles)+1)

    def add(self, candle):
        self.values.append(self.hma.value)
        self.hma.add(candle.close)

        previous = prosperpy.Candle(close=self.values[-1])
        candle = prosperpy.Candle(close=self.hma.value, previous=previous)
        try:
            self.rsi.add(candle)
        except AttributeError:
            if len(self.values) == self.values.maxlen:
                for value in self.values:
                    if value is None:
                        return

                candles = []
                for index, value in enumerate(list(self.values)[1:]):
                    try:
                        previous = prosperpy.Candle(close=self.values[index-1])
                    except IndexError:
                        previous = prosperpy.Candle(close=self.values[0])
                    candle = prosperpy.Candle(close=value, previous=previous)
                    candles.append(candle)
                self.rsi = prosperpy.indicators.RelativeStrengthIndex(candles)

    def trade(self):
        if self.hma.value is None or self.values[-1] is None or self.rsi is None:
            return

        if self.hma.value > self.values[-1] and self.trend < 0 and self.rsi.value < 20:
            self.buy()
            self.trend = self.hma.value - self.values[-1]
        elif self.hma.value < self.values[-1] and self.trend > 0 and self.rsi.value > 80:
            self.sell()
            self.trend = self.hma.value - self.values[-1]
