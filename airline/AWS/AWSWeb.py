import collections
import re
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_WS_logger
from utils.searchparser import SearchParam


class AWSWeb(AirAgentV3Development):
    """test-apiw.westjet.com"""
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.westjet.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.westjet.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "macOS",
        }

    def search(self, searchParam: SearchParam):
        url = "https://test-apiw.westjet.com/bookingservices/flightSearch?guests=[%7B%22type%22:%22adult%22,%22count%22:%22" + str(
            searchParam.adt) + \
              "%22%7D,%7B%22type%22:%22child%22,%22count%22:%220%22%7D,%7B%22type%22:%22infant%22,%22count%22:%220%22%7D]" + \
              "&trips=[%7B%22order%22:1,%22departure%22:%22" + searchParam.dep + "%22,%22arrival%22:%22" + searchParam.arr \
              + "%22,%22departureDate%22:%22" + searchParam.date +\
              "%22%7D]&currency=CAD&showMemberExclusives=false&promoCode=&bookId=&appSource=widgetOW"
        self.search_response = self.get(
            url=url, headers=self._headers)

    def convert_search(self):
        results = []
        print(self.search_response.text)
        for flightOption in self.search_response.json()["flights"][0]["flightOptions"]:
            segments = []
            adultfare = flightOption["adultFare"]["priceDetails"][0]["totalFareAmount"]
            cabin = flightOption["adultFare"]["priceDetails"][0]["cabinCodes"][0]
            totalTaxAmount = flightOption["adultFare"]["priceDetails"][0]["taxInfo"]["totalTaxAmount"]
            for flightSegment in flightOption["flightDetails"]["flightSegments"]:
                segment = {
                    'carrier': flightSegment["marketingAirline"],
                    'flightNumber': flightSegment["marketingAirline"] + str(int(flightSegment["flightNumber"])),
                    'depAirport': flightSegment["originCode"],
                    'depTime': datetime.strptime(flightSegment["departureDateRaw"].split(".")[0],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                    'arrAirport': flightSegment["destinationCode"],
                    'arrTime': datetime.strptime(flightSegment["arrivalDateRaw"].split(".")[0],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                    'codeshare': False,
                    'cabin': cabin,
                    'num': 0,
                    'aircraftCode': '',
                    'segmentType': 0
                }
                segments.append(segment)
            item = {
                "data": "/".join(map(lambda x: x["flightNumber"], segments)),
                "productClass": "ECONOMIC",
                "fromSegments": segments,
                "cur": self.search_response.json()["flights"][0]["currency"],
                "adultPrice": adultfare,
                "adultTax": totalTaxAmount,
                "childPrice": 0,
                "childTax": 0,
                "promoPrice": 0,
                "adultTaxType": 0,
                "childTaxType": 0,
                "priceType": 0,
                "applyType": 0,
                "max": 10,
                "limitPrice": True,
                "info": self.search_response.json()["flights"][0]["flightSearchId"]
            }
            results.append(item)
        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AWSWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_WS_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
