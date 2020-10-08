"""
Contains test cases for eeBook's included cabin baggage and checked baggage comparison from Availability to Summary Screen.
"""
# If you want to execute this scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import sys
import os
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
import unittest2 as unittest
from eeqcutils.universalCaseReader import UniversalCaseReader
from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM

cfg = configurator.Configurator()
testData = UniversalCaseReader.getCasesFromFile("./SummaryScreen/{}_EEBKG_SS_PaxAndFltCombinations.csv".format(cfg.airline.upper()))
baseURL = cfg.URL
initlog.removeOldFile("eeBookIncludedBags_TestSuite_", "../", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("eeBookIncludedBags_TestSuite_%s" % cfg.gridHost).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_SS_IncludedBags(unittest.TestCase):
    """
    Used for running eeBook Included checked and cabin Bags test suite.
    """
    @classmethod
    def setUpClass(cls):
        if not os.path.isdir("./screenshots/"):
            os.mkdir("screenshots")
        if not os.path.isdir("./logs/"):
            os.mkdir("logs")

    def failSubTest(self, failureMsg=None):
        """
        Called when a sub-test fails to take a screenshot and log additional messages if needed.
        :param failureMsg: String - if set it will be logged as part of unittest fail() method.
        :return:
        """
        try:
            failureMsg = self.driver.find_element_by_xpath("//div[@class='alert alert-danger']//small").text
            logger.info("WARNING: Test case not loaded, error message found: {}".format(failureMsg))
        except:
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/")

        self.fail(failureMsg)

    def setUp(self):
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

    def test_checkIncludedBags(self):
        """
        Proceed to Summary Screen and check if the correct cabin and checked bags are included.
        """
        for test in testData:
            with self.subTest(case=test):
                # Set the test case number parameter which is then used for later logging/screenshots
                self.tcNumber = test.TCNumber
                logger.info("Running case: {}".format(test.TCNumber))
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
                includedBaggageList = zip(fareFamilyNamesList, (zip(cabinBaggageList, checkedBaggageList)))

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
                for ticketType in includedBaggageList:
                    if ticketType[0].lower() == outboundFareName.lower():
                        outboundSelectedBaggage = ticketType
                        break

                # Compare the active Inbound Ticket Type with the list of Ticket Types to get the needed baggage allowances
                if test.type == "RT":
                    for ticketType in includedBaggageList:
                        if ticketType[0].lower() == inboundFareName.lower():
                            inboundSelectedBaggage = ticketType
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

                    # Read baggages for outbound flights
                    summaryOutboundServicesList = servicesList[0].find_elements_by_class_name("passenger-service-item")
                    outboundServicesList = []
                    try:
                        summaryCabinBaggage = str(summaryOutboundServicesList[0].text)
                        if "Cabin baggage" in summaryCabinBaggage:
                            summaryCabinBaggage = summaryCabinBaggage.split(" ")
                            del summaryCabinBaggage[1:5]
                            outboundServicesList.append(summaryCabinBaggage)
                        elif "Cabin baggage" not in summaryCabinBaggage:
                            outboundServicesList.append("No")
                    except:
                        outboundServicesList.append("No")

                    try:
                        summaryCheckedBaggage = str(summaryOutboundServicesList[1].text)
                        if "Checked baggage" in summaryCheckedBaggage:
                            summaryCheckedBaggage = summaryCheckedBaggage.split(" ")
                            del summaryCheckedBaggage[1:5]
                            outboundServicesList.append(summaryCheckedBaggage)
                        elif "Checked baggage" not in summaryCheckedBaggage:
                            outboundServicesList.append(["No"])
                    except:
                        outboundServicesList.append(["No"])

                    # Read baggages for inbound flights
                    if test.type == "RT":
                        summaryInboundServicesList = servicesList[1].find_elements_by_class_name("passenger-service-item")
                        inboundServicesList = []
                        try:
                            summaryCabinBaggage = str(summaryInboundServicesList[0].text)
                            if "Cabin baggage" in summaryCabinBaggage:
                                summaryCabinBaggage = summaryCabinBaggage.split(" ")
                                del summaryCabinBaggage[1:5]
                                inboundServicesList.append(summaryCabinBaggage)
                            elif "Cabin baggage" not in summaryCabinBaggage:
                                inboundServicesList.append(["No"])
                        except:
                            inboundServicesList.append(["No"])

                        try:
                            summaryCheckedBaggage = str(summaryInboundServicesList[1].text)
                            if "Checked baggage" in summaryCabinBaggage:
                                summaryCheckedBaggage = summaryCheckedBaggage.split(" ")
                                del summaryCheckedBaggage[1:5]
                                outboundServicesList.append(summaryCheckedBaggage)
                            elif "Checked baggage" not in summaryCheckedBaggage:
                                inboundServicesList.append(["No"])
                        except:
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
                    logger.info(
                        "Checking if the included baggage on the Availability and Summary screen are a match...")
                    if outboundSelectedBaggage == outboundBaggageList:
                        logger.info("Included Outbound Baggage on the Availability and Summary screen are the same!")
                    else:
                        self.failSubTest()
                    if test.type == "RT":
                        if inboundSelectedBaggage == inboundBaggageList:
                            logger.info("Included Outbound Baggage on the Availability and Summary screen are the same!")
                        else:
                            self.failSubTest()

                # TODO
                # better implement try except


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

    def tearDown(self):
        # If the driver is still active, close it.
        if self.driver:
            time.sleep(2)
            self.driver.quit()
            time.sleep(2)
