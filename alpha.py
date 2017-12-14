import math

import scipy.stats


class Code:
    def __init__(self):
        self.ccyList = ["AUD_CAD"]
        '''
        "AUD_JPY", "AUD_NZD", "AUD_USD", "CAD_JPY", "CHF_JPY", "EUR_AUD", "EUR_CAD", "EUR_CHF", "EUR_GBP", "EUR_JPY",
        "EUR_NZD", "EUR_USD", "GBP_AUD", "GBP_CAD", "GBP_CHF", "GBP_JPY", "GBP_USD", "NZD_CAD", "NZD_JPY", "NZD_USD",
        "USD_CAD", "USD_CHF", "USD_JPY"};
        '''

        self.length = len(self.ccyList)
        self.trading = []
        self.deltaS = [0.25/100.0, 0.5/100.0, 1.0/100.0, 1.5/100.0]

        for ccy in self.ccyList:
            self.trading.append(FXrateTrading(ccy, self.deltaS))

        price = self.PriceFeedData()

        for trader in self.trading:
            trader.runTradingAsymm(price)


class FXrateTrading:
    def __init__(self, rate, deltas):
        self.coastTraderLong = []
        self.coastTraderShort = []
        self.FXrate = rate
        self.liquidity = None
        self.currentTime = 1136073600000.0
        self.oneDay = 24.0 * 60.0 * 60.0 * 1000.0

        for delta in deltas:
            self.coastTraderLong.append(CoastlineTrader(delta, delta, delta, delta, 1))
            self.coastTraderShort.append(CoastlineTrader(delta, delta, delta, delta, -1))

    def runTradingAsymm(self, price):
        for long, short in zip(self.coastTraderLong, self.coastTraderShort):
            long.runPriceAsymm(price, short.tP)
            short.runPriceAsymm(price, long.tP)

        if price.elems.time >= self.currentTime + self.oneDay:
            while self.currentTime <= price.elems.time:
                self.currentTime += self.oneDay
            self.printDataAsymm(self.currentTime)

    def printDataAsymm(self, time):
        print('----------')
        print(time)

        price = self.coastTraderLong[0].lastPrice
        total_long = 0
        total_short = 0
        total_pos = 0
        pnl = 0
        pnl_perc = 0

        for long, short in zip(self.coastTraderLong, self.coastTraderShort):
            total_long += long.tP
            total_short += short.tP
            total_pos += long.tP + short.tP
            pnl += long.pnl + long.tempPnl + long.computePnlLastPrice() + short.pnl + short.tempPnl + short.computePnlLastPrice()
            pnl_perc += long.pnlPerc + (long.tempPnl + long.computePnlLastPrice())/long.cashLimit*long.profitTarget + short.pnlPerc + (short.tempPnl + short.computePnlLastPrice())/short.cashLimit*short.profitTarget

        print(time, pnl, pnl_perc, total_pos, total_long, total_short, price)


