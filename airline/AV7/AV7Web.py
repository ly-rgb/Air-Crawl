import collections
import json
import traceback
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_V7_logger
from utils.searchparser import SearchParam
from airline.AV7.awsv4 import AwsV4
import os


class V7JWeb(AirAgentV3Development):
    search_response: Response
    """
    支持多天  亚马逊检测
    https://book.volotea.com/search
    """

    def __init__(self, proxies_type=7, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._Request = collections.namedtuple('Request', ["method", "path", "body", 'headers'])

    def _authorization_params(self, request, date_stamp):
        arg = {
            "service": "execute-api",
            "host": "api.volotea.com",
            "region": "eu-west-1",
            "endpoint": "https://api.volotea.com/",
            "access_key": "AKIATLNGK7P7IQRWEQ4J",
            "secret_key": "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",
            "date_stamp": date_stamp
        }
        return AwsV4(request, **arg).get_authorization()

    def get_headers(self, request):
        date_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        authorization = self._authorization_params(request, date_stamp)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
            "X-Amz-Date": date_stamp,
            "x-api-key": "e94ab0cb5c614fc3b1ce49d89f6a-spa",
            "content-Type": "application/json",
            "accept": "application/json",
            "Authorization": authorization,
            "Host": "api.volotea.com",
        }
        return headers

    # token定时更新，不用每次访问
    def login_token(self):
        """通过登录接口拿到token"""
        body = """{
          "isRemembered": false,
          "hash": "",
          "username": "",
          "password": ""
        }"""
        request = self._Request("POST", "/api/spa/voe/v1/account/login", body, headers={"accept": "application/json"})
        headers = self.get_headers(request)

        try:
            response = self.post('https://api.volotea.com/api/spa/voe/v1/account/login',
                                 headers=headers, data=body)
            token = response.json()["data"]["token"]
            return token
        except:
            spider_V7_logger.error(traceback.format_exc())

    def search_body(self, searchParam: SearchParam, is_now):
        criteria = []
        for day in range(5):
            criteria.append({
                "selectedDate": (datetime.strptime(searchParam.date, "%Y-%m-%d") + timedelta(days=day)).strftime(
                    "%Y-%m-%d"),
                "origin": searchParam.dep,
                "destination": searchParam.arr
            })
        body = {
            "criteria": criteria if is_now else [criteria[0]],
            "codes": {
                "currency": "EUR",
                "promotionCode": "",
                "bookingType": 1,
                "residentType": "NONE"
            },
            "passengers": [
                {
                    "type": "ADT",
                    "count": searchParam.adt
                }
            ],
            "forcedPreselectedFareType": "S"
        }

        return json.dumps(body, indent=1)

    def search(self, searchParam: SearchParam):
        is_now = True

        if 'CRAWlLCC' not in searchParam.args:
            is_now = False
        spider_V7_logger.info("proxy_type{}".format(self.proxies_type))

        token = self.login_token()

        body = self.search_body(searchParam, is_now)
        request = self._Request("POST", "/api/spa/voe/v1/flights/search", body,
                                headers={"accept": "application/json"})
        headers = self.get_headers(request)
        headers["x-session-token"] = token
        response = self.post(url="https://api.volotea.com/api/spa/voe/v1/flights/search", data=body, headers=headers)
        self.search_response = response
        spider_V7_logger.info(
            "status_code:{},search_response: {}".format(self.search_response.status_code, self.search_response.text))

    def convert_search(self):
        results = []

        for trip in self.search_response.json()["data"]["trips"]:
            for ele in trip["journeysAvailable"]:
                if not ele.get('fares', None):
                    continue
                if ele.get("ticketsAvailable", 0) <= 0:
                    continue
                fares = list(filter(lambda x: x['fareType'] == 'Regular', ele['fares']))
                if not fares:
                    continue
                fare = fares[0]

                fromSegments = []

                for segments in ele.get("segments"):
                    flightNumber = segments["identifier"]["carrierCode"] + str(int(str(segments["identifier"]
                                                                                       ["identifier"]).strip()))
                    dep_air_port = segments["designator"]["origin"]
                    arr_air_port = segments["designator"]["destination"]
                    dep_time = datetime.strptime(segments["designator"]["departure"],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                    arr_time = datetime.strptime(segments["designator"]["arrival"],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                    fromSegments.append({
                        'carrier': segments["identifier"]["carrierCode"],
                        'flightNumber': flightNumber,
                        'depAirport': dep_air_port,
                        'depTime': dep_time,
                        'arrAirport': arr_air_port,
                        'arrTime': arr_time,
                        'codeshare': False,
                        'cabin': fare["fareClassOfService"],
                        'num': 0,
                        'aircraftCode': '',
                        'segmentType': 0
                    })

                data = {
                    'data': "/".join(map(lambda x: x['flightNumber'], fromSegments)),
                    'productClass': 'ECONOMIC',
                    'fromSegments': fromSegments,
                    'cur': 'EUR',
                    'adultPrice': float(fare["passengerFares"][0]["fareAmount"]['eurAmount']) - 1,
                    'adultTax': 1,
                    'childPrice': 0,
                    'childTax': 0,
                    'promoPrice': 0,
                    'adultTaxType': 0,
                    'childTaxType': 0,
                    'priceType': 0,
                    'applyType': 0,
                    'max': fare["availabilityCount"],
                    'limitPrice': True,
                    'info': fare["fareType"]
                }
                if len(data["data"].split("/")) != len(set(data["data"].split("/"))):
                    spider_V7_logger.info(f"{data['data']}经停过滤！")
                else:
                    results.append(data)
        return results


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0
    try:
        app = V7JWeb(proxies_type=proxies_type)

        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = -1
            spider_V7_logger.info("当天没有航班")
    except Exception:
        import traceback
        spider_V7_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = -1
    return code, result
