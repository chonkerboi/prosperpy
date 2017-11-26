import unittest
import decimal

import prosperpy


def get_prices():
    prices = ['22.27', '22.19', '22.08', '22.17', '22.18', '22.13', '22.23', '22.43', '22.24', '22.29', '22.15',
              '22.39', '22.38', '22.61', '23.36', '24.05', '23.75', '23.83', '23.95', '23.63', '23.82', '23.87',
              '23.65', '23.19', '23.10', '23.33', '22.68', '23.10', '22.40', '22.17']
    return [decimal.Decimal(price) for price in prices]


class TestSimpleMovingAverage(unittest.TestCase):
    def test_simple_moving_average(self):
        prices = get_prices()
        sma = prosperpy.overlays.SimpleMovingAverage(prices[0:10])
        self.assertEqual(sma.period, 10)
        self.assertEqual(sma.value, decimal.Decimal('22.221'))
        data = ['22.209', '22.229', '22.259', '22.303', '22.421', '22.613', '22.765', '22.905', '23.076', '23.21',
                '23.377', '23.525', '23.652', '23.71', '23.684', '23.612', '23.505', '23.432', '23.277', '23.131']
        data = [decimal.Decimal(item) for item in data]

        for price, value in zip(prices[10:], data):
            self.assertEqual(sma(price), value)


class TestExponentialMovingAverage(unittest.TestCase):
    def test_exponential_moving_average(self):
        prices = get_prices()
        ema = prosperpy.overlays.ExponentialMovingAverage(prices[0:10])
        self.assertEqual(ema.period, 10)
        self.assertEqual(ema.value, decimal.Decimal('22.221'))
        data = ['22.19827272727273', '22.25827272727273', '22.28100000000000', '22.35881818181818', '22.59172727272727',
                '22.87427272727273', '22.94409090909091', '23.07318181818182', '23.23490909090909', '23.28636363636364',
                '23.45754545454545', '23.58772727272727', '23.65163636363636', '23.61545454545455', '23.57781818181818',
                '23.56072727272727', '23.35500000000000', '23.37163636363636', '23.11754545454545', '22.95627272727273']
        data = [decimal.Decimal(item) for item in data]

        for price, value in zip(prices[10:], data):
            self.assertEqual(ema(price), value)


if __name__ == '__main__':
    unittest.main()
