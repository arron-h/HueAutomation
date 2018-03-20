from astral import Astral

class LocationAwareness(object):

    def __init__(self, city):
        self.astral = Astral()
        self.city = self.astral[city]

    def get_sun(self):
        return self.city.sun()

    def get_timezone(self):
        return self.city.tz
