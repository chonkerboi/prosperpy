import sys
import logging
import argparse
import decimal
import collections

import prosperpy
import prosperpy.traders

LOGGER = logging.getLogger(__name__)


def init_logging(options):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    fmt = '%(asctime)s|%(levelname)s|%(name)s|%(message)s|%(filename)s|%(lineno)s'
    handler.setFormatter(logging.Formatter(fmt=fmt))

    if options.verbosity:
        level = logging.DEBUG
    elif options.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    if options.verbosity >= 2:
        prosperpy.engine.set_debug(True)

    logging.root.setLevel(level)
    logging.root.addHandler(handler)


def real_time(feed):
    prosperpy.engine.create_task(feed())
    prosperpy.engine.run_forever()
    prosperpy.engine.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity', default=0)
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False)
    options = parser.parse_args()
    init_logging(options)
    product = 'BTC-USD'
    auth = prosperpy.gdax.auth.GDAXAuth(
        '727677e8492b36cd13b3b9325d20a5b7',
        'G/EGnZRm5MG+gxZCgw1CIOlLBQcViib78486kJhsvAYkiyojJTI5EsLTEVc0UGw/W1Ko5xhqwmFOUIQGzigJwQ==',
        'hus9I7src8U2')
    api = prosperpy.gdax.api.GDAXAPI(auth)
    run(product, api)


def run(product, api):
    feed = prosperpy.gdax.TickGDAXFeed(product)
    #feed.traders.append(prosperpy.traders.ADXTrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.RSITrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.HMATrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.SMATrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.PercentageTrader(decimal.Decimal('0.8'), product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.RandomForestRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.ExtraTreesRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.AdaBoostRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.BaggingRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.GradientBoostingRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.HODLTrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.PerfectTrader(product, feed, api))
    real_time(feed)


if __name__ == '__main__':
    main()
