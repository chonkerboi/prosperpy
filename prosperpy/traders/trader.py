import decimal
import logging

import prosperpy

LOGGER = logging.getLogger(__name__)


class Trader:
    def __init__(self, product, feed, api, investment=decimal.Decimal('100.0'), recurring=decimal.Decimal('0.0')):
        self.product = product
        self.feed = feed
        self.api = api
        self.investment = investment
        self.recurring = recurring
        self.liquidity = self.investment
        self.buys = 0
        self.sells = 0
        self.volume = decimal.Decimal('0.0')
        self.positions = []
        self.fee = decimal.Decimal('0.0025')
        #self.fee = decimal.Decimal('0.0')
        self.callback = None

    def initialize(self):
        raise NotImplementedError()

    def clean_positions(self):
        self.positions = [position for position in self.positions if position.amount > 0]

    def return_on_investment(self):
        liquidity = self.liquidity + sum([self.feed.price * position.amount for position in self.positions])
        return liquidity * 100 / self.investment

    def __str__(self):
        return '{}<{}>'.format(self.__class__.__name__, str(self.feed))

    def buy(self):
        self.liquidity += self.recurring
        self.investment += self.recurring

        if self.liquidity:
            amount = self.liquidity / self.feed.price
            amount -= amount * self.fee
            position = prosperpy.Position(self.product, amount, self.feed.price)
            self.volume += position.amount
            LOGGER.info('{} Buying {:.8f} at {:.2f}'.format(self, position.amount, self.feed.price))
            self.liquidity = decimal.Decimal('0.0')
            self.buys += 1
            self.positions.append(position)
            try:
                self.callback('buy', self.feed.price)
            except Exception:
                pass
        else:
            LOGGER.info('Not enough liquidity to act on buy signal')

        self.summary()

    def sell(self):
        for position in self.positions:
            profit = position.amount * self.feed.price
            profit -= profit * self.fee

            if position.amount > 0 and profit > position.price * position.amount:
                LOGGER.info('{} Selling {:.8f} at {:.2f} bought at {:.2f}'.format(
                    self, position.amount, self.feed.price, position.price))
                self.liquidity += profit
                self.sells += 1
                self.volume += position.amount
                position.amount = decimal.Decimal('0')
                try:
                    self.callback('sell', self.feed.price)
                except Exception:
                    pass
            else:
                LOGGER.info("Not selling at a loss '%s < %s'", profit, position.price * position.amount)

        self.summary()
        self.clean_positions()

    def summary(self):
        LOGGER.info('{} {:.2f}% ({},{},{:.2f})'.format(
            self, self.return_on_investment(), self.buys, self.sells, self.volume))

    def add(self, candle):
        raise NotImplementedError()

    def trade(self):
        raise NotImplementedError()
