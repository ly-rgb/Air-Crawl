import collections
import re
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_XP_logger
from utils.searchparser import SearchParam
import json


class AXPWeb(AirAgentV3Development):
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._headers = {
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            "tenant-identifier": "pkj8YY4yi4CMVBniXmwajQuhJ3pzGZuikbNqH3rjwsXx29TbN7z7uiBdCb6fmew9",
            "x-useridentifier": "PZ49QGY0YY1pKLEsisIm5WvkJ0MEOw",
            "Connection": "close"
        }

    def search_body(self, searchParam):
        
        date2 = searchParam.date
        if 'CRAWlLCC' in searchParam.args:
            date2 = (datetime.strptime(searchParam.date, "%Y-%m-%d")
                     + timedelta(days=5)).strftime('%Y-%m-%d')

        body = {'passengers': [{'code': 'ADT', 'count': searchParam.adt},
                               {'code': 'CHD', 'count': searchParam.chd},
                               {'code': 'SOC', 'count': 0},
                               {'code': 'INF', 'count': 0}],
                'routes': [{'fromAirport': searchParam.dep,
                            'toAirport': searchParam.arr,
                            'departureDate': datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%Y-%m-%d"),
                            'startDate': datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%Y-%m-%d"),
                            'endDate': date2}],
                'currency': 'USD',
                'fareTypeCategories': None,
                'isManageBooking': False,
                'languageCode': 'en-us'
                }

        return json.dumps(body, indent=1)

    def search(self, searchParam: SearchParam):
        response = self.post(url="https://api-production-xtra-booksecure.ezyflight.se/api/v1/Availability/SearchShop",
                             data=self.search_body(searchParam), headers=self._headers)
        self.search_response = response

    def convert_search(self):
        results = []
        currency = self.search_response.json()["currency"]
        for info in self.search_response.json()["routes"]:
            for flight in info["flights"]:

                # 首先判断票是否被卖完
                soldOut = flight["soldOut"]
                if soldOut:
                    continue

                fromSegments = []
                flightNumbers = []
                # 保留两位小数，不是四舍五入
                adultTax = float(str(flight["lowestPriceSinglePax"] - flight["lowestPriceSinglePaxWithoutTax"]).split('.')[0] \
                           + '.' + str(flight["lowestPriceSinglePax"] - flight["lowestPriceSinglePaxWithoutTax"]).split('.')[1][:2])
                for fareType in flight["fareTypes"]:
                    if len(fareType["fares"]) != 0 and fareType["fares"][0]["seatCount"] > 0:
                        fare_obj = fareType["fares"][0]
                        break

                # 遍历每个leg，将每一次中转站都记录下来，组成完整的行程
                for leg in flight["legs"]:
                    fromSegment = {
                        "carrier": leg["carrierCode"],
                        "flightNumber": (leg["carrierCode"] + str(int(leg['flightNumber']))).replace(" ", ""),
                        "depAirport": leg["from"]["code"],
                        "depTime": datetime.strptime(leg["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                        "arrAirport": leg["to"]["code"],
                        "arrTime": datetime.strptime(leg["arrivalDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                        "codeshare": False,
                        "cabin": "Y",
                        'num': 0,
                        'aircraftCode': '',
                        'segmentType': 0
                    }
                    flightNumbers.append((leg["carrierCode"] + str(int(leg['flightNumber']))).replace(" ", ""))
                    fromSegments.append(fromSegment)

                data = {
                        'data': "/".join(flightNumbers),
                        'productClass': "ECONOMIC",
                        'fromSegments': fromSegments,
                        'cur': currency,
                        'adultPrice': flight["lowestPriceSinglePaxWithoutTax"],
                        'adultTax': adultTax,
                        'childPrice': 0,
                        'childTax': 0,
                        'promoPrice': 0,
                        'adultTaxType': 0,
                        'childTaxType': 0,
                        'priceType': 0,
                        'applyType': 0,
                        'max': fare_obj["seatCount"],
                        'limitPrice': True,
                        'info': ""
                    }
                results.append(data)

        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AXPWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = -1
            spider_XP_logger.info("当天没有航班")
    except Exception:
        import traceback
        spider_XP_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = -1
    return code, result
