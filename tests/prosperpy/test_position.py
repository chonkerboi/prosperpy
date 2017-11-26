import unittest

import prosperpy


class TestPosition(unittest.TestCase):
    def test_position(self):
        position = prosperpy.Position(0, 1, 2)
        self.assertEqual(position.product, 0)
        self.assertEqual(position.amount, 1)
        self.assertEqual(position.price, 2)


if __name__ == '__main__':
    unittest.main()
