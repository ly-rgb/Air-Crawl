import json

from typing import Dict
from config import config
from robot import NotHoldPayRobot
from spider.spider import SpiderAgent
from utils.searchparser import SearchParam
from robot.business.robot import BusinessRobot
from airline.AVY.service import api_search, no_hold_pay, refund_tax, \
    judge_type, refund_run_describe
from utils.log import spider_VY_logger, booking_VY_logger, refund_VY_logger, \
    refund_check_VY_logger, refund_VY_Full_logger


class SpiderVY(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search()

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_VY_logger


class PayRobotVY(NotHoldPayRobot):
    def __init__(self, max_workers=1, proxies_type=None):
        self.proxies_type = proxies_type
        super().__init__("VY_PAY", config.agent, "AVY", max_workers=max_workers)
        self.logger = booking_VY_logger

    def do(self, task):
        self.logger.info(f"task: {json.dumps(task)}")
        code, result = no_hold_pay()
        self.logger.info(f"task: {json.dumps(task)} code: {code} {result}")
        return result


class RefundTaxRobotVY(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__('VY_refund', refund_VY_logger, 'VY',
                         'WITHHOLDING:REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task)
        self.logger.info(f"task: {json.dumps(task)} result {result}")
        return result


class RefundCheckRobotVY(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__('VY_refund', refund_check_VY_logger, 'AVY',
                         'WITHHOLDING:REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task)
        self.logger.info(f"task: {json.dumps(task)} result {result}")
        return result


class RefundTaxRobotVYFull(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None, operator="refund_ticket"):
        super().__init__('VY_refund_full', refund_VY_Full_logger, 'VY',
                         'REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type
        self._operator = operator

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task)
        self.logger.info(f"task: {json.dumps(task)} result {result}")
        return result