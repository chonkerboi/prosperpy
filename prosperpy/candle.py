import decimal
import enum


class Trend(enum.Enum):
    UP = True
    DOWN = False


class Candle(object):
    def __init__(self, timestamp=None, low=decimal.Decimal('+infinity'), high=decimal.Decimal('-infinity'),
                 open=decimal.Decimal('NaN'), close=decimal.Decimal('NaN'), price=decimal.Decimal('0'),
                 volume=decimal.Decimal('0'), previous=None):
        self.timestamp = timestamp
        self.low = low
        self.high = high
        self.open = open
        self.close = close
        self.price = price
        self.volume = volume
        self.previous = previous

    @property
    def trend(self):
        if self.price >= self.previous.price:
            return Trend.UP
        else:
            return Trend.DOWN

    def __str__(self):  # pragma: no cover
        return '{}<{} {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}>'.format(
            self.__class__.__name__, self.timestamp, self.low, self.high, self.open, self.close, self.price,
            self.volume)

    def __repr__(self):  # pragma: no cover
        # Cannot repr self.previous because of infinite recursion.
        return '{}(timestamp={}, low={}, high={}, open={}, close={}, price={}, volume={})'.format(
            self.__class__.__name__, repr(self.timestamp), repr(self.low), repr(self.high), repr(self.open),
            repr(self.close), repr(self.price), repr(self.volume))
