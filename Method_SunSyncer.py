from Method import Method
from HueStateValues import HueStateValues
import datetime

class Method_SunSyncer(Method):

    def __init__(self, options):
        self.location = options["location"]
        self.threshold = options["threshold"]

    def lerp(self, start, end, delta):
        return start + delta * (end - start)

    def interpolate_ct(self, t):
        return self.lerp(HueStateValues.CT_WARM, HueStateValues.CT_COOL, t)

    def execute(self, timeFunc):
        sun = self.location.city.sun()
        timezone = self.location.city.tz

        state = {
            'ct': HueStateValues.DEFAULT_CT,
        }

        timeNow = timeFunc(timezone)
        if timeNow <= sun['sunrise'] or timeNow >= sun['sunset']:
            state['ct'] = HueStateValues.CT_WARM
        else:
            srPlusHour = sun['sunrise'] + datetime.timedelta(minutes=self.threshold)
            ssMinusHour = sun['sunset'] - datetime.timedelta(minutes=self.threshold)

            if timeNow >= srPlusHour and timeNow <= ssMinusHour:
                state['ct'] = HueStateValues.CT_COOL
            else:
                # Interpolate
                if timeNow < srPlusHour:
                    deltaTime = srPlusHour - timeNow
                else:
                    deltaTime = timeNow - ssMinusHour

                unitDelta = deltaTime.seconds / (float(self.threshold) * 60.0)
                state['ct'] = int(self.interpolate_ct(unitDelta))

                print "[" + str(timeNow) + "]" + " (delta = " + str(deltaTime) + ") -- Interpolated ct = " + str(state["ct"]) + "(" + str(unitDelta * 100) + "%)"

        return state
