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
    def __init__(self, product, granularity, period, candles):
        self.feed = prosperpy.gdax.GDAXFeed(product, granularity, candles[0:period])
        self.candles = candles[period:]

    def run(self):
        for candle in self.candles:
            self.feed.price = decimal.Decimal(sum([candle.low, candle.high, candle.open, candle.close])/4)
            self.feed.candles.append(candle)

            for trader in self.feed.traders:
                trader.trade(candle)


def main():
    'EI4+LBJLYCfPWFd1X7c4RtZqPnVm4wDPpFgwNvFF/VY7yJxSmIY4/u2b6zloxTTskQx37ljJ3TcBf2DvfUGlTg=='
    'v2ZKzU74X3yM'
    'e3690555d24ed594054de83c598ddabd'
    parser = argparse.ArgumentParser()
    parser.add_argument('--granularity', type=int, dest='granularity', required=True)
    parser.add_argument('--period', type=int, dest='period', required=True)
    parser.add_argument('--reverse', action='store_true', dest='reverse', default=False)
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity', default=0)
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False)
    options = parser.parse_args()
    init_logging(options)
    product = 'BTC-USD'

    #factor = 365 * (3600 * 24) / (options.granularity * options.period)
    #candles = prosperpy.gdax.rest.get_candles(options.period * factor, options.granularity, product)
    candles = get_candles(options.granularity, reverse=options.reverse)

    #[print(candle) for candle in candles]
    #return

    agent = Agent(product, options.granularity, options.period, candles)
    agent.feed.register_trader(prosperpy.traders.ADXTrader(product, agent.feed))
    agent.feed.register_trader(prosperpy.traders.SMATrader(product, agent.feed))
    agent.feed.register_trader(prosperpy.traders.HODLTrader(product, agent.feed))
    agent.feed.register_trader(prosperpy.traders.PercentageTrader(decimal.Decimal('0.8'), product, agent.feed))
    #agent.register_trader(prosperpy.traders.PercentageTrader(decimal.Decimal('0.6'), agent))
    #agent.register_trader(prosperpy.traders.PercentageTrader(decimal.Decimal('0.4'), agent))
    #agent.register_trader(prosperpy.traders.PercentageTrader(decimal.Decimal('0.2'), agent))
    #agent.register_trader(prosperpy.traders.PercentageTrader(decimal.Decimal('0.05'), agent))

    agent.run()

    LOGGER.info('----------------------------------------')
    for trader in agent.feed.traders:
        trader.summary()

    return

    agents = [prosperpy.gdax.Agent(product, options.granularity, candles)]

    for agent in agents:
        prosperpy.engine.create_task(agent())

    prosperpy.engine.run_forever()
    prosperpy.engine.close()


if __name__ == '__main__':
    main()
