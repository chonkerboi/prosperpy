import collections

import prosperpy

from .trader import Trader


class HMATrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hma1 = None
        self.hma2 = None
        self.rsi = None
        self.dpp = None
        self.trend = None
        self.values = None

    def initialize(self):
        prices = [candle.close for candle in self.feed.candles]
        self.hma1 = prosperpy.overlays.HullMovingAverage(prices)
        self.hma2 = prosperpy.overlays.HullMovingAverage(self.feed.candles, moving_average_class=prosperpy.overlays.VolumeWeightedMovingAverage)
        self.trend = self.feed.candle.trend
        self.values = collections.deque(maxlen=len(self.feed.candles)+1)

    def add(self, candle):
        self.values.append(self.hma2.value)
        self.hma1.add(candle.close)
        self.hma2.add(candle)

        try:
            self.dpp.add(candle)
            previous = prosperpy.Candle(close=self.values[-1])
            candle = prosperpy.Candle(close=self.hma2.value, previous=previous)
            self.rsi.add(candle)
        except AttributeError:
            if len(self.values) == self.values.maxlen:
                for value in self.values:
                    if value is None:
                        return

                self.dpp = prosperpy.overlays.DemarkPivotPoints(list(self.feed.candles)[-self.hma2.full.period:])
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
        if self.hma2.value is None or self.values[-1] is None or self.rsi is None or self.dpp is None:
            return

        if self.hma2.value > self.values[-1] and self.trend < 0:
            self.buy()
            self.trend = self.hma2.value - self.values[-1]
        elif self.hma2.value < self.values[-1] and self.trend > 0:
            self.sell()
            self.trend = self.hma2.value - self.values[-1]

        '''
        if self.hma2.value > self.values[-1] and self.values[-1] < self.values[-2]:
            self.buy()
        elif self.hma2.value < self.values[-1] and self.values[-1] > self.values[-2]:
            self.sell()
        '''

        '''
        if self.hma1.value > self.values[-1] and self.trend < 0 and self.rsi.value < 20:
            self.buy()
            self.trend = self.hma1.value - self.values[-1]
        elif self.hma1.value < self.values[-1] and self.trend > 0 and self.rsi.value > 80:
            self.sell()
            self.trend = self.hma1.value - self.values[-1]
        '''
