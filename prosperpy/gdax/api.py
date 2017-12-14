import logging
import datetime
import decimal
import time
import urllib.parse

import requests

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
        json_data = resp.json()
        LOGGER.debug('Received %s/%s candles', len(json_data) + len(data), period)
        return json_data

    for _ in range(int(period/MAX_RESPONSE_LEN)):
        now = (then + datetime.timedelta(seconds=MAX_RESPONSE_LEN * granularity))
        data += get(then, now)
        then = now
        time.sleep(REQUESTS_RATE)

    remainder = period % MAX_RESPONSE_LEN
    if remainder:
        now = (then + datetime.timedelta(seconds=remainder * granularity))
        data += get(then, now)

    # take care of duplicated (timestamp) and unordered data
    tmp = {}
    for item in data:
        if item[0] not in tmp.keys():
            tmp[item[0]] = item
    data = sorted(tmp.values(), key=lambda value: value[0])

    if dump is not None:
        with open(dump, 'w') as dump_file:
            import json
            json.dump(data, dump_file)

    candles = []
    for index, item in enumerate(data):
        kwargs = dict(
            timestamp=item[0], low=decimal.Decimal(item[1]), high=decimal.Decimal(item[2]),
            open=decimal.Decimal(item[3]), close=decimal.Decimal(item[4]), volume=decimal.Decimal(item[5]))
        candle = prosperpy.Candle(**kwargs)

        try:
            candle.previous = candles[index - 1]
        except IndexError:
            pass

        candles.append(candle)

    return candles


class GDAXAPI:
    def __init__(self, auth):
        self.session = requests.Session()
        self.session.auth = auth
        #import json
        #r = self.session.get('https://api-public.sandbox.gdax.com/accounts')
        #print(json.dumps(r.json(), indent=2, sort_keys=True))
