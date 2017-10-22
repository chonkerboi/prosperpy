import logging
import datetime
import requests
import decimal
import time
import urllib.parse

import prosperpy

BASE_URL = 'https://api.gdax.com'
MAX_REQUESTS_PER_SECOND = 3
REQUESTS_RATE = 1 / MAX_REQUESTS_PER_SECOND
MAX_RESPONSE_LEN = 200
TIMEOUT = 2
LOGGER = logging.getLogger(__name__)


def get_candles(period, granularity, product, dump=None):
    url = urllib.parse.urljoin(BASE_URL, 'products/{}/candles'.format(product))
    data = []
    then = datetime.datetime.now() - datetime.timedelta(seconds=period * granularity)

    def get(start, end):
        resp = None
        while not resp:
            try:
                params = dict(start=start.isoformat(), end=end.isoformat(), granularity=granularity)
                resp = requests.get(url, params=params, timeout=TIMEOUT)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as ex:
                LOGGER.error(ex)
                time.sleep(REQUESTS_RATE)
        return resp.json()

    for _ in range(int(period/MAX_RESPONSE_LEN)):
        now = (then + datetime.timedelta(seconds=MAX_RESPONSE_LEN * granularity))
        data += get(then, now)
        LOGGER.debug('Received %s candles out of %s total', len(data), period)
        then = now
        time.sleep(REQUESTS_RATE)

    remainder = period % MAX_RESPONSE_LEN
    if remainder:
        now = (then + datetime.timedelta(seconds=remainder * granularity))
        data += get(then, now)
        LOGGER.debug('Received %s candles out of %s total', len(data), period)

    # take care of duplicated (timestamp) and unordered data
    tmp = {}
    for item in data:
        if item[0] not in tmp.keys():
            tmp[item[0]] = item
    data = sorted(tmp.values(), key=lambda item: item[0])

    if dump is not None:
        with open(dump, 'w') as dump_file:
            import json
            json.dump(data, dump_file)

    candles = []
    for index, item in enumerate(data):
        candle = prosperpy.Candle(*list(map(decimal.Decimal, item[1:5])))

        try:
            candle.previous = candles[index - 1]
        except IndexError:
            pass

        candles.append(candle)

    return candles
