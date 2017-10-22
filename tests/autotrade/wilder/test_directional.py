import unittest
import unittest.mock
import decimal

import autotrade

decimal.getcontext().prec = 16


def get_candles():
    data = [('29.41', '30.20', '29.87'), ('29.32', '30.28', '30.24'), ('29.96', '30.45', '30.10'),
            ('28.74', '29.35', '28.90'), ('28.56', '29.35', '28.92'), ('28.41', '29.29', '28.48'),
            ('28.08', '28.83', '28.56'), ('27.43', '28.73', '27.56'), ('27.66', '28.67', '28.47'),
            ('27.83', '28.85', '28.28'), ('27.40', '28.64', '27.49'), ('27.09', '27.68', '27.23'),
            ('26.18', '27.21', '26.35'), ('26.13', '26.87', '26.33'), ('26.63', '27.41', '27.03'),
            ('26.13', '26.94', '26.22'), ('25.43', '26.52', '26.01'), ('25.35', '26.52', '25.46'),
            ('25.88', '27.09', '27.03'), ('26.96', '27.69', '27.45'), ('27.14', '28.45', '28.36'),
            ('28.01', '28.53', '28.43'), ('27.88', '28.67', '27.95'), ('27.99', '29.01', '29.01'),
            ('28.76', '29.87', '29.38'), ('29.14', '29.80', '29.36'), ('28.71', '29.75', '28.91'),
            ('28.93', '30.65', '30.61'), ('30.03', '30.60', '30.05'), ('29.39', '30.76', '30.19'),
            ('30.14', '31.17', '31.12'), ('30.43', '30.89', '30.54'), ('29.35', '30.04', '29.78'),
            ('29.99', '30.66', '30.04'), ('29.52', '30.60', '30.49'), ('30.94', '31.97', '31.47'),
            ('31.54', '32.10', '32.05'), ('31.36', '32.03', '31.97'), ('30.92', '31.63', '31.13'),
            ('31.20', '31.85', '31.66'), ('32.13', '32.71', '32.64'), ('32.23', '32.76', '32.59')]

    candles = []
    for index, item in enumerate(data):
        low, high, close = map(decimal.Decimal, item)
        candle = autotrade.Candle(low=low, high=high, open=decimal.Decimal('0.00'), close=close)

        try:
            candle.previous = candles[index-1]
        except IndexError:
            pass

        candles.append(candle)

    return candles


class TestAverageDirectionalMovement(unittest.TestCase):
    def test_raise_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            autotrade.wilder.AverageDirectionalMovement(get_candles())


class TestMinusDirectionalMovement(unittest.TestCase):
    def test_directional_movement(self):
        period = 15
        candles = get_candles()
        data = ['4.511428571428571', '4.889183673469387', '4.619956268221574', '4.289959391920033', '3.983533721068602',
                '3.698995598135130', '3.434781626839764', '3.189440082065495', '2.961622933346531', '2.750078438107493',
                '2.553644263956958', '2.801241102245747', '2.601152452085336', '2.415355848364955', '2.882830430624601',
                '2.676913971294272', '2.485705830487538', '3.388155414024142', '3.146144313022418', '3.391419719235102',
                '3.149175453575452', '2.924234349748634', '2.895360467623732', '3.128549005650608', '2.905081219532707',
                '2.697575418137514', '2.504891459699120']
        data = map(decimal.Decimal, data)

        minus_dm = autotrade.wilder.MinusDirectionalMovement(candles[0:period])
        self.assertEqual(minus_dm.period, period - 1)  # The first candle is ignored
        self.assertEqual(minus_dm.value, decimal.Decimal('4.32'))

        for candle, value in zip(candles[period:], data):
            minus_dm.add(candle)
            self.assertEqual(minus_dm.value, value)

    def test_directional_indicator(self):
        period = 15
        candles = get_candles()
        data = ['33.90594803521579', '36.36349837588415', '33.83362085899002', '29.97964187513043', '28.41836512391926',
                '25.81976825435624', '24.84846225744931', '23.40776693590424', '21.59828076633093', '19.86640635796926',
                '18.89617192349879', '20.61435136832775', '18.11619255504262', '17.36094861374958', '20.17542094822074',
                '18.72204272969498', '17.79712633997544', '23.92890339854958', '22.42779062052937', '24.04257588881927',
                '21.60176016051675', '20.64114106178588', '20.91254507226802', '22.49758631586793', '21.30940824159248',
                '19.67728736016378', '18.89078124365508']
        data = map(decimal.Decimal, data)

        true_range = autotrade.wilder.TrueRange(candles[0:period])
        minus_dm = autotrade.wilder.MinusDirectionalMovement(candles[0:period], true_range=true_range)
        self.assertEqual(minus_dm.indicator, decimal.Decimal('32.33532934131737'))

        for candle, value in zip(candles[period:], data):
            true_range.add(candle)
            minus_dm.add(candle)
            self.assertEqual(minus_dm.indicator, value)


