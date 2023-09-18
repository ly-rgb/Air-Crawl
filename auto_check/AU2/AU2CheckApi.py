# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AU2CheckApi.py
@effect: "请填写用途"
@Date: 2022/12/9 14:59
"""
import time

from airline.base import AirAgentV3Development
from utils.log import check_PNR_U2_logger
import traceback


class AU2Web(AirAgentV3Development):
    """
    质检请求接口
    """
    pass


class AU2PnrWeb(AirAgentV3Development):
    """
    检查PNR状态接口
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_PNR_U2_logger, request_log=True):
        super(AU2PnrWeb, self).__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout,
                                        logger=logger, request_log=request_log)
        self.check_url1 = "http://43.133.13.187:5000/Check/U2"
        self.check_response = None
        # 0: 正常 -1: 请求失败
        self.req_code = -1

    def check(self, pnr, last_name):

        params = {
            'recordLocator': pnr,
            'lastName': last_name
        }

        headers = {
            "Connection": "close"
        }

        try:
            for i in range(20):
                time.sleep(0.2)
                response1 = self.get(url=self.check_url1, params=params, headers=headers)
                if response1.status_code == 200 and response1.json()["code"] == 200:
                    self.req_code = 0
                    self.check_response = response1
                    self.logger.info(f"请求成功!!!!")
                    self.logger.info(f"请求参数: {params}")
                    self.logger.info(f"请求结果: {response1.text}")
                    break
                else:
                    self.req_code = -1
                    self.logger.error(f"params: {params}, 已经重试{i + 1}")
                    self.logger.error(f"错误结果: {response1.text}")

        except Exception:
            self.req_code = -1

