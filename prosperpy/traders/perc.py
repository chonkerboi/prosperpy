import decimal
import logging

from .adx import ADXTrader

LOGGER = logging.getLogger(__name__)


class PercentageTrader(ADXTrader):
    def __init__(self, percentage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.percentage = percentage

    def __str__(self):
        return '{}{}<{}>'.format(self.__class__.__name__, self.percentage, str(self.feed))

    def sell(self):
        for position in self.positions:
            profit = position.amount * self.feed.price
            profit -= profit * decimal.Decimal('0.025')

            if position.amount > 0 and profit > position.price * position.amount:
                if position.amount < decimal.Decimal('0.01'):
                    LOGGER.info('{} Liquidating {:.8f} at {:.2f} bought at {:.2f}'.format(
                        self, position.amount, self.feed.price, position.price))
                    self.liquidity += profit
                    self.sells += 1
                    self.volume += position.amount
                    position.amount = decimal.Decimal('0')
                else:
                    profit = profit * self.percentage
                    LOGGER.info('{} Selling {:.8f} at {:.2f} bought at {:.2f}'.format(
                        self, position.amount, self.feed.price, position.price))
                    self.liquidity += profit
                    position.amount *= decimal.Decimal('1') - self.percentage
                    position.price = self.feed.price
                    self.volume += position.amount
                    self.sells += 1
                self.summary()

        self.clean_positions()