class TestPlusDirectionalMovement(unittest.TestCase):
    def test_directional_movement(self):
        period = 15
        candles = get_candles()
        data = ['0.8264285714285714', '0.7673979591836734', '0.7125838192419824', '1.231684975010412',
                '1.743707476795383', '2.379156942738570', '2.289217161114386', '2.265701649606216', '2.443865817491486',
                '3.129303973384951', '2.905782261000312', '2.698226385214575', '3.405495929127820', '3.162246219904404',
                '2.936371489911232', '3.136630669203287', '2.912585621403052', '2.704543791302834', '3.131362091924060',
                '2.907693371072341', '4.070000987424317', '3.909286631179723', '3.630051871809743', '3.370762452394761',
                '3.349993705795135', '3.970708441095482', '3.737086409588662']
        data = map(decimal.Decimal, data)

        plus_dm = autotrade.wilder.PlusDirectionalMovement(candles[0:period])
        self.assertEqual(plus_dm.period, period - 1)  # The first candle is ignored
        self.assertEqual(plus_dm.value, decimal.Decimal('0.89'))

        for candle, value in zip(candles[period:], data):
            plus_dm.add(candle)
            self.assertEqual(plus_dm.value, value)

    def test_directional_indicator(self):
        period = 15
        candles = get_candles()
        data = ['6.211080094481424', '5.707552897604808', '5.218510602864439', '8.607418178209047', '12.43953715837662',
                '16.60701649205057', '16.56103135715002', '16.62831556500988', '17.82242414694456', '22.60590952294986',
                '21.50188338724709', '19.85626540018778', '23.71818689367206', '22.72940203198125', '20.55012679204915',
                '21.93725089630091', '20.85349506942225', '19.10088505720813', '22.32241320401097', '20.61332548694108',
                '27.91816031831011', '27.59427841755248', '26.21905777631745', '24.23935795350198', '24.57293896073465',
                '28.96407288320004', '28.18344945798794']
        data = map(decimal.Decimal, data)

        true_range = autotrade.wilder.TrueRange(candles[0:period])
        plus_dm = autotrade.wilder.PlusDirectionalMovement(candles[0:period], true_range=true_range)
        self.assertEqual(plus_dm.indicator, decimal.Decimal('6.661676646706587'))

        for candle, value in zip(candles[period:], data):
            true_range.add(candle)
            plus_dm.add(candle)
            self.assertEqual(plus_dm.indicator, value)


class TestTrueRange(unittest.TestCase):
    def test_true_range(self):
        period = 15
        candles = get_candles()
        data = ['13.30571428571429', '13.44530612244898', '13.65492711370262', '14.30957517700958', '14.01746266436604',
                '14.32621533119704', '13.82291423611154', '13.62556321924643', '13.71230870358597', '13.84285808190126',
                '13.51408250462260', '13.58879089714956', '14.35816297592459', '13.91257990621569', '14.28882419862886',
                '14.29819389872680', '13.96689433453203', '14.15925902492260', '14.02788338028527', '14.10589171026489',
                '14.57832801667454', '14.16701887262636', '13.84508895315305', '13.90615402792783', '13.63285731164727',
                '13.70908178938675', '13.25986166157341']
        data = map(decimal.Decimal, data)

        true_range = autotrade.wilder.TrueRange(candles[0:period])
        self.assertEqual(true_range.period, period - 1)  # The first candle is ignored
        self.assertEqual(true_range.value, decimal.Decimal('13.36'))

        for candle, value in zip(candles[period:], data):
            true_range.add(candle)
            self.assertEqual(true_range.value, value)


class TestDirectionalIndex(unittest.TestCase):
    @unittest.mock.patch('autotrade.wilder.MinusDirectionalMovement.add')
    @unittest.mock.patch('autotrade.wilder.PlusDirectionalMovement.add')
    @unittest.mock.patch('autotrade.wilder.TrueRange.add')
    def test_add(self, mock_true_range_add, mock_plus_directional_movement, mock_minus_directional_movement):
        period = 15
        candles = get_candles()
        index = autotrade.wilder.DirectionalIndex(candles[0:period])
        index.add(candles[period])
        self.assertTrue(mock_true_range_add.called)
        self.assertTrue(mock_plus_directional_movement.called)
        self.assertTrue(mock_minus_directional_movement.called)

    def test_directional_index(self):
        period = 15
        candles = get_candles()
        data = ['69.03519336277266', '72.86707736157085', '73.27413174381120', '55.38702266349971', '39.10829257738574',
                '21.71447074618567', '20.01335968372594', '16.93335348367206', '9.578358955511209', '6.450091331636884',
                '6.450091331636899', '1.873176216898502', '13.39088666415382', '13.39088666415381',
                '0.9200756395423420', '7.907683286829797', '7.907683286829822', '11.22017679985927',
                '0.2354791878302297', '7.679277085961185', '12.75527120544156', '14.41500339547161',
                '11.25892688414837', '3.726755492604078', '7.112824251887108', '19.09236394001392', '19.74045688230126']
        data = map(decimal.Decimal, data)

        index = autotrade.wilder.DirectionalIndex(candles[0:period])
        self.assertEqual(index.value, decimal.Decimal('65.83493282149711'))

        for candle, value in zip(candles[period:], data):
            index.add(candle)
            self.assertEqual(index.value, value)


class TestAverageDirectionalIndex(unittest.TestCase):
    def test_average_directional_index(self):
        period = 28
        candles = get_candles()
        data = ['29.96188519904392', '27.88747023050809', '26.46034259167393', '25.13515264132792', '24.14122579550874',
                '22.43367246638884', '21.37978708207258', '20.76375023374179', '20.31026831672249', '19.66374392868149',
                '18.52538761181882', '17.71020451468084', '17.80893018791891', '17.94689638037479']
        data = map(decimal.Decimal, data)

        adx = autotrade.wilder.AverageDirectionalIndex(candles[0:period])
        self.assertEqual(adx.value, decimal.Decimal('31.23657739403547'))

        for candle, value in zip(candles[period:], data):
            adx.add(candle)
            self.assertEqual(adx.value, value)


if __name__ == '__main__':
    unittest.main()
