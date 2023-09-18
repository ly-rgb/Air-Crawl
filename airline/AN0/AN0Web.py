import json
import traceback
from airline.base import AirAgentV3Development
from robot import HoldTask
from typing import Dict
from utils.log import spider_N0_logger
from utils.searchparser import SearchParam
from datetime import datetime
import base64
import math


class AN0Web(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self.token = None
        self.token_url = "https://services.flynorse.com/api/v1/token"
        self.search_url = "https://services.flynorse.com/api/v1/availability/search?clear=true"
        self.search_response = None

    @property
    def base_headers(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"'
        }
        return headers

    def get_token(self):

        try:

            payload = json.dumps({
                "platformType": "Web"
            })

            response = self.post(url=self.token_url, headers=self.base_headers, data=payload)
            result = response.json()
            if result["errors"] is None:
                self.token = result["data"]["token"]
                spider_N0_logger.info(f"TOKEN: {self.token}")
        except Exception:
            spider_N0_logger.error(f"没有取到TOKEN，请检查接口{self.token_url}")
            spider_N0_logger.error(f"{traceback.format_exc()}")

    def search(self, searchParam: SearchParam):
        try:

            body = json.dumps({
                "criteria": [
                    {
                        "origin": searchParam.dep,
                        "destination": searchParam.arr,
                        "beginDate": searchParam.date
                    }
                ],
                "passengers": [
                    {
                        "type": "ADT",
                        "count": searchParam.adt
                    }
                ],
                "currencyCode": "USD",
                "promotionCode": "",
                "clearBooking": True
            })

            cookies = {
                "X-Access-Token": self.token
            }

            response = self.post(url=self.search_url, headers=self.base_headers, data=body, cookies=cookies)
            if response.status_code == 200 and response.json()["errors"] is None:
                self.search_response = response

                spider_N0_logger.info(f"请求载体: {body}")
                spider_N0_logger.info(f"cookie: {cookies}")

        except Exception:
            spider_N0_logger.error(f"search接口请求失败，请检查接口{self.search_url}")
            spider_N0_logger.error(f"{traceback.format_exc()}")

    def convert_search(self):
        result = []
        flight_num_list = []
        from_segments_list = []

        if self.search_response is not None:
            all_info = self.search_response.json()["data"]["results"][0]["trips"]

            for flight in all_info:
                # 初始化最低价格信息
                lowest_price = {
                    "adultPrice": 100000,
                    "adultTax": 0,
                    "max": 0,
                    "cabin": "",
                    "info": ""
                }

                journeys = flight["journeysAvailableByMarket"][0]

                # 提取价格，座位数等信息
                for fare in journeys["fares"]:
                    if lowest_price["adultPrice"] >= fare["details"]["totals"]["roundedFareTotal"]:
                        lowest_price.update({
                            "adultPrice": fare["details"]["totals"]["publishedTotal"],
                            "adultTax": math.ceil(fare["details"]["totals"]["taxesAndFeesTotal"]),
                            "max": fare["details"]["availableCount"],
                            "cabin": 'E' if fare["details"]["cabin"] == "Economy" else "Y",
                            "info": AN0Web.decrypt_key(fare["fareAvailabilityKey"])
                        })

                spider_N0_logger.info(f"最低价格信息：{lowest_price}")

                # 提取航段信息
                for segment in journeys["segments"]:
                    flight_num = segment["identifier"]["carrierCode"] + segment["identifier"]["identifier"]
                    carrier = segment["identifier"]["carrierCode"]
                    dep = segment["designator"]["origin"]
                    arr = segment["designator"]["destination"]
                    dep_time = datetime.strptime(segment["designator"]["departure"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M")
                    arr_time = datetime.strptime(segment["designator"]["arrival"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M")

                    fromSegments = {
                        'carrier': carrier,
                        'flightNumber': flight_num,
                        'depAirport': dep,
                        'depTime': dep_time,
                        'arrAirport': arr,
                        'arrTime': arr_time,
                        'codeshare': False,
                        'cabin': lowest_price["cabin"],
                        'num': 0,
                        'aircraftCode': '',
                        'segmentType': 0
                    }

                    from_segments_list.append(fromSegments)
                    flight_num_list.append(flight_num)
                    spider_N0_logger.info(f"航段信息fromSegment: {fromSegments}")

                data = {
                    'data': "/".join(flight_num_list),
                    'productClass': 'ECONOMIC',
                    'fromSegments': from_segments_list,
                    'cur': 'USD',
                    'adultPrice': lowest_price["adultPrice"],
                    'adultTax': lowest_price["adultTax"],
                    'childPrice': 0,
                    'childTax': 0,
                    'promoPrice': 0,
                    'adultTaxType': 0,
                    'childTaxType': 0,
                    'priceType': 0,
                    'applyType': 0,
                    'max': lowest_price["max"],
                    'limitPrice': True,
                    'info': lowest_price["info"]
                }
                spider_N0_logger.info(f"data所有信息: {data}")
                result.append(data)

        return result

    @staticmethod
    def decrypt_key(encrypt_key):
        """
        对fareAvailabilityKey进行解密，得到info字段
        :param key:
        :return:
        """

        key = base64.b64decode(encrypt_key.replace('-', '=').encode(), altchars='_-'.encode()).decode()

        return key