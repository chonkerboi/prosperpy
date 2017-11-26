import prosperpy

from .trader import Trader


class RSITrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rsi = None

    def initialize(self):
        self.rsi = prosperpy.indicators.RelativeStrengthIndex(list(self.feed.candles))

    def add(self, candle):
        self.rsi.add(candle)

    def trade(self):
        if self.rsi.value > 70:
            self.sell()
        elif self.rsi.value < 30:
            self.buy()
