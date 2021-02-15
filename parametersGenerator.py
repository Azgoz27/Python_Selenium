from builtins import object
from xeger import Xeger
import requests
import random


class ScriptParameters(object):
    """
    Used for running different eeBook customer specific scenarios.
    """

    def __init__(self, airline, airlineClass=None):

        if airline == "bwa":
            self.fqtv = True
            self.paxType = ["adult", "child", "infant"]  # TODO - add "junior" when added as separate element
            self.documentType = [1, 1]
            self.focSSR = ["FOC_BLIND", "FOC_ASSISTANCE", "FOC_WHEELCHAIR"]
            self.origin = "POS"
            self.destination = "BGI"
            self.originConnectingFlight = "POS"
            self.destinationConnectingFlight = "JFK"
            self.appID = random.randint(1, 14)
            self.fakeIP = None
            self.eVoucher = None
            self.elementsRm = None
            self.elementsOsi = None
            self.useClass = airlineClass

        elif airline == "tcv":
            self.fqtv = False
            self.paxType = ["adult", "child", "infant"]
            self.documentType = [1, 2]
            self.focSSR = ["FOC_BLIND", "FOC_ASSISTANCE", "FOC_WHEELCHAIR"]
            self.origin = "LIS"
            self.destination = "SID"
            self.originConnectingFlight = "LIS"
            self.destinationConnectingFlight = "REC"
            self.appID = None
            self.fakeIP = False
            self.eVoucher = None
            self.elementsRm = None
            self.elementsOsi = None
            self.useClass = airlineClass

        else:
            self.travelAgencyData = {
                "travelAgencyName": None,
                "pseudoCityName": None,
                "iataNumber": None,
                "travelAgencyID": "12345678",
                "travelAgentID": None,
                "travelAgencyPhoneNumber": None,
                "travelAgencyEmail": None
            }
            self.recipientData = {
                "aggregatorID": None,
                "airlineID": "HR"
            }

            self.participantData = {
                "aggregatorID": None
            }

    @staticmethod
    def numberOfCountries(airline):
        """
        Gets number of countries for specific airline
        :param airline: airline to use
        :return: integer - number of countries
        """
        getCountries = requests.get("http://{}int:30580/catalog/countries"
                                    .format("bwa" if airline == "bwa" else "tcv")).json()
        numberOfCountries = getCountries['page']['totalElements']
        return numberOfCountries


    @staticmethod
    def defaultPhoneCode(airline):
        """
        Gets default phone code for specific airline
        :param airline: airline to use
        :return: unicode - default phone code
        """
        getDefaultPhoneCode = requests.get("http://bwaint:30580/catalog/countries?countryCode={}"
                                           .format("tt" if airline == "bwa" else "cv")).json()
        defaultPhoneCode = getDefaultPhoneCode['content'][0]['dialingPrefix']
        return defaultPhoneCode


    @staticmethod
    def getFQTVNo():
        """
        Gets current fqtv format as Regex and generates random fqtv number
        :return: unicode - random fqtv number
        """
        getFQTVProgram = requests.get("http://bwaint:30580/catalog/fqtv_simple").json()
        fqtvFormat = getFQTVProgram['content'][1]['memberIdFormat']
        randomFQTVNumber = Xeger(limit=10).xeger(fqtvFormat)
        return randomFQTVNumber

