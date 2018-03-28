import unittest, datetime
from ..Method_SunSyncer import Method_SunSyncer

FULL_WARM = 500
FULL_COOL = 153

class Method_SunSyncer_Test(unittest.TestCase):

    class MockLocation(object):

        class MockCity(object):
            tz = None

            def set_sun_vals(self, sunrise, sunset):
                self.sunrise = sunrise
                self.sunset = sunset

            def sun(self):
                return {
                    "sunrise": self.sunrise,
                    "sunset": self.sunset
                }

        def __init__(self):
            self.city = self.MockCity()

    def time_func(self, tz=None):
        return datetime.datetime.now(tz)

    def make_opts(self, sunrise, sunset):
        opts = {}
        opts['threshold'] = 60

        mockLoc = self.MockLocation()
        mockLoc.city.set_sun_vals(sunrise, sunset)
        opts['location'] = mockLoc

        return opts

    def test_FullWarmDuringEvening(self):
        # Sunrise in 120 minutes
        method = Method_SunSyncer(self.make_opts(
             datetime.datetime.now() + datetime.timedelta(minutes=120), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=240)  # Sunset
        ))

        state = method.execute(self.time_func)
        self.assertEqual(FULL_WARM, state['ct'])

    def test_FullCoolDuringDay(self):
        # Sunset in 120 minutes
        method = Method_SunSyncer(self.make_opts(
             datetime.datetime.now() - datetime.timedelta(minutes=120), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=120)  # Sunset
        ))

        state = method.execute(self.time_func)
        self.assertEqual(FULL_COOL, state['ct'])

    def test_TransitionsWarmToCoolAM(self):
        # Sunrise 30 minutes ago
        method = Method_SunSyncer(self.make_opts(
             datetime.datetime.now() - datetime.timedelta(minutes=30), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=240)  # Sunset
        ))

        state = method.execute(self.time_func)
        expected = int(FULL_COOL + (FULL_WARM - FULL_COOL) / 2.0)
        self.assertEqual(expected, int(state['ct']))

        # Sunrise 45 minutes ago
        method = Method_SunSyncer(self.make_opts(
             datetime.datetime.now() - datetime.timedelta(minutes=45), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=240)  # Sunset
        ))

        state = method.execute(self.time_func)
        expected = int(FULL_COOL + (FULL_WARM - FULL_COOL) / 1.33333333)
        self.assertEqual(expected, int(state['ct']))

    def test_TransitionsCoolToWarmPM(self):
        # Sunset in 30 minutes
        method = Method_SunSyncer(self.make_opts(
             datetime.datetime.now() - datetime.timedelta(minutes=240), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=30)  # Sunset
        ))

        state = method.execute(self.time_func)
        expected = int(FULL_COOL + (FULL_WARM - FULL_COOL) / 2.0)
        self.assertEqual(expected, int(state['ct']))

        # Sunset in 15 minutes
        method = Method_SunSyncer(self.make_opts(
             datetime.datetime.now() - datetime.timedelta(minutes=240), # Sunrise
             datetime.datetime.now() + datetime.timedelta(minutes=15)  # Sunset
        ))

        state = method.execute(self.time_func)
        expected = int(FULL_COOL + (FULL_WARM - FULL_COOL) / 4.0)
        self.assertEqual(expected, int(state['ct']))
