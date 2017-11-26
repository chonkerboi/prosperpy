import logging

from .trader import Trader

LOGGER = logging.getLogger(__name__)


class HODLTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_buy = True

    def initialize(self):
        pass

    def add(self, candle):
        pass

    def trade(self):
        if self.initial_buy:
            self.buy()
            self.initial_buy = False

    def sell(self):
        LOGGER.info('Not selling because HODL 4 life')
