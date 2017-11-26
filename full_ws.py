import sys
import logging
import argparse
import json

import prosperpy

LOGGER = logging.getLogger(__name__)


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


class Full:
    def __init__(self, params, timeout, auth):
        #self.connection = prosperpy.gdax.GDAXWebsocketConnection(params, timeout, auth=auth)
        self.connection = prosperpy.gdax.GDAXWebsocketConnection(params, timeout, auth=auth, url='wss://ws-feed-public.sandbox.gdax.com')

    async def __aenter__(self):
        await self.connection.connect()
        return self

    async def __aexit__(self, *_):
        await self.connection.close()

    @staticmethod
    def consume(message):
        LOGGER.info(json.loads(message))

    @prosperpy.error.fatal
    async def run(self):
        async with self:
            while True:
                self.consume(await self.connection.recv())

    async def __call__(self):
        return await self.run()


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
    #api = prosperpy.gdax.api.GDAXAPI(auth)
    params = dict(type='subscribe', channels=[dict(name='full', product_ids=[product])])
    full = Full(params, 300, auth)
    prosperpy.engine.create_task(full())
    prosperpy.engine.run_forever()
    prosperpy.engine.close()


if __name__ == '__main__':
    main()
