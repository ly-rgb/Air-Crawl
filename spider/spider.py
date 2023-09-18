import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import List

from config import config
from utils.log import spider_logger
from utils.redis import spider_counter
import time
import requests
from abc import ABCMeta, abstractmethod

from utils.searchparser import parser_from_task, SearchParam


class Spider(object):
    import json
    SUCCESS = 0
    NO_FLIGHTS = 2

    def __init__(self, name, urlGrabber, worker_host, logger=None):
        self.name = name
        self.worker_host = worker_host
        self.grabber = urlGrabber['grabber']
        self.threadNum = urlGrabber['threadNum']
        self.grabSleep = urlGrabber['grabSleep']
        self.airline = self.name.split("_")[-1]
        self.threadPool = ThreadPoolExecutor(max_workers=self.threadNum)
        self.addWorkerThreads = []
        for _ in range(3):
            self.addWorkerThreads.append(Thread(target=self.add_task))
        self.running = False
        self.max_worker_sleep = 0.1
        self.error_sleep = 3
        self.max_cache_worker = 0
        self.logger = logger or spider_logger

    def update_pool(self):
        setattr(self.threadPool, "_max_workers", self.threadNum)

    def update(self, urlGrabber, worker_host):
        self.worker_host = worker_host
        self.grabber = urlGrabber['grabber']
        threadNum = urlGrabber['threadNum']
        if self.threadNum != threadNum:
            self.threadNum = urlGrabber['threadNum']
            self.threadPool.shutdown()
            self.threadPool = ThreadPoolExecutor(max_workers=self.threadNum)
        self.threadNum = urlGrabber['threadNum']
        self.grabSleep = urlGrabber['grabSleep']
        self.update_pool()

    def get_curr_thread_num(self):
        return len(getattr(self.threadPool, "_threads"))

    def get_cache_work_num(self):
        return getattr(self.threadPool, "_work_queue").qsize()

    def add_task(self):
        while self.running:
            try:
                if self.get_cache_work_num() <= 0:
                    self.threadPool.submit(self.call_do)
                else:
                    time.sleep(self.max_worker_sleep)
            except Exception:
                import traceback
                traceback.print_exc()
                self.logger.error(traceback.format_exc())
                time.sleep(self.error_sleep)

    def run(self):
        if self.running:
            self.logger.info(self.name + " is running")
            return
        self.running = True
        for addWorkerThread in self.addWorkerThreads:
            addWorkerThread.start()
        self.logger.info(self.name + " is running")

    def stop(self):
        self.running = False
        for addWorkerThread in self.addWorkerThreads:
            addWorkerThread.join()
        self.logger.info(self.name + " is stop")

    def do(self, params):
        pass

    def call_do(self):
        st = time.time()
        try:
            url = "http://{}/api/GetTask".format(self.worker_host)
            body = {"url": self.name, "version": config.version, "agent": config.agent}
            rep = requests.post(url, json=body, timeout=10)
            self.logger.info(f"get task {rep.text}")
            rep_json = rep.json()
            if rep_json['errorString'] != "OK":
                time.sleep(self.error_sleep)

                # self.logger.info("add worker error. url: {} body: {} result: {}".format(url, body, rep.text))
                return
            self.logger.info("submit: {}".format(rep.text))
            result, status = self.do(rep_json)
            self.push_result(result, status)
            spider_logger.info(f'{self.__str__()} {self.name} {status}')
            spider_counter(self.name, status)
            spider_counter(self.name, "Total")
        except Exception:
            import traceback
            self.logger.error("call_do error: {}".format(traceback.format_exc()))
            time.sleep(self.error_sleep)
        self.logger.info("call do use time: {}".format(time.time() - st))

    def push_result(self, result, status):
        try:
            url = "http://{}/api/AddResult".format(self.worker_host)
            self.logger.info(f'回填的url为{url}')
            rep = requests.post(url, json=result, timeout=10)
            self.logger.info(f'回填的响应状态码为{rep.status_code}')
            rep_json = rep.json()
            if rep_json['errorString'] == "OK":
                self.logger.info(f"push result success: {status} {json.dumps(result)}")
                return True
            else:
                self.logger.error("push result error: {} {}".format(rep.text, json.dumps(result)))
                return False
        except Exception as e:
            import traceback
            self.logger.error(traceback.format_exc())


