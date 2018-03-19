from Method import Method
from HueStateValues import HueStateValues
import datetime, math

class Method_Wakeup(Method):

    def lerp(self, start, end, delta):
        return start + delta * (end - start)

    def interpolate_ct(self, t):
        return self.lerp(HueStateValues.CT_COOL, HueStateValues.CT_WARM, t)

    def interpolate_bri(self, t):
        return self.lerp(HueStateValues.BRI_MIN, HueStateValues.BRI_MAX, t)

    def execute(self, args):
        period = args['period']
        alarm = args['alarm']

        timeNow = datetime.datetime.now()
        state = {
            'on': True,
            'ct': HueStateValues.DEFAULT_CT,
            'bri': HueStateValues.DEFAULT_BRI
        }

        if timeNow.time() < (alarm - datetime.timedelta(minutes=period)).time():
            state['on'] = False
        elif timeNow.time() >= alarm.time():
            state['ct'] = HueStateValues.CT_COOL
            state['bri'] = HueStateValues.BRI_MAX
        else:
            # Interpolate
            deltaTime = alarm - timeNow
            unitDelta = deltaTime.seconds / (float(period) * float(60.0))

            state['ct'] = self.interpolate_ct(unitDelta)
            state['bri'] = self.interpolate_bri(unitDelta)

        return state
