from .trader import Trader


class HODLTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.should_buy = True

    def trade(self, candle):
        if self.should_buy:
            self.buy()
            self.should_buy = False
