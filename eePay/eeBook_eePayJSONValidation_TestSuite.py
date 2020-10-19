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
import requests
from selenium.webdriver.common.keys import Keys

cfg = configurator.Configurator()
baseURL = "http://qba.2e-systems.com:7200/qcpay/"
headers = {"Content-Type": "application/json"}
initlog.removeOldFile("eeBook_eePayJSONValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBook_eePayJSONValidation_TestSuite_%s" % cfg.gridHost, multipleLogs=True).getLogger()
airline = cfg.airline
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

with open("./eePay/testData_eePayJSONValidation") as json_file:
    widgetData = json.load(json_file)

FOP = {"credit", "debit", "installment"}

testCards = {
    "MASTERCARD": "5555555555554444",
    "VISA": "4111111111111111",
    "VINTI4": "6034450006000115",
    "AMEX": "376449047333005",
    "DINERS": "36490102462661",
    "HIPER": "6370950000000005",
    "HIPERCARD": "6062825624254001"
    }

class EEBKG_EEPAY_ValidateJSON(unittest.TestCase):
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
        Initiate POST request and load the eePay widget.
        """
        requests.post(url="http://qba.2e-systems.com:18199/qcPayUpdate",
                      json=widgetData,
                      headers=headers)

        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
        self.driver.switch_to.frame(self.driver.find_element_by_id("eepay"))

    def selectFOP(self, FOP):
        """
        Selects the FOP from eePay widget drop down menu.
        """
        # Select FOP type
        self.driver.find_element_by_xpath('//*[@class="{}"]'.format("payment-dropdown")).click()
        self.driver.find_element_by_xpath('//*[@data-value="{}"]'.format(FOP)).click()

    def checkAvailableCards(self, type):
        #  Check if test cards are loaded
        foundCards = []
        availableCards = self.driver.find_elements_by_xpath('//*[@class="avilable-cards"]')
        for availableCard in availableCards:
            foundCard = availableCard.get_attribute("alt")
            foundCards.append(foundCard.upper())
        return foundCards

    def enterCardNumber(self, cardNumber):
        """
        :param cardNumber: integer
        """
        # Enter card number
        cardNumberInput = self.driver.find_element_by_xpath('//*[@id="{}"]'.format("cardNumber"))
        # For some reason the .clear() command does not work when I run the code, even when debugging
        # it does work when I use "evalute expression" option on that line
        cardNumberInput.clear()
        cardNumberInput.send_keys(Keys.CONTROL + "a")
        cardNumberInput.send_keys(Keys.DELETE)
        time.sleep(0.5)
        cardNumberInput.send_keys(cardNumber)


    def test_01_LoadAndCompareTestCards(self):
        """
        Loads the test cards, iterate through forms of payment and compares them with the test data cards.
        """
        logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.

        # Load the eePay widget
        self.loadEEPayWidget()

        # Iterate through Form of Payment options, find the available cards and compare them to the test cards
        for type in FOP:
            self.selectFOP(type)
            foundCards = self.checkAvailableCards(type)
            if set(foundCards) == set(list(testCards)):
                logger.info("SUCCESS: Displayed {} cards match the test cards.".format(type))
            else:
                logger.info("FAIL: Displayed {} cards DO NOT match the test cards.".format(type))
                chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/",
                                         filePrefix=self._testMethodName)
                self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_inputCardsAndValidatesImage(self):
        """
        Validates test cards input and image shown
        """
        logger.info("Test case: %s" % self._testMethodName)
        # Wait for eePay widget too load
        self.loadEEPayWidget()
        # Iterate through Form of Payment options, find the loaded cards and compare them to the test cards
        for type in FOP:
            self.selectFOP(type)
            logger.info("TESTING {} CARDS:".format(type.upper()))
            # Input test data cards
            for key, value in testCards.items():
                # Input the test card
                self.enterCardNumber(value)
                # Read the generated card image
                cardImage = self.driver.find_element_by_xpath('//*[@id="{}"]'.format("cardNumber")).get_attribute("style").split("/")[
                    3].split(".")[0].upper()
                # Compare the generated card image with the test data key
                if key in cardImage:
                    logger.info("SUCCESS: Displayed {} card matches the test card.".format(key))
                else:
                    logger.info("FAIL: Displayed {} card DOES NOT match the test cards.".format(key))
                    chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/",
                                             filePrefix=self._testMethodName)
                    self.fail("Test case: %s failed, check logs" % self._testMethodName)

    # def test_03_noInputDataCC(self):
    #     """
    #     Validates if the Pay button is disabled when no input has been made for CC.
    #     """
    #     logger.info("Test case: %s" % self._testMethodName)
    #     self.driver = seleniumBrowser(cfg=cfg, url=baseURL)
    #     # Wait for eePay widget too load
    #     self.loadEEPayWidget()
    #     # Input test data
    #     self.enterFields(**testData[2])
    #     # Check if the Pay button is disabled
    #     self.driver.switch_to.default_content()
    #     enabled = self.driver.find_element_by_id("submit-button").is_enabled()
    #
    #     if not enabled:
    #         logger.info("SUCCESS: The Pay button has been disabled.")
    #     else:
    #         logger.info("FAIL: The Pay button has not been disabled.")
    #         chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
    #         self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def tearDown(self):
        # If the driver is still active, close it.
        if self.driver:
            time.sleep(2)
            self.driver.quit()
            time.sleep(2)