class CoastlineTrader:
    def __init__(self, dOriginal, dUp, dDown, profitT, lS):
        self.tP = 0.0
        self.prices = []
        self.sizes = []
        self.profitTarget = self.cashLimit = profitT
        self.pnl = self.tempPnl = self.pnlPerc = 0.0
        self.deltaOriginal = dOriginal
        self.deltaUp = dUp
        self.deltaDown = dDown
        self.shrinkFlong = self.shrinkFshort = 1.0
        self.longShort = lS
        self.runner = None
        self.runnerG = []
        self.increaseLong = self.increaseShort = 0.0
        self.lastPrice = None
        self.liquidity = None

    def computePnl(self, price):
        # TODO: Compute PnL with current price
        return 0.0

    def computePnlLastPrice(self):
        # TODO: Compute PnL with last available price
        return 0.0

    def getPercPnl(self, price):
        # TODO: Percentage PnL
        return 0.0

    def tryToClose(self, price):
        # TODO: Check if PnL target hit implementation
        return False

    def assignCashTarget(self):
        # TODO: Compute cash value corresponding to percentage PnL
        return True

    def runPriceAsymm(self, price, oppositeInv):
        self.runner = Runner(self.deltaUp, self.deltaDown, price, self.deltaUp, self.deltaDown)
        self.runnerG.append([
            Runner(0.75*self.deltaUp, 1.50*self.deltaDown, price, 0.75*self.deltaUp, 0.75*self.deltaUp),
            Runner(0.50 * self.deltaUp, 2.00 * self.deltaDown, price, 0.50 * self.deltaUp, 0.50 * self.deltaUp)])
        self.runnerG.append([
            Runner(1.50 * self.deltaUp, 0.75 * self.deltaDown, price, 0.75 * self.deltaDown, 0.75 * self.deltaDown),
            Runner(2.00 * self.deltaUp, 0.50 * self.deltaDown, price, 0.50 * self.deltaDown, 0.50 * self.deltaDown)])
        self.liquidity = LocalLiquidity(self.deltaOriginal, self.deltaUp, self.deltaDown, self.deltaOriginal*2.525729, price, 50.0)

        self.liquidity.computation(price)

        if self.tryToClose(price):  # Try to close position
            # print('Close')
            return True

        fraction = 1.0

        if self.liquidity.liq < 0.1:
            size = 0.1
        elif self.liquidity.liq < 0.5:
            size = 0.5
        else:
            size = 1.0

        if self.liquidity.liq < 0.1:
            size = 0.1

        if self.longShort == 1: # Long positions only
            event = self.runner.run(price)

            if 15.0 <= self.tP < 30.0:
                event = self.runnerG[0][0].run(price)
                self.runnerG[0][1].run(price)
                fraction = 0.5
            elif self.tP >= 30.0:
                event = self.runnerG[0][1].run(price)
                self.runnerG[0][0].run(price)
                fraction = 0.25
            else:
                self.runnerG[0][0].run(price)
                self.runnerG[0][1].run(price)

            if event < 0:
                if self.tP == 0.0: # Open long position
                    sign = -self.runner.type
                    if abs(oppositeInv) > 15.0:
                        size = 1.0
                        if abs(oppositeInv) > 30.0:
                            size = 1.0

                    sizeToAdd = sign * size

                    if sizeToAdd < 0.0:
                        print('How did this happen! increase position but negative size: ' + str(sizeToAdd))
                        sizeToAdd = -sizeToAdd

                    self.tP += sizeToAdd
                    self.sizes.append(sizeToAdd)

                    if sign == 1:
                        self.prices.append(price.elems.ask)
                    else:
                        self.prices.append(price.elems.bid)

                    self.assignCashTarget()
                    print('Open long')

                elif self.tP > 0.0: # Increase long position (buy)
                    sign = -self.runner.type
                    sizeToAdd = sign * size * fraction * self.shrinkFlong

                    if sizeToAdd < 0.0:
                        print('How did this happen! increase position but negative size: ' + str(sizeToAdd))
                        sizeToAdd = -sizeToAdd

                    self.increaseLong += 1.0
                    self.tP += sizeToAdd
                    self.sizes.append(sizeToAdd)

                    if sign == 1:
                        self.prices.append(price.elems.ask)
                    else:
                        self.prices.append(price.elems.bid)

                    print('Cascade long')

            elif event > 0 and self.tP > 0.0: # Possibility to decrease long position only at intrinsic events
                if self.tP > 0.0:
                    pricE = price.elems.bid
                else:
                    pricE = price.elems.ask

                to_remove = []
                for i in range(0, len(self.prices)):
                    if self.tP > 0.0:
                        tempP = math.log(pricE / self.prices[i])
                        tmpDelta = self.deltaUp
                    else:
                        tempP = math.log(self.prices[i] / pricE)
                        tmpDelta = self.deltaDown

                    if tempP >= tmpDelta:
                        addPnl = (pricE - self.prices[i]) * self.sizes[i]

                        if addPnl < 0.0:
                            print("Decascade long with a loss: " + addPnl)

                        self.tempPnl += addPnl
                        self.tP -= self.sizes[i]
                        to_remove.append(i)
                        self.increaseLong += -1.0
                        print('Decascade long')

                for i in to_remove:
                    del self.prices[i]
                    del self.sizes[i]

        elif self.longShort == -1: # Short positions only
            event = self.runner.run(price)

            if -30.0 < self.tP < -15.0:
                event = self.runnerG[1][0].run(price)
                self.runnerG[1][1].run(price)
                fraction = 0.5
            elif self.tP <= -30.0:
                event = self.runnerG[1][1].run(price)
                self.runnerG[1][0].run(price)
                fraction = 0.25
            else:
                self.runnerG[1][0].run(price)
                self.runnerG[1][1].run(price)

            if event > 0:
                if self.tP == 0.0: # Open short position
                    sign = -self.runner.type
                    if abs(oppositeInv) > 15.0:
                        size = 1.0
                        if abs(oppositeInv) > 30.0:
                            size = 1.0

                    sizeToAdd = sign * size
                    if sizeToAdd > 0.0:
                        print("How did this happen! decrease position but positive size: " + str(sizeToAdd))
                        sizeToAdd = -sizeToAdd

                    self.tP += sizeToAdd
                    self.sizes.append(sizeToAdd)

                    if sign == 1:
                        self.prices.append(price.elems.bid)
                    else:
                        self.prices.append(price.elems.ask)
                    print("Open short")
                    self.assignCashTarget()

                elif self.tP < 0.0:
                    sign = -self.runner.type
                    sizeToAdd = sign * size * fraction * self.shrinkFshort

                    if sizeToAdd > 0.0:
                        print("How did this happen! decrease position but negative size: " + str(sizeToAdd))
                        sizeToAdd = -sizeToAdd

                    self.tP += sizeToAdd
                    self.sizes.append(sizeToAdd)
                    self.increaseShort += 1.0
                    if sign == 1:
                        self.prices.append(price.elems.bid)
                    else:
                        self.prices.append(price.elems.ask)

                    print("Cascade short")

            elif event < 0 and self.tP < 0.0:
                if self.tP > 0.0:
                    pricE = price.elems.bid
                else:
                    pricE = price.elems.ask

                to_remove = []
                for i in range(0, len(self.prices)):
                    if self.tP > 0.0:
                        tempP = math.log(pricE / self.prices[i])
                        tmpDelta = self.deltaUp
                    else:
                        tempP = math.log(self.prices[i] / pricE)
                        tmpDelta = self.deltaDown

                    if tempP >= tmpDelta:
                        addPnl = (pricE - self.prices[i]) * self.sizes[i]

                        if addPnl < 0.0:
                            print("Descascade short with a loss: " + addPnl)

                        self.tempPnl += (pricE - self.prices[i]) * self.sizes[i]
                        self.tP -= self.sizes[i]
                        to_remove.append(i)
                        self.increaseShort += -1.0
                        print("Decascade short")

                for i in to_remove:
                    del self.prices[i]
                    del self.sizes[i]

        else:
            raise RuntimeError("Should never happen! " + self.longShort)

        return True


