from .adx import ADXTrader


class SMATrader(ADXTrader):
    def trade(self, candle):
        self.adx.add(candle)

        if self.adx.value > 20:
            return

        big_sma = self.feed.simple_moving_average(int(self.adx.period * 2))
        small_sma = self.feed.simple_moving_average(int(self.adx.period / 2))

        if self.above and big_sma > small_sma:
            self.above = False
            self.sell()

        elif not self.above and small_sma > big_sma:
            self.above = True
            self.buy()
