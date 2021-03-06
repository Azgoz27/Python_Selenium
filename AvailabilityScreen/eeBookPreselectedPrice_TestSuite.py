"""
This script contains test cases for testing prices preselected by default on the eeBook's availability screen.
"""
# If you want to execute this scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import sys
import os
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
initlog.removeOldFile("eeBookPreselectedPrice_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)
filePath = "./AvailabilityScreen/{}_EEBKG_AV_PaxAndFltCombinations.csv".format(airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)


class EEBKG_AV_PreselectedPrice(TestFixturesUIBaseClass):
    """
    Used for running eeBook Preselected Price Screen test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_AV_PreselectedPrice, self).__init__(
            tcNumber,
            logFileName="logs/eeBookPreselectedPrice_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def checkPreselectedPrices(self, direction):
        # Find all offered compartment prices for all outbound or inbound flights
        prices = []
        try:
            flight = self.driver.find_element_by_id(direction[0])
            flightDirection = flight.find_element_by_class_name("availability__flights-list")
            offer = flightDirection.find_elements_by_class_name("amount")
        except:
            self.failSubTest()
        for amount in offer:
            prices.append(float(amount.text))
        prices.sort()

        # Find price selected by default
        activePrice = flightDirection.find_element_by_class_name("active")
        selectedPrice = float(activePrice.find_elements_by_class_name("amount")[0].text)
        # Compare all offered prices with the selected price to determine if the lowest price is selected by default
        if prices[0] == selectedPrice:
            self.logger.info("SUCCESS: Lowest {} price is correctly selected by default.".format(direction))
        else:
            self.logger.info("FAIL: {} lowest price is NOT selected by default!".format(direction))
            self.failSubTest()

    def test_CheckPreselectedPrices(self):
        """
        First build the deeplink for each test case.
        Check if the Fare families modal is loaded for each case.
        If testing fails mark test case as failed and continue to the next case.
        :return:
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

                # Open fare rules modal for outbound flights
                self.checkPreselectedPrices("outbound")
                # Open fare rules modal for inbound flights
                if test.type == "RT":
                    self.checkPreselectedPrices("inbound")