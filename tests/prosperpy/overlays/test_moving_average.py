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


class TestHullMovingAverage(unittest.TestCase):
    def test_hull_moving_average(self):
        prices = [1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 18, 17, 16, 15,
                  14, 15, 16, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        prices = [decimal.Decimal(price) for price in prices]
        data = ['4.501010101010096', '5.872727272727272', '7.268686868686868', '8.688888888888887', '10.06666666666666',
                '11.35757575757576', '12.53939393939394', '13.63030303030304', '14.66060606060607', '15.66666666666667',
                '16.66666666666667', '17.66666666666667', '18.66666666666666', '19.18181818181818', '19.00404040404040',
                '18.16363636363636', '16.89090909090908', '15.41616161616162', '14.45454545454546', '14.31111111111112',
                '14.47878787878787', '14.96767676767676', '15.74949494949494', '16.75757575757576', '17.87676767676767',
                '19.09292929292929', '20.30909090909091', '21.47272727272726', '22.57575757575757', '23.63636363636365']
        data = [decimal.Decimal(item) for item in data]

        hma = prosperpy.overlays.HullMovingAverage(prices[:10])
        self.assertEqual(hma.period, 3)
        # The first 3 (period) values should be None
        self.assertIsNone(hma.value)
        self.assertIsNone(hma(prices[10]))
        self.assertIsNone(hma(prices[11]))

        for price, value in zip(prices[12:], data):
            self.assertEqual(hma(price), value)


if __name__ == '__main__':
    unittest.main()
