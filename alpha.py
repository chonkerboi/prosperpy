import math
import logging
import decimal
import enum

import scipy.stats

LOGGER = logging.getLogger(__name__)


class Event(enum.Enum):
    INCREASE = 1
    DECREASE = -1
    NOTHING = 0


class Math:
    @staticmethod
    def log(x, base=None):
        if base is None:
            return decimal.Decimal(str(math.log(float(x))))
        else:
            return decimal.Decimal(str(math.log(float(x), base)))

    @staticmethod
    def exp(x):
        return decimal.Decimal(str(math.exp(float(x))))

    @staticmethod
    def pow(x, y):
        return decimal.Decimal(str(math.pow(float(x), float(y))))

    @staticmethod
    def sqrt(x):
        return decimal.Decimal(str(math.sqrt(float(x))))

    @staticmethod
    def cdf(x):
        return decimal.Decimal(scipy.stats.norm.cdf(float(x)))


class CoastlineTrader:
    def __init__(self, product, feed, api, delta, delta_up=None, delta_down=None):
        self.product = product
        self.feed = feed
        self.api = api
        self.investment = self.capital = decimal.Decimal('10000.0')
        self.positions = decimal.Decimal('0.0')
        self.prices = []
        self.sizes = []
        self.delta = delta
        self.delta_up = delta_up or delta
        self.delta_down = delta_down or delta
        self.shrink = decimal.Decimal('1.0')
        self.runner = None
        self.runners = []
        self.increase = decimal.Decimal('0.0')
        self.liquidity = None
        self.plot = None

    def try_to_close(self):
        #LOGGER.info('TODO: check if PnL reached profit target (current price is: %s)', self.feed.price)
        # TODO: Check if PnL target hit implementation

        profit = self.capital
        for i in range(0, len(self.prices)):
            profit += self.feed.price * self.sizes[i]

        roi = (profit / self.investment) * decimal.Decimal('100.0')
        LOGGER.info('profit: %s, investment: %s (%s%%)', profit, self.investment, roi)

        return False

    def __call__(self, tick):
        if not self.runner:
            self.runner = Runner(self.delta_up, self.delta_down, tick, self.delta_up, self.delta_down)
            self.runners.append([
                Runner(decimal.Decimal('0.75') * self.delta_up, decimal.Decimal('1.50') * self.delta_down, tick, decimal.Decimal('0.75') * self.delta_up, decimal.Decimal('0.75') * self.delta_up),
                Runner(decimal.Decimal('0.50') * self.delta_up, decimal.Decimal('2.00') * self.delta_down, tick, decimal.Decimal('0.50') * self.delta_up, decimal.Decimal('0.50') * self.delta_up)])
            self.runners.append([
                Runner(decimal.Decimal('1.50') * self.delta_up, decimal.Decimal('0.75') * self.delta_down, tick, decimal.Decimal('0.75') * self.delta_down, decimal.Decimal('0.75') * self.delta_down),
                Runner(decimal.Decimal('2.00') * self.delta_up, decimal.Decimal('0.50') * self.delta_down, tick, decimal.Decimal('0.50') * self.delta_down, decimal.Decimal('0.50') * self.delta_down)])
            self.liquidity = LocalLiquidity(self.delta, self.delta_up, self.delta_down, self.delta * decimal.Decimal('2.525729'), tick, decimal.Decimal('50.0'))

        self.liquidity.computation(tick)

        if self.liquidity.liq is None:
            LOGGER.warning('Could not compute liquidity')
            return

        if self.try_to_close():
            return

        if self.liquidity.liq < decimal.Decimal('0.1'):
            size = decimal.Decimal('0.1')
        elif self.liquidity.liq < decimal.Decimal('0.5'):
            size = decimal.Decimal('0.5')
        else:
            size = decimal.Decimal('1.0')

        if self.liquidity.liq < decimal.Decimal('0.1'):
            size = decimal.Decimal('0.1')

        fraction = decimal.Decimal('1.0')
        event = self.runner.run(tick)

        if decimal.Decimal('15.0') <= self.positions < decimal.Decimal('30.0'):
            event = self.runners[0][0].run(tick)
            self.runners[0][1].run(tick)
            fraction = decimal.Decimal('0.5')
        elif self.positions >= decimal.Decimal('30.0'):
            event = self.runners[0][1].run(tick)
            self.runners[0][0].run(tick)
            fraction = decimal.Decimal('0.25')
        else:
            self.runners[0][0].run(tick)
            self.runners[0][1].run(tick)

        LOGGER.info(event)

        if event == Event.INCREASE:
            if self.positions == decimal.Decimal('0.0'):  # Open long position
                sign = -self.runner.type
                volume = sign * size

                if volume < decimal.Decimal('0.0'):
                    LOGGER.error('How did this happen! increase position but negative size: %s', volume)
                    volume = -volume

                self.positions += volume
                self.sizes.append(volume)

                if sign == 1:
                    price = tick.ask
                else:
                    price = tick.bid

                self.prices.append(price)
                self.capital -= volume * price

                if self.capital < 0:
                    self.investment += -self.capital
                    self.capital = decimal.Decimal('0.0')

                try:
                    self.plot('open: {:.4f}'.format(volume), tick.timestamp, price)
                except Exception:
                    pass

                LOGGER.info('Open')

            elif self.positions > decimal.Decimal('0.0'):  # Increase long position (buy)
                sign = -self.runner.type
                volume = sign * size * fraction * self.shrink

                if volume < decimal.Decimal('0.0'):
                    LOGGER.error('How did this happen! increase position but negative size: %s', volume)
                    volume = -volume

                self.increase += decimal.Decimal('1.0')
                self.positions += volume
                self.sizes.append(volume)

                if sign == 1:
                    price = tick.ask
                else:
                    price = tick.bid

                self.prices.append(price)
                self.capital -= volume * price

                if self.capital < 0:
                    self.investment += -self.capital
                    self.capital = decimal.Decimal('0.0')

                try:
                    self.plot('cascade: {:.4f}'.format(volume), tick.timestamp, price)
                except Exception:
                    pass

                LOGGER.info('Cascade')

        # Possibility to decrease position only at intrinsic events
        elif event == Event.DECREASE and self.positions > decimal.Decimal('0.0'):
            if self.positions > decimal.Decimal('0.0'):
                price = tick.bid
            else:
                price = tick.ask

            to_remove = []
            for i in range(0, len(self.prices)):
                if self.positions > decimal.Decimal('0.0'):
                    tempP = Math.log(price / self.prices[i])
                    tmpDelta = self.delta_up
                else:
                    tempP = Math.log(self.prices[i] / price)
                    tmpDelta = self.delta_down

                if tempP >= tmpDelta:
                    profit = price * self.sizes[i]
                    self.capital += profit
                    net_profit = profit - (self.prices[i] * self.sizes[i])

                    try:
                        self.plot('decascade: {:.4f}'.format(net_profit), tick.timestamp, tick.price)
                    except Exception:
                        pass

                    if net_profit > decimal.Decimal('0.0'):
                        LOGGER.warning("Decascade with loss: %s", net_profit)
                    else:
                        LOGGER.info('Decascade with profit: %s', net_profit)

                    self.positions -= self.sizes[i]
                    if self.positions < decimal.Decimal('0.0'):
                        LOGGER.warning('Rectifying negative number of positions (rounding error?)')
                        self.positions = decimal.Decimal('0.0')

                    to_remove.append(i)
                    self.increase -= decimal.Decimal('1.0')

            self.prices = [price for index, price in enumerate(self.prices) if index in to_remove]
            self.sizes = [size for index, size in enumerate(self.sizes) if index in to_remove]


