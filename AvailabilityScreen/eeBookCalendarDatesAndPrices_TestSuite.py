"""
This script contains test cases for selecting and comparing calendar dates and prices on the eeBook's availability screen.
"""
# If you want to execute this scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import sys
import os
import suds
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
initlog.removeOldFile("eeBookCalendarPrices_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)
filePath = "./AvailabilityScreen/{}_EEBKG_AV_PaxAndFltCombinations.csv".format(airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)



class EEBKG_AV_CalendarDatesAndPrices(TestFixturesUIBaseClass):
    """
    Used for running eeBook Calendar Dates and Prices Screen test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_AV_CalendarDatesAndPrices, self).__init__(
            tcNumber,
            logFileName="logs/eeBookCalendarPrices_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def readCalendar(self, direction):
        # Read the calendar dates with flights and prices
        try:
            flightDirection = self.driver.find_element_by_id(direction[0])
            flightCalendar = flightDirection.find_elements_by_class_name("price-tab-item")
            sp.useClass(self.driver, cfg).waitForSplashScreenToDissapear(self.driver)
            return flightCalendar
        except:
            self.logger.info("FAIL: Couldn't read the {} calendar dates.".format(direction))
            self.failSubTest()

    def checkCalendarPrices(self, flightDirection, dateDirection, calendarDirection):
        # Open the outbound/inbound calendar in the past or next week
        try:
            self.readCalendar(flightDirection[0])[dateDirection].click()
            sp.useClass(self.driver, cfg).waitForSplashScreenToDissapear(self.driver)
        except:
            self.logger.info("FAIL: Couldn't open {} calendar in the past or next week.".format(flightDirection))
            self.failSubTest()

        # There is no saved price at the start of the script to compare with the previously saved price
        savedPrice = None

        # Find valid flight dates in the calendar and add them to the list
        calendarDates = self.readCalendar(flightDirection[0])
        validCalendarDates = []
        for calendarDate in calendarDates:
            if "disabled" not in calendarDate.get_attribute("class"):
                validCalendarDates.append(calendarDate.text)
        self.logger.info("***Found {} valid priced dates in the {} flight calendar***".format(len(validCalendarDates), flightDirection))

        # Open each of the found valid dates
        for validCalendarDate in validCalendarDates:
            # Each time we open a calendar date we have to read the calendar again to avoid stale elements
            flightDates = self.readCalendar(flightDirection[0])
            for flightDate in flightDates:
                # There are valid dates hidden under the left and right calendar arrows and are displayed without the currency
                if validCalendarDate == flightDate.text or validCalendarDate == flightDate.text[:-4]:
                    try:
                        flightDate.click()
                        time.sleep(6)
                    except:
                        self.logger.info("FAIL: Couldn't open an {} priced calendar date!".format(flightDirection))
                        self.failSubTest()

                    # Find all the prices for selected date and sort them to get the lowest price in the list
                    flightPriceList = []
                    flightList = self.driver.find_element_by_id(flightDirection[0])
                    pricesList = flightList.find_element_by_class_name("availability__flights-list")
                    flightOffer = pricesList.find_elements_by_class_name("amount")
                    for amount in flightOffer:
                        flightPriceList.append(float(amount.text))
                    flightPriceList.sort()

                    # Find active calendar price and date
                    calendarDateList = self.driver.find_elements_by_class_name("price-tabs")[calendarDirection]
                    calendarActiveDate = calendarDateList.find_element_by_class_name("price-tab-item--active")
                    calendarActivePrice = float(
                        calendarActiveDate.find_elements_by_class_name("amount")[0].text)
                    calendarPriceDate = calendarActiveDate.text

                    # Check if the previously selected active date and price are correctly saved in the calendar
                    if not savedPrice:
                        self.logger.info("No previously active price and date saved yet.")
                    elif savedPrice not in calendarDateList.text:
                        self.logger.info("FAIL: Previously saved {} active price and date are NOT found!".format(flightDirection))
                        self.failSubTest()
                    else:
                        self.logger.info("SUCCESS: Previously active calendar price and date are displayed correctly: {}".format(savedPrice.replace("\n", " ")))

                    # Compare the lowest sorted price from the offered price list with the currently active calendar price to determine if the lowest price is selected as active by default
                    if flightPriceList[0] == calendarActivePrice:
                        self.logger.info("SUCCESS: Lowest {} active price is correctly selected by default: {}".format(flightDirection, calendarActivePrice))
                    else:
                        self.logger.info("FAIL: {} lowest active price is NOT selected by default!".format(flightDirection))
                        self.failSubTest()

                    # Save the active calendar price and open the next valid date in the loop
                    savedPrice = calendarPriceDate[:-4]
                    self.logger.info("Saving the new {} active price and date: {}".format(flightDirection, calendarPriceDate.replace("\n", " ")))
                    # Break the loop and go the the next date
                    break


    def test_CheckCalendarDatesAndPrices(self):
        """
        First build the deeplink for each test case.
        Checks if the correct info is shown for previously selected Calendar Dates and Prices for each case.
        If testing fails mark test case as failed and continue to the next case.
        :return:
        """
        # setup the client to clear cache by route
        if airline == "bwa":
            client = suds.client.Client(url="http://bwaint:30010/eebkgbe_support?wsdl")
        elif airline == "tcv":
            client = suds.client.Client(url="http://tcvint:30010/eebkgbe_support?wsdl")

        # Clear cache and build deeplink and loop through each test case
        for test in testData:
            with self.subTest(case=test):
                # Set the test case number parameter which is then used for later logging/screenshots
                self.tcNumber = test.TCNumber
                self.logger.info("Running case: {}".format(test.TCNumber))
                # Run the client to clear the cache by route
                client.service.clearPriceCacheByRoute(test.origin, test.destination)

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

                # Check calendar dates and prices for outbound flights 5 days prior
                self.logger.info("***Looking for priced OUTBOUND flights in the previous 5 days***")
                self.checkCalendarPrices("outbound", 0, 0)
                # Check calendar dates and prices for outbound flights 5 days after
                self.logger.info("***Looking for priced OUTBOUND flights in the next 5 days***")
                self.checkCalendarPrices("outbound", 6, 0)
                # Check calendar dates and prices for inbound flights 5 days prior
                if test.type == "RT":
                    self.logger.info("***Looking for priced INBOUND flights in the previous 5 days***")
                    self.checkCalendarPrices("inbound", 0, 1)
                    # Check calendar dates and prices for inbound flights 5 days prior
                    self.logger.info("***Looking for priced INBOUND flights in the next 5 days***")
                    self.checkCalendarPrices("inbound", 6, 1)