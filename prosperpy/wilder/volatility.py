def true_range(candle):
    choices = [candle.high - candle.low]

    try:
        choices.append(abs(candle.high - candle.previous.close))
    except AttributeError:
        pass

    try:
        choices.append(abs(candle.low - candle.previous.close))
    except AttributeError:
        pass

    return max(choices)


class AverageTrueRange:
    def __init__(self, candles):
        self.period, self.value = self._process_candles(candles)

    @staticmethod
    def _process_candles(candles):
        data = [true_range(candle) for candle in candles]
        return len(candles), sum(data) / len(data)

    def smooth(self,  candle):
        return ((self.value * (self.period - 1)) + true_range(candle)) / self.period

    def add(self, candle):
        self.value = self.smooth(candle)
