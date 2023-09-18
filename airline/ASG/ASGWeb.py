import collections
import datetime
import json
from typing import Dict
from requests.models import Response
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.log import spider_SG_logger
from utils.searchparser import SearchParam


class ASGWeb(AirAgentV3Development):
    search_response: Response
    """http://www.spicejet.com 不支持多天"""

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._Request = collections.namedtuple('Request', ["method", "path", "body", 'headers'])
        self.fare_response = None

    def get_token(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/101.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "os": "web",
            "referer": "https://www.spicejet.com/search"
        }
        response = self.post(url="https://www.spicejet.com/api/v1/token", headers=headers, data="{}")
        return response.json().get("data").get("token")

    def search(self, searchParam: SearchParam):
        body = {"destinationStationCode": searchParam.arr, "originStationCode": searchParam.dep,
                "onWardDate": searchParam.date,
                "currency": "INR", "pax": {"journeyClass": "ff", "adult": searchParam.adt, "child": 0, "infant": 0}}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8",
            "authorization": self.get_token(),
            "os": "web"
        }
        response = self.post(url="https://www.spicejet.com/api/v3/search/availability", headers=headers,
                             data=json.dumps(body))
        fare_response = self.low_fare(searchParam.dep, searchParam.arr, searchParam.date)
        self.fare_response = fare_response
        self.search_response = response

    def low_fare(self, dep, arr, date):
        url = "https://www.spicejet.com/api/v2/search/lowfare"
        data = {"pax": {"journeyClass": "ff", "adult": 1, "child": 0, "infant": 0},
                "codes": {"currency": {"currency": "INR"}}, "origin": dep, "destination": arr,
                "centerDate": "2022-07-17"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8",
            "authorization": self.get_token(),
            "os": "web"
        }
        response = self.post(url=url, headers=headers, data=json.dumps(data))
        return response.json()

    def convert_search(self):

        results = []
        for idx, journey in enumerate(self.search_response.json()["data"]["trips"][0]["journeysAvailable"]):
            flightnumber = journey.get("carrierString")
            flightnumber = "/".join(map(lambda x: x.split()[0] + x.split()[1], flightnumber.split(",")))
            segments = []
            for segment in journey["segments"]:
                deptime = datetime.datetime.strptime(segment["designator"]["departure"],
                                                     "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                arrtime = datetime.datetime.strptime(segment["designator"]["arrival"],
                                                     "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                fromsegments_data = {
                    'carrier': segment["carrierString"].split()[0],
                    'flightNumber': segment["carrierString"].replace(" ", ""),
                    'depAirport': segment["designator"]["origin"],
                    'depTime': deptime,
                    'arrAirport': segment["designator"]["destination"],
                    'arrTime': arrtime,
                    'codeshare': False,
                    'cabin': "Y",
                    'num': 0,
                    'aircraftCode': "",
                    'segmentType': segment["segmentType"]
                }
                segments.append(fromsegments_data)
            data = {
                'data': flightnumber,
                'productClass': 'ECONOMIC',
                'fromSegments': segments,
                'cur': self.search_response.json()["data"]["currencyCode"],
                'adultPrice': self.fare_response["data"]["lowFareDateMarkets"][idx]["lowestFareAmount"]["fareAmount"],
                'adultTax': self.fare_response["data"]["lowFareDateMarkets"][idx]["lowestFareAmount"]
                ["taxesAndFeesAmount"],
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': journey["fares"][list(journey["fares"].keys())[0]]["availableCount"],
                'limitPrice': True,
                'info': None
            }
            if len(data["data"].split("/")) != len(set(data["data"].split("/"))):
                spider_SG_logger.info(f"{data['data']}经停过滤！")
            else:
                results.append(data)
        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = ASGWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_SG_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