class LocalLiquidity:
    def __init__(self, d, dUp, dDown, dS, price, a):
        self.surp, self.upSurp, self.downSurp = 0.0, 0.0, 0.0
        self.liq, self.upLiq, self.downLiq = 0.0, 0.0, 0.0
        self.H1, self.H2 = 0.0, 0.0

        self.type = -1
        self.deltaUp = dUp
        self.deltaDown = dDown
        self.dStar = dS
        self.delta = d
        self.alpha = a
        self.alphaWeight = math.exp(-2.0 / (a + 1.0))
        self.computeH1H2exp(dS)
        self.extreme = self.reference = price.elems.mid

    def computeH1H2exp(self, dS):
        self.H1 = -math.exp(-self.dStar/self.delta)*math.log(math.exp(-self.dStar/self.delta)) - (1.0 - math.exp(-self.dStar/self.delta))*math.log(1.0 - math.exp(-self.dStar/self.delta))
        self.H2 = math.exp(-self.dStar/self.delta)*math.pow(math.log(math.exp(-self.dStar/self.delta)), 2.0) - (1.0 - math.exp(-self.dStar/self.delta))*math.pow(math.log(1.0 - math.exp(-self.dStar/self.delta)), 2.0) - self.H1*self.H1

    def run(self, price):
        if self.type == -1:
            if math.log(price.elems.bid/self.extreme) >= self.deltaUp:
                self.type = 1
                self.extreme = price.elems.ask
                self.reference = price.elems.ask
                return 1
            if price.elems.ask < self.extreme:
                self.extreme = price.elems.ask
            if math.log(self.reference / self.extreme) >= self.dStar:
                self.reference = self.extreme
                return 2
        elif self.type == 1:
            if math.log(price.elems.ask/self.extreme) <= -self.deltaDown:
                self.type = -1
                self.extreme = price.elems.bid
                self.reference = price.elems.bid
                return -1
            if price.elems.bid > self.extreme:
                self.extreme = price.elems.bid
            if math.log(self.reference/self.extreme) <= -self.dStar:
                self.reference = self.extreme
                return -2
        return 0

    def computation(self, price):
        event = self.run(price)
        if event != 0:
            if abs(event) == 1:
                surp = 0.08338161
            else:
                surp = 2.525729
            self.surp = (self.alphaWeight * surp) + ((1.0 - self.alphaWeight) * self.surp)

            if event > 0:  # down moves
                if event == 1:
                    surp = 0.08338161
                else:
                    surp = 2.525729
                self.downSurp = (self.alphaWeight * surp) + ((1.0 - self.alphaWeight) * self.downSurp)
            elif event < 0:  # up moves
                if event == -1:
                    surp = 0.08338161
                else:
                    surp = 2.525729
                self.upSurp = (self.alphaWeight * surp) + ((1.0 - self.alphaWeight) * self.upSurp)

            self.liq = 1.0 - scipy.stats.norm.cdf(math.sqrt(self.alpha) * (surp - self.H1)/math.sqrt(self.H2))
            self.upLiq = 1.0 - scipy.stats.norm.cdf(math.sqrt(self.alpha) * (self.upSurp - self.H1) / math.sqrt(self.H2))
            self.downLiq = 1.0 - scipy.stats.norm.cdf(math.sqrt(self.alpha) * (self.downSurp - self.H1) / math.sqrt(self.H2))


