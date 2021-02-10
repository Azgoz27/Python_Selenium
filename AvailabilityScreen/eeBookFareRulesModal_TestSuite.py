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
initlog.removeOldFile("eeBookFareRulesModal_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBookFareRulesModal_TestSuite_%s" % cfg.gridHost).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_AV_FareRulesModal(unittest.TestCase):
    """
    Used for running eeBook Fare Rules Modal test suite.
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
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/",
                                     filePrefix=self.tcNumber + "_" + self._testMethodName)

        self.fail(failureMsg)


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
                logger.info("Checking for {} fare rules modal...".format(direction))
                fareRulesModal[0].find_element_by_class_name("btn-link").click()
                time.sleep(1)
            except:
                logger.info("FAIL: {} fare rules modal not found!!!".format(direction))
                self.failSubTest()
        elif direction[0] == "i":
            try:
                logger.info("Checking for {} fare rules modal...".format(direction))
                fareRulesModal[1].find_element_by_class_name("btn-link").click()
                time.sleep(2)
            except:
                logger.info("FAIL: {} fare rules modal not found!!!".format(direction))
                self.failSubTest()

        # Close the modal if it's not empty
        if not self.driver.find_element_by_class_name("modal-body").text:
            logger.info("FAIL: {} fare rules modal is empty!!!".format(direction))
            self.failSubTest()
        else:
            self.driver.find_element_by_xpath(
                "//div[@class='modal-content']//button[contains(@class, 'close')]").click()
            logger.info("SUCCESS: {} fare rules modal successfully checked.".format(direction))
            time.sleep(2)


    def test_CheckFareRulesModal(self):
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

                # Open fare rules modal for outbound flights
                self.checkFareRulesModalDirection("outbound")
                # Open fare rules modal for inbound flights
                if test.type == "RT":
                    self.checkFareRulesModalDirection("inbound")

    # When done close the browser window
    def tearDown(self):
        # If the driver is still active, close it.
        if self.driver:
            time.sleep(2)
            self.driver.quit()
            time.sleep(2)

