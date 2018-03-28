import qhue, os, pprint, time, json, sys
from Method_SunSyncer import *
from Method_Wakeup import *
from LocationAwareness import *

CRED_FILE = "qhue_username.txt"
POLL_TIME = 5
TRANS_THRESH = 60
WAKEUP_THRESH = 30
ALARM_H = 6
ALARM_M = 30

class HueAutomation(object):

    def __init__(self, bridgeIP, lightConfig):
        self.managedLights = {}
        self.bridgeIP = bridgeIP

        self.lightDesc = {}
        for lightName, lightMethod in lightConfig.iteritems():
            self.lightDesc[lightName] = getattr(sys.modules[__name__], "Method_" + lightMethod)()

    def run(self):
        username = self.get_username()
        bridge = qhue.Bridge(self.bridgeIP, username)
        self.location = LocationAwareness()

        while (True):
            self.purge_lights(bridge)
            self.search_lights(bridge)

            # Iterate over lights
            for lightIdx, lightMethod in self.managedLights.iteritems():
                args = self.args_for_method(lightMethod.__class__.__name__)
                state = lightMethod.execute(args)

                if 'ct' in state and 'on' in state and 'bri' in state:
                    bridge.lights[lightIdx].state(ct=state['ct'], on=state['on'], bri=state['bri'])
                elif 'ct' in state:
                    bridge.lights[lightIdx].state(ct=state['ct'])

            time.sleep(POLL_TIME)

    def purge_lights(self, bridge):
        for lightIdx in self.managedLights.keys():
            if bridge.lights[lightIdx]()['state']['reachable'] == False:
                print ("Light \"" + bridge.lights[lightIdx]()['name'] + "\" has become inactive.")

                del self.managedLights[lightIdx]

    def search_lights(self, bridge):
        lights = bridge.lights()

        for lightIdx in lights:
            lightDetails = bridge.lights[lightIdx]()

            if not lightIdx in self.managedLights:
                if lightDetails['state']['reachable']:
                    if lightDetails['name'] in self.lightDesc:
                        print ("Found light \"" + lightDetails['name'] + "\"")
                        self.managedLights[lightIdx] = self.lightDesc[lightDetails['name']]

    # TODO: Replace with a method to construct light methods
    # which passes the 'args' as construction params.
    # Args should be retrieved from config file.
    def args_for_method(self, methodName):
        args = {}
        if methodName == "Method_SunSyncer":
            args['timezone'] = self.location.get_timezone()
            args['sun'] = self.location.get_sun()
            args['threshold'] = TRANS_THRESH
        elif methodName == "Method_Wakeup":
            args['period'] = WAKEUP_THRESH
            args['alarm'] = datetime.time(hour=ALARM_H, minute=ALARM_M)

        return args

    def get_username(self):
        if not os.path.exists(CRED_FILE):
            while True:
                try:
                    username = qhue.create_new_username(self.bridgeIP)
                    break
                except qhue.QhueException as e:
                    print("Error: {}".format(e))

            with open(CRED_FILE, "w") as cred_file:
                cred_file.write(username)
        else:
            with open(CRED_FILE, "r") as cred_file:
                username = cred_file.read()

        return username

if __name__ == "__main__":
    bridgeIP = None
    lightConfig = {}

    with open("config.json") as configFile:
        config = json.load(configFile)
        bridgeIP = config["bridgeAddress"]
        lightConfig = config["lights"]

    automation = HueAutomation(bridgeIP, lightConfig)
    automation.run()

