import json

from airline.ADD.service import api_search,no_hold_pay
from spider.spider import SpiderAgent
from utils.log import spider_DD_logger,booking_DD_logger
from utils.searchparser import SearchParam
from robot import NotHoldPayRobot
from config import config

class SpiderDD(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_DD_logger


class PayRobotDD(NotHoldPayRobot):
    def __init__(self, max_workers=1, proxies_type=None):
        self.proxies_type = proxies_type
        super().__init__("DD_PAY", config.agent, "DD", max_workers=max_workers)
        self.logger = booking_DD_logger

    def do(self, task):
        self.logger.info(f"task: {json.dumps(task)}")
        code, result = no_hold_pay(task, proxies_type=self.proxies_type)
        self.logger.info(f"task: {json.dumps(task)} code: {code} {result}")
        return result
