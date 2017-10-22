import json
import decimal
import collections
import asyncio
import logging
import itertools

import prosperpy.gdax.websocket

LOGGER = logging.getLogger(__name__)


class GDAXFeed:
    def __init__(self, product, granularity, candles):
        self.product = product
        self.granularity = granularity
        self.connection = prosperpy.gdax.WebsocketConnection(self.product, self.granularity)
        self.price = decimal.Decimal('0')
        self.candles = collections.deque(iterable=candles, maxlen=len(candles) * 10)
        self.traders = []

    def __str__(self):
        return '{}<{}>'.format(self.__class__.__name__, self.product)

    def register_trader(self, trader):
        self.traders.append(trader)

    async def __aenter__(self):
        await self.connection.connect()
        return self

    async def __aexit__(self, *_):
        await self.connection.close()

    async def __call__(self):
        return await self.run()

    @property
    def candle(self):
        return self.candles[-1]

    def consume(self, message):
        try:
            self.price = decimal.Decimal(json.loads(message)['price'])
        except KeyError:
            return

        if self.price > self.candle.high:
            self.candle.high = self.price

        if self.price < self.candle.low:
            self.candle.low = self.price

        if self.candle.open.is_nan():
            self.candle.open = self.price

        # TODO: write message to disk

    def is_trade_ready(self):
        """Make sure the current candle was populated with data.

        Returns:
            bool: True if the candle is ready for trade, False otherwise.
        """
        return (self.candle.low != decimal.Decimal('+infinity')
                and self.candle.high != decimal.Decimal('-infinity')
                and not self.candle.open.is_nan())

    def simple_moving_average(self, period):
        length = len(self.candles)
        prices = [candle.close for candle in collections.deque(itertools.islice(self.candles, length - period, length))]
        return sum(prices) / period

    def new_candle(self):
        """Append a new candle to the tracked candles."""
        self.candles.append(prosperpy.Candle(previous=self.candle))

    @prosperpy.error.fatal
    async def trade(self):
        while True:
            if self.is_trade_ready():
                self.candle.close = self.price

                for trader in self.traders:
                    trader.trade(self.candle)

                self.new_candle()

            await asyncio.sleep(self.granularity)

    @prosperpy.error.fatal
    async def run(self):
        self.new_candle()
        prosperpy.engine.call_later(self.granularity, prosperpy.engine.create_task, self.trade())

        async with self:
            while True:
                self.consume(await self.connection.recv())
