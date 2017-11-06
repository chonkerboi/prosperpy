import math
import random
import itertools
import time
import decimal


def gen_deltas(offset=120):
    counter = itertools.count(start=offset, step=10)
    for count in counter:
        yield (math.sin(math.radians(count)) * random.randint(0, 20)) + 1


def chunks(iterable, chunksize=10):
    for index in range(0, len(iterable), chunksize):
        yield iterable[index:index+chunksize]


class Trader(object):
    def __init__(self, strategy, liquidity=decimal.Decimal('1.0'), security=decimal.Decimal('1.0')):
        self.strategy = strategy
        self.score = self._make_score()
        self.liquidity = liquidity
        self.security = security
        self._price = None
        self.price = decimal.Decimal('0.0')

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = decimal.Decimal(price)

    def __str__(self):
        return '{}<{}, {}, score={}>'.format(self.__class__.__name__, ''.join(self.strategy), self.total, self.score)

    def buy(self):
        self.security += self.liquidity / self.price
        self.liquidity = decimal.Decimal('0.0')

    def sell(self):
        self.liquidity += self.security * self.price
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


def main(size):
    start_time = time.time()
    price = decimal.Decimal('500.0')
    prices = []
    gen = gen_deltas()
    last_price = decimal.Decimal('0.0')
    up = True
    fee = decimal.Decimal('0.025')
    while len(prices) < size:
        price += decimal.Decimal(gen.__next__())
        try:
            delta = ((price * 100 / last_price) - 100) / 100
            if delta > fee and delta > 0 and not up:
                prices.append(price)
                up = True
            elif delta < fee and delta < 0 and up:
                prices.append(price)
                up = False
        except (decimal.DivisionByZero, IndexError):
            prices.append(price)
        last_price = price
    print(prices)

    best_traders = [Trader('B'*len(prices)) for _ in range(0, 10)]
    for actions in itertools.product('BSN', repeat=len(prices)):
        trader = Trader(actions, liquidity=decimal.Decimal('0.0'), security=decimal.Decimal('1.0'))

        for price, action in zip(prices, actions):
            trader.price = price
            if action == 'B':
                trader.buy()
            elif action == 'S':
                trader.sell()

        '''
        trader = Trader(())
        for chunked_prices, chunked_actions in zip(chunks(prices), chunks(actions)):
            strategy = trader.strategy + chunked_actions
            trader = Trader(strategy, money=trader.money, security=trader.security, price=trader.price)
            for price, action in zip(chunked_prices, chunked_actions):
                trader.price = price
                if action == 'B':
                    trader.buy()
                elif action == 'S':
                    trader.sell()
        '''

        for index, best_trader in enumerate(best_traders):
            if trader.total > best_trader.total:
                best_traders[index] = trader
                break
            elif trader.total == best_trader.total and trader.score > best_trader.score:
                best_traders[index] = trader
                break

    print('----------')
    for trader in best_traders:
        print(trader)

    time_delta = time.time() - start_time
    print(time_delta)
    return time_delta


if __name__ == '__main__':
    main(10)

    '''
    data = {}
    for key in range(10, 100, 10):
        data[key] = main(key)

    for key in sorted(data.keys()):
        print('{}: {}'.format(key, data[key]))
    '''
