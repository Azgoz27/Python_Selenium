"""
Contains test cases for eeBook's for checkup if the dropdown basket is hidden on the Summary Screen
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
initlog.removeOldFile("eeBookBasketHidden_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
filePath = "./SummaryScreen/{}_EEBKG_SS_PaxAndFltCombinations.csv".format(cfg.airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_SS_BasketHidden(TestFixturesUIBaseClass):
    """
    Used for running eeBook Hidden Basket test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_SS_BasketHidden, self).__init__(
            tcNumber,
            logFileName="logs/eeBookBasketHidden_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def test_checkIfBasketIsHidden(self):
        """
        Proceed to Summary screen and check if the dropdown basket is hidden
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

                # Proceed to the Pax screen
                if airline == "bwa":
                    if self.driver.find_element_by_class_name("basket-xs").is_displayed():
                        self.logger.info("Availability Screen: BASKET IS VISIBLE!")
                    else:
                        self.logger.info("FAIL! Availability Screen: BASKET IS NOT VISIBLE!")
                        self.failSubTest()
                else:
                    if self.driver.find_element_by_class_name("header__basket").is_displayed():
                        self.logger.info("Availability Screen: BASKET IS VISIBLE!")
                    else:
                        self.logger.info("FAIL! Availability Screen: BASKET IS NOT VISIBLE!")
                        self.failSubTest()

                self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

                # Skip the BWA upsell screen if it comes up
                if airline == "bwa":
                    self.skipUpsellScreen()
                else:
                    pass

                # Fill in the Pax details
                sp.useClass(self.driver, cfg).enterPaxData(test.adult, test.child, test.infant, junior=test.junior, startIndex=1)
                if airline == "bwa":
                    if self.driver.find_element_by_class_name("basket-xs").is_displayed():
                        self.logger.info("Passenger Screen: BASKET IS VISIBLE!")
                    else:
                        self.logger.info("FAIL! Passenger Screen: BASKET IS NOT VISIBLE!")
                        self.failSubTest()
                else:
                    if self.driver.find_element_by_class_name("header__basket").is_displayed():
                        self.logger.info("Passenger Screen: BASKET IS VISIBLE!")
                    else:
                        self.logger.info("FAIL! Passenger Screen: BASKET IS NOT VISIBLE!")
                        self.failSubTest()

                # Proceed to the Anx Screen
                time.sleep(2)
                self.driver.find_element_by_class_name("btn-primary").click()
                time.sleep(2)
                if airline == "bwa":
                    if self.driver.find_element_by_class_name("basket-xs").is_displayed():
                        self.logger.info("Ancillary Screen: BASKET IS VISIBLE!")
                    else:
                        self.logger.info("FAIL! Ancillary Screen: BASKET IS NOT VISIBLE!")
                        self.failSubTest()
                else:
                    if self.driver.find_element_by_class_name("header__basket").is_displayed():
                        self.logger.info("Ancillary Screen: BASKET IS VISIBLE!")
                    else:
                        self.logger.info("FAIL! Ancillary Screen: BASKET IS NOT VISIBLE!")
                        self.failSubTest()

                # Proceed to the Summary Screen
                time.sleep(2)
                self.driver.find_element_by_class_name("btn-primary").click()
                time.sleep(2)

                # Check if the basket is visible
                if airline == "bwa":
                    try:
                        self.driver.find_element_by_class_name("basket-xs").click()
                        self.logger.info("FAIL! Summary Screen: BASKET IS VISIBLE!")
                        self.failSubTest()
                    except:
                        self.logger.info("SUCCESS! Summary Screen: BASKET IS NOT VISIBLE!")

                else:
                    if not self.driver.find_element_by_class_name("header__basket").is_displayed():
                        self.logger.info("SUCCESS! Summary Screen: BASKET IS NOT VISIBLE!")
                    else:
                        self.logger.info("FAIL! Summary Screen: BASKET IS VISIBLE!")
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