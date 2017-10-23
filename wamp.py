import sys
import logging
import argparse
import decimal

import prosperpy

LOGGER = logging.getLogger(__name__)


def get_candles(granularity, reverse=False):
    import json
    with open('data.json', 'r') as data_file:
        candles = []
        raw = json.load(data_file)

        data = []
        aux = []
        timestamp = raw[0][0]
        for item in raw:
            aux.append(item)
            if aux[-1][0] > timestamp + granularity:
                timestamp = timestamp + granularity
                data.append([aux[0][0], aux[0][1], aux[-1][2], min([i[3] for i in aux]), max([i[4] for i in aux])])
                aux = []

        if reverse:
            data = reversed(data)

        for index, item in enumerate(data):
            candle = prosperpy.Candle(*list(map(decimal.Decimal, item[1:5])))

            try:
                candle.previous = candles[index - 1]
            except IndexError:
                pass

            candles.append(candle)

        return candles


def init_logging(options):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    fmt = '%(asctime)s|%(levelname)s|%(name)s|%(message)s|%(filename)s|%(lineno)s'
    handler.setFormatter(logging.Formatter(fmt=fmt))

    if options.verbosity:
        level = logging.DEBUG
        prosperpy.engine.set_debug(True)
    elif options.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    logging.root.setLevel(level)
    logging.root.addHandler(handler)


class Agent:
    def __init__(self, feeds, traders, candles):
        self.feeds = feeds
        self.traders = traders
        self.candles = candles

    def __call__(self):
        for candle in self.candles:
            for feed in self.feeds:
                feed.price = decimal.Decimal(sum([candle.low, candle.high, candle.open, candle.close])/4)
                feed.candles.append(candle)

            for trader in self.traders:
                trader.trade(candle)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--granularity', type=int, dest='granularity', required=True)
    parser.add_argument('--period', type=int, dest='period', required=True)
    parser.add_argument('--reverse', action='store_true', dest='reverse', default=False)
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity', default=0)
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False)
    options = parser.parse_args()
    init_logging(options)
    product = 'BTC-USD'
    auth = prosperpy.gdax.api.GDAXAuth(
        'e607d4feebe87f28beacff087243b011',
        'XRIqlNO9bE49AO15Xb800mqa1qTDqUcHS8NjfYXbK6DO5sdWDHk46bKXEBrc5IFrvYZOqkUwJscA2NLEi471kA==',
        '92Ka6n64Tzya')
    api = prosperpy.gdax.api.GDAXAPI(auth)

    #factor = 365 * (3600 * 24) / (options.granularity * options.period)
    #factor = 10
    #candles = prosperpy.gdax.api.get_candles(options.period * factor, options.granularity, product)
    #candles = get_candles(options.granularity, reverse=options.reverse)
    #[print(candle) for candle in candles]
    #return

    #feed = prosperpy.gdax.GDAXFeed(product, options.granularity, candles[0:options.period])
    feed = prosperpy.gdax.GDAXFeed(product, options.period, options.granularity)
    feed.traders.append(prosperpy.traders.ADXTrader(product, feed, api))
    feed.traders.append(prosperpy.traders.SMATrader(product, feed, api))
    feed.traders.append(prosperpy.traders.HODLTrader(product, feed, api))
    feed.traders.append(prosperpy.traders.PercentageTrader(decimal.Decimal('0.8'), product, feed, api))

    prosperpy.engine.create_task(feed())
    prosperpy.engine.run_forever()
    prosperpy.engine.close()
    return

    agent = Agent([feed], traders, candles[options.period:])
    agent()

    LOGGER.info('--------------------------------------------------------------------------------')
    for trader in traders:
        trader.summary()


if __name__ == '__main__':
    main()
