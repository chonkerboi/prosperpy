import sys
import logging
import argparse
import decimal
import collections

import prosperpy
import prosperpy.traders

LOGGER = logging.getLogger(__name__)


def get_candles(granularity, filename='data.json', reverse=False):
    import json
    with open(filename, 'r') as data_file:
        candles = []
        raw = json.load(data_file)

        data = []
        aux = []
        timestamp = raw[0][0]
        for item in raw:
            aux.append(item)
            if aux[-1][0] > timestamp + granularity:
                timestamp = timestamp + granularity
                data.append([aux[0][0],
                             aux[0][1],
                             aux[-1][2],
                             min([i[3] for i in aux]),
                             max([i[4] for i in aux]),
                             aux[0][5]])
                aux = []

        if reverse:
            data = reversed(data)

        for index, item in enumerate(data):
            kwargs = dict(
                timestamp=item[0], low=decimal.Decimal(item[1]), high=decimal.Decimal(item[2]),
                open=decimal.Decimal(item[3]), close=decimal.Decimal(item[4]), volume=decimal.Decimal(item[5]))
            candle = prosperpy.Candle(**kwargs)

            try:
                candle.previous = candles[index - 1]
                if candle.open.is_nan():
                    candle.open = candle.previous.close
            except IndexError:
                if candle.open.is_nan():
                    candle.open = candle.close

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


def plotme(curves, actions):
    import matplotlib.pyplot
    import matplotlib.ticker
    fig = matplotlib.pyplot.figure()
    plot = fig.add_subplot(111)
    for x, y, color in curves:
        plot.plot(x, y, color=color)
    formatter = matplotlib.ticker.FormatStrFormatter('$%1.2f')
    plot.yaxis.set_major_formatter(formatter)

    for tick in plot.yaxis.get_major_ticks():
        tick.label1On = False
        tick.label2On = True
        tick.label2.set_color('green')

    for counter, side, price in actions:
        bbox = dict(boxstyle="round", fc="0.8")
        arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10")
        offset = 64
        plot.annotate('{} ({:.2f})'.format(side, price), (counter, price), xytext=(-2 * offset, offset),
                      textcoords='offset points', bbox=bbox, arrowprops=arrowprops)

    matplotlib.pyplot.show()


def the_past(period, granularity, feed, product, reverse):
    # factor = 365 * (3600 * 24) / (granularity * period)
    factor = 10
    #candles = prosperpy.gdax.api.get_candles(period * factor, options.granularity, product)
    ltc_candles = get_candles(granularity, filename='ltc-usd.json', reverse=reverse)
    btc_candles = get_candles(granularity, filename='btc-usd.json', reverse=reverse)

    feed.candles = collections.deque(iterable=ltc_candles[1:feed.period+1], maxlen=feed.period*factor)
    ltc_x = [candle.timestamp for candle in ltc_candles[1:feed.period+1]]
    ltc_y = [candle.close for candle in ltc_candles[1:feed.period + 1]]
    btc_x = [candle.timestamp for candle in btc_candles[1:feed.period+1]]
    btc_y = [candle.close * decimal.Decimal('0.01') for candle in btc_candles[1:feed.period+1]]

    for candle in btc_candles[feed.period+1:]:
        btc_x.append(candle.timestamp)
        btc_y.append(candle.close * decimal.Decimal('0.01'))

    for candle in ltc_candles[feed.period + 1:]:
        ltc_x.append(candle.timestamp)
        ltc_y.append(candle.close)

    plotme([(ltc_x, ltc_y, 'blue'), (btc_x, btc_y, 'orange')], [])


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
    auth = prosperpy.gdax.auth.GDAXAuth(
        '727677e8492b36cd13b3b9325d20a5b7',
        'G/EGnZRm5MG+gxZCgw1CIOlLBQcViib78486kJhsvAYkiyojJTI5EsLTEVc0UGw/W1Ko5xhqwmFOUIQGzigJwQ==',
        'hus9I7src8U2')
    api = prosperpy.gdax.api.GDAXAPI(auth)
    run(product, options.period, options.granularity, api, options.reverse)
    return

    feeds = {}
    for period in [10, 50, 100, 200, 500, 1000, 2000]:
        for granularity in [60, 120, 300, 600, 1800, 3600, 7200, 21400, 43200, 86400]:
            feeds[str(period) + '-' + str(granularity)] = run(product, period, granularity, api, False)

    for key, feed in feeds.items():
        LOGGER.info('-' * 40 + key + '-' * 40)
        for trader in feed.traders:
            trader.summary()


def run(product, period, granularity, api, reverse):
    feed = prosperpy.gdax.GDAXFeed(product, period, granularity)
    #feed.traders.append(prosperpy.traders.ADXTrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.RSITrader(product, feed, api))
    feed.traders.append(prosperpy.traders.HMATrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.SMATrader(product, feed, api))
    #feed.traders.append(prosperpy.traders.PercentageTrader(decimal.Decimal('0.8'), product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.RandomForestRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.ExtraTreesRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.AdaBoostRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.BaggingRegressor, product, feed, api))
    #feed.traders.append(prosperpy.traders.RegressorTrader(sklearn.ensemble.GradientBoostingRegressor, product, feed, api))
    feed.traders.append(prosperpy.traders.HODLTrader(product, feed, api))
    feed.traders.append(prosperpy.traders.PerfectTrader(product, feed, api))

    #real_time(feed)
    the_past(period, granularity, feed, product, reverse)
    return feed


if __name__ == '__main__':
    main()
