# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: ATKCheckApi.py
@effect: "请填写用途"
@Date: 2022/11/30 15:58
"""
from airline.base import AirAgentV3Development
from utils.log import check_TK_logger


class ATKCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_TK_logger):

        super(ATKCheckWeb, self).__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout, logger=logger)
        self.check_url = "https://www.turkishairlines.com/com.thy.web.online.ibs/ibs/booking/searchreservation"
        self.check_response = None
        self.error_code = "-1"
        self.__message = None

    @property
    def base_headers(self):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://www.turkishairlines.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.turkishairlines.com/en-us/index.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'country': 'us',
            'page': 'https://www.turkishairlines.com/en-us/index.html',
            'pageRequestId': '3febbdbe-f6ee-43a2-bdff-d8067b0ff089',
            'requestId': '1aaffdfd-565f-41d8-acf1-d3237dbbae74',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        return headers

    def check(self, last_name, pnr):

        body = {
            "pnr": pnr,
            "surname": last_name,
            "passengers": [],
            "tccManageBooking": False,
            "retrieveBaggage": True
        }
        try:
            response = self.post(url=self.check_url, headers=self.base_headers, json=body)

            if response.status_code == 200:
                is_success = response.json()["type"]
                if is_success == "SUCCESS":
                    self.error_code = "1"
                    self.check_response = response
                    self.logger.info("---------请求成功-------------")
                    self.logger.info(f"请求接口: {self.check_url}")
                    self.logger.info(f"请求载荷: {body}")
                elif is_success == "ERROR":
                    self.error_code = "0"
                    self.__message = response.json()["error"]["messages"]
                    self.logger.error(f"__message: {self.__message}")
            else:
                raise Exception(f"请求失败，请检查代理，UA等...状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.error("---------请求失败-------------")
            self.logger.error(f"请求接口: {self.check_url}")
            self.logger.error(f"请求载荷: {body}")
            self.logger.error(f"错误message: {self.__message}")