class LocalLiquidity:
    def __init__(self, delta, delta_up, delta_down, delta_star, tick, alpha):
        self.delta_up = delta_up
        self.delta_down = delta_down
        self.delta_star = delta_star
        self.delta = delta
        self.alpha = alpha
        self.weight = Math.exp(-decimal.Decimal('2.0') / (alpha + decimal.Decimal('1.0')))
        self.extreme = self.reference = tick.mid
        self.surprise = decimal.Decimal('0.0')
        self.liq = None
        self.type = -1
        self.h = self.compute_h_exp()

    def compute_h_exp(self):
        h = [-Math.exp(-self.delta_star/self.delta)*Math.log(Math.exp(-self.delta_star/self.delta)) - (decimal.Decimal('1.0') - Math.exp(-self.delta_star/self.delta))*Math.log(decimal.Decimal('1.0') - Math.exp(-self.delta_star/self.delta))]
        h.append(Math.exp(-self.delta_star/self.delta)*Math.pow(Math.log(Math.exp(-self.delta_star/self.delta)), decimal.Decimal('2.0')) - (decimal.Decimal('1.0') - Math.exp(-self.delta_star/self.delta))*Math.pow(Math.log(decimal.Decimal('1.0') - Math.exp(-self.delta_star/self.delta)), decimal.Decimal('2.0')) - h[0]*h[0])
        return h

    def run(self, tick):
        if self.type == -1:
            if Math.log(tick.bid/self.extreme) >= self.delta_up:
                self.type = 1
                self.extreme = tick.ask
                self.reference = tick.ask
                return 1
            if tick.ask < self.extreme:
                self.extreme = tick.ask
            if Math.log(self.reference / self.extreme) >= self.delta_star:
                self.reference = self.extreme
                return 2
        elif self.type == 1:
            if Math.log(tick.ask/self.extreme) <= -self.delta_down:
                self.type = -1
                self.extreme = tick.bid
                self.reference = tick.bid
                return -1
            if tick.bid > self.extreme:
                self.extreme = tick.bid
            if Math.log(self.reference/self.extreme) <= -self.delta_star:
                self.reference = self.extreme
                return -2
        return 0

    def computation(self, tick):
        event = self.run(tick)
        if event != 0:
            if abs(event) == 1:
                surprise = decimal.Decimal('0.08338161')
            else:
                surprise = decimal.Decimal('2.525729')
            self.surprise = (self.weight * surprise) + ((decimal.Decimal('1.0') - self.weight) * self.surprise)
            self.liq = decimal.Decimal('1.0') - Math.cdf(Math.sqrt(self.alpha) * (self.surprise - self.h[0])/Math.sqrt(self.h[1]))


