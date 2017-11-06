import decimal
import collections
import logging
import traceback
import itertools

import prosperpy

from .trader import Trader

LOGGER = logging.getLogger(__name__)


class RegressorTrader(Trader):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.price_errors = collections.deque()
        self.trend_errors = collections.deque()
        self.trend_error_threshold = decimal.Decimal('0.4')
        self.n_predictions = 10
        self.history = collections.deque(maxlen=self.n_predictions)
        self.errors = []
        self.regressor = None
        self.sma_periods = [5, 10]

    def __str__(self):
        return '{}<{} model={}>'.format(self.__class__.__name__, str(self.feed), self.model.__name__)

    @property
    def trend_error(self):
        return sum(self.trend_errors) / len(self.trend_errors)

    @property
    def price_error(self):
        return sum(self.price_errors) / len(self.price_errors)

    def initialize(self):
        self.errors = [collections.deque(maxlen=self.feed.candles.maxlen) for _ in range(self.history.maxlen)]
        self.trend_errors = collections.deque(maxlen=self.feed.candles.maxlen)
        self.price_errors = collections.deque(maxlen=self.feed.candles.maxlen)

    def add(self, candle):
        try:
            self.fit()
            self.predict(candle)
        except Exception as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())

    def fit(self):
        self.regressor = self.model(n_estimators=10)

        candles = list(self.feed.candles)[-self.feed.period:]
        input_variables = []
        output_variables = []

        for index, candle in enumerate(candles):
            input_var = [candle.price, candle.volume]
            '''
            if len(self.feed.candles) > self.feed.period + max(self.sma_periods):
                # We have enough candles to compute simple moving averages
                for period in self.sma_periods:
                    sma_candles = list(self.feed.candles)[-self.feed.period-period+index:-self.feed.period+index]
                    data = [c.price for c in sma_candles]
                    input_var.append(sum(data)/len(data))
            '''

            input_variables.append(input_var)

            try:
                output_variables.append([candle.previous.price, candle.previous.volume])
            except AttributeError:
                output_variables.append([decimal.Decimal('0'), decimal.Decimal('0')])

        self.regressor.fit(input_variables, output_variables)

    def predict(self, candle):
        candles = []
        for _ in range(0, self.n_predictions):
            data = [candle.price, candle.volume]
            '''
            if len(self.feed.candles) > self.feed.period + max(self.sma_periods):
                for period in self.sma_periods:
                    sma_data = [c.price for c in list(self.feed.candles)[-self.feed.period-period-1:]]
                    sma_data.append(candle.price)
                    sma = sum(sma_data) / len(sma_data)
                    data.append(sma)
            '''

            price, volume = map(decimal.Decimal, self.regressor.predict([data])[0])
            timestamp = candle.timestamp + self.feed.granularity
            candle = prosperpy.Candle(timestamp=timestamp, price=price, volume=volume, previous=candle)
            candles.append(candle)

        self.history.append(candles)
        LOGGER.debug('%s predictions are %s', self, candles)

    def compute_accuracy(self):
        if len(self.history) != self.history.maxlen:
            return

        try:
            predictions = self.history[0]
            for index, prediction in enumerate(predictions):
                price = self.feed.candles[-len(predictions)+index].price
                error = abs((prediction.price - price) / price)
                self.errors[index].append(error)
                accuracy = decimal.Decimal('100') - error * decimal.Decimal('100')
                error_avg = sum(self.errors[index]) / len(self.errors[index])
                accuracy_avg = decimal.Decimal('100') - error_avg * decimal.Decimal('100')
                LOGGER.debug('{} accuracy[{}] is {:.4f}% (avg: {:.4f}%)'.format(self, index, accuracy, accuracy_avg))

            prediction = self.history[-2][0]
            if prediction.price >= self.feed.price:
                trend = prosperpy.candle.Trend.UP
            else:
                trend = prosperpy.candle.Trend.DOWN

            if prediction.trend == trend:
                trend_error = decimal.Decimal('0')  # 0% error
            else:
                trend_error = decimal.Decimal('1')  # 100% error

            self.trend_errors.append(trend_error)
            accuracy = decimal.Decimal('100') - trend_error * decimal.Decimal('100')
            accuracy_avg = decimal.Decimal('100') - self.trend_error * decimal.Decimal('100')
            LOGGER.info('{} trend accuracy is {:.4f}% (avg: {:.4f}%)'.format(self, accuracy, accuracy_avg))

            price_error = abs((prediction.price - self.feed.price) / self.feed.price)
            self.price_errors.append(price_error)
            accuracy = decimal.Decimal('100') - price_error * decimal.Decimal('100')
            accuracy_avg = decimal.Decimal('100') - self.price_error * decimal.Decimal('100')
            LOGGER.info('{} accuracy is {:.4f}% (avg: {:.4f}%)'.format(self, accuracy, accuracy_avg))

        except (IndexError, decimal.InvalidOperation, decimal.DivisionByZero) as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())

    def check_accuracy(self):
        try:
            if self.trend_error > self.trend_error_threshold:
                LOGGER.warning("{} trend error is '{:.4f}' but trend error threshold is '{:.4f}'".format(
                    self, self.trend_error, self.trend_error_threshold))
                return False
        except (ZeroDivisionError, decimal.InvalidOperation, decimal.DivisionByZero) as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())
            return False
        return True

    def trade(self):
        self.compute_accuracy()
        if not self.check_accuracy():
            return

        '''
        prices = []
        last_price = self.feed.candles[-1].price
        trend = self.feed.candles[-1].trend

        for prediction in self.history[-1]:
            try:
                delta = ((prediction.price * 100 / last_price) - 100) / 100
                if delta > self.fee and delta > 0 and trend == prosperpy.candle.Trend.DOWN:
                    prices.append(prediction.price)
                    trend = prosperpy.candle.Trend.UP
                elif delta < self.fee and delta < 0 and trend == prosperpy.candle.Trend.UP:
                    prices.append(prediction.price)
                    trend = prosperpy.candle.Trend.DOWN
            except (decimal.DivisionByZero, IndexError):
                prices.append(prediction.price)
            last_price = prediction.price

        if len(prices) < 10:
            prices = [prediction.price for prediction in self.history[-1]]

        prices = prices[0:10]
        '''
        prices = [prediction.price for prediction in self.history[-1]]

        best_traders = [DummyFutureTrader('B' * len(prices), self.fee) for _ in range(0, 10)]

        for actions in itertools.product('BSN', repeat=len(prices)):
            securities = sum([position.amount for position in self.positions])
            trader = FutureTrader(actions, self.fee, self.liquidity, securities)
            for price, action in zip(prices, actions):
                trader.price = price
                if action == 'B':
                    trader.buy()
                elif action == 'S':
                    trader.sell()

            for index, best_trader in enumerate(best_traders):
                if trader.total > best_trader.total:
                    best_traders[index] = trader
                    break
                elif trader.total == best_trader.total and trader.score > best_trader.score:
                    best_traders[index] = trader
                    break

        best_trader = best_traders[0]
        for trader in best_traders:
            if trader.total > best_trader.total:
                best_trader = trader
            elif trader.total == best_trader.total and trader.score > best_trader.score:
                best_trader = trader

        LOGGER.info(best_trader)
        if best_trader.strategy[0] == 'B':
            self.buy()
        elif best_trader.strategy[0] == 'S':
            self.sell()

        '''
        try:
            predictions = self.history[-1]
            prediction = predictions[-1]
            index = len(predictions) - 1
            LOGGER.info('{} prediction[{}] {:.4f} (current {:.4f})'.format(
                self, index, prediction.price, self.feed.price))
            if prediction.price > self.feed.price:
                self.buy()
            else:
                self.sell()
        except IndexError as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())
        '''


class FutureTrader:
    def __init__(self, strategy, fee, liquidity, security):
        self.strategy = strategy
        self.fee = fee
        self.score = self._make_score()
        self.liquidity = liquidity
        self.security = security
        self.price = decimal.Decimal('0.0')

    def __str__(self):
        return '{}<{}, {}, score={}>'.format(self.__class__.__name__, ''.join(self.strategy), self.total, self.score)

    def buy(self):
        self.security += self.liquidity / self.price
        self.liquidity = decimal.Decimal('0.0')

    def sell(self):
        profit = self.security * self.price
        profit -= self.fee * profit
        self.liquidity += profit
        self.security = decimal.Decimal('0.0')

    @property
    def total(self):
        return self.liquidity + (self.security * self.price)

    def _make_score(self):
        score = 0
        for item in self.strategy:
            if item in 'BS':
                score -= 1
            else:
                score += 1
        return score


class DummyFutureTrader(FutureTrader):
    def __init__(self, strategy, fee):
        super().__init__(strategy, fee, decimal.Decimal('0.0'), decimal.Decimal('0.0'))
