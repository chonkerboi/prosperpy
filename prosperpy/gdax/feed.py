import json
import decimal
import collections
import asyncio
import logging
import itertools
import time

import prosperpy

LOGGER = logging.getLogger(__name__)


class GDAXFeed:
    def __init__(self, product, period, granularity):
        self.product = product
        self.period = period
        self.granularity = granularity
        self.ticker = prosperpy.gdax.Ticker(self.product, self.granularity)
        self.ticker.on_connection.append(self.load_candles)
        self.price = decimal.Decimal('0')
        self.candles = collections.deque()
        self.traders = []

    def __str__(self):
        return '{}<{}, period={}, granularity={}>'.format(
            self.__class__.__name__, self.product, self.period, self.granularity)

    async def __aenter__(self):
        await self.ticker.connect()
        return self

    async def __aexit__(self, *_):
        await self.ticker.close()

    async def __call__(self):
        return await self.run()

    @property
    def candle(self):
        return self.candles[-1]

    def consume(self, message):
        try:
            data = json.loads(message)
            self.price = decimal.Decimal(data['price'])
            volume = decimal.Decimal(data['last_size'])
        except KeyError:
            return

        if self.candle.timestamp is None:
            self.candle.timestamp = time.time()

        if self.price > self.candle.high:
            self.candle.high = self.price

        if self.price < self.candle.low:
            self.candle.low = self.price

        if self.candle.open.is_nan():
            self.candle.open = self.price

        self.candle.volume += volume

    def is_candle_valid(self):
        """Make sure the current candle was populated with data.

        Returns:
            bool: True if the candle is valid and ready for trade, False otherwise.
        """
        return (self.candle.timestamp is not None
                and self.candle.low != decimal.Decimal('+infinity')
                and self.candle.high != decimal.Decimal('-infinity')
                and not self.candle.open.is_nan()
                and self.candle.volume > 0)

    def add_candle(self, candle=None):
        """Feed current candle to the traders and then add a new candle to the tracked candles.

        Args:
            candle (prosperpy.Candle, optional): the candle to add, if None a new candle will be created.
        """
        LOGGER.info('Adding %s', self.candle)
        for trader in self.traders:
            trader.add(self.candle)

        if candle is None:
            candle = prosperpy.Candle()

        if candle.previous is None:
            candle.previous = self.candle

        self.candles.append(candle)

    @prosperpy.error.fatal
    async def trade(self):
        while True:
            if self.is_candle_valid():
                self.candle.close = self.price
                self.add_candle()

                for trader in self.traders:
                    trader.trade()

            await asyncio.sleep(self.granularity)

    def load_candles(self):
        factor = 10
        candles = prosperpy.gdax.api.get_candles(self.period*factor, self.granularity, self.product)
        self.candles = collections.deque(iterable=candles[0:self.period], maxlen=self.period*factor)

        for trader in self.traders:
            trader.initialize()

        for candle in candles[self.period:]:
            self.add_candle(candle=candle)

    @prosperpy.error.fatal
    async def run(self):
        async with self:
            self.add_candle()
            prosperpy.engine.call_later(self.granularity, prosperpy.engine.create_task, self.trade())

            while True:
                self.consume(await self.ticker.recv())
