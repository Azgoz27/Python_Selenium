"""
Contains test cases for eeBook's Passenger Data dropdown menu validation on passengers screen.
"""

# If you want to execute these scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import os
import sys
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
# import unittest2 as unittest
import random
import string
from datetime import date, timedelta, datetime
from dateutil.parser import parse
# from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeBookTCV.tcvIBEUtils.CommonFunctions import waitForSplashScreenToDissapear
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

baseURL = cfg.URL
airline = cfg.airline
initlog.removeOldFile("eeBookTravelDocumentValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

# generate random dates (for enterTestCase)
randomOutboundDate = (date.today() + timedelta(random.randint(90, 95))).strftime("%d.%m.%Y")
randomInboundDate = (date.today() + timedelta(random.randint(100, 105))).strftime("%d.%m.%Y")

# save formatted elements and their locators as key/value pairs (e.g. "nationality_adult-passenger-1": "id")
travelDocumentElements = {}

testData = [  # Valid travel doc info
            {"nationality": [i for i in range(1, sp.numberOfCountries(airline))],
             "docType": sp.documentType,
             "docNumber": ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(15)),
             "expirationDate": (datetime.now() + timedelta(weeks=random.randint(1, 500))).strftime('%d %m %Y').split(),
             "issuingCountry": [i for i in range(1, sp.numberOfCountries(airline))],
             "gender": [1, 2]},

            # Invalid travel doc info
            {"nationality": [0, 0],
             "docType": [0, 0],
             "docNumber": ''.join(random.choice(string.ascii_lowercase + string.digits) for y in range(16)),
             "expirationDate": (datetime.now() - timedelta(1)).strftime('%d %m %Y').split(),
             "issuingCountry": [0, 0],
             "gender": [0, 0]},

            # Invalid travel doc info #2
            {"nationality": [0, 0],
             "docType": [0, 0],
             "docNumber": "",
             "expirationDate": None,  # last flight date minus one day is used
             "issuingCountry": [0, 0],
             "gender": [0, 0]}
]

