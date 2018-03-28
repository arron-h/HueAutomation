import qhue, os, time, json, sys
from Method_SunSyncer import *
from Method_Wakeup import *
from LocationAwareness import *

CRED_FILE = "qhue_username.txt"

class HueAutomation(object):

    def __init__(self, bridgeIP, lightConfig, location):
        self.managedLights = {}
        self.bridgeIP = bridgeIP
        self.location = location

        self.lightDesc = {}
        for lightName, lightValDict in lightConfig.iteritems():
            lightMethod = lightValDict["method"]
            lightOpts = lightValDict["options"]
            lightOpts["location"] = self.location
            self.lightDesc[lightName] = self.construct_light(lightMethod, lightOpts)

    def construct_light(self, methodName, options):
        methodClass = getattr(sys.modules[__name__], "Method_" + methodName)
        return methodClass(options)

    def run(self, pollFrequency, timeFunc):
        username = self.get_username()
        bridge = qhue.Bridge(self.bridgeIP, username)

        while (True):
            self.purge_lights(bridge)
            self.search_lights(bridge)

            # Iterate over lights
            for lightIdx, lightMethod in self.managedLights.iteritems():
                state = lightMethod.execute(timeFunc)

                if 'ct' in state and 'on' in state and 'bri' in state:
                    bridge.lights[lightIdx].state(ct=state['ct'], on=state['on'], bri=state['bri'])
                elif 'ct' in state:
                    bridge.lights[lightIdx].state(ct=state['ct'])

            time.sleep(pollFrequency)

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

def time_getter(timezone):
    return datetime.datetime.now(timezone)

if __name__ == "__main__":
    bridgeIP = None
    location = None
    lightConfig = {}

    with open("config.json") as configFile:
        config = json.load(configFile)
        bridgeIP = config["bridgeAddress"]
        lightConfig = config["lights"]
        city = config["city"]
        pollFrequency = config["pollFrequency"]

    if city == None:
        print ("Config Error: Missing 'city' key in JSON configuration")
        sys.exit(-1)

    location = LocationAwareness(city)
    automation = HueAutomation(bridgeIP, lightConfig, location)
    automation.run(pollFrequency, time_getter)

