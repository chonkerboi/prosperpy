import decimal


class Candle(object):
    def __init__(self, timestamp=None, low=decimal.Decimal('+infinity'), high=decimal.Decimal('-infinity'),
                 open=decimal.Decimal('NaN'), close=decimal.Decimal('NaN'), volume=decimal.Decimal('0'), previous=None):
        self.timestamp = timestamp
        self.low = low
        self.high = high
        self.open = open
        self.close = close
        self.volume = volume
        self.previous = previous

    @property
    def trend(self):
        return self.close - self.previous.close

    def __str__(self):  # pragma: no cover
        # Cannot str self.previous because of infinite recursion.
        return '{}<timestamp: {}, low: {:.4f}, high: {:.4f}, open: {:.4f}, close: {:.4f}, volume: {:.4f}>'.format(
            self.__class__.__name__, self.timestamp, self.low, self.high, self.open, self.close, self.volume)

    def __repr__(self):  # pragma: no cover
        # Cannot repr self.previous because of infinite recursion.
        return '{}(timestamp={}, low={}, high={}, open={}, close={}, volume={})'.format(
            self.__class__.__name__, repr(self.timestamp), repr(self.low), repr(self.high), repr(self.open),
            repr(self.close), repr(self.volume))
