import decimal
import collections
import logging

import sklearn.ensemble
import numpy

from .trader import Trader

LOGGER = logging.getLogger(__name__)


class ForestTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = collections.deque()
        self.error_threshold = decimal.Decimal('0.01')
        self.predicted_price = decimal.Decimal('0')
        self.lookforward = 10
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
        diffs = numpy.diff([c.price for c in self.feed.candles]).tolist()
        input_variables = []
        output_variables = []

        lookback = int(len(self.feed.candles) / 4)
        for index in range(0, len(diffs) - lookback):
            input_variables.append(diffs[index:index+lookback])
            output_variables.append(diffs[index+lookback])

        model.fit(input_variables, output_variables)

        prices = [c.price for c in list(self.feed.candles)[-lookback - 1:]]
        diffs = numpy.diff(prices).tolist()
        for _ in range(0, self.lookforward):
            prediction = model.predict([diffs])
            self.predicted_price = candle.price + decimal.Decimal(str(prediction[0]))
            prices = prices[1:len(prices)] + [self.predicted_price]
            diffs = numpy.diff(prices).tolist()

    def trade(self):
        try:
            price = list(self.feed.candles)[-self.lookforward].price
            self.errors.append(abs((self.predicted_price - price) / price))
            LOGGER.info('{} Error: {:.4f}%'.format(self, self.error*100))
        except (decimal.InvalidOperation, decimal.DivisionByZero):
            pass

        try:
            if self.error > self.error_threshold:
                LOGGER.warning("{} Error '{:.4f}' with threshold '{:.4f}'".format(self, self.error, self.error_threshold))
                return
        except (ZeroDivisionError, decimal.InvalidOperation, decimal.DivisionByZero):
            return

        if self.predicted_price - self.feed.price > 0:
            self.buy()
        else:
            self.sell()
