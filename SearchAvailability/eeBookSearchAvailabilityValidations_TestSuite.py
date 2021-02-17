"""
Contains test cases for eeBook's search availability screen.
"""

import sys
import os
import json
sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
import datetime
from eeqcutils.standardSeleniumImports import *
from eeqcutils import initlog
from eeBookGEN.parametersGenerator import ScriptParameters
from eeqcutils import eeBookJson
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM
from eeqcutils.TestFixturesUI import TestFixturesUIBaseClass, cfg

baseURL = cfg.URL
airline = cfg.airline
initlog.removeOldFile("eeBookSearchAvailability_TestSuite_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class EEBKG_SA_Validations(TestFixturesUIBaseClass):
    """
    Used for running eeBook Flight Search Screen test suite.
    """
    def __init__(self, tcNumber):
        super(EEBKG_SA_Validations, self).__init__(
            tcNumber,
            logFileName="logs/eeBookSearchAvailability_TestSuite",
            uiErrorSelectors=[(By.XPATH, "//div[@class='alert alert-danger']//small")])


    def test_UndefinedRoute(self):
        """
        Check if correct error message is shown in case deep link is containing a undefined route.
        :return:
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.caseSkipped = False
        self.casePassed = False
        self.driver = None

        # expectedErrorCode="BADROUTE"
        # Generate a outbound date
        outDate = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%d.%m.%Y")
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=outDate,
                                               inboundDate=None,
                                               origin="FRA",
                                               destination=sp.destination,
                                               adult=1,
                                               child=0,
                                               infant=0,
                                               junior=0)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "BADROUTE"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        self.casePassed = True

    def test_InvalidNumberOfPassengersBE(self):
        """
        Check if correct error message is shown in case deep link is containing an invalid number of passengers. This
        validations are done on the BE side.
        :return:
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.caseSkipped = False
        self.casePassed = False
        self.driver = None

        # expectedErrorCode="TOOMANYPASSENGERS"
        # Generate a outbound date
        outDate = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%d.%m.%Y")
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=outDate,
                                               inboundDate=None,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=10,
                                               child=0,
                                               infant=0,
                                               junior=0)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "TOOMANYPASSENGERS"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # expectedErrorCode="TOOMANYPASSENGERS"
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=outDate,
                                               inboundDate=None,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=5,
                                               child=5,
                                               infant=0,
                                               junior=0)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "TOOMANYPASSENGERS"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # expectedErrorCode="TOOMANYPASSENGERS"
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=outDate,
                                               inboundDate=None,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=5,
                                               child=0,
                                               infant=0,
                                               junior=5)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "TOOMANYPASSENGERS"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # expectedErrorCode="TOOMANYPASSENGERS"
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=outDate,
                                               inboundDate=None,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=3,
                                               child=3,
                                               infant=0,
                                               junior=4)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "TOOMANYPASSENGERS"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # expectedErrorCode="TOOMANYINFANTS"
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=outDate,
                                               inboundDate=None,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=3,
                                               child=3,
                                               infant=4,
                                               junior=0)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "TOOMANYINFANTS"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        self.casePassed = True

    def test_InvalidDate(self):
        """
        Check if correct error message is shown in case deep link contains invalid date.
        :return:
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.caseSkipped = False
        self.casePassed = False
        self.driver = None

        # Generate an outbound date
        outDate = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%d.%m.%Y")
        # Generate a faulty inbound date
        badInDate = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")

        # expectedErrorCode="BADDATE"
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="RT",
                                               outboundDate=outDate,
                                               inboundDate=badInDate,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=10,
                                               child=0,
                                               infant=0,
                                               junior=0)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "BADDATE"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # Generate a faulty outbound date
        badOutDate = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%d.%m.%Y")

        # expectedErrorCode="BADDATE"
        response = eeBookJson.requestJsonAvail(client=cfg.airline,
                                               system=cfg.environment,
                                               routeType="OW",
                                               outboundDate=badOutDate,
                                               inboundDate=None,
                                               origin=sp.origin,
                                               destination=sp.destination,
                                               adult=10,
                                               child=0,
                                               infant=0,
                                               junior=0)

        responseParsed = json.loads(response._content)
        # Collect error code
        errorCode = responseParsed["errors"]["error"][0]["code"]
        # Compare the error codes
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "BADDATE"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        self.casePassed = True

    def test_MissingParameters(self):
        """
        Check if correct error message is shown in case deep link is missing mandatory parameters.
        :return:
        """
        self.logger.info("Test case: %s" % self._testMethodName)
        # Set these to flags to track the status of the test case. If the case was skipped, it means the browser was
        # not loaded, so the script can just continue. If the case was not skipped, then the browser needs to be closed
        # and if it failed screen shot is also taken.
        self.caseSkipped = False
        self.casePassed = False

        # Generate a outbound date
        outDate = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%d.%m.%Y")
        inDate = (datetime.datetime.now() + datetime.timedelta(days=6)).strftime("%d.%m.%Y")

        # expectedErrorCode="ADT_TYPES_INVALID"
        sp.useClass(self.driver, cfg).enterTestcase(self.driver,
                                                    baseURL,
                                                    sp.origin,
                                                    sp.destination,
                                                    "OW",
                                                    outDate,
                                                    inDate,
                                                    0,
                                                    0,
                                                    0,
                                                    0,
                                                    sp.eVoucher,
                                                    sp.elementsRm,
                                                    sp.elementsOsi,
                                                    '' if airline == "bwa" else sp.fakeIP
                                                    )

        errorCode = self.driver.find_element_by_xpath("//div[@class='alert alert-danger']//small").text
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "ADT_TYPES_INVALID"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)


        # expectedErrorCode="DATE_DEPARTURE_INVALID"
        sp.useClass(self.driver, cfg).enterTestcase(self.driver,
                                                    baseURL,
                                                    sp.origin,
                                                    sp.destination,
                                                    "OW",
                                                    "",
                                                    inDate,
                                                    1,
                                                    0,
                                                    0,
                                                    0,
                                                    sp.eVoucher,
                                                    sp.elementsRm,
                                                    sp.elementsOsi,
                                                    '' if airline == "bwa" else sp.fakeIP
                                                    )

        errorCode = self.driver.find_element_by_xpath("//div[@class='alert alert-danger']//small").text
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "DATE_DEPARTURE_INVALID"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # expectedErrorCode="NO_ORIGIN"
        sp.useClass(self.driver, cfg).enterTestcase(self.driver,
                                                    baseURL,
                                                    "",
                                                    sp.destination,
                                                    "OW",
                                                    outDate,
                                                    inDate,
                                                    1,
                                                    0,
                                                    0,
                                                    0,
                                                    sp.eVoucher,
                                                    sp.elementsRm,
                                                    sp.elementsOsi,
                                                    '' if airline == "bwa" else sp.fakeIP
                                                    )

        errorCode = self.driver.find_element_by_xpath("//div[@class='alert alert-danger']//small").text
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "NO_ORIGIN"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        # expectedErrorCode="NO_DESTIN"
        sp.useClass(self.driver, cfg).enterTestcase(self.driver,
                                                    baseURL,
                                                    sp.origin,
                                                    "",
                                                    "OW",
                                                    outDate,
                                                    inDate,
                                                    1,
                                                    0,
                                                    0,
                                                    0,
                                                    sp.eVoucher,
                                                    sp.elementsRm,
                                                    sp.elementsOsi,
                                                    '' if airline == "bwa" else sp.fakeIP
                                                    )

        errorCode = self.driver.find_element_by_xpath("//div[@class='alert alert-danger']//small").text
        self.logger.info("Checking error code: %s" % errorCode)
        assert (errorCode == "NO_DESTIN"), self.logger.info("FAIL: Wrong error code returned.")
        self.logger.info("SUCCESS: Correct error code found: %s" % errorCode)

        self.casePassed = True