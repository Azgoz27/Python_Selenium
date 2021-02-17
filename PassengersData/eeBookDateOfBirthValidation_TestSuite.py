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
from collections import OrderedDict
from datetimerange import DateTimeRange as timeRange
from datetime import date, timedelta, datetime
from dateutil.parser import parse
from eeqcutils.standardSeleniumImports import *
from eeqcutils import initlog
from eeBookTCV.tcvIBEUtils.CommonFunctions import waitForSplashScreenToDissapear
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

baseURL = cfg.URL
airline = cfg.airline
initlog.removeOldFile("eeBookDateOfBirthValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

# generate random dates (for enterTestCase)
randomOutboundDate = (date.today() + timedelta(random.randint(90, 95))).strftime("%d.%m.%Y")
randomInboundDate = (date.today() + timedelta(random.randint(100, 105))).strftime("%d.%m.%Y")

# save formatted elements and their locators as key/value pairs (e.g. "day_adult-passenger-1": "id")
dobDropdownElements = {}

# save passenger DOB as key/value pairs (e.g. "adult": ["26", "09", "1933"])
passengerDOB = {}
passengerDOB = OrderedDict(passengerDOB)


class EEBKG_PD_ValidateDOBDropdowns(TestFixturesUIBaseClass):
    """
    Used for running eeBook Passenger screen date of birth dropdown test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_PD_ValidateDOBDropdowns, self).__init__(
            tcNumber,
            logFileName="logs/eeBookDateOfBirthValidation_TestSuite",
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

    def generateDateOfBirthCase(self, failCase=True, endDOB=True):
        """
        Generates date of birth parameters for selectDateOfBirthDropdowns method. Takes valid range for adult, child
        or infant passenger and generates either valid or invalid DOB and saves them in passengerDOB dictionary.
        :param failCase: set True if it should generate valid pax DOB, False if it should return invalid pax DOB
        :param endDOB: set True for ending invalid DOB, False for starting invalid DOB outside of valid DOB range
        """
        getLastFlightDate = self.driver.find_elements_by_class_name("basket-flight__departure")
        time.sleep(0.5)
        lastFlight = parse(getLastFlightDate[-1].text)

        if airline == "bwa":
            adultRange = 5844
        else:
            adultRange = 4383

        validAdultDOB = timeRange(date(datetime.now().year - 100, 1, 1), lastFlight - timedelta(adultRange))
        validChildDOB = timeRange(lastFlight - timedelta(4382), lastFlight - timedelta(731))
        validInfantDOB = timeRange(lastFlight - timedelta(730), date.today())

        listOfValidAdultDOBs = [v for v in validAdultDOB.range(timedelta(1))]
        listOfValidChildDOBs = [v for v in validChildDOB.range(timedelta(1))]
        listOfValidInfantDOBs = [v for v in validInfantDOB.range(timedelta(1))]

        if not failCase:
            adultDOB = random.choice(listOfValidAdultDOBs)
            childDOB = random.choice(listOfValidChildDOBs)
            infantDOB = random.choice(listOfValidInfantDOBs)
        else:
            adultDOB = validAdultDOB.end_datetime + timedelta(1)
            childDOB = validChildDOB.end_datetime + timedelta(1) if endDOB else validChildDOB.start_datetime - timedelta(1)
            infantDOB = validInfantDOB.end_datetime + timedelta(1) if endDOB else validInfantDOB.start_datetime - timedelta(1)

        passengerDOB['adult'] = adultDOB.strftime('%d %m %Y').split()
        passengerDOB['child'] = childDOB.strftime('%d %m %Y').split()
        passengerDOB['infant'] = infantDOB.strftime('%d %m %Y').split()

    def selectDateOfBirthDropdowns(self):
        """
        Selects dates of birth from dropdown menus.
        """
        paxElem = "%s_%s-%s"

        for paxNumber, passenger in enumerate(list(passengerDOB.keys()), start=1):
            for index, dmy in enumerate(["day", "month", "year"]):
                if passenger == 'adult':
                    pax = 'adt'
                elif passenger == 'junior':
                    pax = 'jun'
                elif passenger == 'child':
                    pax = 'chd'
                elif passenger == 'infant':
                    pax = 'inf'
                dobElement = paxElem % (dmy, pax, paxNumber)
                Select(self.driver.find_element_by_xpath('//*[@id="%s"]' % dobElement)) \
                    .select_by_value(passengerDOB[passenger][index])
                dobDropdownElements[dobElement] = "id"
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

    def test_01_validDOBDropdownValues(self):
        """
        Validates no error messages are shown when valid dropdown date of birth values are selected.
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.

        self.enterFlightDetailsAndGoToPaxScreen()
        self.generateDateOfBirthCase(failCase=False)
        self.selectDateOfBirthDropdowns()

        found = self.findErrorElements(dobDropdownElements)

        if not found:
            self.logger.info("SUCCESS: No errors were found")
        else:
            self.logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_invalidEndingDOBValues(self):
        """
        Validates error messages are shown when invalid ending DOB dropdown values are selected
        (outside of valid ending range).
        """
        self.logger.info("Test case: %s" % self._testMethodName)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.generateDateOfBirthCase()
        self.selectDateOfBirthDropdowns()

        expected = list(dobDropdownElements.keys())
        found = self.findErrorElements(dobDropdownElements)

        if found and found == expected:
            self.logger.info("SUCCESS: All expected errors were found")
        else:
            self.logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_03_invalidStartingDOBValues(self):
        """
        Validates error messages are shown when invalid starting DOB dropdown values are selected
        (outside of valid starting range - only for child and infant passengers).
        """
        self.logger.info("Test case: %s" % self._testMethodName)

        self.enterFlightDetailsAndGoToPaxScreen()
        self.generateDateOfBirthCase(endDOB=False)
        self.selectDateOfBirthDropdowns()

        expected = list(dobDropdownElements.keys())
        found = self.findErrorElements(dobDropdownElements)

        if found and found == expected:
            self.logger.info("SUCCESS: All expected errors were found")
        else:
            self.logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)