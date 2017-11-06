from .trader import Trader


class PerfectTrader(Trader):
    def initialize(self):
        pass

    def add(self, candle):
        pass

    def trade(self):
        profit = self.feed.candle.price - self.feed.candle.previous.price
        if profit:
            self.liquidity += profit
