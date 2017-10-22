import autotrade

from .trader import Trader


class ADXTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adx = autotrade.wilder.AverageDirectionalIndex(list(self.feed.candles))
        self.above = True

    def trade(self, candle):
        self.adx.add(candle)

        if self.adx.value > 20:
            return

        if self.above and self.adx.index.minus.indicator > self.adx.index.plus.indicator:
            self.above = False
            self.sell()

        elif not self.above and self.adx.index.plus.indicator > self.adx.index.minus.indicator:
            self.above = True
            self.buy()
