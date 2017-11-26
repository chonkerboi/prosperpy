import unittest
import unittest.mock
import decimal

import prosperpy


def get_candles():
    data = ['44.34', '44.09', '44.15', '43.61', '44.33', '44.83', '45.10', '45.42', '45.84', '46.08', '45.89', '46.03',
            '45.61', '46.28', '46.28', '46.00', '46.03', '46.41', '46.22', '45.64', '46.21', '46.25', '45.71', '46.45',
            '45.78', '45.35', '44.03', '44.18', '44.22', '44.57', '43.42', '42.66', '43.13']

    candles = []
    for index, item in enumerate(data):
        close = decimal.Decimal(item)
        candle = prosperpy.Candle(close=close)

        try:
            candle.previous = candles[index-1]
        except IndexError:
            pass

        candles.append(candle)

    return candles


class TestRelativeStrengthIndex(unittest.TestCase):
    def test_relative_strength_index(self):
        period = 14
        candles = get_candles()
        data = ['66.24961855355508', '66.48094183471267', '69.34685316290870', '66.29471265892625', '57.91502067008556',
                '62.88071830996238', '63.20878871828775', '56.01158478954756', '62.33992931089785', '54.67097137765515',
                '50.38681519511423', '40.01942379131357', '41.49263540422286', '41.90242967845816', '45.49949723868043',
                '37.32277831337997', '33.09048257272346', '37.78877198205783']
        data = [decimal.Decimal(item) for item in data]

        rsi = prosperpy.indicators.RelativeStrengthIndex(candles[1:period+1])
        self.assertEqual(rsi.period, period)
        self.assertEqual(rsi.value, decimal.Decimal('70.46413502109705'))

        for candle, value in zip(candles[period+1:], data):
            rsi.add(candle)
            self.assertEqual(rsi.value, value)

    def test_zero_average_gain(self):
        period = 14
        candles = get_candles()
        rsi = prosperpy.indicators.RelativeStrengthIndex(candles[1:period + 1])
        rsi.average_gain = 0
        self.assertEqual(rsi.value, decimal.Decimal('0.0'))

    def test_zero_average_loss(self):
        period = 14
        candles = get_candles()
        rsi = prosperpy.indicators.RelativeStrengthIndex(candles[1:period + 1])
        rsi.average_loss = 0
        self.assertEqual(rsi.value, decimal.Decimal('100.0'))


if __name__ == '__main__':
    unittest.main()
