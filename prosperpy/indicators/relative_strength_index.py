import decimal


class RelativeStrengthIndex:
    def __init__(self, candles):
        self.period = len(candles)

        gains = []
        losses = []
        for candle in candles:
            delta = candle.close - candle.previous.close
            if delta > 0:
                gains.append(delta)
            elif delta < 0:
                losses.append(abs(delta))

        self.average_gain = decimal.Decimal(sum(gains) / self.period)
        self.average_loss = decimal.Decimal(sum(losses) / self.period)

    @property
    def value(self):
        if self.average_loss == 0:
            return decimal.Decimal('100.0')

        if self.average_gain == 0:
            return decimal.Decimal('0.0')

        return decimal.Decimal('100.0') - decimal.Decimal('100.0') / (1 + (self.average_gain / self.average_loss))

    def smooth(self, average, value):
        return (average * (self.period - 1) + value) / self.period

    def add(self, candle):
        delta = candle.close - candle.previous.close
        gain = decimal.Decimal('0.0')
        loss = decimal.Decimal('0.0')

        if delta > 0:
            gain = delta
        else:
            loss = abs(delta)

        self.average_gain = self.smooth(self.average_gain, gain)
        self.average_loss = self.smooth(self.average_loss, loss)
