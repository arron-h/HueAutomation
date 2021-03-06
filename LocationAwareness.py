from astral import Astral

class LocationAwareness(object):

    def __init__(self):
        self.astral = Astral()
        self.city = self.astral['London']

    def get_sun(self):
        return self.city.sun()

    def get_timezone(self):
        return self.city.tz
