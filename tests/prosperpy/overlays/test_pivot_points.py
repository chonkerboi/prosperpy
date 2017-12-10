import unittest
import decimal

import prosperpy


def get_candles():
    data = [('29.41', '30.20', '29.87'), ('29.32', '30.28', '30.24'), ('29.96', '30.45', '30.10'),
            ('28.74', '29.35', '28.90'), ('28.56', '29.35', '28.92'), ('28.41', '29.29', '28.48'),
            ('28.08', '28.83', '28.56'), ('27.43', '28.73', '27.56'), ('27.66', '28.67', '28.47'),
            ('27.83', '28.85', '28.28'), ('27.40', '28.64', '27.49'), ('27.09', '27.68', '27.23'),
            ('26.18', '27.21', '26.35'), ('26.13', '26.87', '26.33'), ('26.63', '27.41', '27.03'),
            ('26.13', '26.94', '26.22'), ('25.43', '26.52', '26.01'), ('25.35', '26.52', '25.46'),
            ('25.88', '27.09', '27.03'), ('26.96', '27.69', '27.45'), ('27.14', '28.45', '28.36'),
            ('28.01', '28.53', '28.43'), ('27.88', '28.67', '27.95'), ('27.99', '29.01', '29.01'),
            ('28.76', '29.87', '29.38'), ('29.14', '29.80', '29.36'), ('28.71', '29.75', '28.91'),
            ('28.93', '30.65', '30.61'), ('30.03', '30.60', '30.05'), ('29.39', '30.76', '30.19')]

    candles = []
    for index, item in enumerate(data):
        low, high, close = map(decimal.Decimal, item)
        candle = prosperpy.Candle(low=low, high=high, close=close)

        try:
            candle.previous = candles[index-1]
            candle.open = candle.previous.close
        except IndexError:
            candle.open = candle.close

        candles.append(candle)

    return candles


class TestStandardPivotPoints(unittest.TestCase):
    def test_standard_pivot_points(self):
        candles = get_candles()

        spp = prosperpy.overlays.StandardPivotPoints(candles[:10])
        self.assertEqual(spp.pivot_point, decimal.Decimal('28.72'))
        self.assertEqual(spp.support[0], decimal.Decimal('26.99'))
        self.assertEqual(spp.support[1], decimal.Decimal('25.70'))
        self.assertEqual(spp.resistance[0], decimal.Decimal('30.01'))
        self.assertEqual(spp.resistance[1], decimal.Decimal('31.74'))

        for candle in candles[10:20]:
            spp.add(candle)

        self.assertEqual(spp.pivot_point, decimal.Decimal('27.14666666666667'))
        self.assertEqual(spp.support[0], decimal.Decimal('25.65333333333334'))
        self.assertEqual(spp.support[1], decimal.Decimal('23.85666666666667'))
        self.assertEqual(spp.resistance[0], decimal.Decimal('28.94333333333334'))
        self.assertEqual(spp.resistance[1], decimal.Decimal('30.43666666666667'))

        for candle in candles[20:30]:
            spp.add(candle)

        self.assertEqual(spp.pivot_point, decimal.Decimal('29.36333333333333'))
        self.assertEqual(spp.support[0], decimal.Decimal('27.96666666666666'))
        self.assertEqual(spp.support[1], decimal.Decimal('25.74333333333333'))
        self.assertEqual(spp.resistance[0], decimal.Decimal('31.58666666666666'))
        self.assertEqual(spp.resistance[1], decimal.Decimal('32.98333333333333'))


class TestFibonacciPivotPoints(unittest.TestCase):
    def test_fibonacci_pivot_points(self):
        candles = get_candles()

        fpp = prosperpy.overlays.FibonacciPivotPoints(candles[:10])
        self.assertEqual(fpp.pivot_point, decimal.Decimal('28.72'))
        self.assertEqual(fpp.support[0], decimal.Decimal('27.56636'))
        self.assertEqual(fpp.support[1], decimal.Decimal('26.85364'))
        self.assertEqual(fpp.support[2], decimal.Decimal('25.700'))
        self.assertEqual(fpp.resistance[0], decimal.Decimal('29.87364'))
        self.assertEqual(fpp.resistance[1], decimal.Decimal('30.58636'))
        self.assertEqual(fpp.resistance[2], decimal.Decimal('31.740'))

        for candle in candles[10:20]:
            fpp.add(candle)

        self.assertEqual(fpp.pivot_point, decimal.Decimal('27.14666666666667'))
        self.assertEqual(fpp.support[0], decimal.Decimal('25.88988666666667'))
        self.assertEqual(fpp.support[1], decimal.Decimal('25.11344666666667'))
        self.assertEqual(fpp.support[2], decimal.Decimal('23.85666666666667'))
        self.assertEqual(fpp.resistance[0], decimal.Decimal('28.40344666666667'))
        self.assertEqual(fpp.resistance[1], decimal.Decimal('29.17988666666667'))
        self.assertEqual(fpp.resistance[2], decimal.Decimal('30.43666666666667'))

        for candle in candles[20:30]:
            fpp.add(candle)

        self.assertEqual(fpp.pivot_point, decimal.Decimal('29.36333333333333'))
        self.assertEqual(fpp.support[0], decimal.Decimal('27.98049333333333'))
        self.assertEqual(fpp.support[1], decimal.Decimal('27.12617333333333'))
        self.assertEqual(fpp.support[2], decimal.Decimal('25.74333333333333'))
        self.assertEqual(fpp.resistance[0], decimal.Decimal('30.74617333333333'))
        self.assertEqual(fpp.resistance[1], decimal.Decimal('31.60049333333333'))
        self.assertEqual(fpp.resistance[2], decimal.Decimal('32.98333333333333'))


class TestDemarkPivotPoints(unittest.TestCase):
    def test_demark_pivot_points(self):
        candles = get_candles()
        candles[0].open = candles[9].close

        dpp = prosperpy.overlays.DemarkPivotPoints(candles[:10])
        self.assertEqual(dpp.pivot_point, decimal.Decimal('28.61'))
        self.assertEqual(dpp.support[0], decimal.Decimal('26.77'))
        self.assertEqual(dpp.resistance[0], decimal.Decimal('29.79'))

        for candle in candles[10:20]:
            dpp.add(candle)

        self.assertEqual(dpp.pivot_point, decimal.Decimal('26.6975'))
        self.assertEqual(dpp.support[0], decimal.Decimal('24.755'))
        self.assertEqual(dpp.resistance[0], decimal.Decimal('28.045'))

        for candle in candles[20:30]:
            dpp.add(candle)

        self.assertEqual(dpp.pivot_point, decimal.Decimal('29.7125'))
        self.assertEqual(dpp.support[0], decimal.Decimal('28.665'))
        self.assertEqual(dpp.resistance[0], decimal.Decimal('32.285'))


if __name__ == '__main__':
    unittest.main()
