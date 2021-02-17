"""
Contains test cases for eeBook's Passenger Data dropdown menu validation on passengers screen.
"""

# If you want to execute these scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import sys, os
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
import random
from datetime import date, timedelta
from eeqcutils.standardSeleniumImports import *
from eeqcutils import initlog
from eeBookTCV.tcvIBEUtils.CommonFunctions import waitForSplashScreenToDissapear
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

baseURL = cfg.URL
airline = cfg.airline
initlog.removeOldFile("eeBookDropdownValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

# generate random date (for enterTestCase)
randomDate = (date.today() + timedelta(random.randint(90, 95))).strftime("%d.%m.%Y")

# save formatted elements and their locators as key/value pairs (e.g. "title_adult-passenger-1": "id")
dropdownElements = {}

testData = [  # Valid dropdown values
            {"title": [1, 2, 3],
             "gender": [1, 2],
             "phoneCode": [i for i in range(1, sp.numberOfCountries(airline))],
             "fqtvProgram": 1},

            # Invalid / No dropdown values
            {"title": [0, 0, 0],
             "gender": [0, 0],
             "phoneCode": [0 for i in range(1, sp.numberOfCountries(airline))],
             "fqtvProgram": 0}]


class EEBKG_PD_ValidateDropdowns(TestFixturesUIBaseClass):
    """
    Used for running eeBook Passenger screen dropdown test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_PD_ValidateDropdowns, self).__init__(
            tcNumber,
            logFileName="logs/eeBookDropdownValidation_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def enterFlightDetailsAndGoToPaxScreen(self):
        """
        Enters flight details and goes to Passenger screen.
        """
        sp.useClass(self.driver, cfg) \
            .enterTestcase(self.driver, baseURL, sp.origin, sp.destination, "OW", randomDate, "", 1, 1, 1, "", "", "",
                           "", sp.appID if airline == "bwa" else sp.fakeIP)

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

    def selectDropdowns(self, title, gender, phoneCode, fqtvProgram):
        """
        Selects dropdown values from test data and creates dictionary with formatted elements
        as keys and their locators as values.
        :param title: Title to select
        :param gender: Gender to select
        :param phoneCode: Phone code to select
        :param fqtvProgram: FQTV program to select
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

            # Select title
            titleElem = "title" + paxElem % (pax, paxNumber)
            if passenger == "adult":
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % titleElem)) \
                    .select_by_index(random.choice(title))
            else:
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % titleElem)) \
                    .select_by_index(random.choice(title[0:2]))
            dropdownElements[titleElem] = "id"

            # Select gender
            genderElem = "gender" + paxElem % (pax, paxNumber)
            Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % genderElem)) \
                .select_by_index(random.choice(gender))
            dropdownElements[genderElem] = "id"

            if passenger == "adult":
                # Select Phone code
                phoneCodeElem = "phoneCode" + paxElem % (pax, paxNumber)
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % phoneCodeElem)) \
                    .select_by_index(random.choice(phoneCode))
                dropdownElements[phoneCodeElem] = "id"

            if passenger != "infant" and sp.fqtv:
                # Select FQTV program
                fqtvProgramElem = "fqtv_program" + paxElem % (pax, paxNumber)
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % fqtvProgramElem)) \
                    .select_by_index(fqtvProgram)
                dropdownElements[fqtvProgramElem] = "id"

                # We must enter FQTV number to test FQTV selection
                fqtvNumberElem = "fqtvNumber" + paxElem % (pax, paxNumber)
                try:
                    self.driver.find_element_by_xpath('//*[@name="%s"]' % fqtvNumberElem).send_keys(sp.getFQTVNo())
                except:
                    self.logger.info("FQTV Numbers couldn't be entered!")
        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

    def findErrorElements(self, elementDict):
        """
        Finds error elements if they exist.
        :param elementDict: Dictionary with element names / locators to use (e.g. dropdownElements = {})
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

    def test_01_validDropdownValues(self):
        """
        Validates no error messages are shown when valid dropdown values are selected.
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.

        self.enterFlightDetailsAndGoToPaxScreen()
        self.selectDropdowns(**testData[0])

        found = self.findErrorElements(dropdownElements)

        if not found:
            self.logger.info("SUCCESS: No errors were found")
        else:
            self.logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_noDropdownValues(self):
        """
        Validates error messages are shown when no dropdown values are selected.
        """
        self.logger.info("Test case: %s" % self._testMethodName)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.selectDropdowns(**testData[1])

        expectedError = list(dropdownElements.keys())
        expected = []
        for error in expectedError:
            if "fqtv" not in error:
                expected.append(error)

        found = self.findErrorElements(dropdownElements)

        if found and found == expected:
            self.logger.info("SUCCESS: All expected errors were found")
        else:
            self.logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_03_validateDefaultPhoneCodes(self):
        """
        Validates default phone codes are shown when no other selected
        """
        self.logger.info("Test case: %s" % self._testMethodName)

        self.enterFlightDetailsAndGoToPaxScreen()
        checkPhoneCode = Select(self.driver.find_element_by_id("phoneCode_adt-1")).first_selected_option
        defaultPhoneCode = checkPhoneCode.get_attribute("value")

        if sp.defaultPhoneCode(airline) in defaultPhoneCode:
            self.logger.info("SUCCESS: Default phone code shown")
        else:
            self.logger.info("FAIL: Default phone code not shown. Code shown: %s" % defaultPhoneCode)
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)