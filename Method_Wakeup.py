from Method import Method
from HueStateValues import HueStateValues
import datetime

class Method_Wakeup(Method):

    def __init__(self, options):
        self.period = options["period"]
        self.alarm = datetime.datetime.strptime(
            options["alarm"], "%H:%M:%S").time()

    def lerp(self, start, end, delta):
        return start + delta * (end - start)

    def interpolate_ct(self, t):
        return self.lerp(HueStateValues.CT_COOL, HueStateValues.CT_WARM, t)

    def interpolate_bri(self, t):
        return self.lerp(HueStateValues.BRI_MIN, HueStateValues.BRI_MAX, t)

    def execute(self, timeFunc):
        timeNow = timeFunc()
        state = {
            'on': True,
            'ct': HueStateValues.DEFAULT_CT,
            'bri': HueStateValues.DEFAULT_BRI
        }

        alarmToday = datetime.datetime.combine(datetime.date.today(), self.alarm)

        if timeNow.time() < (alarmToday - datetime.timedelta(minutes=self.period)).time():
            state['on'] = False
        elif timeNow.time() >= self.alarm:
            state['ct'] = HueStateValues.CT_COOL
            state['bri'] = HueStateValues.BRI_MAX
        else:
            # Interpolate
            deltaTime = alarmToday - timeNow
            unitDelta = deltaTime.seconds / (float(self.period) * float(60.0))

            state['ct'] = self.interpolate_ct(unitDelta)
            state['bri'] = self.interpolate_bri(unitDelta)

        return state
