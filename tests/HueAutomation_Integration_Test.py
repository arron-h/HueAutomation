import unittest, datetime
from ..HueAutomation import HueAutomation
from ..LocationAwareness import *

class HueAutomation_Test(unittest.TestCase):

    def time_getter(self):
        now = datetime.datetime.now()
        now.replace(hour=self.timeStart.hour,
                    minute=self.timeStart.minute + self.timer)
        self.timer = self.timer + 1
        return now

    def test_SingleWakeupLight(self):
        location = LocationAwareness('London')
        bridgeIP = "192.168.0.23"

        lightConfig = {
            "SAD Lamp": {
                "method": "Wakeup",
                "options": {
                    "alarm": "07:00:00",
                    "period": 30
                }
            }
        }

        self.timer = 0
        self.timeStart = datetime.time(hour=6, minute=30)

        automation = HueAutomation(bridgeIP, lightConfig, location)
        automation.run(1, self.time_getter)

if __name__ == "__main__":
  unittest.main()
