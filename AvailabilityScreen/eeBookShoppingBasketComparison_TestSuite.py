"""
This script contains test cases for testing shopping basket comparison on the eeBook's availability screen.
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
testData = UniversalCaseReader.getCasesFromFile("./AvailabilityScreen/{}_EEBKG_AV_PaxAndFltCombinations.csv".format(cfg.airline.upper()))
baseURL = cfg.URL
initlog.removeOldFile("eeBookShoppingBasketComparison_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBookShoppingBasketComparison_TestSuite_%s" % cfg.gridHost).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_AV_ShoppingBasketComparison(unittest.TestCase):
    """
    Used for running eeBook Shopping Basket comparison test suite.
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
            error = self.driver.find_element_by_xpath("//div[@class='alert alert-danger']//small").text
            logger.info("WARNING: Test case not loaded, error message found: {}".format(error))
        except:
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/",
                                     filePrefix=self.tcNumber + "_" + self._testMethodName)

        self.fail(failureMsg)

    def compareShoppingBaskets(self):
        # Parsing information from the lower (main) shopping basket on the availability screen
        # Parsing list of flight numbers
        lowerFlightNumberList = []
        for flightType in self.driver.find_elements_by_class_name("basket-flights"):
            for flightNumber in (flightType.find_elements_by_class_name("flightNumber")):
                lowerFlightNumberList.append(flightNumber.text)
        # Parsing list of travel dates
        lowerTravelDateList = []
        for travelDate in (self.driver.find_elements_by_class_name("basket-flight__departure")):
            lowerTravelDateList.append(travelDate.text)
        # Parsing list of flight departure times
        lowerDepartureTimeList = []
        for departureTime in (self.driver.find_elements_by_class_name("basket-departure__time")):
            lowerDepartureTimeList.append(departureTime.text)
        # Parsing list of flight arrival times
        lowerArrivalTimeList = []
        for arrivalTime in (self.driver.find_elements_by_class_name("basket-arrival__time")):
            lowerArrivalTimeList.append(arrivalTime.text)
        # Parsing list of departing airports
        lowerDepartureAirportList = []
        for departureAirport in (self.driver.find_elements_by_class_name("basket-departure__airport")):
            lowerDepartureAirportList.append(
                departureAirport.text.replace("\n", " ").replace("(", "").replace(")", ""))
        # Parsing list of arriving airports
        lowerArrivalAirportList = []
        for arrivalAirport in (self.driver.find_elements_by_class_name("basket-arrival__airport")):
            lowerArrivalAirportList.append(
                arrivalAirport.text.replace("\n", " ").replace("(", "").replace(")", ""))

        # Parsing the total price
        try:
            lowerTotalPrice = self.driver.find_elements_by_class_name("basket-total__amount")[0].text
        except:
            self.failSubTest()

        # This opens the upper (drop-down) shopping basket on the availability screen
        self.driver.find_element_by_class_name("icon-shopping-cart").click()
        time.sleep(2)

        # Parsing information from the upper (drop-down) shopping basket on the availability screen
        # Parsing list of flight numbers
        upperFlightNumberList = []
        for flightType in self.driver.find_elements_by_class_name("basket-xs__body"):
            for flightNumber in (flightType.find_elements_by_class_name("flightNumber")):
                upperFlightNumberList.append(flightNumber.text)
        # Parsing list of travel dates
        upperTravelDateList = []
        for travelDate in (self.driver.find_elements_by_class_name("basket-flight-xs__departure")):
            upperTravelDateList.append(travelDate.text)
        # Parsing list of flight departure times
        upperDepartureTimeList = []
        for departureTime in (
                self.driver.find_elements_by_xpath("//span[contains(@class, 'basket-departure-xs__time')]")):
            upperDepartureTimeList.append(departureTime.text)
        # Parsing list of flight arrival times
        upperArrivalTimeList = []
        for arrivalTime in (self.driver.find_elements_by_class_name("basket-arrival-xs__time")):
            upperArrivalTimeList.append(arrivalTime.text)
        # Parsing list of departing airports
        upperDepartureAirportList = []
        for departureAirport in (self.driver.find_elements_by_class_name("basket-departure-xs__airport")):
            upperDepartureAirportList.append(
                departureAirport.text.replace("\n", " ").replace("(", "").replace(")", ""))
        # Parsing list of arriving airports
        upperArrivalAirportList = []
        for arrivalAirport in (self.driver.find_elements_by_class_name("basket-arrival-xs__airport")):
            upperArrivalAirportList.append(
                arrivalAirport.text.replace("\n", " ").replace("(", "").replace(")", ""))
        # Parsing the total price
        upperTotalPrice = self.driver.find_elements_by_class_name("basket-price-row-xs__amount")[0].text

        # Comparison of content in lower (main) and upper (drop-down) baskets
        # Comparison of upper and lower flight number lists
        if lowerFlightNumberList == upperFlightNumberList:
            logger.info("SUCCESS: Flight Numbers in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Flight Numbers in both upper and lower baskets are not the same!")
            self.failSubTest()
        # Comparison of upper and lower travel date lists
        if lowerTravelDateList == upperTravelDateList:
            logger.info("SUCCESS: Travel Dates in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Travel Dates in both upper and lower baskets is not the same!")
            self.failSubTest()
        # Comparison of upper and lower departure time lists
        if lowerDepartureTimeList == upperDepartureTimeList:
            logger.info("SUCCESS: Departure Times in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Departure Times in both upper and lower baskets are not the same!")
            self.failSubTest()
        # Comparison of upper and lower arrival time lists
        if lowerArrivalTimeList == upperArrivalTimeList:
            logger.info("SUCCESS: Arrival Times in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Arrival Times in both upper and lower baskets are not the same!")
            self.failSubTest()
        # Comparison of upper and lower departing airport lists
        if lowerDepartureAirportList == upperDepartureAirportList:
            logger.info("SUCCESS: Departure Airports in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Departure Airports in both upper and lower baskets are not the same!")
            self.failSubTest()
        # Comparison of upper and lower arriving airport lists
        if lowerArrivalAirportList == upperArrivalAirportList:
            logger.info("SUCCESS: Arrival Airports in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Arrival Airports in both upper and lower baskets are not the same!")
            self.failSubTest()
        # Comparison of upper and lower total prices
        if lowerTotalPrice == upperTotalPrice:
            logger.info("SUCCESS: Total Price in both upper and lower baskets match!")
        else:
            logger.info("FAIL: Total Price in both upper and lower baskets are not the same!")
            self.failSubTest()

    def test_CompareShoppingBaskets(self):
        """
        First build the deeplink for each test case.
        Check if the Fare families modal is loaded for each case.
        If testing fails mark test case as failed and continue to the next case.
        :return:
        """
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
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

                # Start comparing shopping baskets
                self.compareShoppingBaskets()

    def tearDown(self):
        # If the driver is still active, close it.
        if self.driver:
            time.sleep(2)
            self.driver.quit()
            time.sleep(2)

