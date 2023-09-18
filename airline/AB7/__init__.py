from spider.spider import SpiderAgent
from utils.log import spider_B7_logger
from utils.searchparser import SearchParam
from airline.AB7.service import api_search


class SpiderB7(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_B7_logger
