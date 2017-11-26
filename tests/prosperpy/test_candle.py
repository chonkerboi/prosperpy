import unittest

import prosperpy


class TestCandle(unittest.TestCase):
    def test_candle(self):
        candle1 = prosperpy.Candle(timestamp=0, low=1, high=2, open=3, close=4, volume=5, previous=None)
        candle2 = prosperpy.Candle(6, 7, 8, 9, 10, 11, candle1)
        self.assertEqual(candle1.timestamp, 0)
        self.assertEqual(candle1.low, 1)
        self.assertEqual(candle1.high, 2)
        self.assertEqual(candle1.open, 3)
        self.assertEqual(candle1.close, 4)
        self.assertEqual(candle1.volume, 5)
        self.assertEqual(candle1.previous, None)
        self.assertEqual(candle2.timestamp, 6)
        self.assertEqual(candle2.low, 7)
        self.assertEqual(candle2.high, 8)
        self.assertEqual(candle2.open, 9)
        self.assertEqual(candle2.close, 10)
        self.assertEqual(candle2.volume, 11)
        self.assertEqual(candle2.previous, candle1)

    def test_candle_trend(self):
        candle1 = prosperpy.Candle(close=500)
        candle2 = prosperpy.Candle(close=600, previous=candle1)
        self.assertEqual(candle2.trend, 100)


if __name__ == '__main__':
    unittest.main()
