# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: __init__.py.py
@effect: "请填写用途"
@Date: 2022/11/29 14:33
"""
import json
from config import config
from robot import NotHoldPayRobot
from spider import SpiderAgent
from utils.log import spider_Z9_logger, booking_Z9_logger
from utils.searchparser import SearchParam
from airline.AZ9.service import api_search, no_hold_pay, add_on
from spider.spider import SpiderAgentV2


class SpiderZ9(SpiderAgentV2):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_Z9_logger


class PayRobotZ9(NotHoldPayRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__("Z9_PAY", config.agent, "Z9", max_workers=max_workers)
        self.proxies_type = proxies_type
        self.logger = booking_Z9_logger

    def do(self, task: dict) -> dict:
        self.logger.info(f"task: {json.dumps(task)}")
        code, result = no_hold_pay(task, proxies_type=self.proxies_type)
        self.logger.info(f"task: {task} code: {code} result: {result}")
        return result