class SpiderAgent(Spider, metaclass=ABCMeta):

    def do(self, params):
        self.logger.info(f'do: {params}')
        taskKey = params['task']['taskKey']
        sub_data = {"taskKey": taskKey, "url": params['task']['url'], "status": -1, "results": [],
                    'agent': config.agent}
        code = 0
        all_code = []
        for taskItem in params['task']['taskItems']:
            try:
                code, result = self.api_search(parser_from_task(taskItem))
                all_code.append(code)
                self.logger.info(f"taskItem: {taskItem}  code: {code} results: {result}")
                if not result:
                    continue
                result = self.json.dumps(result)
                if code == 0:
                    sub_data['status'] = 0
                    sub_data["results"].append(result)
            except Exception as e:
                self.logger.error(traceback.format_exc())
        no_flight_codes = list(filter(lambda x: x == 2, all_code))
        if len(no_flight_codes) > 0 and len(no_flight_codes) == len(all_code) and not sub_data["results"]:
            self.logger.info(f"no_flights: {params}")
            sub_data["results"].append("no_flights")
            sub_data['status'] = 0
        # if code == 2 and not sub_data["results"]:
        #     self.logger.info(f"no_flights: {params}")
        #     sub_data["results"].append("no_flights")
        return sub_data, code

    @abstractmethod
    def api_search(self, taskItem: SearchParam) -> (int, list):
        pass

    def before_task(self, task):
        pass

    def after_task(self, task, result):
        pass


class SpiderAgentPython310(SpiderAgent, metaclass=ABCMeta):

    def __init__(self, name, urlGrabber, worker_host, logger=None):
        self.name = name
        self.worker_host = worker_host
        self.grabber = urlGrabber['grabber']
        self.threadNum = urlGrabber['threadNum']
        self.grabSleep = urlGrabber['grabSleep']
        self.airline = self.name.split("_")[-1]
        self.threadPool: List[threading.Thread] = list()
        self.addWorkerThreads = []
        for _ in range(self.threadNum):
            self.threadPool.append(Thread(target=self.add_task))
        self.running = False
        self.max_worker_sleep = 0.1
        self.error_sleep = 1
        self.max_cache_worker = 0
        self.logger = logger or spider_logger

    def add_task(self):
        while self.running:
            self.logger.info(self.name + "add_task start")
            try:
                self.call_do()
            except Exception:
                import traceback
                traceback.print_exc()
                self.logger.error(traceback.format_exc())
                time.sleep(self.error_sleep)

    def run(self):
        if self.running:
            self.logger.info(self.name + " is running")
            return
        self.running = True
        for thread in self.threadPool:
            thread.start()
        self.logger.info(self.name + " is running")


class SpiderAgentV2(SpiderAgent, metaclass=ABCMeta):

    def __init__(self, name, urlGrabber, worker_host, logger=None):
        # super().__init__(name, urlGrabber, worker_host, logger)
        self.name = name
        self.worker_host = worker_host
        self.grabber = urlGrabber['grabber']
        self.threadNum = urlGrabber['threadNum']
        self.grabSleep = urlGrabber['grabSleep']
        self.airline = self.name.split("_")[-1]
        self.threadPool: List[threading.Thread] = list()
        self.addWorkerThreads = []
        for _ in range(self.threadNum):
            self.threadPool.append(Thread(target=self.add_task))
        self.running = False
        self.max_worker_sleep = 0.1
        self.error_sleep = 1
        self.max_cache_worker = 0
        self.logger = logger or spider_logger

    def add_task(self):
        self.logger.info(self.name + "add_task start")
        while self.running:
            try:
                self.call_do()
            except Exception:
                import traceback
                traceback.print_exc()
                self.logger.error(traceback.format_exc())
                time.sleep(self.error_sleep)

    def run(self):
        if self.running:
            self.logger.info(self.name + " is running")
            return
        self.running = True
        for thread in self.threadPool:
            thread.start()
        self.logger.info(self.name + " is running")

