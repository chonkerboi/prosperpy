import unittest
import decimal

import prosperpy


def get_prices():
    prices = ['22.2734', '22.1940', '22.0847', '22.1741', '22.1840', '22.1344', '22.2337', '22.4323', '22.2436',
              '22.2933', '22.1542', '22.3926', '22.3816', '22.6109', '23.3558', '24.0519', '23.7530', '23.8324',
              '23.9516', '23.6338', '23.8225', '23.8722', '23.6537', '23.1870', '23.0976', '23.3260', '22.6805',
              '23.0976', '22.4025', '22.1725']
    return [decimal.Decimal(price) for price in prices]


class TestSimpleMovingAverage(unittest.TestCase):
    def test_simple_moving_average(self):
        prices = get_prices()
        data = ['22.21283', '22.23269', '22.26238', '22.30606', '22.42324', '22.61499', '22.76692', '22.90693',
                '23.07773', '23.21178', '23.37861', '23.52657', '23.65378', '23.71139', '23.68557', '23.61298',
                '23.50573', '23.43225', '23.27734', '23.13121']
        data = [decimal.Decimal(item) for item in data]

        sma = prosperpy.overlays.SimpleMovingAverage(prices[:10])
        self.assertEqual(sma.period, 10)
        self.assertEqual(sma.value, decimal.Decimal('22.22475'))

        for price, value in zip(prices[10:], data):
            self.assertEqual(sma(price), value)


class TestExponentialMovingAverage(unittest.TestCase):
    def test_exponential_moving_average(self):
        prices = get_prices()
        data = ['22.21192272727273', '22.24477314049587', '22.26965075131480', '22.33169606925756', '22.51789678393800',
                '22.79680645958564', '22.97065983057007', '23.12733986137551', '23.27720534112542', '23.34204073364807',
                '23.42939696389388', '23.50990660682227', '23.53605086012731', '23.47258706737689', '23.40440760058109',
                '23.39015167320271', '23.26112409625676', '23.23139244239189', '23.08068472559336', '22.91556023003093']
        data = [decimal.Decimal(item) for item in data]

        ema = prosperpy.overlays.ExponentialMovingAverage(prices[:10])
        self.assertEqual(ema.period, 10)
        self.assertEqual(ema.value, decimal.Decimal('22.22475'))

        for price, value in zip(prices[10:], data):
            self.assertEqual(ema(price), value)


class TestWeightedMovingAverage(unittest.TestCase):
    def test_weighted_moving_average(self):
        prices = ['90.91', '90.83', '90.28', '90.36', '90.90']
        prices = [decimal.Decimal(price) for price in prices]
        wma = prosperpy.overlays.WeightedMovingAverage(prices)
        self.assertEqual(wma.period, 5)
        self.assertEqual(wma.denominator, 15)
        self.assertEqual(wma.value, decimal.Decimal('90.62333333333333'))


if __name__ == '__main__':
    unittest.main()
