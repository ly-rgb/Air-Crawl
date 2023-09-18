# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AVBCheckApi.py
@effect: "请填写用途"
@Date: 2022/11/11 15:38
"""
from utils.log import check_VB_logger
from airline.base import AirAgentV3Development
import traceback


class AVBCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout)

        self.error_code = "-1"
        self.check_url = "https://api.vivaaerobus.com/web/v1/booking/full"
        self.check_response = None

    @property
    def base_header(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'X-Channel': 'web',
            'x-api-key': 'zasqyJdSc92MhWMxYu6vW3hqhxLuDwKog3mqoYkf',
        }

        return headers

    def check(self, last_name, pnr):
        params = {
            "pnr": pnr,
            "lastName": last_name
        }

        try:
            response = self.get(url=self.check_url, headers=self.base_header, params=params)
            if response.status_code == 200:
                self.error_code = "1"
                self.check_response = response
                check_VB_logger.info(f"请求成功，接口地址: {self.check_url}")
                check_VB_logger.info(f"请求载荷: {params}")
            else:
                self.error_code = "0"
                check_VB_logger.error(f"状态码: {response.status_code}")
                check_VB_logger.error(f"失败结果: {response.text}")

        except Exception:
            self.error_code = "-1"
            check_VB_logger.error(f"请求失败，接口地址: {self.check_url}")
            check_VB_logger.error(f"请求载荷: {params}")
