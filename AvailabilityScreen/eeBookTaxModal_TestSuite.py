"""
Contains test cases for eeBook's tax modal checkup on the availability screen.
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
initlog.removeOldFile("eeBookTaxModal_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
filePath = "./AvailabilityScreen/{}_EEBKG_AV_PaxAndFltCombinations.csv".format(airline.upper())
testData = UniversalCaseReader.getCasesFromFile(filePath)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_AV_TaxModal(TestFixturesUIBaseClass):
    """
    Used for running eeBook Tax Modal test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_AV_TaxModal, self).__init__(
            tcNumber,
            logFileName="logs/eeBookTaxModal_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def checkTaxModalDirection(self, direction):
        # Open the Tax modal
        try:
            paxModalList = self.driver.find_element_by_class_name("pax-subtotal")
            time.sleep(1)
            self.logger.info("Checking tax modal...")
            paxModalList.find_element_by_tag_name('a').click()
            time.sleep(1)
        except:
            self.logger.info("WARNING: tax modal not found!!!")
            self.failSubTest()
        # Check if the modal is not empty
        modal = self.driver.find_element_by_class_name("modal-body--tax-details")
        if not modal.text:
            self.logger.info("WARNING: Tax modal is empty!!!")
            self.failSubTest()
        else:
            # Set the starting pax type tax totals
            adultModalTax = 0.0
            juniorModalTax = 0.0
            childModalTax = 0.0
            infantModalTax = 0.0
            # Get the Pax list
            paxList = modal.find_elements_by_class_name("justify-content-end")
            paxList = paxList[0].text.lower().split("\n")
            # Get the Tax list and iterate through them
            taxList = modal.find_elements_by_class_name("tax-details-table__row")
            for tax in taxList:
                parseTax = tax.text.split("\n")
                # Add the each tax to the pax type tax total
                if "adult" in paxList:
                    adultModalTax += float(parseTax[paxList.index("adult") * 2 + 1])
                if "junior" in paxList:
                    juniorModalTax += float(parseTax[paxList.index("junior") * 2 + 1])
                if "child" in paxList:
                    childModalTax += float(parseTax[paxList.index("child") * 2 + 1])
                if "infant" in paxList:
                    infantModalTax += float(parseTax[paxList.index("infant") * 2 + 1])

            # Close the tax modal
            self.driver.find_element_by_class_name("close--tax-details").click()
            self.logger.info("SUCCESS: Tax modal successfully checked!")
            time.sleep(2)
            # Parse the Taxes per Pax Type from the Flight Price basket
            taxBasketList = []
            paxBasketList = self.driver.find_elements_by_class_name("pax-subtotal")
            for tax in paxBasketList:
                amount = tax.find_element_by_class_name("taxes")
                taxBasketList.append(amount.find_element_by_class_name("amount"))
            # Set the starting pax type total
            adultBasketTax = 0.0
            juniorBasketTax = 0.0
            childBasketTax = 0.0
            infantBasketTax = 0.0
            # Add the each tax to the pax type tax total
            if "adult" in paxList:
                adultBasketTax = float(taxBasketList[paxList.index("adult")].text)
            if "junior" in paxList:
                juniorBasketTax = float(taxBasketList[paxList.index("junior")].text)
            if "child" in paxList:
                childBasketTax = float(taxBasketList[paxList.index("child")].text)
            if "infant" in paxList:
                infantBasketTax = float(taxBasketList[paxList.index("infant")].text)

        # Compare the basket and modal taxes per pax type
        if str(round(adultModalTax, 2)) == str(adultBasketTax):
            self.logger.info("SUCCESS: Adult Tax in modal and basket are the same!")
        else:
            self.logger.info("FAIL: Adult Tax in modal and basket are NOT the same!")
            self.failSubTest()
        if str(round(juniorModalTax, 2)) == str(juniorBasketTax):
            self.logger.info("SUCCESS: Junior Tax in modal and basket are the same!")
        else:
            self.logger.info("FAIL: Junior Tax in modal and basket are NOT the same!")
            self.failSubTest()
        if str(round(childModalTax, 2)) == str(childBasketTax):
            self.logger.info("SUCCESS: Child Tax in modal and basket are the same!")
        else:
            self.logger.info("FAIL: Child Tax in modal and basket are NOT the same!")
            self.failSubTest()
        if str(round(infantModalTax, 2)) == str(infantBasketTax):
            self.logger.info("SUCCESS: Infant Tax in modal and basket are the same!")
        else:
            self.logger.info("FAIL: Infant Tax in modal and basket are NOT the same!")
            self.failSubTest()

    def test_CheckTaxModal(self):
        """
        First build the deeplink for each test case.
        Check if the Fare families modal is loaded for each case.
        If testing fails mark test case as failed and continue to the next case.
        :return:
        """
        for test in testData:
            with self.subTest(case=test, name="{}_{}-{}-{}".format(test.TCNumber, test.origin, test.destination, test.type)):
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

                # Open fare rules modal for outbound flights
                self.checkTaxModalDirection("outbound")
                # Open fare rules modal for inbound flights
                if test.type == "RT":
                    self.checkTaxModalDirection("inbound")