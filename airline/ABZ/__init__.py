from airline.ABZ.service import api_search
from spider.spider import SpiderAgent
from utils.log import spider_BZ_logger
from utils.searchparser import SearchParam


class SpiderBZ(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_BZ_logger