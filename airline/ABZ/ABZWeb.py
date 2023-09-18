import json
from datetime import datetime
from typing import Dict
import traceback
import requests
from utils.log import spider_BZ_logger
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam


class ABZWeb(AirAgentV3Development):
    """
    这个航司比较特殊，只有直达航班，没有中转航班
    """
    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self.session = requests.session()
        self.currency_choice_url = "https://booking.bluebirdair.com/controllers/general/currencyHandler.php"
        self.front_search_url = "https://booking.bluebirdair.com/controllers/general/sessionHandler.php"
        self.search_url = "https://booking.bluebirdair.com/controllers/flightresults/flightList.php?action=flightsPull"
        self.search_response = None
        self.front_search_response = None
        self.cur = "EUR"

    @property
    def base_headers(self):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"'
        }
        return headers

    def currency_choice(self, cur="EUR"):
        """
        选择币种，（使用EUR）
        :return:
        """
        try:

            payload = json.dumps({
                "checkin": 0,
                "currencyToChange": cur
            })

            response = self.session.get(url=self.currency_choice_url, headers=self.base_headers, params=payload)
            if response.status_code == 200:
                self.cur = cur
                spider_BZ_logger.info(f"使用的币种为{self.cur}")
                spider_BZ_logger.info(f"请求参数为: {payload}")

        except Exception:
            spider_BZ_logger.error(f"请求失败，请检查接口: {self.currency_choice_url}")
            spider_BZ_logger.error(f"{traceback.format_exc()}")

    def front_search(self, searchParam: SearchParam):

        try:
            data = f'/flight-results/{searchParam.dep}-{searchParam.arr}/{searchParam.date}/NA/{searchParam.adt}/0/0'
            payload = json.dumps({
                'container': 'recentSearch',
                'data': data,
                'action': 'add'
            })

            response = self.session.post(url=self.front_search_url, headers=self.base_headers, data=payload)

            if response.status_code == 200:
                self.front_search_response = response
                spider_BZ_logger.info(f"set-cookie: {response.cookies}")
        except Exception:
            spider_BZ_logger.error(f"前置请求发送失败，请检查接口：{self.front_search_url}")
            spider_BZ_logger.error(f"{traceback.format_exc()}")

    def search(self):

        try:
            response = self.session.get(url=self.search_url, headers=self.base_headers)

            if response.status_code == 200:
                self.search_response = response
                spider_BZ_logger.info(f"请求结果为：{response.text}")
        except Exception:
            spider_BZ_logger.error(f"请求发送失败，请检查接口： {self.search_url}")
            spider_BZ_logger.error(f"{traceback.format_exc()}")

    def convert_search(self):
        result = []
        from_segment_list = []
        try:
            all_info = self.search_response.json()["outbound"]
            for flight in all_info:
                # 初始化最低价格信息
                lowest_price = {
                    "adultPrice": 100000,
                    "adultTax": 0,
                    "max": 0,
                    "cabin": "",
                    "info": ""
                }

                # 提取价格信息
                for price_info in flight["classes"]:
                    print(price_info)

                    if price_info["cabincode"] != "ECO":
                        spider_BZ_logger.error("这个不是经济舱，请注意")

                    if lowest_price["adultPrice"] >= float(price_info["rackfarebreakdown"]["adultfare"]):
                        lowest_price.update({
                            "adultPrice": price_info["rackfarebreakdown"]["adultfare"],
                            "adultTax": price_info["rackfarebreakdown"]["tax"],
                            "max": 0,
                            "cabin": "E" if price_info["cabincode"] == "ECO" else "Y",
                            "info": price_info["fareconditions"]
                        })

                spider_BZ_logger.info(f"最低价格信息：{lowest_price}")

                # 提取航班信息
                carrier = flight["fltnum"][:2]
                flight_number = flight["fltnum"][2:]
                dep = flight["fromcode"]
                arr = flight["tocode"]
                dep_time = datetime.strptime(flight["stdinutc"], "%Y/%m/%d %H:%M:%S.000").strftime("%Y%m%d%H%M")
                arr_time = datetime.strptime(flight["stainutc"], "%Y/%m/%d %H:%M:%S.000").strftime("%Y%m%d%H%M")

                from_segments = {
                    'carrier': carrier,
                    'flightNumber': flight_number,
                    'depAirport': dep,
                    'depTime': dep_time,
                    'arrAirport': arr,
                    'arrTime': arr_time,
                    'codeshare': False,
                    'num': 0,
                    'cabin': lowest_price["cabin"],
                    'aircraftCode': '',
                    'segmentType': 0
                }
                from_segment_list.append(from_segments)
                spider_BZ_logger.info(f"航段信息为： {from_segment_list}")

                data = {
                    "data": flight["fltnum"],
                    "productClass": "ECONOMIC",
                    "fromSegments": from_segment_list,
                    "cur": self.cur,
                    "adultPrice": lowest_price["adultPrice"],
                    "adultTax": lowest_price["adultTax"],
                    'childPrice': 0,
                    'childTax': 0,
                    'promoPrice': 0,
                    'adultTaxType': 0,
                    'childTaxType': 0,
                    'priceType': 0,
                    'applyType': 0,
                    'max': lowest_price["max"],
                    "limitPrice": True,
                    "info": lowest_price["info"]
                }
                result.append(data)

            spider_BZ_logger.info(f"最终结果为: {result}")
            return result
        except Exception:
            spider_BZ_logger.error("解析数据失败，请检查json结构是否改变")
            spider_BZ_logger.error(f"{traceback.format_exc()}")








