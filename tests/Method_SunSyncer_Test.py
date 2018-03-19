import unittest, datetime
from ..Method_SunSyncer import Method_SunSyncer

FULL_WARM = 500
FULL_COOL = 153

class Method_SunSyncer_Test(unittest.TestCase):

    def make_args(self, sunrise, sunset):
        args = {}
        args['timezone'] = None
        args['threshold'] = 60
        args['sun'] = {}
        args['sun']['sunrise'] = sunrise
        args['sun']['sunset'] = sunset

        return args

    def test_FullWarmDuringEvening(self):
        method = Method_SunSyncer()

        # Sunrise in 120 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() + datetime.timedelta(minutes=120), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=240)  # Sunset
        ))
        self.assertEqual(FULL_WARM, state['ct'])

    def test_FullCoolDuringDay(self):
        method = Method_SunSyncer()

        # Sunset in 120 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() - datetime.timedelta(minutes=120), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=120)  # Sunset
        ))
        self.assertEqual(FULL_COOL, state['ct'])

    def test_TransitionsWarmToCoolAM(self):
        method = Method_SunSyncer()

        # Sunrise 30 minutes ago
        state = method.execute(self.make_args(
             datetime.datetime.now() - datetime.timedelta(minutes=30), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=240)  # Sunset
        ))
        expected = FULL_COOL + (FULL_WARM - FULL_COOL) / 2.0
        self.assertEqual(expected, state['ct'])

        # Sunrise 45 minutes ago
        state = method.execute(self.make_args(
             datetime.datetime.now() - datetime.timedelta(minutes=45), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=240)  # Sunset
        ))
        expected = FULL_COOL + (FULL_WARM - FULL_COOL) / 4.0
        self.assertEqual(expected, state['ct'])

    def test_TransitionsCoolToWarmPM(self):
        method = Method_SunSyncer()

        # Sunset in 30 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() - datetime.timedelta(minutes=240), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=30)  # Sunset
        ))
        expected = FULL_COOL + (FULL_WARM - FULL_COOL) / 2.0
        self.assertEqual(expected, state['ct'])

        # Sunset in 15 minutes
        state = method.execute(self.make_args(
             datetime.datetime.now() - datetime.timedelta(minutes=240), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=15)  # Sunset
        ))
        expected = round(FULL_COOL + (FULL_WARM - FULL_COOL) / 1.3333333, 2)
        self.assertEqual(expected, state['ct'])
