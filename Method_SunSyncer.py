from Method import Method
from HueStateValues import HueStateValues
import datetime, math

class Method_SunSyncer(Method):

    def lerp(self, start, end, delta):
        return start + delta * (end - start)

    def interpolate_ct(self, t):
        return self.lerp(HueStateValues.CT_COOL, HueStateValues.CT_WARM, t)

    def execute(self, args):
        sun = args['sun']
        timezone = args['timezone']
        threshold = args['threshold']

        state = {
            'ct': HueStateValues.DEFAULT_CT,
        }

        timeNow = datetime.datetime.now(timezone)
        if timeNow <= sun['sunrise'] or timeNow >= sun['sunset']:
            state['ct'] = HueStateValues.CT_WARM
        else:
            srPlusHour = sun['sunrise'] + datetime.timedelta(minutes=threshold)
            ssMinusHour = sun['sunset'] - datetime.timedelta(minutes=threshold)

            if timeNow >= srPlusHour and timeNow <= ssMinusHour:
                state['ct'] = HueStateValues.CT_COOL
            else:
                # Interpolate
                if timeNow < srPlusHour:
                    deltaTime = srPlusHour - timeNow
                else:
                    deltaTime = timeNow - ssMinusHour

                unitDelta = deltaTime.seconds / (float(threshold) * 60.0)
                state['ct'] = self.interpolate_ct(unitDelta)

        return state
