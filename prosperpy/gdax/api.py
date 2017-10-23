import logging
import datetime
import decimal
import time
import urllib.parse
import base64
import hashlib
import hmac

import requests.auth

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


class GDAXAuth(requests.auth.AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = (timestamp + request.method + request.path_url + (request.body or '')).encode(encoding='utf-8')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, msg=message, digestmod=hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        header = {'CB-ACCESS-SIGN': signature_b64, 'CB-ACCESS-TIMESTAMP': timestamp, 'CB-ACCESS-KEY': self.api_key,
                  'CB-ACCESS-PASSPHRASE': self.passphrase, 'Content-Type': 'application/json'}
        request.headers.update(header)
        return request


class GDAXAPI:
    def __init__(self, auth):
        self.session = requests.Session()
        self.session.auth = auth
        import json
        r = self.session.get('https://api-public.sandbox.gdax.com/accounts')
        print(json.dumps(r.json(), indent=2, sort_keys=True))