class EEBKG_PD_ValidateTravelDocument(TestFixturesUIBaseClass):
    """
    Used for running eeBook Passenger screen travel document test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_PD_ValidateTravelDocument, self).__init__(
            tcNumber,
            logFileName="logs/eeBookTravelDocumentValidation_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def enterFlightDetailsAndGoToPaxScreen(self):
        """
        Enters flight details and goes to Passenger screen.
        """
        sp.useClass(self.driver, cfg) \
            .enterTestcase(self.driver, baseURL, sp.origin, sp.destination, "RT", randomOutboundDate, randomInboundDate,
                           1, 1, 1, "", "", "", "", sp.appID if airline == "bwa" else sp.fakeIP)

        waitForSplashScreenToDissapear(self.driver)
        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

        # Skip the BWA upsell screen if it comes up
        if airline == "bwa":
            self.skipUpsellScreen()
        else:
            pass

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

    def selectAndEnterTravelDocument(self, nationality, docType, docNumber, expirationDate, issuingCountry, gender):
        """
        Selects Travel document dropdowns and enters test data. Creates dictionary with formatted elements
        as keys and their locators as values.
        :param nationality: Nationality to select
        :param docType: Document type to select
        :param docNumber: string - Document Number to enter
        :param expirationDate: Expiration date to select
        :param issuingCountry: Issuing country to select
        :param gender: Gender to select
        """
        paxElem = "_%s-%s"

        for paxNumber, passenger in enumerate(sp.paxType, start=1):
            if passenger == 'adult':
                pax = 'adt'
            elif passenger == 'junior':
                pax = 'jun'
            elif passenger == 'child':
                pax = 'chd'
            elif passenger == 'infant':
                pax = 'inf'
            travelDocumentCheckbox = self.driver.find_element_by_xpath("//*[@for='travel_document{}']".format(paxElem % (pax, paxNumber)))
            # temporary fix
            # if not travelDocumentCheckbox.is_selected():
            if not travelDocumentCheckbox.is_selected():
                travelDocumentCheckbox.click()

            # Select nationality
            nationalityElem = "nationality" + paxElem % (pax, paxNumber)
            Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % nationalityElem))\
                .select_by_index(random.choice(nationality))
            travelDocumentElements[nationalityElem] = "id"

            # Select document type
            documentTypeElem = "doc_type" + paxElem % (pax, paxNumber)
            Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % documentTypeElem))\
                .select_by_index(random.choice(docType))
            travelDocumentElements[documentTypeElem] = "id"

            # Enter document number
            documentNumberElem = "doc_number" + paxElem % (pax, paxNumber)
            self.driver.find_element_by_xpath('//*[@name="%s"]' % documentNumberElem).send_keys(docNumber)

            # Select expiration date
            for element, value in zip(["expirate_day", "expirate_month", "expirate_year"], expirationDate):
                expirationDateElem = element + paxElem % (pax, paxNumber)
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % expirationDateElem)).select_by_value(value)
                travelDocumentElements[expirationDateElem] = "id"

            # Select issuing country
            issuingCountryElem = "issuing_country" + paxElem % (pax, paxNumber)
            Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % issuingCountryElem))\
                .select_by_index(random.choice(issuingCountry))
            travelDocumentElements[issuingCountryElem] = "id"

            if airline == "tcv":
                # Select gender
                genderElem = "gender" + paxElem % (pax, paxNumber)
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % genderElem))\
                    .select_by_index(random.choice(gender))
                travelDocumentElements[genderElem] = "id"

        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

    def findErrorElements(self, elementDict):
        """
        Finds error elements if they exist.
        :param elementDict: Dictionary with element names / locators to use (e.g. dobDropdownElements = {})
        :return: list of errors found
        """
        errorsFound = []

        for element, locator in list(elementDict.items()):
            try:
                self.driver.implicitly_wait(0.3)
                self.driver.find_element_by_xpath("//select[@%s='%s']/following-sibling::small/span" % (locator, element))
                errorsFound.append(element)
            except NoSuchElementException:
                continue
        return errorsFound

    def test_01_validTravelDocumentValues(self):
        """
        Validates error messages are not shown when valid values are selected or entered.
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.

        self.enterFlightDetailsAndGoToPaxScreen()
        self.selectAndEnterTravelDocument(**testData[0])

        found = self.findErrorElements(travelDocumentElements)

        if not found:
            self.logger.info("SUCCESS: No errors were found")
        else:
            self.logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_invalidTravelDocumentValues_01(self):
        """
        Validates error messages are shown when invalid values are selected or entered.
        """
        self.logger.info("Test case: %s" % self._testMethodName)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.selectAndEnterTravelDocument(**testData[1])

        expected = list(travelDocumentElements.keys())
        found = self.findErrorElements(travelDocumentElements)

        if found and found == expected:
            self.logger.info("SUCCESS: All expected errors were found")
        else:
            self.logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_03_invalidTravelDocumentValues_02(self):
        """
        Validates error messages are shown when invalid values are selected or entered.
        This one checks if errors are shown if doc expiration date is before last flight date.
        """
        self.logger.info("Test case: %s" % self._testMethodName)

        self.enterFlightDetailsAndGoToPaxScreen()

        getLastFlightDate = self.driver.find_elements_by_class_name("basket-flight__departure")
        lastFlight = parse(getLastFlightDate[-1].text)
        testData[2]['expirationDate'] = (lastFlight - timedelta(1)).strftime('%d %m %Y').split()

        self.selectAndEnterTravelDocument(**testData[2])

        expected = list(travelDocumentElements.keys())
        found = self.findErrorElements(travelDocumentElements)

        if found and found == expected:
            self.logger.info("SUCCESS: All expected errors were found")
        else:
            self.logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)