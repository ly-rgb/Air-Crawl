from spider.spider import SpiderAgent
from airline.AG8.AG8App import AG8App
from airline.AG8.service import add_on
from utils.log import spider_G8_logger
from airline.AG8.AG8Web import api_search
from utils.searchparser import SearchParam


class SpiderG8(SpiderAgent):

    def api_search(self, taskItem: SearchParam) -> (int, list):
        return api_search(taskItem)

    def __init__(self, name, urlGrabber, worker_host):
        super().__init__(name, urlGrabber, worker_host)
        self.logger = spider_G8_logger
