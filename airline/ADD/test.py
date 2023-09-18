import os

os.chdir("../../")

import unittest
from airline.ADD.service import api_search,no_hold_pay
from utils.searchparser import parser_from_task

# os.environ['http_proxy'] = 'http://127.0.0.1:8888'
# os.environ['https_proxy'] = 'http://127.0.0.1:8888'

# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here
#
#     def test_api_search(self):
#         task = 'ADD,DMK,CEI,2022-09-30,,1,,,AFARE,0,,CRAWlLCC'
#         code, req = api_search(parser_from_task(task), proxies_type=7)
#         print(code, req)
#         for x in req:
#             print(x)
#         self.assert_(req)



def test_api_search():
    task = 'ADD,DMK,LPT,2022-12-20,,3,,,AFARE,0,,CRAWlLCC'
    code, req = api_search(parser_from_task(task), proxies_type=6)
    print(code, req)
    for x in req:
        print(x)
def test_no_hold_pay():
    task =  {
  "payOrderDetail": {
    "payOrder": {
      "uuid": "DRCP5636039150554195_xxxxx1",
      "otaId": "869735444",
      "otaCompany": 15,
      "groupCode": "weelfly",
      "fromFlightNum": "DD121",
      "fromFlightSegment": "CNX-DMK",
      "fromFlightCarrier": "DD",
      "depDate": "Nov 19, 2022 7:10:00 PM",
      "ticketPrice": 299,
      "ticketTax": 1,
      "totalPrice": 300,
      "bookingTime": "Oct 16, 2022 11:16:01 PM",
      "payTime": "Oct 16, 2022 11:20:07 PM",
      "createTime": "Oct 16, 2022 11:21:01 PM",
      "apiSystemUuid": "DRCP7283155417278",
      "depAirport": "CNX",
      "arrAirport": "DMK",
      "tripType": 1,
      "commissionPrice": 0,
      "remark": "用优惠码AMZTH300在 DD代理人账号--2022泰铢 账户出，用账户余额支付   多人订单的话拆分出票 一个人一个人出(登陆名称：INC00039）\n优惠码订单机器人不处理\n2BAPVZ / 58865936\n重跑次数过多 ",
      "selPnr": "Aivu98",
      "adtCount": 1,
      "chidCount": 0,
      "infantCount": 0,
      "status": 3,
      "userId": 129,
      "userName": "姜华",
      "orderType": 0,
      "tags": ",UNHOLD,BaggageOrder,PROMOCODE,NoDecision,",
      "cost": 282.13,
      "profit": 17.87,
      "totalBaggagePrice": 229,
      "baggageCommissionPrice": 0,
      "baggageCost": 88.97,
      "baggageProfit": 140.03,
      "checkinProfit": 0,
      "outTicketTime": "Oct 16, 2022 11:56:03 PM",
      "handleRank": 1194,
      "releaseTime": "Oct 16, 2022 11:21:01 PM",
      "firstPullTime": 5,
      "otaFillStatus": 1,
      "productId": "2",
      "priceId": "81505",
      "quoteChannel": "0",
      "outTicketChannel": "0",
      "priceGroupId": "",
      "shuaPiao": "false"
    },
    "payFlightSegments": [
      {
        "oid": 3831495,
        "payOrderUuid": "DRCP5636039150554195",
        "carrier": "DD",
        "depCity": "CNX",
        "depPort": "CNX",
        "arrCity": "BKK",
        "arrPort": "DMK",
        "flightNum": "DD121",
        "flightNumPull": "DD121",
        "depDate": "Nov 19, 2022 07:10:00 AM",
        "arrDate": "Nov 19, 2022 12:00:00 AM",
        "cabin": "L",
        "depTime": "07:00:00",
        "arrTime": "20:15:00",
        "sequence": 1,
        "flightType": 1
      }
    ],
    "payPassengers": [
      {
        "oid": 4989072,
        "payOrderUuid": "DRCP5636039150554195",
        "passengerName": "KHANSUWAN/CHUREEPATE",
        "ageType": 0,
        "birthday": "Jun 13, 1955 12:00:00 AM",
        "cardNo": "",
        "cardTimeLimit": "Oct 16, 2032 12:00:00 AM",
        "cardType": "护照",
        "gender": "F",
        "nationality": "TH",
        "certIssueCountry": "TH",
        "enNationality": "TH",
        "enCertIssueCountry": "TH",
        "enCardType": "护照"
      }
    ],
    "payPassengerBaggages": [
      {
        "oid": 813554,
        "payOrderUuid": "DRCP5636039150554195",
        "payPassengerOid": 4989072,
        "payFlightSegmentOid": 3831495,
        "baggageWeight": 0,
        "baggagePrice": 229,
        "payOrderInfoOid": 8372047,
        "payPassengerName": "KHANSUWAN/CHUREEPATE",
        "otaBaggageId": "21423264274"
      }
    ],
    "noPayedUnitList": [
      {
        "payFlightSplicedSegment": {
          "splicedOid": "3831495",
          "carrier": "DD",
          "citySegment": "CNX-BKK",
          "portSegment": "CNX-DMK",
          "flightNum": "DD121",
          "depDate": "Nov 19, 2022 07:10:00 AM",
          "arrDate": "Nov 19, 2022 12:00:00 AM",
          "flightType": 1,
          "depTime": "07:10:00",
          "arrTime": "20:15:00"
        },
        "payPassenger": {
          "oid": 4989072,
          "payOrderUuid": "DRCP5636039150554195",
          "passengerName": "KHANSUWAN/CHUREEPATE",
          "ageType": 0,
          "birthday":"Jun 13, 1955 12:00:00 AM",
          "cardNo": "",
          "cardTimeLimit": "Oct 16, 2032 12:00:00 AM",
          "cardType": "护照",
          "gender": "F",
          "nationality": "TH",
          "certIssueCountry": "TH",
          "enNationality": "TH",
          "enCertIssueCountry": "TH",
          "enCardType": "护照"
        },
        "payOrderInfoIds": "8372047",
        "type": "TICKET"
      }
    ],
    "noPayedUnitBagList": [
      {
        "payFlightSplicedSegment": {
          "splicedOid": "3831495",
          "carrier": "DD",
          "citySegment": "CNX-BKK",
          "portSegment": "CNX-DMK",
          "flightNum": "DD121",
          "depDate": "Nov 19, 2022 07:10:00 AM",
          "arrDate": "Nov 11, 2022 12:00:00 AM",
          "flightType": 1,
          "depTime": "07:10:00",
          "arrTime": "20:15:00"
        },
        "payPassenger": {
          "oid": 4989072,
          "payOrderUuid": "DRCP5636039150554195",
          "passengerName": "KHANSUWAN/CHUREEPATE",
          "ageType": 0,
          "birthday": "Jun 13, 1955 12:00:00 AM",
          "cardNo": "",
          "cardTimeLimit": "Oct 16, 2032 12:00:00 AM",
          "cardType": "护照",
          "gender": "F",
          "nationality": "TH",
          "certIssueCountry": "TH",
          "enNationality": "TH",
          "enCertIssueCountry": "TH",
          "enCardType": "护照"
        },
        "payPassengerBaggage": {
          "oid": 813554,
          "payOrderUuid": "DRCP5636039150554195",
          "payPassengerOid": 4989072,
          "payFlightSegmentOid": 3831495,
          "baggageWeight": 0,
          "baggagePrice": 229,
          "payOrderInfoOid": 8372047,
          "payPassengerName": "KHANSUWAN/CHUREEPATE",
          "otaBaggageId": "21423264274"
        },
        "payOrderInfoIds": "813554",
        "type": "BAGGAGE"
      }
    ]
  },
  "guidePriceList": [
    {
      "totalPrice": 1029,
      "currency": "THB",
      "tripType": 1
    }
  ],
  "paymentMethod": {
    "id": 1,
    "payment": 99,
    "paynumber": "0000000000",
    "name": "账户余额",
    "cardexpired": "N/A",
    "CVV": "N/A",
    "owner": "账户余额",
    "password": "0",
    "status": 0
  },
  "paymentAccount": {
    "id": 28,
    "carrier": "DD",
    "short_name": "DD大然泰铢代理人账户",
    "account": "BJDRT",
    "password": "Noknok2018",
    "status": 1
  },
  "carrier": "DD",
  "freeBaggageWeight": 0,
  "taskNum": "DRCP5636039150554195_1_1666002260466",
  "contactName": "CTRIP/CTRIP",
  "contactMobile": "18611715578",
  "contactEmail": "nevergiveup17apr04@qq.com",
  "taskExpirationTime": "Oct 17, 2022 6:44:37 PM",
  "type": 1,
  "code": 0
}
    no_hold_pay(task,proxies_type=0)

if __name__ == '__main__':
    # unittest.main()
    test_api_search()
    # test_no_hold_pay()

