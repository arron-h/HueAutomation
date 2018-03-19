import unittest, datetime
from ..HueStateValues import HueStateValues
from ..Method_Wakeup import Method_Wakeup

class Method_Wakeup_Test(unittest.TestCase):

    def make_args(self, alarm):
        args = {}
        args['period'] = 30
        args['alarm'] = alarm

        return args

    def test_OffBeforeAlarmPeriod(self):
        method = Method_Wakeup()

        # Wakeup in 120 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() + datetime.timedelta(minutes=35)
        ))
        self.assertEqual(False, state['on'])

    def test_OnAfterAlarmPeriod(self):
        method = Method_Wakeup()

        # Wakeup 10 minutes ago
        state = method.execute(self.make_args(
             datetime.datetime.now() - datetime.timedelta(minutes=10)
        ))
        self.assertEqual(True, state['on'])
        self.assertEqual(HueStateValues.CT_COOL, state['ct'])
        self.assertEqual(HueStateValues.BRI_MAX, state['bri'])

    def test_TransitionsBrightnessAndTempDuringPeriod(self):
        method = Method_Wakeup()

        # Wakeup in 15 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() + datetime.timedelta(minutes=15)
        ))
        self.assertEqual(True, state['on'])
        self.assertEqual(326.5, state['ct'])
        self.assertEqual(127.5, state['bri'])

        # Wakeup in 5 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() + datetime.timedelta(minutes=5)
        ))
        self.assertEqual(True, state['on'])

        expectedCt = HueStateValues.CT_COOL + (HueStateValues.CT_WARM - HueStateValues.CT_COOL) / 6.0
        expectedBri = HueStateValues.BRI_MIN + (HueStateValues.BRI_MAX - HueStateValues.BRI_MIN) / 6.0
        self.assertEqual(int(expectedCt), int(state['ct']))
        self.assertEqual(int(expectedBri), int(state['bri']))
