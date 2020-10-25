from unittest import TestLoader, TestSuite
from HtmlTestRunner import HTMLTestRunner
import glob
import os
from eeqcutils.htmlTestReportRunner import send_mail

# Search Availability script imports
from eeBookGEN.SearchAvailability.eeBookSearchAvailabilityCombinations_TestSuite import EEBKG_SA_PaxAndFltCombinations
from eeBookGEN.SearchAvailability.eeBookSearchAvailabilityValidations_TestSuite import EEBKG_SA_Validations
# Availability Screen script imports
from eeBookGEN.AvailabilityScreen.eeBookCalendarDatesAndPrices_TestSuite import EEBKG_AV_CalendarDatesAndPrices
from eeBookGEN.AvailabilityScreen.eeBookFareFamiliesModal_TestSuite import EEBKG_AV_FareFamiliesModal
from eeBookGEN.AvailabilityScreen.eeBookFareRulesModal_TestSuite import EEBKG_AV_FareRulesModal
from eeBookGEN.AvailabilityScreen.eeBookFlightDetailsModal_TestSuite import EEBKG_AV_FlightDetailsModal
from eeBookGEN.AvailabilityScreen.eeBookPreselectedPrice_TestSuite import EEBKG_AV_PreselectedPrice
from eeBookGEN.AvailabilityScreen.eeBookShoppingBasketComparison_TestSuite import EEBKG_AV_ShoppingBasketComparison
from eeBookGEN.AvailabilityScreen.eeBookTaxModal_TestSuite import EEBKG_AV_TaxModal
# Passenger Data script imports
from eeBookGEN.PassengersData.eeBookDateOfBirthValidation_TestSuite import EEBKG_PD_ValidateDOBDropdowns
from eeBookGEN.PassengersData.eeBookDropdownValidation_TestSuite import EEBKG_PD_ValidateDropdowns
from eeBookGEN.PassengersData.eeBookFieldsValidation_TestSuite import EEBKG_PD_ValidateFields
from eeBookGEN.PassengersData.eeBookFOC_SSR_Check_TestSuite import EEBKG_PD_FOC_TestSuite
from eeBookGEN.PassengersData.eeBookTravelDocumentValidation_TestSuite import EEBKG_PD_ValidateTravelDocument
# Summary Screen script imports
from eeBookGEN.SummaryScreen.eeBookBasketHidden import EEBKG_SS_BasketHidden
from eeBookGEN.SummaryScreen.eeBookIncludedBags import EEBKG_SS_IncludedBags
# eePay widget script imports
from eeBookGEN.eePay.eeBook_eePay_Compare_Payments import eeBook_eePay_Compare_Payments
from eeBookGEN.eePay.eeBook_eePayFieldsValidation_TestSuite import EEBKG_EEPAY_ValidateFields
from eeBookGEN.eePay.eeBook_eePayJSONValidation_TestSuite import EEBKG_EEPAY_ValidateJSON
# eeBook to Amadeus comparison
from eeBookGEN.eeBookToAmadeusComparison.eeBookToAmadeusCompareTests import EEBKG_GEN_eeBookToAmadeusCompareTests

paxAndFlitCombinationsSuite = TestLoader().loadTestsFromTestCase(EEBKG_SA_PaxAndFltCombinations)
searchAvailabilityValidationsSuite = TestLoader().loadTestsFromTestCase(EEBKG_SA_Validations)
calendarDatesAndPricesSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_CalendarDatesAndPrices)
fareFamiliesModalSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_FareFamiliesModal)
fareRulesModalSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_FareRulesModal)
flightDetailsSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_FlightDetailsModal)
preselectedPriceSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_PreselectedPrice)
shoppingBasketComparisonSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_ShoppingBasketComparison)
taxModalSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_TaxModal)
validatePaxDOBDropdownsSuite = TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateDOBDropdowns)
validatePaxDropdownsSuite = TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateDropdowns)
validatePaxFieldsSuite = TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateFields)
FOCPaxSuite = TestLoader().loadTestsFromTestCase(EEBKG_PD_FOC_TestSuite)
validatePaxTravelDocumentSuite = TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateTravelDocument)
BasketHiddenSuite = TestLoader().loadTestsFromTestCase(EEBKG_SS_BasketHidden)
IncludedBagsSuite = TestLoader().loadTestsFromTestCase(EEBKG_SS_IncludedBags)
PaymentInfoSuite = TestLoader().loadTestsFromTestCase(eeBook_eePay_Compare_Payments)
eePayValidateFieldsSuite = TestLoader().loadTestsFromTestCase(EEBKG_EEPAY_ValidateFields)
eePayValidateJSONSuite = TestLoader().loadTestsFromTestCase(EEBKG_EEPAY_ValidateJSON)
eeBookAmadeusCompareSuite = TestLoader().loadTestsFromTestCase(EEBKG_GEN_eeBookToAmadeusCompareTests)


suite = TestSuite([paxAndFlitCombinationsSuite,
                   searchAvailabilityValidationsSuite,
                   calendarDatesAndPricesSuite,
                   fareFamiliesModalSuite,
                   fareRulesModalSuite,
                   flightDetailsSuite,
                   preselectedPriceSuite,
                   shoppingBasketComparisonSuite,
                   taxModalSuite,
                   validatePaxDOBDropdownsSuite,
                   validatePaxDropdownsSuite,
                   validatePaxFieldsSuite,
                   FOCPaxSuite,
                   validatePaxTravelDocumentSuite,
                   BasketHiddenSuite,
                   IncludedBagsSuite,
                   PaymentInfoSuite,
                   eePayValidateFieldsSuite,
                   eePayValidateJSONSuite,
                   eeBookAmadeusCompareSuite
                   ])

runner = HTMLTestRunner(output="reports",
                        combine_reports=True,
                        report_name="TestResults_eeBookGEN",
                        template="../eeqcutils/HTMLTestRunner_qba_test_report_template.html",
                        report_title="Test Results for eeBookGEN script")

runner.run(suite)

# Locate the generated report
htmlFile = max(glob.iglob("../eeBookGEN/reports/*"), key=os.path.getctime)
filesToSend = [htmlFile]
try:
    htmlContent = open(htmlFile, "r").read()
except:
    htmlContent = "HTML file not found"

# Send the generated report
emails = ["tomislav.stanceric@2e-systems.com", "davorin.gerovec@2e-systems.com", "sinisa.sambol@2e-systems.com"]
send_mail(send_from="twoeqc@gmail.com",
          send_to=emails,
          username='twoeqc@gmail.com', password='shagme123',
          subject=htmlFile,
          text="Report GEN test Suite",
          server='smtp.gmail.com:587',
          htmlToShow=htmlContent,
          files=filesToSend)

