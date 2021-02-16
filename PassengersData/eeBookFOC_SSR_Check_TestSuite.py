"""
Contains test cases for eeBook's Passenger Data dropdown menu validation on passengers screen.
"""

# If you want to execute these scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...

import sys, os
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
# import unittest2 as unittest
import random
import pymysql
from datetime import date, timedelta
# from eeqcutils.chromeScreenShooter import chromeTakeFullScreenshot
from eeqcutils.standardSeleniumImports import *
from eeqcutils import configurator, initlog
from eeBookTCV.tcvIBEUtils.CommonFunctions import waitForSplashScreenToDissapear
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

# cfg = configurator.Configurator()
baseURL = cfg.URL
airline = cfg.airline
dbConnection = pymysql.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.db)
initlog.removeOldFile("eeBookFOC_SSR_Check_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
# logger = initlog.Logger("logs/eeBookFOC_SSR_Check_TestSuite_%s" % cfg.gridHost, multipleLogs=True).getLogger()
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)

# generate random dates (for enterTestCase)
randomOutboundDate = (date.today() + timedelta(random.randint(90, 95))).strftime("%d.%m.%Y")
randomInboundDate = (date.today() + timedelta(random.randint(100, 105))).strftime("%d.%m.%Y")


class EEBKG_PD_FOC_TestSuite(TestFixturesUIBaseClass):
    """
    Used for running eeBook Passenger screen FOC SSR test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_PD_FOC_TestSuite, self).__init__(
            tcNumber,
            logFileName="logs/eeBookFOC_SSR_Check_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])

    def enterTestcaseAndGoToPaxScreen(self):
        """
        Enters flight details / goes to Passenger screen and stores flight data.
        """
        sp.useClass(self.driver, cfg) \
            .enterTestcase(self.driver, baseURL, sp.origin, sp.destination, "RT", randomOutboundDate, randomInboundDate,
                           1, 1, 1, "", "", "", "", sp.appID if airline == "bwa" else sp.fakeIP)

        waitForSplashScreenToDissapear(self.driver)

        # Set the header to be static
        element = self.driver.find_element_by_id("twoe-header")
        self.driver.execute_script("arguments[0].style.position = 'absolute';", element)

        # Store flight data
        self.flightData = sp.useClass(self.driver, cfg).storeFlightDataScr(self.driver, "RT")

        self.dbData = {"carrier": self.flightData[0].carrier,
                       "departureDate": self.flightData[0].date,
                       "arrivalDate": self.flightData[1].date,
                       "originCode": sp.origin,
                       "destinationCode": sp.destination,
                       "fare": self.flightData[0].fare,
                       "startNumber": self.flightData[0].number,
                       "endNumber": self.flightData[1].number}

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

    def getFOC_SSRFromDB(self, category, carrier, departureDate, arrivalDate, originCode, destinationCode, fare,
                         startNumber, endNumber):
        """
        Sends query and gets FOC SSR details from DB.

        :param category: string - FOC category to get, e.g. "FOC_BLIND", "FOC_ASSISTANCE" or "FOC_WHEELCHAIR"
        :param carrier: string - Two letter carrier code
        :param departureDate: string - flight date in dd.mm.yyyy format
        :param arrivalDate: string - flight date in dd.mm.yyyy format
        :param originCode: string - three letter origin code
        :param destinationCode: string - three letter destination code
        :param fare: string - two letter fare code
        :param startNumber: string - flight number "from"
        :param endNumber: string - flight number "to"
        :return: Dictionary of foc ssr for adult and child passenger
        """

        db = dbConnection.cursor()
        db.execute("SELECT DISTINCT CAT.type_name, CAT.passenger_allowed, CAC.offer_unit, "
                   "CAC.max_items, CAR.priority, CAT.type_description, CAR.fare_family "
                   "FROM cat_eebkg_ancillary_category "
                   "AS CAC INNER JOIN cat_eebkg_ancillary_type "
                   "AS CAT ON CAC.category_id = CAT.category_id "
                   "INNER JOIN cat_eebkg_ancillary_rule "
                   "AS CAR ON CAR.type_id = CAT.type_id "
                   "WHERE(route_origin='{}' or route_origin = '*') "
                   "AND(route_destination='{}' or route_destination = '*') "
                   "AND CAC.active = 1 "
                   "AND CAT.active = 1 "
                   "AND CAR.active = 1 "
                   "AND(ISNULL(fare_family) "
                   "OR fare_family = '{}' ) "
                   "AND(ISNULL(operating_carrier) "
                   "OR operating_carrier = '{}') "
                   "AND(ISNULL(flight_range_start) "
                   "OR flight_range_start < '{}') "
                   "AND(ISNULL(flight_range_end) "
                   "OR flight_range_end > '{}') "
                   "AND(ISNULL(travel_period_start) "
                   "OR travel_period_start < DATE('{}')) "
                   "AND(ISNULL(travel_period_end) "
                   "OR travel_period_end > DATE('{}')) "
                   "AND(category_name='{}') "
                   "AND(ISNULL(CAR.sale_phase) "
                   "OR CAR.sale_phase = '' "
                   "OR CAR.sale_phase LIKE '%BOOK%') "
                   "ORDER BY priority ASC;"
                   .format(originCode, destinationCode, fare, carrier, startNumber,
                           endNumber, departureDate, arrivalDate, category))
        queryResults = db.fetchall()
        FOCAdult = []
        FOCChild = []

        for result in queryResults:
            if 'ADT' in result[1]:
                FOCAdult.append(result[0])

            if 'CHD' in result[1]:
                FOCChild.append(result[0])

        FOC_SSR = {'adult': FOCAdult, 'child': FOCChild}

        return FOC_SSR

    def clickAllFOCs(self):
        """
        Clicks / selects all FOC elements available from db
        :return: dictionary - booleans for all clicked / selected FOC elements (e.g. "adult - Blind": True)
        """
        selectedFOCs = {}
        clickedSSRButton = []

        # get foc from db for every category
        for category in sp.focSSR:
            currentCategory = self.getFOC_SSRFromDB(category, **self.dbData)

            # click on "Special assistance" button for every passenger
            for paxNumber, passenger in enumerate(currentCategory, start=1):
                if passenger == 'adult':
                    pax = 'adt'
                elif passenger == 'junior':
                    pax = 'jun'
                elif passenger == 'child':
                    pax = 'chd'
                elif passenger == 'infant':
                    pax = 'inf'
                paxElem = "{}-{}".format(pax, paxNumber)
                time.sleep(2)
                ssrButton = self.driver.find_element_by_xpath("//*[@for='specialNeeds_{}']".format(paxElem))

                if paxElem not in clickedSSRButton:
                    ssrButton.click()
                    clickedSSRButton.append(paxElem)

                # click / select every foc defined in category for every passenger type
                for foc in currentCategory[passenger]:
                    time.sleep(0.5)
                    element = self.driver.find_element_by_xpath("//label[contains(@for, '{}-{}-{}')]"
                                                                .format(paxElem, category, foc))
                    element.click()
                    selectedFOCs[passenger + " - " + element.text] = element.is_enabled()

        return selectedFOCs

    def test_01_checkAllFOC_SSRsAreClicked(self):
        """
        Checks if all foc elements for all passengers were clicked
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.driver = seleniumBrowser(cfg=cfg, url=baseURL)

        self.enterTestcaseAndGoToPaxScreen()
        FOCNotSelected = False
        selectedFOCs = self.clickAllFOCs()

        if FOCNotSelected not in list(selectedFOCs.values()):
            self.logger.info("SUCCESS: All FOC_SSRs were clicked: \n{}".format('\n'.join(sorted(selectedFOCs))))
        else:
            self.logger.info("FAIL: Not all FOC_SSRs were clicked, check screenshot")
            self.chromeTakeFullScreenshot(self.driver, screenshotFolder="./screenshots/", filePrefix=self._testMethodName)
            self.fail("Test case: %s failed, check logs" % self._testMethodName)

    # def tearDown(self):
    #     # If the driver is still active, close it.
    #     if self.driver:
    #         time.sleep(2)
    #         self.driver.quit()
    #         time.sleep(2)
