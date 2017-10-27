import decimal
import collections
import logging

import sklearn.ensemble
import numpy

import prosperpy

from .trader import Trader

LOGGER = logging.getLogger(__name__)


class ForestTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = collections.deque()
        self.error_threshold = decimal.Decimal('0.01')
        self.predicted_price = decimal.Decimal('0')
        self.predictions = []

    @property
    def prediction(self):
        return self.predictions[-1]

    @property
    def error(self):
        return sum(self.errors) / len(self.errors)

    def initialize(self):
        self.errors = collections.deque(maxlen=self.feed.candles.maxlen)

    def add(self, candle):
        model = sklearn.ensemble.RandomForestRegressor()
        price_deltas = numpy.diff([item.price for item in self.feed.candles]).tolist()
        input_variables = []
        output_variables = []

        lookback = int(len(self.feed.candles) / 4)
        for index in range(0, len(price_deltas) - lookback):
            input_variables.append(price_deltas[index:index+lookback])
            output_variables.append(price_deltas[index+lookback])

        model.fit(input_variables, output_variables)

        self.predictions = []
        prices = [item.price for item in list(self.feed.candles)[-lookback - 1:]]
        price_deltas = numpy.diff(prices).tolist()
        previous = candle
        for _ in range(0, int(lookback / 4)):
            delta = decimal.Decimal(str(model.predict([price_deltas])[0]))
            prediction = prosperpy.Candle(timestamp=previous.timestamp+self.feed.granularity, price=candle.price+delta,
                                          previous=previous)
            self.predictions.append(prediction)
            previous = self.prediction
            prices = prices[1:len(prices)] + [self.prediction.price]
            price_deltas = numpy.diff(prices).tolist()
        LOGGER.info('%s predictions are %s', self, self.predictions)

    def trade(self):
        try:
            candle = self.predictions[0]
            self.errors.append(abs((candle.price - candle.previous.price) / candle.previous.price))
            accuracy = decimal.Decimal('100') - self.error * decimal.Decimal('100')
            LOGGER.info('{} accuracy {:.4f}%'.format(self, accuracy))
            LOGGER.info('%s knows about %s predictions', self, len(self.predictions))
        except (IndexError, decimal.InvalidOperation, decimal.DivisionByZero):
            pass

        try:
            if self.error > self.error_threshold:
                LOGGER.warning("{} Error '{:.4f}' with threshold '{:.4f}'".format(self, self.error, self.error_threshold))
                return
        except (ZeroDivisionError, decimal.InvalidOperation, decimal.DivisionByZero):
            return

        if self.prediction.price - self.feed.price > 0:
            self.buy()
        else:
            self.sell()
