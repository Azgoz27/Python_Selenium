"""
Contains tests for eePay db / api response payment comparisons
"""
# If you want to execute these scripts for "Debug" in Pycharm, just make sure that you define the "workfolder" as the
# eeBookGEN root folder and not the folder where this script actually is...
import sys, os

sys.path.append("../eeqcutils")
sys.path.append("..")
sys.path.append(os.getcwd())
import unittest2 as unittest
import requests
import pymysql
from pprint import pprint
from deepdiff import DeepDiff
from eeqcutils import configurator, initlog
from eeBookGEN.parametersGenerator import ScriptParameters
from eeBookBWA.bwaIBELib import bwaIbeMain as bIM
from eeBookTCV.tcvIBELib import tcvIbeMain as tIM

cfg = configurator.Configurator()
dbConnection = pymysql.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.db)
baseURL = cfg.URL
initlog.removeOldFile("eeBook_eePay_Compare_Payments.py", "./logs/", 30)
initlog.removeOldFile("TC#", "./screenshots/", 30)
initlog.removeOldFile("test_", "./screenshots/", 30)
logger = initlog.Logger("logs/eeBook_eePay_Check_TestSuite_%s" % cfg.gridHost, multipleLogs=True).getLogger()
airline = cfg.airline
environment = cfg.environment
sp = ScriptParameters(airline, airlineClass=bIM if airline == "bwa" else tIM)


class PaymentInfo:
    """
    """

    def __init__(self, pnr, status, method, currency):
        self.pnr = pnr
        self.status = str(status)
        self.method = str(method)
        self.currency = str(currency)

        self.transactions = []


class Transaction:
    """
    """

    def __init__(self, transType, currency, amount):
        self.transType = str(transType)
        self.currency = str(currency)
        self.amount = float(amount)


def getBookingInfoFromDB(whatToGet, dayInterval, bookingStatus):
    """
    :param whatToGet:
    :param dayInterval:
    :param bookingStatus:
    :return:
    """
    db = dbConnection.cursor()
    db.execute("SELECT {} FROM {}.db_eebkg_booking "
               "where booking_ts >= DATE(NOW()) - INTERVAL {} DAY "
               "and bks_status = '{}';".format(whatToGet, cfg.db, dayInterval, bookingStatus))

    results = [result for result in db.fetchall()]

    return results


def saveDBPaymentInfo():
    """
    :return:
    """
    sidList = getBookingInfoFromDB('sid, locator',2, 'SENT')
    db = dbConnection.cursor()

    paymentList = []

    for sid, pnr in sidList:
        db.execute(
            "SELECT payment_status, payment_method, pay_currency, pay_authorise_amount, pay_capture_amount  "
            "FROM {}.db_eebkg_booking_payment_ref where booking_sid = {};".format(cfg.db, sid))
        results = db.fetchall()[0]

        payment = PaymentInfo(pnr=pnr,
                              status=results[0],
                              method=results[1],
                              currency=results[2])

        if results[3]:
            authTransRegisterDB = Transaction(transType="REGISTER",
                                              currency=results[2],
                                              amount=results[3])
            payment.transactions.append(authTransRegisterDB)

            authTransAuthoriseDB = Transaction(transType="AUTHORISE",
                                               currency=results[2],
                                               amount=results[3])
            payment.transactions.append(authTransAuthoriseDB)

        if results[4]:
            authTransCaptureDB = Transaction(transType="CAPTURE",
                                             currency=results[2],
                                             amount=results[4])
            payment.transactions.append(authTransCaptureDB)

        paymentList.append(payment)

    return paymentList


def getAPIPaymentInfo():
    """

    :return:
    """
    pnrList = getBookingInfoFromDB('locator', 1, 'SENT')

    paymentList = []

    for pnr in pnrList:
        r = requests.get('http://{}{}:30780/payment?parameters.type=PNR_LOCATOR&parameters.value={}'
                         .format(airline, environment, pnr[0]))

        transactionInfo = None
        for payment in r.json()['content']:
            for parameter in payment["parameters"]:
                if parameter["type"] == "PAYMENT_ITEM" and parameter["value"] == "BOOK":
                    transactionInfo = payment
                    break
        if not transactionInfo:
            logger.critical("WARNING: NO PAYMENT FOUND FOR PNR: {}".format(pnr[0]))
            break

        payment = PaymentInfo(pnr=pnr[0],
                              status=transactionInfo['state'],
                              method='CREDIT' + transactionInfo['method'] if transactionInfo['method'] == 'CARD'
                                     else transactionInfo['method'],
                              currency=transactionInfo['currency']['payCurrency'])

        if transactionInfo['transactions'][0]['type'] == "REGISTER":
            authTransRegisterAPI = Transaction(transType="REGISTER",
                                               currency=transactionInfo['transactions'][0]['currency'],
                                               amount=transactionInfo['transactions'][0]['amount'])
            payment.transactions.append(authTransRegisterAPI)

        if transactionInfo['transactions'][1]['type'] == "AUTHORISE":
            authTransAuthoriseAPI = Transaction(transType="AUTHORISE",
                                                currency=transactionInfo['transactions'][1]['currency'],
                                                amount=transactionInfo['transactions'][1]['amount'])
            payment.transactions.append(authTransAuthoriseAPI)

        if transactionInfo['transactions'][2]['type'] == "CAPTURE":
            authTransCaptureAPI = Transaction(transType="CAPTURE",
                                              currency=transactionInfo['transactions'][2]['currency'],
                                              amount=transactionInfo['transactions'][2]['amount'])
            payment.transactions.append(authTransCaptureAPI)

        paymentList.append(payment)

    return paymentList


class eeBook_eePay_Compare_Payments(unittest.TestCase):
    """

    """

    def test_01(self):
        """

        """
        listOne = saveDBPaymentInfo()
        listTwo = getAPIPaymentInfo()
        for paymentOne in listOne:
            for paymentTwo in listTwo:
                if paymentOne.pnr == paymentTwo.pnr:
                    logger.info("Checking payments for: {}...".format(paymentOne.pnr, paymentTwo.pnr))
                    difference = DeepDiff(paymentOne, paymentTwo)
                    if not difference:
                        logger.info("SUCCESS: Payments are correct!")
                    else:
                        logger.critical("FAIL: Difference found...")
                        logger.critical(pprint(difference))
