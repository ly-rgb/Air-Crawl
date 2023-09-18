import json

from typing import Dict
from config import config
from robot import NotHoldPayRobot
from spider.spider import SpiderAgent
from utils.searchparser import SearchParam
from robot.business.robot import BusinessRobot
from airline.A6E.service import api_search, no_hold_pay, refund_tax
from utils.log import spider_6E_logger, booking_6E_logger, refund_6E_logger, \
    refund_check_6E_logger


class Spider6E(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search()

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_6E_logger


class PayRobot6E(NotHoldPayRobot):
    def __init__(self, max_workers=1, proxies_type=None):
        self.proxies_type = proxies_type
        super().__init__("6E_PAY", config.agent, "A6E", max_workers=max_workers)
        self.logger = booking_6E_logger

    def do(self, task):
        self.logger.info(f"task: {json.dumps(task)}")
        code, result = no_hold_pay()
        self.logger.info(f"task: {json.dumps(task)} code: {code} {result}")
        return result


class RefundTaxRobot6E(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__('6E_refund', refund_6E_logger, '6E',
                         'WITHHOLDING:REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task)
        self.logger.info(f"result: {result}")
        return result


class RefundCheckRobot6E(BusinessRobot):

    def __init__(self, max_workers=1, proxies_type=None):
        super().__init__('6E_refund', refund_check_6E_logger, 'A6E',
                         'WITHHOLDING:REFUND:TICKET', max_workers=max_workers)
        self.proxies_type = proxies_type

    def do(self, task: Dict) -> Dict:
        self.logger.info(f"task: {json.dumps(task)}")
        result = refund_tax(task)
        self.logger.info(f"task: {json.dumps(task)} result {result}")
        return result
