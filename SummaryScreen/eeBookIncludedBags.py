"""
Contains test cases for eeBook's included cabin baggage and checked baggage comparison from Availability to Summary Screen.
"""
# If you want to execute this scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import sys
import os
import unittest2 as unittest
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
from eeqcutils.universalCaseReader import UniversalCaseReader
from eeqcutils.standardSeleniumImports import *
from eeqcutils import initlog
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

baseURL = cfg.URL
airline = cfg.airline
initlog.removeOldFile("eeBookIncludedBags_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
filePath = "./SummaryScreen/{}_EEBKG_SS_PaxAndFltCombinations.csv".format(cfg.airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_SS_IncludedBags(TestFixturesUIBaseClass):
    """
    Used for running eeBook Included checked and cabin Bags test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_SS_IncludedBags, self).__init__(
            tcNumber,
            logFileName="logs/eeBookIncludedBags_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def test_checkIncludedBags(self):
        """
        Proceed to Summary Screen and check if the correct cabin and checked bags are included.
        """
        for test in testData:
            with self.subTest(case=test):
                # Set the test case number parameter which is then used for later logging/screenshots
                self.tcNumber = test.TCNumber
                self.logger.info("Running case: {}".format(test.TCNumber))
                # Build deeplink and loop through each test case
                sp.useClass(self.driver, cfg).enterTestcase(self.driver,
                                                            baseURL,
                                                            test.origin,
                                                            test.destination,
                                                            test.type,
                                                            test.outboundDate,
                                                            test.inboundDate,
                                                            test.adult,
                                                            test.child,
                                                            test.infant,
                                                            test.junior,
                                                            sp.eVoucher,
                                                            sp.elementsRm,
                                                            sp.elementsOsi,
                                                            sp.appID if airline == "bwa" else sp.fakeIP
                                                            )

                # Wait to load the availability screen
                sp.useClass(self.driver, cfg).waitForSplashScreenToDissapear(self.driver)

                # Open the Ticket type Modal and read the cabin bags and checked bags info
                self.driver.find_element_by_class_name("fare-rules-modal-toggle").click()
                time.sleep(1)
                fareFamilyNames = self.driver.find_element_by_class_name("fare-family-names")
                fareFamilyNames = fareFamilyNames.find_elements_by_class_name("compartment-item__name")
                time.sleep(1)

                # List all Ticket Type names from the modal
                fareFamilyNamesList = []
                for fare in fareFamilyNames:
                    fareFamilyNamesList.append(str(fare.text))

                # List all Ticket Type cabin baggages from the Ticket Type modal
                baggageTypes = self.driver.find_elements_by_class_name("cabin-service")
                cabinBaggages = baggageTypes[0].find_elements_by_class_name("cabin-service__comparison")
                time.sleep(0.5)
                cabinBaggageList = []
                for cabinBaggage in cabinBaggages:
                    cabinBaggage = (str(cabinBaggage.text)).replace("\n", " ").replace("(", "").replace(")", "").split(
                        " ")
                    if airline == "tcv":
                        del cabinBaggage[3:]
                    cabinBaggageList.append(cabinBaggage)

                # List all Ticket Type checked baggages from the Ticket Type modal
                checkedBaggages = baggageTypes[1].find_elements_by_class_name("cabin-service__comparison")
                time.sleep(1)
                checkedBaggageList = []
                for checkedBaggage in checkedBaggages:
                    checkedBaggage = (str(checkedBaggage.text)).replace("\n", " ").replace("(", "").replace(")","").split(
                        " ")
                    checkedBaggageList.append(checkedBaggage)

                # Close the Ticket Type modal
                self.driver.find_element_by_class_name("close").click()
                time.sleep(1)

                # Create a dictionary of Ticket type names, cabin baggages and checked baggages
                includedBaggageListOutbound = zip(fareFamilyNamesList, (zip(cabinBaggageList, checkedBaggageList)))
                includedBaggageListInbound = zip(fareFamilyNamesList, (zip(cabinBaggageList, checkedBaggageList)))

                # Select the Fare Type
                sp.useClass(self.driver, cfg).selectFlight(routeType=test.type,
                                                           fareTypes=cfg.fareTypes,
                                                           outbound=test.outbound,
                                                           inbound=test.inbound,
                                                           flightCarrierOutbound=test.flightCarrierOutbound,
                                                           flightCarrierInbound=test.flightCarrierInbound,
                                                           flightNumberOutbound=test.flightNumberOutbound,
                                                           flightNumberInbound=test.flightNumberInbound,
                                                           flightStartIndex=1)


                # Get the active Outbound Ticket Type name
                flights = self.driver.find_element_by_class_name("basket__journeys")
                activeOutboundFare = flights.find_elements_by_class_name("basket-flight")[0]
                outboundFareName = str(activeOutboundFare.find_element_by_class_name("basket-flight__compartment").text)

                # Get the active Inbound Ticket Type name
                if test.type == "RT":
                    flights = self.driver.find_element_by_class_name("basket__journeys")
                    activeInboundFare = flights.find_elements_by_class_name("basket-flight")[1]
                    inboundFareName = str(activeInboundFare.find_element_by_class_name("basket-flight__compartment").text)

                # Compare the active Outbound Ticket Type with the list of Ticket Types to get the needed baggage allowances
                for ticketTypeOutbound in includedBaggageListOutbound:
                    if ticketTypeOutbound[0].lower() == outboundFareName.lower():
                        outboundSelectedBaggage = ticketTypeOutbound
                        break

                # Compare the active Inbound Ticket Type with the list of Ticket Types to get the needed baggage allowances
                if test.type == "RT":
                    for ticketTypeInbound in includedBaggageListInbound:
                        if ticketTypeInbound[0].lower() == inboundFareName.lower():
                            inboundSelectedBaggage = ticketTypeInbound
                            break

                # Proceed to the Pax screen
                self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

                # Skip the BWA upsell screen if it comes up
                if airline == "bwa":
                    self.skipUpsellScreen()
                else:
                    pass

                # Fill in the Pax details
                sp.useClass(self.driver, cfg).enterPaxData(test.adult, test.child, test.infant, junior=test.junior,
                                                           startIndex=1)

                # Proceed to the Anx Screen
                time.sleep(2)
                self.driver.find_element_by_class_name("btn-primary").click()
                time.sleep(2)

                # Proceed to the Summary Screen
                time.sleep(2)
                self.driver.find_element_by_class_name("btn-primary").click()
                time.sleep(2)

                # Read the cabin and checked baggage from the Summary Screen for each passenger
                paxList = self.driver.find_elements_by_class_name("passenger-info")
                time.sleep(0.5)
                for pax in paxList:
                    summaryServicesList = pax.find_element_by_class_name("col-md-7")
                    servicesList = summaryServicesList.find_elements_by_class_name("services")

                    # Read cabin and checked baggage list for outbound flights
                    summaryOutboundServicesList = servicesList[0].find_elements_by_class_name("passenger-service-item")
                    outboundServicesList = []

                    # Read cabin baggage
                    summaryCabinBaggageShown = False
                    try:
                        summaryCabinBaggage = str(summaryOutboundServicesList[0].text)
                        summaryCabinBaggageShown = True
                    except:
                        outboundServicesList.append("No")
                    if summaryCabinBaggageShown:
                        if "Cabin baggage" in summaryCabinBaggage:
                            summaryCabinBaggage = summaryCabinBaggage.split(" ")
                            del summaryCabinBaggage[1:5]
                            outboundServicesList.append(summaryCabinBaggage)
                        else:
                            outboundServicesList.append("No")

                    # Read checked baggage
                    summaryCheckedBaggageShown = False
                    try:
                        summaryCheckedBaggage = str(summaryOutboundServicesList[1].text)
                        summaryCheckedBaggageShown = True
                    except:
                        outboundServicesList.append(["No"])
                    if summaryCheckedBaggageShown:
                        if "Checked baggage" in summaryCheckedBaggage:
                            summaryCheckedBaggage = summaryCheckedBaggage.split(" ")
                            del summaryCheckedBaggage[1:5]
                            outboundServicesList.append(summaryCheckedBaggage)
                        else:
                            outboundServicesList.append(["No"])

                    # Read cabin and checked baggage list for inbound flights
                    if test.type == "RT":
                        summaryInboundServicesList = servicesList[1].find_elements_by_class_name("passenger-service-item")
                        inboundServicesList = []

                        # Read cabin baggage
                        summaryCabinBaggageShown = False
                        try:
                            summaryCabinBaggage = str(summaryInboundServicesList[0].text)
                            summaryCabinBaggageShown = True
                        except:
                            inboundServicesList.append(["No"])
                        if summaryCabinBaggageShown:
                            if "Cabin baggage" in summaryCabinBaggage:
                                summaryCabinBaggage = summaryCabinBaggage.split(" ")
                                del summaryCabinBaggage[1:5]
                                inboundServicesList.append(summaryCabinBaggage)
                            else:
                                inboundServicesList.append(["No"])

                        # Read checked baggage
                        summaryCheckedBaggageShown = False
                        try:
                            summaryCheckedBaggage = str(summaryInboundServicesList[1].text)
                            summaryCheckedBaggageShown = True
                        except:
                            inboundServicesList.append(["No"])
                        if summaryCheckedBaggageShown:
                            if "Checked baggage" in summaryCheckedBaggage:
                                summaryCheckedBaggage = summaryCheckedBaggage.split(" ")
                                del summaryCheckedBaggage[1:5]
                                inboundServicesList.append(summaryCheckedBaggage)
                            else:
                                inboundServicesList.append(["No"])

                    # Read the Summary Screen Ticket Type names
                    summaryTicketTypes = self.driver.find_element_by_class_name("flights-wrap")
                    summaryTicketFares = summaryTicketTypes.find_elements_by_class_name("mb-0")
                    summaryOutboundTicketType = str(summaryTicketFares[0].text).split(" ")
                    summaryOutboundFare = summaryOutboundTicketType[2]
                    if test.type == "RT":
                        summaryInboundTicketType = str(summaryTicketFares[1].text).split(" ")
                        summaryInboundFare = summaryInboundTicketType[2]

                    # Create a tuple of Ticket type names, cabin baggages and checked baggages
                    outboundBaggageList = (summaryOutboundFare, tuple(outboundServicesList))
                    if test.type == "RT":
                        inboundBaggageList = (summaryInboundFare, tuple(inboundServicesList))

                    # Compare the baggage from the Availability screen with the baggage listed on the Summary Screen
                    self.logger.info(
                        "Checking if the included baggage on the Availability and Summary screen are a match...")
                    # First check the infant special rule
                    if ((pax.text).split("\n")[1]).upper() == "INFANT":
                        if outboundSelectedBaggage[1][0] == outboundBaggageList[1][0]:
                            self.logger.info(
                                "SUCCESS: Included Outbound Baggage on the Availability and Summary screen are the same!")
                        else:
                            self.logger.info(
                                "FAIL: Included Outbound Baggage on the Availability and Summary screen are NOT the same!")
                            self.failSubTest()

                    elif outboundSelectedBaggage == outboundBaggageList:
                        self.logger.info("SUCCESS: Included Outbound Baggage on the Availability and Summary screen are the same!")
                    else:
                        self.logger.info(
                            "FAIL: Included Outbound Baggage on the Availability and Summary screen are NOT the same!")
                        self.failSubTest()

                    if test.type == "RT":
                        self.logger.info(
                            "Checking if the included Inbound baggage on the Availability and Summary screen are a match...")
                        # First check the infant special rule
                        if ((pax.text).split("\n")[1]).upper() == "INFANT":
                            if inboundSelectedBaggage[1][0] == inboundBaggageList[1][0]:
                                self.logger.info(
                                    "SUCCESS: Included Inbound Baggage on the Availability and Summary screen are the same!")
                            else:
                                self.logger.info(
                                    "FAIL: Included Inbound Baggage on the Availability and Summary screen are NOT the same!")
                                self.failSubTest()

                        elif inboundSelectedBaggage == inboundBaggageList:
                            self.logger.info("SUCCESS: Included Inbound Baggage on the Availability and Summary screen are the same!")
                        else:
                            self.logger.info(
                                "FAIL: Included Outbound Baggage on the Availability and Summary screen are NOT the same!")
                            self.failSubTest()


    def skipUpsellScreen(self):
        """
        Skips Upsell screen for BWA test cases
        """
        try:
            waitForPageToLoad(self.driver, selector="upsell", how=By.CLASS_NAME, timeoutSeconds=10)
            time.sleep(2)
            self.driver.find_element_by_class_name("btn-primary").click()
            time.sleep(2)
        except:
            pass