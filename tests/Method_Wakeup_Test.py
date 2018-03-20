import unittest, datetime
from ..HueStateValues import HueStateValues
from ..Method_Wakeup import Method_Wakeup

class Method_Wakeup_Test(unittest.TestCase):

    def make_opts(self, alarm):
        opts = {}
        opts['period'] = 30
        opts['alarm'] = alarm.strftime("%H:%M:%S")

        return opts

    def time_func(self, tz=None):
        return datetime.datetime.now(tz)

    def test_OffBeforeAlarmPeriod(self):
        # Wakeup in 120 minutes
        method = Method_Wakeup(self.make_opts(
             datetime.datetime.now() + datetime.timedelta(minutes=35)
        ))

        state = method.execute(self.time_func)
        self.assertEqual(False, state['on'])

    def test_OnAfterAlarmPeriod(self):
        # Wakeup 10 minutes ago
        method = Method_Wakeup(self.make_opts(
             datetime.datetime.now() - datetime.timedelta(minutes=10)
        ))

        state = method.execute(self.time_func)
        self.assertEqual(True, state['on'])
        self.assertEqual(HueStateValues.CT_COOL, state['ct'])
        self.assertEqual(HueStateValues.BRI_MAX, state['bri'])

    def test_TransitionsBrightnessAndTempDuringPeriod(self):
        # Wakeup in 15 minutes
        method = Method_Wakeup(self.make_opts(
             datetime.datetime.now() + datetime.timedelta(minutes=15)
        ))

        state = method.execute(self.time_func)
        self.assertEqual(True, state['on'])
        self.assertEqual(int(326), int(state['ct']))
        self.assertEqual(int(127.5), int(state['bri']))

        # Wakeup in 5 minutes
        method = Method_Wakeup(self.make_opts(
             datetime.datetime.now() + datetime.timedelta(minutes=5)
        ))

        state = method.execute(self.time_func)
        self.assertEqual(True, state['on'])

        expectedCt = HueStateValues.CT_COOL + (HueStateValues.CT_WARM - HueStateValues.CT_COOL) / 6.0
        expectedBri = HueStateValues.BRI_MIN + (HueStateValues.BRI_MAX - HueStateValues.BRI_MIN) / 6.0
        self.assertEqual(int(expectedCt), int(state['ct']))
        self.assertEqual(int(expectedBri), int(state['bri']))
