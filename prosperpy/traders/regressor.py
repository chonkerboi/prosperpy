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
        self.error_threshold = decimal.Decimal('0.1')
        #self.n_predictions = int(self.feed.period / 4)
        self.n_predictions = 2
        self.history = collections.deque(maxlen=self.n_predictions)
        self.errors = []
        self.regressor = None

        self.coastline = None
        self.e = collections.deque()

    def __str__(self):
        return '{}<{}, model={}>'.format(self.__class__.__name__, str(self.feed), self.model.__name__)

    @property
    def price_error(self):
        return sum(self.price_errors) / len(self.price_errors)

    def initialize(self):
        self.errors = [collections.deque(maxlen=self.feed.candles.maxlen) for _ in range(self.history.maxlen)]
        self.price_errors = collections.deque(maxlen=self.feed.candles.maxlen)

        self.coastline = prosperpy.coastline.Coastline(self.feed.candles)
        self.e = [collections.deque(maxlen=self.feed.candles.maxlen) for _ in range(self.history.maxlen)]

    def add(self, candle):
        #self.coastline.add(candle)

        try:
            coastline = self.fit()
            self.predict(coastline, candle)
        except Exception as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())

    def fit(self):
        self.regressor = self.model(n_estimators=10)

        coastline = prosperpy.coastline.Coastline(list(self.feed.candles)[0:self.feed.period])
        input_variables = []
        output_variables = []

        for candle in list(self.feed.candles)[self.feed.period:]:
            try:
                output_variables.append([candle.price, candle.volume])
            except AttributeError:
                continue

            var = [coastline.price.ema5.value, coastline.price.ema10.value, coastline.price.ema_half.value,
                   coastline.price.ema_full.value, coastline.volume.ema5.value, coastline.volume.ema10.value,
                   coastline.volume.ema_half.value, coastline.volume.ema_full.value, coastline.dc.low5,
                   coastline.dc.low10, coastline.dc.high5, coastline.dc.high10, coastline.price.all_time_min,
                   coastline.price.all_time_max]
            input_variables.append(var)
            coastline.add(candle)

        self.regressor.fit(input_variables, output_variables)
        return coastline

    def predict(self, coastline, candle):
        candles = []
        for _ in range(0, self.n_predictions):
            coastline.add(candle)
            data = [coastline.price.ema5.value, coastline.price.ema10.value, coastline.price.ema_half.value,
                    coastline.price.ema_full.value, coastline.volume.ema5.value, coastline.volume.ema10.value,
                    coastline.volume.ema_half.value, coastline.volume.ema_full.value, coastline.dc.low5,
                    coastline.dc.low10, coastline.dc.high5, coastline.dc.high10, coastline.price.all_time_min,
                    coastline.price.all_time_max]
            price, volume = map(decimal.Decimal, self.regressor.predict([data])[0])
            timestamp = candle.timestamp + self.feed.granularity
            candle = prosperpy.Candle(timestamp=timestamp, price=price, volume=volume, previous=candle)
            candles.append(candle)

        self.history.append(candles)
        LOGGER.debug('%s predictions are %s', self, candles)

    def fit_old(self):
        self.regressor = self.model(n_estimators=10)

        candles = list(self.feed.candles)[-self.feed.period:]
        input_variables = []
        output_variables = []

        for index, candle in enumerate(candles):
            input_var = [candle.price, candle.volume]
            input_variables.append(input_var)

            try:
                output_variables.append([candle.previous.price, candle.previous.volume])
            except AttributeError:
                output_variables.append([decimal.Decimal('0'), decimal.Decimal('0')])

        self.regressor.fit(input_variables, output_variables)

    def predict_old(self, candle):
        candles = []
        for _ in range(0, self.n_predictions):
            data = [candle.price, candle.volume]
            price, volume = map(decimal.Decimal, self.regressor.predict([data])[0])
            timestamp = candle.timestamp + self.feed.granularity
            candle = prosperpy.Candle(timestamp=timestamp, price=price, volume=volume, previous=candle)
            candles.append(candle)

        self.history.append(candles)
        LOGGER.debug('%s predictions are %s', self, candles)

    def compute_accuracy(self):
        if len(self.history) != self.history.maxlen:
            LOGGER.debug('Not enough prediction history to compute accuracy')

        try:
            predictions = self.history[0]
            for index, prediction in enumerate(predictions):
                candle = self.feed.candles[-len(predictions)+index]
                error = abs((prediction.price - candle.price) / candle.price)
                self.errors[index].append(error)
                accuracy = decimal.Decimal('100') - error * decimal.Decimal('100')
                error_avg = sum(self.errors[index]) / len(self.errors[index])
                accuracy_avg = decimal.Decimal('100') - error_avg * decimal.Decimal('100')
                LOGGER.info('{} accuracy[{}] is {:.4f}% (avg: {:.4f}%)'.format(self, index, accuracy, accuracy_avg))

                i = -len(predictions)+index+1
                c = self.feed.candles[i]
                print('-- {} {:.4f} {:.4f}'.format(i, c.previous.price, c.price))
                real_delta = abs(c.price - c.previous.price)
                if real_delta < decimal.Decimal('0.0001'):
                    real_delta = decimal.Decimal('0.0001')
                print('-- {}, {:.4f} {:.4f}'.format(-len(predictions)+index, candle.price, prediction.price))
                prediction_delta = abs(prediction.price - candle.price)
                print('-- {:.4f} {:.4f}'.format(real_delta, prediction_delta))
                error = abs((prediction_delta - real_delta) / real_delta)
                print('-- {:.4f}'.format(error))
                self.e[index].append(error)
                avg = sum(self.e[index]) / len(self.e[index])
                print('-- {:.4f}'.format(avg))
                break
                #print('-- {:.4f}'.format(abs((prediction_delta - real_delta) / real_delta)))
                #delta = abs((candle.price - candle.previous.price) / candle.previous.price)
                #print('-- {:.4f} {:.4f}'.format(delta, error))
                #print(error * decimal.Decimal('100.0') / delta)
                #print(abs((error - delta) / delta))

        except (IndexError, decimal.InvalidOperation, decimal.DivisionByZero, AttributeError) as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())
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
            if self.price_error > self.error_threshold:
                LOGGER.warning("{} error is '{:.4f}' but error threshold is '{:.4f}'".format(
                    self, self.price_error, self.error_threshold))
                return False
        except (ZeroDivisionError, decimal.InvalidOperation, decimal.DivisionByZero) as ex:
            LOGGER.error('%s %s: %s', self, ex.__class__.__name__, ex)
            LOGGER.debug(traceback.format_exc())
            return False
        return True

    def trade(self):
        self.compute_accuracy()
        return
        if not self.check_accuracy():
            return

        target = 5
        trend = self.feed.candle.trend
        prices = [self.history[-1][0].price]
        for prediction in self.history[-1]:
            if prediction.price > prices[-1] and trend == prosperpy.candle.Trend.DOWN:
                prices.append(prediction.price)
                trend = prosperpy.candle.Trend.UP
            elif prediction.price < prices[-1] and trend == prosperpy.candle.Trend.UP:
                prices.append(prediction.price)
                trend = prosperpy.candle.Trend.DOWN

        if len(prices) < 4:
            prices = [prediction.price for prediction in self.history[-1]]

        prices = prices[0:target]

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


class FutureTrader:
    def __init__(self, strategy, fee, liquidity, security):
        self.strategy = strategy
        self.fee = fee
        self.score = self._make_score()
        self.liquidity = liquidity
        self.security = security
        self.price = decimal.Decimal('0.0')

    def __str__(self):
        return '{}<{}, {:.4f}, score={}>'.format(self.__class__.__name__, ''.join(self.strategy), self.total, self.score)

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
