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
# import unittest2 as unittest
# from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
import json
import requests
from selenium.webdriver.common.keys import Keys
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

cfg = configurator.Configurator()
baseURL = "http://qba.2e-systems.com:7200/qcpay/"
airline = cfg.airline
headers = {"Content-Type": "application/json"}
initlog.removeOldFile("eeBook_eePayJSONValidation_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBook_eePayJSONValidation_TestSuite_%s" % cfg.gridHost, multipleLogs=True).getLogger()
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

with open("./eePay/testData_eePayJSONValidation") as json_file:
    widgetData = json.load(json_file)

FOP = {"credit", "debit"}  # "installment" is not being tested at this moment

testCardsCredit = {
    "MASTERCARD": "5555666677778884",
    "VISA": "4012001037141112",
    "AMEX": "376449047333005",
    "DINERS": "36490102462661",
    "HIPER": "6370950000000005",
    "HIPERCARD": "6062825624254001"
    }

testCardsDebit = {
    "MASTERCARD": "5555666677778884",
    "VISA": "4012001037141112",
    "VINTI4": "6034450006000115"
    }

class EEBKG_EEPAY_ValidateJSON(TestFixturesUIBaseClass):
    """
    Used for running eePay widget screen JSON validation test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_EEPAY_ValidateJSON, self).__init__(
            tcNumber,
            logFileName="logs/eeBook_eePayJSONValidation_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

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
        Selects the Form of Payment from eePay widget drop down menu.
        """
        self.driver.find_element_by_tag_name("button").click()
        self.driver.find_element_by_xpath('//*[@data-value="{}"]'.format(FOP)).click()

    def checkAvailableCards(self):
        """
        Checks if available test card images are loaded on the widget and returns the found cards
        """
        foundCards = []
        availableCards = self.driver.find_elements_by_xpath('//*[@class="avilable-cards"]')
        for availableCard in availableCards:
            foundCard = availableCard.get_attribute("alt")
            foundCards.append(foundCard.upper())
        return foundCards

    def determineTestCards(self, type):
        """
        Checks the Form of Payment selected to return the correct set of test cards to use
        """
        if type == 'credit':
            testCards = testCardsCredit
        else:
            testCards = testCardsDebit
        return testCards

    def enterCardNumber(self, cardNumber):
        """
        Inputs the card number into the field
        :param cardNumber: integer
        """
        cardInput = self.driver.find_element_by_xpath('//*[@id="{}"]'.format("cardNumber"))
        # TODO
        # For some reason the .clear() command below does not work when I run the code, even when debugging
        # however, it does work when I use "evalute expression" option on the line, using dirty fix for now
        cardInput.clear()
        cardInput.send_keys(Keys.CONTROL + "a")
        cardInput.send_keys(Keys.DELETE)
        time.sleep(0.5)
        cardInput.send_keys(cardNumber)
        time.sleep(0.5)

    def test_01_LoadAndCompareTestCards(self):
        """
        Loads the test cards, iterates through forms of payment and compares them with the test data cards.
        """
        logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.

        # Load the eePay widget
        self.loadEEPayWidget()

        # Iterate through Form of Payment options available and determine which test cards to use
        for type in FOP:
            self.selectFOP(type)
            testCards = self.determineTestCards(type)

            # Find the available cards images
            foundCards = self.checkAvailableCards()

            # Compare the found card images to the test cards
            if set(foundCards) == set(list(testCards)):
                logger.info("SUCCESS: Displayed {} cards match the test cards.".format(type))
            else:
                logger.info("FAIL: Displayed {} cards DO NOT match the test cards.".format(type))
                self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/",
                                         filePrefix=self._testMethodName)
                self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_02_inputCardsAndValidatesImage(self):
        """
        Validates test cards input if the correct image is shown in that field
        """
        logger.info("Test case: %s" % self._testMethodName)

        # Load the eePay widget
        self.loadEEPayWidget()

        # Iterate through Form of Payment options and determine which test cards to use
        for type in FOP:
            self.selectFOP(type)
            testCards = self.determineTestCards(type)
            logger.info("TESTING {} CARDS:".format(type.upper()))

            # Iterate through each test card and input the test card field
            for key, value in testCards.items():
                self.enterCardNumber(value)

                # Read the generated card image from the field
                cardImage = self.driver.find_element_by_xpath('//*[@id="{}"]'
                                                              .format("cardNumber")).get_attribute("style").split("/")[
                    3].split(".")[0].upper()

                # Compare the generated input field image with the card name that was put in the field
                if key in cardImage:
                    logger.info("SUCCESS: Displayed card image matches the test {} card.".format(key))
                else:
                    logger.info("FAIL: Displayed card image DOES NOT match the test {} cards.".format(key))
                    self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/",
                                             filePrefix=self._testMethodName)
                    self.fail("Test case: %s failed, check logs" % self._testMethodName)

    def test_03_currencyConversionValidation(self):
        """
        Validates if the test card input returns correct currency choices and conversions
        """
        logger.info("Test case: %s" % self._testMethodName)

        # Load the eePay widget
        self.loadEEPayWidget()

        # Iterate through Form of Payment options, find the loaded cards and compare them to the test cards
        for type in FOP:
            self.selectFOP(type)
            testCards = self.determineTestCards(type)
            logger.info("TESTING {} CARDS:".format(type.upper()))

            # Iterate through each test card and put it into the field to get the currency choices
            for key, value in testCards.items():
                self.enterCardNumber(value)

                # Iterate through each available currency option and log them
                if self.driver.find_elements_by_xpath('//*[@id="currency"]'):
                    currencySelector = self.driver.find_elements_by_xpath('//*[@id="currency"]')[0]
                    currencyOptions = currencySelector.find_elements_by_tag_name("option")
                    for currency in currencyOptions:
                        currency.click()
                        price = self.driver.find_element_by_xpath('//*[@class="total-price"]')
                        logger.info("Found {} currency option with price total:{}.".format(currency.text, price.text))
                    currencySelector.find_elements_by_tag_name("option")[1].click()
                    logger.info("Currency selector loaded for {}.".format(key))
                else:
                    logger.info("WARNING: Currency selector NOT loaded for {}.".format(key))

                # TODO need to compare the currency resulsts with the JSON data or something else
                # add currencies to the test script


        #     if not enabled:
        #         logger.info("SUCCESS: The Pay button has been disabled.")
        #     else:
        #         logger.info("FAIL: The Pay button has not been disabled.")
        #         chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
        #         self.fail("Test case: %s failed, check logs" % self._testMethodName)

    # def tearDown(self):
    #     # If the driver is still active, close it.
    #     if self.driver:
    #         time.sleep(2)
    #         self.driver.quit()
    #         time.sleep(2)
