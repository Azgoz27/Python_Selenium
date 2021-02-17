"""
This script contains test cases for testing Flight Details modal on the eeBook's availability screen.
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
initlog.removeOldFile("eeBookFlightDetailsModal_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)
filePath = "./AvailabilityScreen/{}_EEBKG_AV_PaxAndFltCombinations.csv".format(airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)


class EEBKG_AV_FlightDetailsModal(TestFixturesUIBaseClass):
    """
    Used for running eeBook Flight Details Modal test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_AV_FlightDetailsModal, self).__init__(
            tcNumber,
            logFileName="logs/eeBookFlightDetailsModal_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def checkFlightDetailsModalDirection(self, direction):
        """
        Opens the flight details modal, checks if the modal contains the flight number and then closes it. Will fail the case if it can't
        be loaded or no content is shown,
        :param direction: String - outbound or inbound
        :return:
        """
        if direction[0] == "o":
            try:
                flights = self.driver.find_elements_by_class_name("basket-flight")[0]
            except:
                self.failSubTest()
        else:
            flights = self.driver.find_elements_by_class_name("basket-flight")[1]
        flight = flights.find_elements_by_class_name("basket-leg__number")

        for flightNumber in flight:
            # Read the Flight Number and open the Flight Details modal
            try:
                self.logger.info("Checking for {} flight details modal...".format(direction))
                number = flightNumber.find_element_by_class_name("flightNumber")
                flightNumberClicked = number.text
                number.click()
                time.sleep(2)
            except:
                self.logger.info("FAIL: {} flight details modal not found!!!".format(direction))
                self.failSubTest()

            # Close the modal if it's not empty
            # TODO:
            # Sinisa: Verify here if the modal contains flightNumber. It's going to be a more precise check than
            # only checking if any text appeared.
            if not self.driver.find_element_by_class_name("flight-details-modal").text:
                self.logger.info("FAIL: {} flight details modal is empty!!!".format(direction))
                self.failSubTest()
            else:
                # Check if correct Flight Number is present
                try:
                    flightNumberShown = self.driver.find_elements_by_xpath("//div[@class='modal-content']//div[@class='flight-details-modal']//div[@class='col content']/span/span[@class='code']/..")
                    time.sleep(1)
                    flightNumbersFound = []
                    for number in flightNumberShown:
                        flightNumbersFound.append(number.text)
                        self.logger.info("{} Flight Number {} is successfully found in the modal!".format(direction, number.text))
                    time.sleep(2)
                except:
                    self.logger.info("FAIL: {} Flight Number not found!!!".format(direction))
                    self.failSubTest()
                # Compare the Flight Number clicked and the modal Flight Number
                if flightNumberClicked in flightNumbersFound:
                    self.logger.info("SUCCESS: {} Flight Number {} is opened and is found in the modal!".format(direction, flightNumberClicked))
                else:
                    self.logger.info(
                        "SUCCESS: {} Flight Number opened and Flight Number shown in the modal are NOT a match!".format(
                            direction))
                    self.failSubTest()
                # Close the modal
                self.driver.find_element_by_xpath(
                    "//div[@class='modal-content']//button[contains(@class, 'close')]").click()
                self.logger.info("SUCCESS: {} flight details modal successfully checked!".format(direction))
                time.sleep(2)

    def test_CheckFlightDetailsModal(self):
        """
        First build the deeplink for each test case.
        Check if the Fare families modal is loaded for each case.
        If testing fails mark test case as failed and continue to the next case.
        :return:
        """
        for test in testData:
            with self.subTest(case=test, name="{}_{}-{}-{}".format(test.TCNumber, test.origin, test.destination, test.type)):
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

                # Open flight details modal for outbound flights
                self.checkFlightDetailsModalDirection("outbound")
                # Open flight details modal for inbound flights
                if test.type == "RT":
                    self.checkFlightDetailsModalDirection("inbound")