class Runner:
    def __init__(self, threshUp, threshDown, price, dStarUp, dStarDown):
        self.prevExtreme = price.elems.mid
        self.prevExtremeTime = price.elems.time
        self.prevDC = price.elems.mid
        self.prevDCTime = price.elems.time
        self.extreme = price.elems.mid
        self.extremeTime = price.elems.time
        self.deltaUp = threshUp
        self.deltaDown = threshDown
        self.deltaStarUp = dStarUp
        self.deltaStarDown = dStarDown
        self.osL = 0.0
        self.type = -1
        self.reference = price.elems.mid

    def run(self, price):
        if self.type == -1:
            if math.log(price.elems.bid/self.extreme) >= self.deltaUp:
                self.prevExtreme = self.extreme
                self.prevExtremeTime = self.extremeTime
                self.type = 1
                self.extreme = price.elems.ask
                self.extremeTime = price.elems.time
                self.prevDC = price.elems.ask
                self.prevDCTime = price.elems.time
                self.reference = price.elems.ask
                return 1

            if price.elems.ask < self.extreme:
                self.extreme = price.elems.ask
                self.extremeTime = price.elems.time
                self.osL = -math.log(self.extreme/self.prevDC)/self.deltaDown

                if math.log(self.extreme/self.reference) <= -self.deltaStarUp:
                    self.reference = self.extreme
                    return -2

                return 0

        elif self.type == 1:
            if math.log(price.elems.ask/self.extreme) <= -self.deltaDown:
                self.prevExtreme = self.extreme
                self.prevExtremeTime = self.extremeTime
                self.type = -1
                self.extreme = price.elems.bid
                self.extremeTime = price.elems.time
                self.prevDC = price.elems.bid
                self.prevDCTime = price.elems.time
                self.reference = price.elems.bid
                return -1

            if price.elems.bid > self.extreme:
                self.extreme = price.elems.bid
                self.extremeTime = price.elems.time
                self.osL = math.log(self.extreme/self.prevDC)/self.deltaUp

                if math.log(self.extreme/self.reference) >= self.deltaStarDown:
                    self.reference = self.extreme
                    return 2

                return 0

        return 0
