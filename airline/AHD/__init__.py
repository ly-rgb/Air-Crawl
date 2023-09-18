from airline.AHD.service import api_search
from spider.spider import SpiderAgent
from utils.log import spider_HD_logger
from utils.searchparser import SearchParam


class SpiderHD(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_HD_logger