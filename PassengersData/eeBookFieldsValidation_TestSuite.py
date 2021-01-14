"""
Contains test cases for eeBook's Passenger Data fields validation on passengers screen.
"""

# If you want to execute these scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import os
import sys
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
import unittest2 as unittest
import random
import string
from datetime import date, timedelta
from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeBookTCV.tcvIBEUtils.CommonFunctions import waitForSplashScreenToDissapear
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM

cfg = configurator.Configurator()
baseURL = cfg.URL
initlog.removeOldFile("eeBookFieldsValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBookFieldsValidation_TestSuite_%s" % cfg.gridHost, multipleLogs=True).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

# generate random string (for names or relationship field)
randomString = ''.join(random.choice(string.ascii_lowercase) for x in range(61))

# generate random date (for enterTestCase)
randomDate = (date.today() + timedelta(random.randint(90, 95))).strftime("%d.%m.%Y")

# save formatted elements and their locators as key/value pairs (e.g. "email_adult-passenger-1": "id")
passengerElements = {}
emergencyContactElements = {}

testData = [  # Valid input field data
            {"firstName": "Tester",
             "lastName": "McTesterson",
             "phoneNumber": "093117666",
             "email": "tester.mctesterson@email.com",
             # TODO
             # sp.getFQTVNo() method returns wrong data, needs to be checked
             #"fqtvNumber": sp.getFQTVNo()},
             "fqtvNumber": "0123456789"},

            # Invalid input field data
            {"firstName": randomString,
             "lastName": randomString,
             "phoneNumber": "123ABC",
             "email": "noemail.com",
            # TODO
            # sp.getFQTVNo() method returns wrong data, needs to be checked
             #"fqtvNumber": sp.getFQTVNo() + "A"},
             "fqtvNumber": "0123456789A"},

            # No input field data
            {"firstName": "",
             "lastName": "",
             "phoneNumber": "",
             "email": "",
             "fqtvNumber": ""},

            # Valid emergency contact input data
            {"emergency_first_name": "Testy",
             "emergency_last_name": "Testinsky",
             "emergency_relationship": "Brother from another mother",
             "emergency_phonenum": "093354155"},

            # Invalid emergency contact input data
            {"emergency_first_name": randomString,
             "emergency_last_name": randomString,
             "emergency_relationship": randomString,
             "emergency_phonenum": "ABC345"},

            # No emergency contact input data
            {"emergency_first_name": "",
             "emergency_last_name": "",
             "emergency_relationship": "",
             "emergency_phonenum": ""}]


