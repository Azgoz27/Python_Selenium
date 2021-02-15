"""
Script used to test and compare created PNR data between eeBook and Amadeus
"""
# If you want to execute these scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import os
import sys
import glob

sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
from eeqcutils import configurator, initlog
from deepdiff import DeepDiff
import unittest2 as unittest
from eeBookGEN.eeBookToAmadeusComparison import eeBookToAmadeusCompareLib

cfg = configurator.Configurator()
initlog.removeOldFile("eeBook_to_Amadeus_Comparison_", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBook_to_Amadeus_Comparison_%s" % cfg.gridHost, multipleLogs=True).getLogger()

# PNRs for testing will be collected from the latest created PNR file or you can supply a path manually
PNRpath = ("../eeBook{}/createdPNRs/*".format((cfg.airline).upper()))
fileOfJsonStrings = max(glob.iglob(PNRpath), key=os.path.getctime)
#fileOfJsonStrings = "../eeBookBWA/createdPNRs/created_PNRs_16.10.2020_07_00_01.txt"

# airline specific parameters:
airline = cfg.airline
clientcode = 'BWA'
system = 'development'
officeID = 'FLLBW00MA'


class EEBKG_GEN_eeBookToAmadeusCompareTests(unittest.TestCase):

    def test_eeBookToAmadeusCompareTest(self):
        """
        Checks for possible differences between eeBook and Amadeus in created PNRs
        """
        jsonList, amadeusList = eeBookToAmadeusCompareLib.getJsonAndAmadeusLists(fileOfJsonStrings=fileOfJsonStrings,
                                                                                 airline=airline,
                                                                                 clientcode=clientcode,
                                                                                 system=system,
                                                                                 officeID=officeID)

        for elemJ in jsonList:
            for elemA in amadeusList:
                if elemJ.PNR == elemA.PNR:
                    test = (elemJ, elemA)
                    with self.subTest(case=test, name="Compare_Amadeus and eeBook for client {} and PNR:{}"
                                      .format(clientcode, test[0].PNR)):
                        logger.info("Checking differences between Amadeus and eeBook for client {} and PNR: {}"
                                    .format(clientcode, test[0].PNR))
                        difference = DeepDiff(test[0], test[1], ignore_string_type_changes=True, ignore_order=True)
                        if not difference:
                            logger.info("SUCCESS: No differences found")
                        else:
                            logger.critical("FAIL: Differences found for PNR {}:".format(test[0].PNR))
                            logger.critical(difference)
                            self.fail(difference)
