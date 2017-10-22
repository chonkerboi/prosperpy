import unittest
import decimal

import prosperpy

decimal.getcontext().prec = 16


def get_candles():
    data = [('47.79', '48.70', '48.16'), ('48.14', '48.72', '48.61'), ('48.39', '48.90', '48.75'),
            ('48.37', '48.87', '48.63'), ('48.24', '48.82', '48.74'), ('48.64', '49.05', '49.03'),
            ('48.94', '49.20', '49.07'), ('48.86', '49.35', '49.32'), ('49.50', '49.92', '49.91'),
            ('49.87', '50.19', '50.13'), ('49.20', '50.12', '49.53'), ('48.90', '49.66', '49.50'),
            ('49.43', '49.88', '49.75'), ('49.73', '50.19', '50.03'), ('49.26', '50.36', '50.31'),
            ('50.09', '50.57', '50.52'), ('50.30', '50.65', '50.41'), ('49.21', '50.43', '49.34'),
            ('48.98', '49.63', '49.37'), ('49.61', '50.33', '50.23'), ('49.20', '50.29', '49.24'),
            ('49.43', '50.17', '49.93'), ('48.08', '49.32', '48.43'), ('47.64', '48.50', '48.18'),
            ('41.55', '48.32', '46.57'), ('44.28', '46.80', '45.41'), ('47.31', '47.80', '47.77'),
            ('47.20', '48.39', '47.72'), ('47.90', '48.66', '48.62'), ('47.73', '48.79', '47.85')]

    candles = []
    for index, item in enumerate(data):
        low, high, close = map(decimal.Decimal, item)
        candle = prosperpy.Candle(low=low, high=high, open=decimal.Decimal('0.00'), close=close)

        try:
            candle.previous = candles[index-1]
        except IndexError:
            pass

        candles.append(candle)

    return candles


class TestTrueRange(unittest.TestCase):
    def test_true_range(self):
        candles = get_candles()
        data = ['0.91', '0.58', '0.51', '0.50', '0.58', '0.41', '0.26', '0.49', '0.60', '0.32', '0.93', '0.76', '0.45',
                '0.46', '1.10', '0.48', '0.35', '1.22', '0.65', '0.96', '1.09', '0.93', '1.85', '0.86', '6.77', '2.52',
                '2.39', '1.19', '0.94', '1.06']
        data = map(decimal.Decimal, data)

        for candle, value in zip(candles, data):
            self.assertEqual(prosperpy.wilder.true_range(candle), value)


class TestAverageTrueRange(unittest.TestCase):
    def test_average_true_range(self):
        period = 14
        candles = get_candles()
        data = ['0.593265306122449', '0.5851749271137026', '0.5683767180341524', '0.6149212381745701',
                '0.6174268640192436', '0.6418963737321548', '0.6739037756084294', '0.6921963630649701',
                '0.7748966228460436', '0.7809754354998979', '1.208762904392762', '1.302422696936136',
                '1.380106790012126', '1.366527733582689', '1.336061466898211', '1.316342790691196']
        data = map(decimal.Decimal, data)

        atr = prosperpy.wilder.AverageTrueRange(candles[0:period])
        self.assertEqual(atr.period, period)
        self.assertEqual(atr.value, decimal.Decimal('0.5542857142857143'))

        for candle, value in zip(candles[period:], data):
            atr.add(candle)
            self.assertEqual(atr.value, value)


if __name__ == '__main__':
    unittest.main()
