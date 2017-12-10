import collections
import decimal


class StandardPivotPoints:
    """
    Pivot Point (P) = (High + Low + Close)/3
    Support 1 (S1) = (P x 2) - High
    Support 2 (S2) = P - (High - Low)
    Resistance 1 (R1) = (P x 2) - Low
    Resistance 2 (R2) = P + (High - Low)
    """
    def __init__(self, candles, pivots=2):
        self.period = len(candles)
        self.candles = collections.deque(candles, maxlen=self.period)
        self.support = [None] * pivots
        self.resistance = [None] * pivots
        self.pivot_point = None
        self.generate_pivots()

    def generate_pivots(self):
        high = decimal.Decimal('-infinity')
        low = decimal.Decimal('+infinity')
        close = self.candles[-1].close

        for candle in self.candles:
            if candle.high > high:
                high = candle.high
            if candle.low < low:
                low = candle.low

        self.calculate_pivot_point(high, low, close)
        self.calculate_support_levels(high, low)
        self.calculate_resistance_levels(high, low)
        self.candles = collections.deque(maxlen=self.period)

    def calculate_pivot_point(self, high, low, close):
        self.pivot_point = (high + low + close) / 3

    def calculate_support_levels(self, high, low):
        self.support[0] = (self.pivot_point * 2) - high
        self.support[1] = self.pivot_point - (high - low)

    def calculate_resistance_levels(self, high, low):
        self.resistance[0] = (self.pivot_point * 2) - low
        self.resistance[1] = self.pivot_point + (high - low)

    def add(self, candle):
        self.candles.append(candle)

        if len(self.candles) == self.candles.maxlen:
            self.generate_pivots()


class FibonacciPivotPoints(StandardPivotPoints):
    """
    Pivot Point (P) = (High + Low + Close)/3
    Support 1 (S1) = P - {.382 * (High - Low)}
    Support 2 (S2) = P - {.618 * (High - Low)}
    Support 3 (S3) = P - {1 * (High - Low)}
    Resistance 1 (R1) = P + {.382 * (High - Low)}
    Resistance 2 (R2) = P + {.618 * (High - Low)}
    Resistance 3 (R3) = P + {1 * (High - Low)}
    """
    def __init__(self, candles):
        self.fibonnaci = [decimal.Decimal('0.382'), decimal.Decimal('0.618'), decimal.Decimal('1.0')]
        super().__init__(candles, pivots=len(self.fibonnaci))

    def calculate_support_levels(self, high, low):
        for index, fibonacci in enumerate(self.fibonnaci):
            self.support[index] = self.pivot_point - (fibonacci * (high - low))

    def calculate_resistance_levels(self, high, low):
        for index, fibonacci in enumerate(self.fibonnaci):
            self.resistance[index] = self.pivot_point + (fibonacci * (high - low))


class DemarkPivotPoints(StandardPivotPoints):
    """
    If Close < Open, then X = High + (2 x Low) + Close
    If Close > Open, then X = (2 x High) + Low + Close
    If Close = Open, then X = High + Low + (2 x Close)
    Pivot Point (P) = X/4
    Support 1 (S1) = X/2 - High
    Resistance 1 (R1) = X/2 - Low
    """
    def __init__(self, candles):
        super(DemarkPivotPoints, self).__init__(candles, pivots=1)

    def generate_pivots(self):
        high = decimal.Decimal('-infinity')
        low = decimal.Decimal('+infinity')
        open = self.candles[0].open
        close = self.candles[-1].close

        for candle in self.candles:
            if candle.high > high:
                high = candle.high
            if candle.low < low:
                low = candle.low

        if close < open:
            coefficient = high + (2 * low) + close
        elif close > open:
            coefficient = (2 * high) + low + close
        else:
            coefficient = high + low + (2 * close)

        self.calculate_pivot_point(coefficient)
        self.calculate_support_levels(coefficient, high)
        self.calculate_resistance_levels(coefficient, low)
        self.candles = collections.deque(maxlen=self.period)

    def calculate_pivot_point(self, coefficient):
        self.pivot_point = coefficient / 4

    def calculate_support_levels(self, coefficient, high):
        self.support[0] = coefficient / 2 - high

    def calculate_resistance_levels(self, coefficient, low):
        self.resistance[0] = coefficient / 2 - low
