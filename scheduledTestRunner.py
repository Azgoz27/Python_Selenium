from unittest import TestLoader, TestSuite
from HtmlTestRunner import HTMLTestRunner
#from HTMLTestRunner import HTMLTestRunner

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


paxAndFlitCombinationsSuite= TestLoader().loadTestsFromTestCase(EEBKG_SA_PaxAndFltCombinations)
searchAvailabilityValidationsSuite= TestLoader().loadTestsFromTestCase(EEBKG_SA_Validations)
calendarDatesAndPricesSuite= TestLoader().loadTestsFromTestCase(EEBKG_AV_CalendarDatesAndPrices)
fareFamiliesModalSuite= TestLoader().loadTestsFromTestCase(EEBKG_AV_FareFamiliesModal)
fareRulesModalSuite= TestLoader().loadTestsFromTestCase(EEBKG_AV_FareRulesModal)
flightDetailsSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_FlightDetailsModal)
preselectedPriceSuite= TestLoader().loadTestsFromTestCase(EEBKG_AV_PreselectedPrice)
shoppingBasketComparisonSuite= TestLoader().loadTestsFromTestCase(EEBKG_AV_ShoppingBasketComparison)
taxModalSuite = TestLoader().loadTestsFromTestCase(EEBKG_AV_TaxModal)
validatePaxDOBDropdownsSuite= TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateDOBDropdowns)
validatePaxDropdownsSuite= TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateDropdowns)
validatePaxFieldsSuite= TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateFields)
FOCPaxSuite= TestLoader().loadTestsFromTestCase(EEBKG_PD_FOC_TestSuite)
validatePaxTravelDocumentSuite= TestLoader().loadTestsFromTestCase(EEBKG_PD_ValidateTravelDocument)
BasketHiddenSuite= TestLoader().loadTestsFromTestCase(EEBKG_SS_BasketHidden)
IncludedBagsSuite= TestLoader().loadTestsFromTestCase(EEBKG_SS_IncludedBags)

suite = TestSuite([paxAndFlitCombinationsSuite, searchAvailabilityValidationsSuite, calendarDatesAndPricesSuite,
                  fareFamiliesModalSuite, fareRulesModalSuite, flightDetailsSuite, preselectedPriceSuite,
                   shoppingBasketComparisonSuite, taxModalSuite, validatePaxDOBDropdownsSuite,
                   validatePaxDropdownsSuite, validatePaxFieldsSuite, FOCPaxSuite, validatePaxTravelDocumentSuite,
                   BasketHiddenSuite, IncludedBagsSuite])

runner = HTMLTestRunner(output="eeBookGEN_Reports",
                        combine_reports=True,
                        report_name="TestResults_eeBookGEN",
                        template="../eeqcutils/HTMLTestRunner_qba_test_report_template.html",
                        report_title="Test Results for eeBookGEN script")

runner.run(suite)