class EEBKG_PD_ValidateFields(unittest.TestCase):
    """
    Used for running eeBook Passenger screen input field test suite.
    """
    @classmethod
    def setUpClass(cls):
        if not os.path.isdir("./screenshots/"):
            os.mkdir("screenshots")
        if not os.path.isdir("./logs/"):
            os.mkdir("logs")

    def enterFlightDetailsAndGoToPaxScreen(self):
        """
        Enters flight details and goes to Passenger screen.
        """
        sp.useClass(self.driver, cfg) \
            .enterTestcase(self.driver, cfg.URL, sp.origin, sp.destination, "OW", randomDate, "", 1, 1, 1, "", "", "",
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

    def enterFields(self, firstName, lastName, phoneNumber, email, fqtvNumber):
        """
        Populates input fields with test data and creates dictionary with formatted elements
        as keys and their locators as values.
        :param firstName: string - First name to enter
        :param lastName: string - Last name to enter
        :param phoneNumber: string - Phone number to enter
        :param email: string - email to enter
        :param fqtvNumber: string - FQTV number to enter
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
            # Enter first name
            firstNameElem = "firstName" + paxElem % (pax, paxNumber)
            self.driver.find_element_by_xpath('//*[@id="%s"]' % firstNameElem).send_keys(firstName)
            passengerElements[firstNameElem] = "id"

            # Enter last name
            lastNameElem = "lastName" + paxElem % (pax, paxNumber)
            self.driver.find_element_by_xpath('//*[@id="%s"]' % lastNameElem).send_keys(lastName)
            passengerElements[lastNameElem] = "id"

            if passenger == "adult":
                # Enter phone number
                phoneNumberElem = "phoneNumber" + paxElem % (pax, paxNumber)
                self.driver.find_element_by_xpath('//*[@id="%s"]' % phoneNumberElem).send_keys(phoneNumber)
                passengerElements[phoneNumberElem] = "id"

                # Enter email
                emailElem = "email" + paxElem % (pax, paxNumber)
                self.driver.find_element_by_xpath('//*[@id="%s"]' % emailElem).send_keys(email)
                passengerElements[emailElem] = "id"

            if passenger != "infant" and sp.fqtv:
                # We must select FQTV to test input
                Select(self.driver.find_element_by_id("fqtv_program" + paxElem % (pax, paxNumber))) \
                    .select_by_index("1")

                # Enter FQTV number
                fqtvNumberElem = "fqtvNumber" + paxElem % (pax, paxNumber)
                #self.driver.find_element_by_xpath('//*[@name="%s"]' % fqtvNumberElem).send_keys(fqtvNumber)
                time.sleep(0.5)
                self.driver.find_element_by_name(fqtvNumberElem).send_keys(fqtvNumber)
                passengerElements[fqtvNumberElem] = "name"
        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

    def findErrorElements(self, elementDict):
        """
        Finds error elements if they exist.
        :param elementDict: Dictionary with element names / locators to use (e.g. passengerElements = {})
        :return: list of errors found
        """
        errorsFound = []

        for element, locator in list(elementDict.items()):
            try:
                time.sleep(0.5)
                self.driver.implicitly_wait(0)
                self.driver.find_element_by_xpath("//input[@%s='%s']/following-sibling::small" % (locator, element))
                errorsFound.append(element)
            except NoSuchElementException:
                continue
        return errorsFound

    def test_01_validInputData(self):
        """
        Validates no error messages are shown when valid input data is entered.
        """
        logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.enterFields(**testData[0])

        found = self.findErrorElements(passengerElements)

        if not found:
            logger.info("SUCCESS: No errors were found")
        else:
            logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_invalidInputData(self):
        """
        Validates error messages are shown when invalid input data is entered.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.enterFields(**testData[1])

        expected = list(passengerElements.keys())
        found = self.findErrorElements(passengerElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_03_noInputData(self):
        """
        Validates error messages are shown when no input data is entered.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.enterFields(**testData[2])

        expected = list(passengerElements.keys())
        found = self.findErrorElements(passengerElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_04_validEmergencyContactInputData(self):
        """
        Validates no error messages are shown when valid input data is entered.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterFlightDetailsAndGoToPaxScreen()
        time.sleep(2)
        self.driver.find_element_by_xpath("//*[@for='emergency_contact']").click()

        for elementKey, elementValue in list(testData[3].items()):
            self.driver.find_element_by_id(elementKey).send_keys(elementValue)
            emergencyContactElements[elementKey] = "id"
        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

        found = self.findErrorElements(emergencyContactElements)

        if not found:
            logger.info("SUCCESS: No errors were found")
        else:
            logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_05_invalidEmergencyContactInputData(self):
        """
        Validates error messages are shown when invalid input data is entered.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterFlightDetailsAndGoToPaxScreen()
        time.sleep(2)
        self.driver.find_element_by_xpath("//*[@for='emergency_contact']").click()

        for elementKey, elementValue in list(testData[4].items()):
            self.driver.find_element_by_id(elementKey).send_keys(elementValue)
            emergencyContactElements[elementKey] = "id"
        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

        expected = list(emergencyContactElements.keys())
        found = self.findErrorElements(emergencyContactElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_06_noEmergencyContactInputData(self):
        """
        Validates error messages are shown when no input data is entered.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterFlightDetailsAndGoToPaxScreen()
        time.sleep(2)
        self.driver.find_element_by_xpath("//*[@for='emergency_contact']").click()

        for elementKey, elementValue in list(testData[5].items()):
            self.driver.find_element_by_id(elementKey).send_keys(elementValue)
            emergencyContactElements[elementKey] = "id"
        self.driver.find_element_by_xpath("//button[contains(@class, 'btn-primary')]").click()

        expected = list(emergencyContactElements.keys())
        found = self.findErrorElements(emergencyContactElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def tearDown(self):
        # If the driver is still active, close it.
        if self.driver:
            time.sleep(2)
            self.driver.quit()
            time.sleep(2)
