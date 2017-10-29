import decimal
import collections
import logging
import traceback

import sklearn.ensemble
import sklearn.linear_model
import numpy

import prosperpy

from .trader import Trader

LOGGER = logging.getLogger(__name__)


class ForestTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = collections.deque()
        self.error_threshold = decimal.Decimal('0.4')
        self.n_predictions = 10
        self.history = collections.deque(maxlen=2)
        self.model = None

    @property
    def prediction(self):
        return self.history[-1]

    @property
    def error(self):
        return sum(self.errors) / len(self.errors)

    def initialize(self):
        self.errors = collections.deque(maxlen=self.feed.candles.maxlen)

    def add(self, candle):
        try:
            self.fit()
            self.predict(candle)
        except Exception as ex:
            LOGGER.error('%s: %s', ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())

    def fit(self):
        self.model = sklearn.ensemble.RandomForestRegressor()
        price_deltas = numpy.diff([item.price for item in self.feed.candles]).tolist()
        input_variables = []
        output_variables = []

        for index in range(0, len(price_deltas) - self.feed.period):
            input_variables.append(price_deltas[index:index+self.feed.period])
            output_variables.append(price_deltas[index+self.feed.period])

        self.model.fit(input_variables, output_variables)

    def predict(self, candle):
        predictions = []
        prices = [item.price for item in list(self.feed.candles)[-self.feed.period - 1:]]
        price_deltas = numpy.diff(prices).tolist()
        previous = candle
        for _ in range(0, self.n_predictions):
            delta = decimal.Decimal(str(self.model.predict([price_deltas])[0]))
            prediction = prosperpy.Candle(
                timestamp=previous.timestamp+self.feed.granularity, price=candle.price+delta, previous=previous)
            predictions.append(prediction)
            previous = predictions[-1]
            prices = prices[1:len(prices)] + [prediction.price]
            price_deltas = numpy.diff(prices).tolist()
        self.history.append(predictions)
        LOGGER.info('%s knows about %s predictions', self, len(predictions))
        LOGGER.debug('%s predictions are %s', self, predictions)

    def trade(self):
        self.summary()

        try:
            prediction = self.history[-2][0]
            if prediction.price >= self.feed.price:
                trend = prosperpy.candle.Trend.UP
            else:
                trend = prosperpy.candle.Trend.DOWN

            if prediction.trend == trend:
                error = decimal.Decimal('0')  # 0% error
            else:
                error = decimal.Decimal('1')  # 100% error

            #error = abs((self.history[-2][0].price - self.feed.price) / self.feed.price)
            accuracy = decimal.Decimal('100') - error * decimal.Decimal('100')
            LOGGER.info('{} current accuracy is {:.4f}%'.format(self, accuracy))
            self.errors.append(error)
            accuracy = decimal.Decimal('100') - self.error * decimal.Decimal('100')
            LOGGER.info('{} average accuracy is {:.4f}%'.format(self, accuracy))
        except (IndexError, decimal.InvalidOperation, decimal.DivisionByZero) as ex:
            LOGGER.error('%s: %s', ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())

        try:
            if self.error > self.error_threshold:
                LOGGER.warning("{} error is '{:.4f}' but error threshold is '{:.4f}'".format(
                    self, self.error, self.error_threshold))
                return
        except (ZeroDivisionError, decimal.InvalidOperation, decimal.DivisionByZero) as ex:
            LOGGER.error('%s: %s', ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())
            return

        try:
            predictions = self.history[-1]
            candle = predictions[-1]
            LOGGER.info('{} prediction is {:.4f} and current price is {:.4f}'.format(
                self, candle.price, self.feed.price))

            if candle.price >= self.feed.price:
                self.buy()
            else:
                self.sell()
        except IndexError as ex:
            LOGGER.error('%s: %s', ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())
