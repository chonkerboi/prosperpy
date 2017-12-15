import sys
import logging
import argparse
import decimal
import json
import datetime
import random

import matplotlib.pyplot
import matplotlib.ticker

import prosperpy
import prosperpy.traders

import alpha

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


def get_messages():
    seed = 'b6dcff52-3d0d-469a-9bdc-0b92be517ae7'
    random.seed(seed)

    with open('data.json', 'r') as data_file:
        raw = json.load(data_file)
        data = []
        aux = []
        timestamp = raw[0][0]
        for item in raw:
            aux.append(item)
            if aux[-1][0] > timestamp + 60:
                timestamp = timestamp + 60
                data.append([
                    aux[0][0], aux[0][1], aux[-1][2], min([i[3] for i in aux]), max([i[4] for i in aux]), aux[0][5]])
                aux = []

        messages = []
        for item in data:
            date = datetime.datetime.fromtimestamp(int(item[0]))
            bid = float(item[4])
            ask = bid + random.choice([-1, -0.5, 0, 0.5, 1])
            price = random.choice([bid, ask])

            message = json.dumps(dict(
                time=date.isoformat(), best_ask=ask, best_bid=bid, price=price, last_size=item[5]))
            messages.append(message)

        return messages


class Plot:
    curves = {}
    actions = []

    @classmethod
    def add_action(cls, action, x, y):
        cls.actions.append((action, x, y))

    @classmethod
    def plotme(cls):
        fig = matplotlib.pyplot.figure()
        plot = fig.add_subplot(111)
        for x, y, color in cls.curves.values():
            plot.plot(x, y, color=color)
        formatter = matplotlib.ticker.FormatStrFormatter('$%1.2f')
        plot.yaxis.set_major_formatter(formatter)

        for tick in plot.yaxis.get_major_ticks():
            tick.label1On = False
            tick.label2On = True
            tick.label2.set_color('green')

        for action, timestamp, price in cls.actions:
            bbox = dict(boxstyle="round", fc="0.8")
            arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10")
            offset = 64
            plot.annotate('{} ({:.2f})'.format(action, price), (timestamp, price), xytext=(-2 * offset, offset),
                          textcoords='offset points', bbox=bbox, arrowprops=arrowprops)

        matplotlib.pyplot.show()


def the_past(feed):
    Plot.curves['price'] = ([], [], 'blue')

    for message in get_messages():
        feed.consume(message)

        Plot.curves['price'][0].append(feed.tick.timestamp)
        Plot.curves['price'][1].append(feed.tick.price)

    Plot.plotme()


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
    product = 'ETH-USD'
    auth = prosperpy.gdax.auth.GDAXAuth(
        '727677e8492b36cd13b3b9325d20a5b7',
        'G/EGnZRm5MG+gxZCgw1CIOlLBQcViib78486kJhsvAYkiyojJTI5EsLTEVc0UGw/W1Ko5xhqwmFOUIQGzigJwQ==',
        'hus9I7src8U2')
    api = prosperpy.gdax.api.GDAXAPI(auth)
    run(product, api)


def run(product, api):
    feed = prosperpy.gdax.TickGDAXFeed(product)
    trader = alpha.CoastlineTrader(product, feed, api, decimal.Decimal('0.005'))
    trader.plot = Plot.add_action
    feed.traders.append(trader)
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
    #the_past(feed)


if __name__ == '__main__':
    main()
