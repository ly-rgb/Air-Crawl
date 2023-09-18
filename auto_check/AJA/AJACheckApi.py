# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AJACheckApi.py
@effect: "请填写用途"
@Date: 2022/11/18 14:56
"""
from airline.base import AirAgentV3Development
from utils.log import check_JA_logger
import requests
import traceback


class AJACheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_JA_logger):
        super(AJACheckWeb, self).__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout, logger=logger)
        self.session = requests.session()
        self.error_code = "-1"

        self.retrieve_booking_url = "https://booking.jetsmart.com/Booking/Retrieve"
        self.check_url = "https://booking.jetsmart.com/V2/Itinerary"
        self.retrieve_booking_response = None
        self.check_response = None

    @property
    def base_headers(self):
        headers = {
            'authority': 'booking.jetsmart.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        return headers

    def retrieve_check(self, last_name, pnr):

        params = {"rl": pnr,
                  "ln": last_name
                  }
        try:
            response = self.session.get(url=self.retrieve_booking_url, headers=self.base_headers, params=params, allow_redirects=False)

            if response.status_code == 302 and response.headers['location'] == "/V2/Itinerary":
                self.error_code = "1"
                self.retrieve_booking_response = response
                self.logger.info(f"请求成功，正在跳转到location: {self.retrieve_booking_response.headers['location']}")
                self.logger.info(f"请求载荷: {params}")
            elif response.headers['location'] == "/":
                self.error_code = "0"
                self.logger.error(f"请求失败，正在跳转到location: {response.headers['location']}")
                self.logger.error(f"PNR或LastName错误: {params}")
            else:
                self.error_code = "-1"
                self.logger.error("跳转失败")
                self.logger.error(f"请求地址: {self.retrieve_booking_url}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"请求地址: {self.retrieve_booking_url}")
            self.logger.error(f"请求载荷: {params}")
            self.logger.error(f"{traceback.print_exc()}")

    def check(self):

        params = {"culture": "en-US"}

        try:
            response = self.session.get(url=self.check_url, headers=self.base_headers, params=params)

            if response.status_code == 200 and self.error_code == "1":
                self.error_code = "1"
                self.check_response = response
                self.logger.info(f"请求成功")
                self.logger.info(f"请求url: {self.check_url}")
            else:
                self.error_code = "-1"
                self.logger.error(f"请求地址: {self.check_url}")
                self.logger.error(f"请求载荷: {params}")
        except Exception:
            self.error_code = "-1"
            self.logger.error(f"请求地址: {self.check_url}")
            self.logger.error(f"请求载荷: {params}")
            self.logger.error(f"{traceback.print_exc()}")


