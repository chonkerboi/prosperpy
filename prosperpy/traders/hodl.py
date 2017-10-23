import logging

from .adx import ADXTrader

LOGGER = logging.getLogger(__name__)


class HODLTrader(ADXTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_buy = True

    def trade(self):
        if self.initial_buy:
            self.buy()
            self.initial_buy = False

        super().trade()

    def sell(self):
        LOGGER.info('Not selling because HODL 4 life')
