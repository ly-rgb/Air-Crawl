# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/11/29 14:34
"""

import os

os.chdir("../../")

import unittest

from airline.AZ9.service import api_search, no_hold_pay
from airline.base import add_on_select_flight
from airline.AZ9.AZ9Web import AZ9Web
from airline.AZ9.service import add_on
from airline.AZ9.AZ9Baggage import AZ9Baggage
from utils.searchparser import parser_from_task
import os
from robot import HoldTask


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_api_search(self):
        task = 'AZ9,KUL,LGK,2022-12-25,,1,,,AFARE,0,,READTIMELCC'
        code, req = api_search(parser_from_task(task), proxies_type=0)
        print(code, req)

        import requests

        # url = "http://43.153.142.168:10241/curl"
        # headers= {"Content-Type": "application/json"}
        # body = {"postData": "AZ9,KCH,KUL,2022-12-20,,2,,,AFARE,0,Z98102,READTIMELCC", "version": "2.0", "url": "AZ9"}
        # # body = {"postData": "AF9,LAS,ATL,2023-01-09,,3,,,AFARE,0,F92002,READTIMELCC", "version": "2.0", "url": "AF9"}
        # response = requests.post(url=url, headers=headers, data=body)
        # print(response.text)

    def test_api_pay(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"

        task = {'payOrderDetail': {
            'payOrder': {'uuid': 'BDL4958017100860774_xxxxx1', 'otaId': 'BDL8600171906786', 'otaCompany': 50,
                         'groupCode': 'weelfly', 'fromFlightNum': 'Z97703', 'fromFlightSegment': 'KUL-LGK',
                         'fromFlightCarrier': 'Z9', 'depDate': 'Jan 23, 2023 2:50:00 PM', 'ticketPrice': 408,
                         'ticketTax': 4, 'totalPrice': 412.0, 'bookingTime': 'Dec 29, 2022 12:40:10 PM',
                         'payTime': 'Dec 29, 2022 12:45:01 PM', 'createTime': 'Dec 29, 2022 12:45:01 PM',
                         'apiSystemUuid': 'BDL8600171906786', 'depAirport': 'KUL', 'arrAirport': 'LGK', 'tripType': 1,
                         'commissionPrice': 0.0, 'remark': '机器人锁定订单', 'adtCount': 2, 'chidCount': 0, 'status': 2,
                         'userId': 99992, 'userName': 'Trident', 'orderType': 0, 'tags': ',UNHOLD,allCarrier,',
                         'cost': 0.0, 'profit': 0.0, 'totalBaggagePrice': 0.0, 'baggageCommissionPrice': 0.0,
                         'baggageCost': 0.0, 'baggageProfit': 0.0, 'checkinProfit': 0.0, 'handleRank': 2,
                         'releaseTime': 'Dec 29, 2022 12:45:01 PM', 'otaFillStatus': 0, 'productId': '2',
                         'priceId': '83775', 'quoteChannel': '0', 'priceGroupId': '', 'shuaPiao': False},
            'payFlightSegments': [
                {'oid': 4137105, 'payOrderUuid': 'BDL4958017100860774', 'carrier': 'Z9', 'depCity': 'KUL',
                 'depPort': 'KUL', 'arrCity': 'LGK', 'arrPort': 'LGK', 'flightNum': 'Z97703',
                 'depDate': 'Jan 23, 2023 12:00:00 AM', 'arrDate': 'Jan 23, 2023 12:00:00 AM', 'cabin': 'Y',
                 'depTime': '14:50:00', 'arrTime': '15:55:00', 'sequence': 1, 'flightType': 1}], 'payPassengers': [
                {'oid': 5393863, 'payOrderUuid': 'BDL4958017100860774', 'passengerName': 'HAZMAN/NURSYUHADAAZWANI',
                 'ageType': 0, 'birthday': 'Dec 6, 1998 12:00:00 AM', 'cardNo': 'P79546032',
                 'cardTimeLimit': 'Jan 23, 2024 12:00:00 AM', 'cardType': 'PP', 'gender': 'F', 'nationality': 'MY',
                 'certIssueCountry': 'MY', 'enNationality': 'MY', 'enCertIssueCountry': 'MY', 'enCardType': 'PP',
                 'otaPassengerId': '10472577'},
                {'oid': 5393864, 'payOrderUuid': 'BDL4958017100860774', 'passengerName': 'ISHAK/MUHAMMADARIFFADILAH',
                 'ageType': 0, 'birthday': 'Jun 9, 1993 12:00:00 AM', 'cardNo': 'P46935210',
                 'cardTimeLimit': 'Jan 23, 2024 12:00:00 AM', 'cardType': 'PP', 'gender': 'M', 'nationality': 'MY',
                 'certIssueCountry': 'MY', 'enNationality': 'MY', 'enCertIssueCountry': 'MY', 'enCardType': 'PP',
                 'otaPassengerId': '10472578'}], 'noPayedUnitList': [{'payFlightSplicedSegment': {
                'splicedOid': '4137105', 'carrier': 'Z9', 'citySegment': 'KUL-LGK', 'portSegment': 'KUL-LGK',
                'flightNum': 'Z97703', 'depDate': 'Jan 23, 2023 12:00:00 AM', 'arrDate': 'Jan 23, 2023 12:00:00 AM',
                'flightType': 1, 'depTime': '14:50:00', 'arrTime': '15:55:00'}, 'payPassenger': {'oid': 5393863,
                                                                                                 'payOrderUuid': 'BDL4958017100860774',
                                                                                                 'passengerName': 'HAZMAN/NURSYUHADAAZWANI',
                                                                                                 'ageType': 0,
                                                                                                 'birthday': 'Dec 6, 1998 12:00:00 AM',
                                                                                                 'cardNo': 'P79546032',
                                                                                                 'cardTimeLimit': 'Jan 23, 2024 12:00:00 AM',
                                                                                                 'cardType': 'PP',
                                                                                                 'gender': 'F',
                                                                                                 'nationality': 'MY',
                                                                                                 'certIssueCountry': 'MY',
                                                                                                 'enNationality': 'MY',
                                                                                                 'enCertIssueCountry': 'MY',
                                                                                                 'enCardType': 'PP',
                                                                                                 'otaPassengerId': '10472577'},
                                                                      'payOrderInfoIds': '8810424', 'type': 'TICKET'}, {
                                                                         'payFlightSplicedSegment': {
                                                                             'splicedOid': '4137105', 'carrier': 'Z9',
                                                                             'citySegment': 'KUL-LGK',
                                                                             'portSegment': 'KUL-LGK',
                                                                             'flightNum': 'Z97703',
                                                                             'depDate': 'Jan 23, 2023 12:00:00 AM',
                                                                             'arrDate': 'Jan 23, 2023 12:00:00 AM',
                                                                             'flightType': 1, 'depTime': '14:50:00',
                                                                             'arrTime': '15:55:00'},
                                                                         'payPassenger': {'oid': 5393864,
                                                                                          'payOrderUuid': 'BDL4958017100860774',
                                                                                          'passengerName': 'ISHAK/MUHAMMADARIFFADILAH',
                                                                                          'ageType': 0,
                                                                                          'birthday': 'Jun 9, 1993 12:00:00 AM',
                                                                                          'cardNo': 'P46935210',
                                                                                          'cardTimeLimit': 'Jan 23, 2024 12:00:00 AM',
                                                                                          'cardType': 'PP',
                                                                                          'gender': 'M',
                                                                                          'nationality': 'MY',
                                                                                          'certIssueCountry': 'MY',
                                                                                          'enNationality': 'MY',
                                                                                          'enCertIssueCountry': 'MY',
                                                                                          'enCardType': 'PP',
                                                                                          'otaPassengerId': '10472578'},
                                                                         'payOrderInfoIds': '8810425',
                                                                         'type': 'TICKET'}]},
                'guidePriceList': [{'totalPrice': 127.0, 'currency': 'MYR', 'tripType': 1}],
                'paymentMethod': {'id': 1, 'payment': 99, 'paynumber': '0000000000', 'name': '账户余额',
                                  'cardexpired': 'N/A', 'CVV': 'N/A', 'owner': '账户余额', 'password': '0', 'status': 0},
                'paymentAccount': {'id': 253, 'carrier': 'Z9', 'short_name': 'Z9代理人账户', 'account': 'darana_qian',
                                   'password': '1qaz@WSX', 'status': 0}, 'carrier': 'Z9', 'freeBaggageWeight': 0,
                'taskNum': 'BDL4958017100860774_1_1672289114526', 'contactName': '幸游', 'contactMobile': '15320288040',
                'contactEmail': 'flightchg@didatravel.com', 'taskExpirationTime': 'Dec 29, 2022 1:05:14 PM',
                'orderVerifyCabin': 'Y', 'type': 1, 'code': 0}

        no_hold_pay(task=task, proxies_type=None)

    def test_baggage(self):
        task = HoldTask.from_add_on_task("FZ9,KUL,KUL,LGK,baggage,2023-01-13,0")
        app = AZ9Baggage(task=task)
        app.booking_availability()
        flight = app.convert_search()
        # add_on_select_flight(task, flight)
        app.select_flight()
        app.verify_flight()
        app.get_baggage_list()

    def test_baggage_service(self):
        task = HoldTask.from_add_on_task("FZ9,KUL,LGK,baggage,2023-01-13,0")

        code, req = add_on(task)
        print(code, req)
        for x in req:
            print(x)


    def test_baggage_api(self):
        import requests
        import json

        url = "http://43.133.207.164:10241/AddonServices"

        data = {"airline": "Z9", "postData": "FZ9,KUL,LGK,baggage,2023-01-13,0"}

        rsp = requests.get(url=url, params=data)

        print(rsp.text)
        print(rsp.status_code)

