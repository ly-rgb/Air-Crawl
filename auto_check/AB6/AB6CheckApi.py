# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AB6CheckApi.py
@effect: "请填写用途"
@Date: 2022/12/7 15:53
"""
from utils.log import check_B6_logger
from airline.base import AirAgentV3Development
import traceback


class AB6CheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_B6_logger):
        super(AB6CheckWeb, self).__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout, logger=logger)

        self.check_url = "https://managetrips.jetblue.com/api/graphql"
        self.check_response = None
        self.error_message = None
        self.error_code = "-1"

    @property
    def base_headers(self):
        headers = {
            'authority': 'managetrips.jetblue.com',
            'application-id': 'SWS1:B6-DigConShpBk:4047e038e3',
            'authorization': 'Bearer Basic anNvbl91c2VyOmpzb25fcGFzc3dvcmQ=',
            'content-type': 'application/json',
            'referer': 'https://managetrips.jetblue.com/dx/B6DX/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'x-sabre-storefront': 'B6DX'
        }

        return headers

    def check(self, last_name, pnr):
        data = self.json.dumps({
            "operationName": "getMYBTripDetails",
            "variables": {
                "pnrQuery": {
                    "pnr": pnr,
                    "lastName": last_name
                }
            },
            "extensions": {},
            "query": "query getMYBTripDetails($pnrQuery: JSONObject!) {\n  getMYBTripDetails(pnrQuery: $pnrQuery) {\n    originalResponse\n    __typename\n  }\n  getStorefrontConfig {\n    privacySettings {\n      isEnabled\n      maskFrequentFlyerNumber\n      maskPhoneNumber\n      maskEmailAddress\n      maskDateOfBirth\n      maskTravelDocument\n      __typename\n    }\n    __typename\n  }\n}\n"
        })

        try:

            response = self.post(url=self.check_url, headers=self.base_headers, data=data)
            if response.status_code == 200:
                if "PNR.NOT_FOUND" in response.text:
                    self.error_code = "0"
                    self.logger.error(f"没有找到PNR, 请求载体: {data}")
                    self.logger.error(f"{response.text}")
                else:
                    self.error_code = "1"
                    self.check_response = response
                    self.logger.info("请求成功！！！！")
                    self.logger.info(f"请求接口: {self.check_url}\n"
                                     f"请求载荷: {data}\n"
                                     f"请求结果: {response.text}")
            else:
                raise Exception(f"请求失败, 状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")


