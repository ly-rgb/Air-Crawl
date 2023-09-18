import json
from logging import Logger
from typing import Dict

from airline.A6J.service import api_search, no_hold_pay, refund_tax
from config import config
from robot import NotHoldPayRobot
from robot.business.robot import BusinessRobot
from spider.spider import SpiderAgent
from utils.log import spider_6J_logger, booking_6J_logger, refund_6J_logger, refund_check_6J_logger
from utils.searchparser import SearchParam


class Spider6J(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_6J_logger


class PayRobot6J(NotHoldPayRobot):
    def __init__(self, max_workers=1, proxies_type=None):
        self.proxies_type = proxies_type
        super().__init__("6J_PAY", config.agent, "6J", max_workers=max_workers)
        self.logger = booking_6J_logger

    def do(self, task):
        self.logger.info(f"task: {json.dumps(task)}")
        code, result = no_hold_pay(task, proxies_type=self.proxies_type)
        self.logger.info(f"task: {json.dumps(task)} code: {code} {result}")
        return result


class RefundTaxRobot6J(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__('6J_refund', refund_6J_logger, '6J', 'WITHHOLDING:REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task, proxies_type=self.proxies_type)
        self.logger.info(f"task: {json.dumps(task)} result {result}")
        return result


class RefundCheckRobot6J(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__('6J_refund', refund_check_6J_logger, '6J', 'WITHHOLDING:REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task, proxies_type=self.proxies_type)
        self.logger.info(f"task: {json.dumps(task)} result {result}")
        return result
