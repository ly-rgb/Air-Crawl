import collections
import json
import re
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_T3_logger
from utils.searchparser import SearchParam


class AT3Web(AirAgentV3Development):
    """https://www.easternairways.com/
     当前航司只有经停，没有中转，需要过滤
     支持多天"""

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}

        self.country_cur = [{'code': 'ABZ', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'BHD', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'DUB', 'countryCode': 'IE', 'currencyCode': 'EUR'}, {'code': 'HUY', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'JER', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'LGW', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'MAN', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'NCL', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'NQY', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'SOU', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'MME', 'countryCode': 'GB', 'currencyCode': 'GBP'}, {'code': 'WIC', 'countryCode': 'GB', 'currencyCode': 'GBP'}]

    def search(self, searchParam: SearchParam):
        try:
            cur = None
            body = None
            date_format = datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%Y-%m-%d")

            # 从哪个国家出发，就是用本国的货币
            for country_cur in self.country_cur:
                if country_cur["code"] == searchParam.dep:
                    cur = country_cur["currencyCode"]
                    spider_T3_logger.info(f"出发国家: {country_cur['code']}, 使用货币为{cur}")
                    break

            if cur == None:
                spider_T3_logger.error("没有找到该航线所对应的币种，请在浏览器的缓存中找")

            if "CRAWlLCC" in searchParam.args:
                body = json.dumps({'customerId': '0f9ef31c-e69b-43c0-89c7-b2a7a0356d67',
                                   'journeyPriceRequests': [
                                       {'currency': cur,
                                        'destination': searchParam.arr,
                                        'origin': searchParam.dep,
                                        'pax': {'ADT': searchParam.adt, 'CHD': searchParam.chd, 'INF': 0, 'TNG': 0},
                                        'details': {
                                            "allPrice": [
                                                {
                                                    "begin": date_format,
                                                    "end": date_format
                                                }],
                                            'lowestPrice': [
                                                {
                                                    'begin': (datetime.strptime(searchParam.date, "%Y-%m-%d") - timedelta(days=14)).strftime(
                                                        "%Y-%m-%d"),
                                                    'end': (datetime.strptime(searchParam.date, "%Y-%m-%d") + timedelta(days=14)).strftime(
                                                        "%Y-%m-%d")
                                                }
                                            ]},
                                        'filters': {'MaxConnectingSegments': ['20']},
                                        'id': '1'}
                                   ]})

            if "READTIMELCC" in searchParam.args:
                body = json.dumps({'customerId': '0f9ef31c-e69b-43c0-89c7-b2a7a0356d67',
                                   'journeyPriceRequests': [
                                       {'currency': cur,
                                        'destination': searchParam.arr,
                                        'origin': searchParam.dep,
                                        'pax': {'ADT': searchParam.adt, 'CHD': searchParam.chd, 'INF': 0, 'TNG': 0},
                                        'details': {
                                            "allPrice": [
                                                {
                                                    "begin": date_format,
                                                    "end": date_format
                                                }
                                            ],
                                            'lowestPrice': [
                                                {
                                                    'begin': date_format,
                                                    'end': date_format
                                                }
                                            ]},
                                        'filters': {'MaxConnectingSegments': ['20']},
                                        'id': '1'}
                                   ]})

            headers = {
                'authority': 'www.easternairways.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'apikey': 'd9eaa63c9008987381860a36e0d8c2aa2c6a936b41bf35e42bbe11e97bd452ea',
                'cache-control': 'no-cache',
                'content-type': 'application/json; charset=UTF-8',
                'cookie': '_ga=GA1.2.170227451.1657766575; ApiSessionId=ijoufuq3g2y3t5z1wiyyuicn; _gid=GA1.2.1829725814.1660274705; _gat_gtag_UA_4049922_7=1; selectedLanguage=en-GB',
                'origin': 'https://www.easternairways.com',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
            }

            response = self.post(url="https://www.easternairways.com/pricing/api/v1/journeys", data=body,
                                 headers=headers)
            spider_T3_logger.info(f"{response.text}")
            self.search_response = response
            self.is_success = json.loads(response.text)["success"]

            if self.is_success is False:
                spider_T3_logger.error("抓取失败，没有抓到对应航班")
                raise Exception

            spider_T3_logger.info(f"search_response_status: {self.search_response.status_code}")

        except Exception:
            import traceback
            spider_T3_logger.error(f"{traceback.print_exc()}")

    def convert_search(self):
        try:
            result = []

            if self.is_success is True:
                info = self.search_response.json()["journeyPriceResponses"][0]
                print(info)
                for schedule in info["schedules"]:
                    for flight in schedule["journeys"]:
                        if len(flight) == 0:
                            break

                        if flight["scheduleType"] != "LowestPrice":
                            continue

                        if len(flight["segments"][0]['legs']) > 1:
                            continue

                        fromSegments = []
                        lowestPrice = {
                            "cur": "",
                            "adultPrice": 10000,
                            "max": 0,
                            "cabin": "",
                            "info": ""
                        }
                        for idx, fare in enumerate(flight["fares"]):

                            if fare["availableSeats"] == 0 or fare["availableSeats"] == "":
                                continue

                            if lowestPrice["adultPrice"] >= fare["totalAmount"]:
                                lowestPrice.update({"cur": fare["charges"][0]["currency"],
                                                    "adultPrice": fare["totalAmount"],
                                                    "max": fare["availableSeats"],
                                                    "cabin": fare["classOfService"],
                                                    "info": json.dumps({
                                                        "id": fare["id"],
                                                        "fareBasisCode": fare["fareBasisCode"],
                                                        "productClass": fare["productClass"]
                                                    })
                                                    })

                        spider_T3_logger.info(f"最低价格信息: {lowestPrice}")

                        for fs in flight["segments"]:
                            fromSegment = {
                                "carrier": fs["transport"]["carrier"]["code"],
                                "flightNumber": (fs["transport"]["carrier"]["code"] + str(
                                    int(fs["transport"]["number"]))).replace(" ", ""),
                                "depAirport": fs["origin"],
                                "depTime": datetime.strptime(fs["stdutc"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                                "arrAirport": fs["destination"],
                                "arrTime": datetime.strptime(fs["stautc"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                                "codeshare": False,
                                "cabin": lowestPrice["cabin"],
                                'num': 0,
                                'aircraftCode': '',
                                'segmentType': 0
                            }

                            fromSegments.append(fromSegment)

                        spider_T3_logger.info(f"航段信息: {fromSegments}")

                        data = {
                            'data': flight["segments"][0]["transport"]["carrier"]["code"] +
                                    flight["segments"][0]["transport"]["number"],
                            'productClass': "ECONOMIC",
                            'fromSegments': fromSegments,
                            'cur': lowestPrice["cur"],
                            'adultPrice': lowestPrice["adultPrice"] - 1,
                            'adultTax': 1,
                            'childPrice': 0,
                            'childTax': 0,
                            'promoPrice': 0,
                            'adultTaxType': 0,
                            'childTaxType': 0,
                            'priceType': 0,
                            'applyType': 0,
                            'max': lowestPrice["max"],
                            'limitPrice': True,
                            'info': ""
                        }

                        spider_T3_logger.info(f"data: {data}")

                        result.append(data)

            return result

        except Exception:
            import traceback
            spider_T3_logger.error(f"{traceback.format_exc()}")


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0
    try:
        app = AT3Web(proxies_type=proxies_type)
        app.search(taskItem)
        print(taskItem)
        result = app.convert_search()
        if not result:
            code = -1
            spider_T3_logger.info("当天没有航班")
    except Exception:
        import traceback
        spider_T3_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = -1
    return code, result
