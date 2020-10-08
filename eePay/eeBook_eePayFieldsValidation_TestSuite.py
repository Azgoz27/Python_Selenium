"""
This Script contains test cases for eePay widget's fields validation on eeBook's Summary Screen.
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
from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
import json

cfg = configurator.Configurator()
baseURL = "http://qba.2e-systems.com:7200/qcpay/"
initlog.removeOldFile("eeBook_eePayFieldsValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBook_eePayFieldsValidation_TestSuite_%s" % cfg.gridHost, multipleLogs=True).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

with open("./eePay/testData_eePayFieldsValidation") as json_file:
    widgetData = json.load(json_file)

# save formatted elements and their locators as key/value pairs
eePayElements = {}

testData = [  # Valid input field data for CC
            {"nameOnCard": "Tom Bombadil-Piccard",
             "cardNumber": "4111111111111111",
             "expiryDate": "0121",
             "cvc": "123",
             "addressLine1": "Bags End 27",
             "addressLine2": "End of the Street 7",
             "city": "Shire",
             "zip": "10370",
             "companyName": "Mordor inc",
             "email": "twoeqc@gmail.com",
             "phone": "0987654321"
             },

            # Invalid char lenght input field data for CC
            {"nameOnCard": "qweasdyxcrqweasdyxcfqweasdyxcvqweasdyxctqweasdyxcgqweasdyxcbqweasd",
             "cardNumber": "4111 1111 1111 1111 111",
             "expiryDate": "12",
             "cvc": "9",
             "addressLine1": "qweqweqwedqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqeweqweqwer",
             "addressLine2": "qweqweqwedqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqeweqweqwer",
             "city": "qweqweqwerqweqweqwerqweqweqwerqwe",
             "zip": "978654321197865432111",
             "companyName": "qweqweqweeqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqew",
             "email": "qweqweqwedqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqeweqweqwertwoeqc@gmail.com",
             "phone": "98765432109876543210987654321098765432109"
             },

            # No input field data for CC/DC
            {"nameOnCard": "",
             "cardNumber": "",
             "expiryDate": "",
             "cvc": "",
             "addressLine1": "",
             "addressLine2": "",
             "city": "",
             "zip": "",
             "companyName": "",
             "email": "",
             "phone": ""
             },

            # Invalid character input field data for CC/DC
            {"nameOnCard": "X Æ A-12!",
             "cardNumber": "X Æ A-12!",
             "expiryDate": "X Æ A-12!",
             "cvc": "X Æ A-12!",
             "addressLine1": "X Æ A-12!",
             "addressLine2": "X Æ A-12!",
             "city": "X Æ A-12!",
             "zip": "X Æ A-12!",
             "companyName": "X Æ A-12!",
             "email": "X Æ A-12!",
             "phone": "X Æ A-12!"
             },

            # Valid input field data for DC
            {"nameOnCard": "Tom Bombadil-Piccard",
             "cardNumber": "6034450006001501",
             "expiryDate": "0721",
             "cvc": "593",
             "addressLine1": "Bags End 27",
             "addressLine2": "End of the Street 7",
             "city": "Shire",
             "zip": "10370",
             "companyName": "Mordor inc",
             "email": "twoeqc@gmail.com",
             "phone": "0987654321"
             },

            # Invalid char lenght input field data for DC
            {"nameOnCard": "qweasdyxcrqweasdyxcfqweasdyxcvqweasdyxctqweasdyxcgqweasdyxcbqweasd",
             "cardNumber": "603",
             "expiryDate": "12",
             "cvc": "9",
             "addressLine1": "qweqweqwedqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqeweqweqwer",
             "addressLine2": "qweqweqwedqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqeweqweqwer",
             "city": "qweqweqwerqweqweqwerqweqweqwerqwe",
             "zip": "978654321197865432111",
             "companyName": "qweqweqweeqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqew",
             "email": "qweqweqwedqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqweqweqwerqeweqweqwertwoeqc@gmail.com",
             "phone": "98765432109876543210987654321098765432109"
             }
]

class EEBKG_PD_ValidateFields(unittest.TestCase):
    """
    Used for running eePay widget screen input field test suite.
    """
    @classmethod
    def setUpClass(cls):
        if not os.path.isdir("./screenshots/"):
            os.mkdir("screenshots")
        if not os.path.isdir("./logs/"):
            os.mkdir("logs")

    def loadEEPayWidget(self):
        """
        Loads the eePay widget.
        """
        time.sleep(5)
        self.driver.switch_to.frame(self.driver.find_element_by_id("eepay"))

        # mambo jumbo, ignore, need to setup wait for page to load
        # self.driver.implicitly_wait(10)
        # waitForPageToLoad(driver, selector="availability", how=By.CLASS_NAME, timeoutSeconds=5, errorSelector="alert-danger")
        # Find the element by applying explicit wait on it and then click on it
        # WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='skeleton_main']/div[1]/div[2]/div/a"))).click()
        # waitForSplashScreenToDissapear(self.driver)

    def selectDebitCard(self):
        """
        Selects the Debit Card from eePay widget.
        """
        # Select DEBIT card
        self.driver.find_element_by_xpath('//*[@class="{}"]'.format("payment-dropdown")).click()
        self.driver.find_element_by_xpath('//*[@data-value="{}"]'.format("debit")).click()

    def enterFields(self, nameOnCard, cardNumber, expiryDate, cvc, addressLine1, addressLine2, city, zip, companyName, email, phone):
        """
        :param nameOnCard: string
        :param cardNumber: integer
        :param expiryDate: integer
        :param cvc: integer
        :param addressLine1: string
        :param addressLine2: string
        :param city: string
        :param zip:
        :param companyName: string
        :param email: string
        :return:
        """
        # Enter name on card
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("cardHolder")).send_keys(nameOnCard)
        eePayElements["cardHolder"] = "id"

        # Enter card number
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("cardNumber")).send_keys(cardNumber)
        eePayElements["cardNumber"] = "id"

        # Enter expiry date
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("expirationDate")).send_keys(expiryDate)
        eePayElements["expirationDate"] = "id"

        # Enter CVC
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("verificationCode")).send_keys(cvc)
        eePayElements["verificationCode"] = "id"

        # Enter Address Line 1
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("addressLine1")).send_keys(addressLine1)
        eePayElements["addressLine1"] = "id"

        # Enter Address Line 2
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("addressLine2")).send_keys(addressLine2)
        eePayElements["addressLine2"] = "id"

        # Enter City
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("city")).send_keys(city)
        eePayElements["city"] = "id"

        # Enter ZIP
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("postalCode")).send_keys(zip)
        eePayElements["postalCode"] = "id"

        # Enter Company name
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("companyName")).send_keys(companyName)
        eePayElements["companyName"] = "id"

        # Enter Email
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("emailAddr")).send_keys(email)
        eePayElements["emailAddr"] = "id"

        # Enter Phone Number
        self.driver.find_element_by_xpath('//*[@id="{}"]'.format("phoneNumber")).send_keys(phone)
        eePayElements["phoneNumber"] = "id"

        # Select Country
        country = [i for i in range(1, sp.numberOfCountries(airline))]
        Select(self.driver.find_element_by_xpath('//*[@id="{}"]'.format("countryCode"))).select_by_index(random.choice(country))
        # eePayElements["countryCode"] = "id"

        if cfg.airline == "bwa":
            # Select Country Phone Number
            countryPhone = [i for i in range(1, sp.numberOfCountries(airline))]
            Select(self.driver.find_element_by_xpath('//*[@id="{}"]'.format("phoneCode"))).select_by_index(random.choice(countryPhone))
            # eePayElements["phoneCode"] = "id"

        # Switch back from the iFrame to default
        # self.driver.switch_to.default_content()

    def findErrorElements(self, elementDict):
        """
        Finds error elements if they exist.
        :param elementDict: Dictionary with element names / locators to use (e.g. eePayElements = {})
        :return: list of errors found
        """
        errorsFound = []
        #self.driver.switch_to.frame(self.driver.find_element_by_id("eepay"))

        for element, locator in list(elementDict.items()):
            try:
                time.sleep(0.5)
                self.driver.implicitly_wait(0)
                self.driver.find_element_by_xpath('//input[@{}="{}" and @class="is-invalid form-control"]'.format(locator, element))
                errorsFound.append(element)
            except NoSuchElementException:
                continue
        return errorsFound

    def test_01_validInputDataCC(self):
        """
        Validates no error messages are shown when valid input data is entered for CC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Input test data
        self.enterFields(**testData[0])
        # Check for error messages
        found = self.findErrorElements(eePayElements)

        if not found:
            logger.info("SUCCESS: No errors were found")
        else:
            logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_invalidMaxCharInputDataCC(self):
        """
        Validates error messages are shown when invalid max char input data is entered for CC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Input test data
        self.enterFields(**testData[1])
        # Setting up expected error messages
        expected = list(eePayElements.keys())
        # Check for error messages
        found = self.findErrorElements(eePayElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_03_noInputDataCC(self):
        """
        Validates if the Pay button is disabled when no input has been made for CC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Input test data
        self.enterFields(**testData[2])
        # Check if the Pay button is disabled
        self.driver.switch_to.default_content()
        enabled = self.driver.find_element_by_id("submit-button").is_enabled()

        if not enabled:
            logger.info("SUCCESS: The Pay button has been disabled.")
        else:
            logger.info("FAIL: The Pay button has not been disabled.")
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_04_invalidCharacterInputDataCC(self):
        """
        Validates if error messages are shown when invalid character input data is entered for CC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Input test data
        self.enterFields(**testData[3])
        # Set up expected error messages
        expected = ["cardHolder", "cardNumber", "expirationDate", "verificationCode", "city", "emailAddr"]
        # Check for found error messages
        found = self.findErrorElements(eePayElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_05_validInputDataDC(self):
        """
        Validates no error messages are shown when valid input data is entered for DC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Select DEBIT card
        self.selectDebitCard()
        # Input test data
        self.enterFields(**testData[4])
        # Check for error messages
        found = self.findErrorElements(eePayElements)

        if not found:
            logger.info("SUCCESS: No errors were found")
        else:
            logger.info("FAIL: Errors found when none expected. Errors found: %s" % found)
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_06_invalidMaxCharInputDataDC(self):
        """
        Validates error messages are shown when invalid max char input data is entered for DC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Select DEBIT card
        self.selectDebitCard()
        # Input test data
        self.enterFields(**testData[5])
        # Setting up expected error messages
        expected = list(eePayElements.keys())
        # Check for error messages
        found = self.findErrorElements(eePayElements)

        if found and found == expected:
            logger.info("SUCCESS: All expected errors were found")
        else:
            logger.info("FAIL: All expected errors were not found: \nExpected errors: %s\nErrors found: %s"
                        % (expected, found))
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_07_noInputDataDC(self):
        """
        Validates if the Pay button is disabled when no input has been made for DC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Select DEBIT card
        self.selectDebitCard()
        # Input test data
        self.enterFields(**testData[2])
        # Check if the Pay button is disabled
        self.driver.switch_to.default_content()
        enabled = self.driver.find_element_by_id("submit-button").is_enabled()

        if not enabled:
            logger.info("SUCCESS: The Pay button has been disabled.")
        else:
            logger.info("FAIL: The Pay button has not been disabled.")
            chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_08_invalidCharacterInputDataDC(self):
        """
        Validates if error messages are shown when invalid character input data is entered for DC.
        """
        logger.info("Test case: %s" % self._testMethodName)
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Select DEBIT card
        self.selectDebitCard()
        # Input test data
        self.enterFields(**testData[3])
        # Set up expected error messages
        expected = ["cardHolder", "cardNumber", "expirationDate", "verificationCode", "city", "emailAddr"]
        # Check for found error messages
        found = self.findErrorElements(eePayElements)

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
