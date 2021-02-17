"""
This script contains test cases for testing Fare Rules modal on the eeBook's availability screen.
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
initlog.removeOldFile("eeBookFareRulesModal_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)
filePath = "./AvailabilityScreen/{}_EEBKG_AV_PaxAndFltCombinations.csv".format(airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)

class EEBKG_AV_FareRulesModal(TestFixturesUIBaseClass):
    """
    Used for running eeBook Fare Rules Modal test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_AV_FareRulesModal, self).__init__(
            tcNumber,
            logFileName="logs/eeBookFareRulesModal_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def checkFareRulesModalDirection(self, direction):
        """
        Opens the fare rules modal, checks if any content is shown and then closes it. It will fail the case if it can't be loaded or no content is shown at all.
        :param direction: String - outbound or inbound
        :return:
        """
        fareRulesModal = self.driver.find_elements_by_class_name("basket-flight__compartment")
        time.sleep(1)
        # Open Fare rules modal for outbound flights
        if direction[0] == "o":
            try:
                self.logger.info("Checking for {} fare rules modal...".format(direction))
                fareRulesModal[0].find_element_by_class_name("btn-link").click()
                time.sleep(1)
            except:
                self.logger.info("FAIL: {} fare rules modal not found!!!".format(direction))
                self.failSubTest()
        elif direction[0] == "i":
            try:
                self.logger.info("Checking for {} fare rules modal...".format(direction))
                fareRulesModal[1].find_element_by_class_name("btn-link").click()
                time.sleep(2)
            except:
                self.logger.info("FAIL: {} fare rules modal not found!!!".format(direction))
                self.failSubTest()

        # Close the modal if it's not empty
        if not self.driver.find_element_by_class_name("modal-body").text:
            self.logger.info("FAIL: {} fare rules modal is empty!!!".format(direction))
            self.failSubTest()
        else:
            self.driver.find_element_by_xpath(
                "//div[@class='modal-content']//button[contains(@class, 'close')]").click()
            self.logger.info("SUCCESS: {} fare rules modal successfully checked.".format(direction))
            time.sleep(2)


    def test_CheckFareRulesModal(self):
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
                self.checkFareRulesModalDirection("outbound")
                # Open fare rules modal for inbound flights
                if test.type == "RT":
                    self.checkFareRulesModalDirection("inbound")