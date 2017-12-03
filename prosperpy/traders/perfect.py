from .trader import Trader


class PerfectTrader(Trader):
    def initialize(self):
        pass

    def add(self, candle):
        pass

    def trade(self):
        profit = self.feed.candle.close - self.feed.candle.previous.close
        if profit:
            self.liquidity += profit
