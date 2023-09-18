# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AODCheckApi.py
@effect: "ODAPI质检api层"
@Date: 2022/11/8 15:01
"""
from utils.log import check_OD_logger
import traceback
from airline.base import AirAgentV3Development


class AODCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout)

        self.api_check_url = "http://47.74.250.125:8985/supplier/searchPnr"
        self.api_check_response = None
        self.error_code = "-1"

    @property
    def base_headers(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
        }
        return headers

    def api_check(self, pnr: str):
        """
        OD api质检
        :return:
        """
        params = {
            "channel": "AFARE",
            "carrier": "OD",
            "pnr": pnr,
            "ori": "false"
        }

        try:
            response = self.get(url=self.api_check_url, params=params, headers=self.base_headers)
            # is_success = response.json()['success']
            if "非法pnr" in response.text:
                self.error_code = "0"
                check_OD_logger.error("没找到PNR")
                check_OD_logger.error(f"请求载体: {params}")
                check_OD_logger.error(f"接口地址: {self.api_check_url}")
                check_OD_logger.error(f"错误结果为: {response.text}")
            else:
                self.error_code = "1"
                self.api_check_response = response
                check_OD_logger.info(f"接口请求成功！！！")
                check_OD_logger.info(f"接口地址: {self.api_check_url}")
                check_OD_logger.info(f"请求载体: {params}")

        except Exception:
            self.error_code = "-1"
            check_OD_logger.error(f"接口请求异常， 接口地址: {self.api_check_url}")
            check_OD_logger.error(f"请求载体: {params}")
            check_OD_logger.error(f"{traceback.print_exc()}")

