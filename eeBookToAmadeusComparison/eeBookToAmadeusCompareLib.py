"""
Lib used for generating test data for eeBook to Amadeus comparison test scripts.

Should be used by calling the getJsonAndAmadeusLists() function in a test script, in which all necessary parameters
are passed. It returns two lists with test data objects generated from supplied PNRs which can then be compared.

For example:

jsonList, amadeusList = eeBookToAmadeusCompareLib.getJsonAndAmadeusLists
                        (fileOfJsonStrings='../eeBookBWA/createdPNRs/created_PNRs_28.09.2020_13:04:14.txt',
                         airline='bwa',
                         clientcode='BWA',
                         system='development',
                         officeID='FLLBW00MA')
"""

from time import sleep
from datetime import datetime as dt
from eeqcutils.amadeusutil import AmadeusCommunicator
from eeqcutils.amadeusBookingParser import AmadeusTestData
from eeqcutils.JsonObject import generateObjectsFromFileOfJsonStrings
from eeqcutils.Flights import Flight
from eeqcutils.Passengers import Passenger


class eeBookToAmadeusComparison:

    def __init__(self, PNR, flights, passengers):
        self.PNR = PNR
        self.flights = flights
        self.passengers = passengers


def saveJsonTestData(fileOfJsonStrings, returnPNRsOnly=True):
    """
    Generates test data objects from file of json strings, or returns list of PNRs

    :param fileOfJsonStrings: txt file - file to use (usually in CreatedPNRs folder)
    :param returnPNRsOnly: boolean - set to True if only a list of PNRs from the file should be returned
    :return: list - Generated jsonTestData objects(returnPNRsOnly=False) or list of PNRs (returnPNRsOnly=True)
    """
    jsonTestData = generateObjectsFromFileOfJsonStrings(fileOfJsonStrings=fileOfJsonStrings,
                                                        separator="+++",
                                                        caseIdentifier="TC#")
    pnrList = []

    for i, data in enumerate(jsonTestData):
        PNRs = jsonTestData[i].PNR
        pnrList.append(PNRs)

    return pnrList if returnPNRsOnly else jsonTestData


def saveAmadeusTestData(fileOfJsonStrings, airline, clientcode, system, officeID):
    """
    Connects to Amadeus and generates Amadeus test data to use from PNR list taken from saveJsonTestData

    :param fileOfJsonStrings: txt file - file to use for PNR list
    :param airline: string - airline for Amadeus connection
    :param clientcode: string - client code for Amadeus connection
    :param system: string - system to use for Amadeus connection
    :param officeID: string - officeID for Amadeus connection
    :return: list - Generated AmadeusTestData objects
    """
    connectorToAmadeus = AmadeusCommunicator(url="http://{}test:30010/eebkgbe_support?wsdl".format(airline),
                                             clientcode=clientcode,
                                             system=system,
                                             officeId=officeID)
    amadeusTestData = []

    for pnr in saveJsonTestData(fileOfJsonStrings=fileOfJsonStrings, returnPNRsOnly=True):

        currentPNR = []
        tempPNR = connectorToAmadeus.getFinalPNR(pnr)

        for line in tempPNR.fullInfo:
            if line and line != ")" and line != ") " and line.strip():
                currentPNR.append(line)

        amadeusTD = AmadeusTestData(currentPNR, hasTcIdentifier=False)
        amadeusTestData.append(amadeusTD)
        sleep(1)

    return amadeusTestData


def unifyTestData(testData):
    """
    Used to unify test data formats (e.g. date format differences or client specific parameters) and build new objects

    :param testData: list - objects returned from saveAmadeusTestData and saveJsonTestData
    :return: list - unified test data objects
    """
    builtList = []

    for i, data in enumerate(testData):

        PNRs = testData[i].PNR
        passengers = []
        flights = []

        for flight in data.flights:
            newFlight = Flight(carrier=flight.carrier,
                               number=flight.number,
                               date=dt.strptime(flight.date, '%d.%m.%Y').strftime('%d%b') if hasattr(flight, 'date')
                               else dt.strptime(flight.departureDate, '%d%b').strftime('%d%b'),
                               departureTime=None,
                               arrivalTime=None,
                               originCode=flight.originCode if hasattr(flight, 'originCode') else flight.origin,
                               destinationCode=flight.destinationCode if hasattr(flight, 'destinationCode')
                               else flight.destination,
                               direction=None,
                               seqNum=None,
                               bookingClass=None,
                               fare=None,
                               originFull=None,
                               destinationFull=None,
                               includedServices=None)
            flights.append(newFlight)

        for passenger in data.passengers:
            newPassenger = Passenger(firstName=passenger.firstName,
                                     lastName=passenger.lastName,
                                     paxType=passenger.paxType if passenger.paxType != 'junior' else 'adult',
                                     seqNum=None,
                                     dateOfBirth=None,
                                     paxMiles=None,
                                     fqtvNumber=None,
                                     fqtvProgram=None,
                                     passengerTitle=None,
                                     assignedInf=None,
                                     assignedAdt=None)

            passengers.append(newPassenger)

        comparison = eeBookToAmadeusComparison(PNR=PNRs,
                                               flights=flights,
                                               passengers=passengers)
        builtList.append(comparison)

    return builtList


def getJsonAndAmadeusLists(fileOfJsonStrings, airline, clientcode, system, officeID):
    """
    Function to call in test scripts

    :param fileOfJsonStrings: txt file - file that's supplied to saveJsonTestData and saveAmadeusTestData
    :param airline: string - airline to use for Amadeus connection in saveAmadeusTestData
    :param clientcode: string - client code to use for Amadeus connection in saveAmadeusTestData
    :param system: string - system to use for Amadeus connection in saveAmadeusTestData
    :param officeID: string - officeID to use for Amadeus connection in saveAmadeusTestData
    :return: lists - jsonList and amadeusList that are used in test scripts for comparison
    """
    jsonList = unifyTestData(saveJsonTestData(fileOfJsonStrings=fileOfJsonStrings,
                                              returnPNRsOnly=False))

    amadeusList = unifyTestData(saveAmadeusTestData(fileOfJsonStrings=fileOfJsonStrings,
                                                    airline=airline,
                                                    clientcode=clientcode,
                                                    system=system,
                                                    officeID=officeID))

    return jsonList, amadeusList
