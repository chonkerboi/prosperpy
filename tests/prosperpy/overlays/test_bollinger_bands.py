import unittest
import decimal

import prosperpy


def get_prices():
    prices = ['90.704', '92.900', '92.978', '91.802', '92.665', '92.684', '92.302', '92.773', '92.537', '92.949',
              '93.204', '91.067', '89.832', '89.744', '90.399', '90.739', '88.018', '88.087', '88.844', '90.778',
              '90.542', '91.389', '90.650']
    return [decimal.Decimal(price) for price in prices]


class TestSimpleMovingAverage(unittest.TestCase):
    def test_simple_moving_average(self):
        prices = get_prices()
        data = [('91.2422', '94.53214587189516', '87.95225412810484', '6.57989174379032'),
                ('91.16665', '94.36908071900080', '87.96421928099920', '6.40486143800160'),
                ('91.05025', '94.14840337741694', '87.95209662258306', '6.19630675483388')]
        data = [(decimal.Decimal(item[0]), decimal.Decimal(item[1]), decimal.Decimal(item[2])) for item in data]

        bollinger_bands = prosperpy.overlays.BollingerBands(prices[:20])
        self.assertEqual(bollinger_bands.moving_average.value, decimal.Decimal('91.2503'))
        self.assertEqual(bollinger_bands.upper, decimal.Decimal('94.53410225348604'))
        self.assertEqual(bollinger_bands.lower, decimal.Decimal('87.96649774651396'))
        self.assertEqual(bollinger_bands.bandwidth, decimal.Decimal('6.56760450697208'))

        for price, value in zip(prices[20:], data):
            bollinger_bands.add(price)
            self.assertEqual(bollinger_bands.moving_average.value, value[0])
            self.assertEqual(bollinger_bands.upper, value[1])
            self.assertEqual(bollinger_bands.lower, value[2])
