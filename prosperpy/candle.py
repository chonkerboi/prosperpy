import decimal


class Candle(object):
    def __init__(self, low=decimal.Decimal('+infinity'), high=decimal.Decimal('-infinity'), open=decimal.Decimal('NaN'),
                 close=decimal.Decimal('NaN'), previous=None):
        self.low = low
        self.high = high
        self.open = open
        self.close = close
        self.previous = previous

    def __str__(self):
        return '{}<{:.2f}, {:.2f}, {:.2f}, {:.2f}>'.format(
            self.__class__.__name__, self.low, self.high, self.open, self.close)

    def __repr__(self):  # pragma: no cover
        # Cannot repr self.previous because of infinite recursion.
        return '{}(low={}, high={}, open={}, close={})'.format(
            self.__class__.__name__, self.low, self.high, self.open, self.close)
