from airline.ATL.service import api_search
from spider import SpiderAgent
from utils.searchparser import SearchParam
from utils.log import spider_TL_logger


class SpiderTL(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_TL_logger