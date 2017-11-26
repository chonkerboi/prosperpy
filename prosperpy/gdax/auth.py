import base64
import hmac
import hashlib
import time

import requests.auth


class GDAXAuth(requests.auth.AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = str(api_key)
        self.secret_key = str(secret_key)
        self.passphrase = str(passphrase)

    def make_headers(self, method, path_url, body=None):
        timestamp = str(time.time())
        message = (timestamp + method + path_url + (body or '')).encode(encoding='ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, msg=message, digestmod=hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
        return {'Content-Type': 'application/json', 'CB-ACCESS-SIGN': signature_b64, 'CB-ACCESS-KEY': self.api_key,
                'CB-ACCESS-PASSPHRASE': self.passphrase, 'CB-ACCESS-TIMESTAMP': timestamp}

    def __call__(self, request):
        headers = self.make_headers(request.method, request.path_url, body=request.body)
        request.headers.update(headers)
        return request