class Runner:
    def __init__(self, delta_up, delta_down, tick, delta_star_up, delta_star_down):
        self.extreme = tick.mid
        self.delta_up = delta_up
        self.delta_down = delta_down
        self.delta_star_up = delta_star_up
        self.delta_star_down = delta_star_down
        self.type = -1
        self.reference = tick.mid

    def run(self, tick):
        if self.type == -1:
            if Math.log(tick.bid/self.extreme) >= self.delta_up:
                self.type = 1
                self.extreme = tick.ask
                self.reference = tick.ask
                return Event.DECREASE

            if tick.ask < self.extreme:
                self.extreme = tick.ask

                if Math.log(self.extreme/self.reference) <= -self.delta_star_up:
                    self.reference = self.extreme
                    return Event.INCREASE

                return Event.NOTHING

        elif self.type == 1:
            if Math.log(tick.ask/self.extreme) <= -self.delta_down:
                self.type = -1
                self.extreme = tick.bid
                self.reference = tick.bid
                return Event.INCREASE

            if tick.bid > self.extreme:
                self.extreme = tick.bid

                if Math.log(self.extreme/self.reference) >= self.delta_star_down:
                    self.reference = self.extreme
                    return Event.DECREASE

                return Event.NOTHING

        return Event.NOTHING
