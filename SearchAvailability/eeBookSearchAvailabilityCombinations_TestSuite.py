"""
Contains test cases for eeBook's search availability screen.
"""

import sys
import os
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
# import unittest
from eeBookBWA.bwaIBELib import bwaIbeMain
from eeBookTCV.tcvIBELib import tcvIbeMain
# from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeqcutils.universalCaseReader import UniversalCaseReader
from eeqcutils.genericMetaTestClass import GenericMetaTestClass
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils import eeBookJson
import json
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

# cfg = configurator.Configurator()
# baseURL = cfg.URL
initlog.removeOldFile("eeBookSearchAvailability_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBookSearchAvailability_TestSuite_%s" % cfg.gridHost).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)
testData = UniversalCaseReader.getCasesFromFile("./SearchAvailability/{}_EEBKG_SA_PaxAndFltCombinations.csv".format(cfg.airline.upper()))
filePath = "./SearchAvailability/{}_EEBKG_SA_PaxAndFltCombinations.csv".format(cfg.airline.upper())

class EEBKG_SA_PaxAndFltCombinations(unittest.TestCase, metaclass=GenericMetaTestClass):
    """
    Check if deep link request results in correct search results.
    """
    def namingSchema(counter,param):
        return "%03d_%s" % (counter, str(param.TCNumber))

    def logTestCase(self, case):
        logger.info("------------------------------")
        logger.info("Test case:  %s" % case.TCNumber)
        logger.info("Origin: %s" % case.origin)
        logger.info("Destination: %s" % case.destination)
        logger.info("Type: %s" % case.type)
        logger.info("Outbound date: %s" % case.outboundDate)
        logger.info("Inbound date: %s" % case.inboundDate)
        logger.info("Adults: %s" % case.adult)
        logger.info("Children: %s" % case.child)
        logger.info("Infants: %s" % case.infant)
        logger.info("eVoucher: %s" % case.EVO)
        logger.info("RM Elements: %s" % case.elementsRM)
        logger.info("OSI Elements: %s" % case.elementsOSI)

    @classmethod
    def setUpClass(cls):
        if not os.path.isdir("./screenshots/"):
            os.mkdir("screenshots")
        if not os.path.isdir("./logs/"):
            os.mkdir("logs")

        # Create the needed eeBook class instance based on the airline
        if cfg.airline.lower() == "bwa":
            cls.eebkgMain = bwaIbeMain(driver=None, cfg=cfg)
        else:
            cls.eebkgMain = tcvIbeMain(driver=None, cfg=cfg)

    def setUp(self):
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

    def originalAvailabilitySearch(self, case):
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.caseSkipped = False
        self.casePassed = False
        self.case = case

        # Log the current case.
        self.logTestCase(case)

        self.eebkgMain.driver = self.driver

        # Enter test case
        if cfg.airline == "bwa":
            self.eebkgMain.enterTestcase(self.driver, cfg.URL, case.origin, case.destination, case.type, case.outboundDate, case.inboundDate,
                                         case.adult, case.child, case.infant, case.junior, case.EVO, case.elementsRM, case.elementsOSI, cfg.appId)
        else:
            case.junior = "0"
            self.eebkgMain.enterTestcase(self.driver, cfg.URL, case.origin, case.destination, case.type, case.outboundDate, case.inboundDate,
                                         case.adult, case.child, case.infant, case.junior, case.EVO, case.elementsRM, case.elementsOSI, case.fakeIp)

        time.sleep(1)
        self.sessionId = None
        for cookie in self.driver.get_cookies():
            if cookie["name"] == "EEBKG_ID":
                self.sessionId = cookie["value"].split("-")[1]
        logger.info("Session ID: %s" % self.sessionId)
        self.eebkgMain.waitForSplashScreenToDissapear(self.driver)

        try:
            waitForPageToLoad(self.driver, selector="availability", how=By.CLASS_NAME, timeoutSeconds=5, errorSelector="alert-danger")
        except:
            # If the case doesn't load, collect the error message and fail the case
            response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                                   system=cfg.environment,
                                                   routeType=case.type,
                                                   outboundDate=case.outboundDate,
                                                   inboundDate=case.inboundDate,
                                                   origin=case.origin,
                                                   destination=case.destination,
                                                   adult=case.adult,
                                                   child=case.child,
                                                   infant=case.infant,
                                                   junior=case.junior)
            # Check response code
            logger.info("Response code found: %s" % response)
            responseParsed = json.loads(response._content)
            # Collect error code
            errorCode = responseParsed["errors"]["error"][0]["code"]
            logger.info("Error code found: %s" % errorCode)
            # Set Fail with the error codes
            self.fail("Error code found: %s" % errorCode)




        # Set the header to be static!
        element = self.driver.find_element_by_id("twoe-header")
        self.driver.execute_script("arguments[0].style.position = 'absolute';", element)

        logger.info("Checking if flights offered on outbound...")
        fare = self.driver.find_element_by_xpath(
            "//section[@id='o']//label[contains(@class, 'price-item') and contains(@class, 'active')]//span[@class='amount']").text
        logger.info("Preselected fare on outbound: %s" % fare)

        if case.type != "OW":
            logger.info("Checking if flights offered on inbound...")
            fare = self.driver.find_element_by_xpath(
                "//section[@id='i']//label[contains(@class, 'price-item') and contains(@class, 'active')]//span[@class='amount']").text
            logger.info("Preselected fare on inbound: %s" % fare)

        paxScreen = {}
        for priceElement in self.driver.find_elements_by_class_name("pax-subtotal"):
            paxType = priceElement.find_element_by_xpath(".//span[@class='col-5']").text.split()[-1].lower()
            numOfPax = priceElement.find_element_by_xpath(".//span[contains(@class, 'item-count')]").text[-1]
            paxScreen[paxType] = int(numOfPax)

        logger.info("Checking number of passengers in the basket...")
        if case.adult != "0":
            assert (paxScreen["adult"] == int(case.adult)), \
                logger.critical("Number of adult passengers is not correct. Shown: %s Actual: %s" % (paxScreen["adult"], case.adult))
        if case.child != "0":
            assert (paxScreen["child"] == int(case.child)), \
                logger.critical("Number of child passengers is not correct. Shown: %s Actual: %s" % (paxScreen["child"], case.child))
        if case.infant != "0":
            assert (paxScreen["infant"] == int(case.infant)), \
                logger.critical("Number of infant passengers is not correct. Shown: %s Actual: %s" % (paxScreen["infant"], case.infant))
        if case.junior != "0":
            assert (paxScreen["junior"] == int(case.junior)), \
                logger.critical("Number of junior passengers is not correct. Shown: %s Actual: %s" % (paxScreen["junior"], case.junior))

        chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix="%s-EEBKG_SA_PaxAndFltCombinations" % case.TCNumber)
        self.casePassed = True

    def tearDown(self):
        # If the case was skipped, skip everything below.
        if not self.caseSkipped:
            # If the case failed, take a screen shot.
            if not self.casePassed:
                try:
                    self.driver.implicitly_wait(0)
                    logger.info(self.driver.find_element_by_id("errorsection").text)
                    self.driver.implicitly_wait(30)
                except:
                    self.driver.implicitly_wait(30)
                    pass
                self.driver.switch_to.default_content()
                chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix="%s-EEBKG_SA_PaxAndFltCombinations" % self.case.TCNumber)
            # If the driver is still active, close it.
            if self.driver:
                time.sleep(2)
                self.driver.quit()
                time.sleep(2)
