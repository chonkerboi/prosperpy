import decimal


class Tick:
    def __init__(self, price, bid, ask, volume, mid=None, previous=None):
        self.price = decimal.Decimal(price)
        self.bid = decimal.Decimal(bid)
        self.ask = decimal.Decimal(ask)
        self.volume = decimal.Decimal(volume)
        self.previous = previous

        try:
            self.mid = decimal.Decimal(mid)
        except TypeError:
            self.mid = (self.ask + self.bid) / decimal.Decimal('2.0')

    def __str__(self):  # pragma: no cover
        # Cannot str self.previous because of infinite recursion.
        return '{}<price: {:.4f}, bid: {:.4f}, ask: {:.4f}, mid: {:.4f}, volume: {:.4f}>'.format(
            self.__class__.__name__, self.price, self.bid, self.ask, self.mid, self.volume)

    def __repr__(self):  # pragma: no cover
        # Cannot repr self.previous because of infinite recursion.
        return '{}({}, {}, {}, {}, mid={})'.format(
            self.__class__.__name__, repr(self.price), repr(self.ask), repr(self.bid), repr(self.volume),
            repr(self.mid))
