import json
import threading
import traceback
from abc import ABCMeta, abstractmethod, ABC
from logging import Logger
from typing import Optional, Tuple, Dict, List

import requests
import time
from concurrent.futures import ThreadPoolExecutor

from native.api import get_hold_task, get_pay_task, submit_hold, submit_pay, get_no_hold_pay_task, get_refund_task, \
    send_refund_task
from robot.model import HoldTask, HoldResult, RefundTaskV2
from utils.log import robot_logger, pay_logger, spider_bag_log
from hashlib import md5

from utils.redis import redis_53


class Runnable:

    def __init__(self, thread=None) -> None:
        self.thread = thread

    def run(self, *args, **kwargs) -> None:
        self.thread.start()


class BaseRobot(metaclass=ABCMeta):

    def __init__(self, name, logger, max_workers=1):
        self.logger: Logger = logger
        self.running = False
        self.name = name
        self.error_sleep = 10
        self.max_workers = max_workers
        self.pull_task_threads = [threading.Thread(target=self.auto_pull_task) for _ in range(self.max_workers)]

    def get_curr_thread_num(self):
        return len(self.pull_task_threads)

    @abstractmethod
    def get_task(self, *args, **kwargs) -> object:
        pass

    @abstractmethod
    def push_result(self, result):
        pass

    def __do(self, task):
        try:
            if task:
                result = self.do(task)
                self.push_result(result)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(traceback.format_exc())

    @abstractmethod
    def do(self, task) -> object:
        pass

    def testing(self):
        task = self.get_task()
        if not task:
            self.logger.info('[没有任务]')
        else:
            self.__do(task)

    def auto_pull_task(self):
        while self.running:
            try:
                task = self.get_task()
                if not task:
                    time.sleep(self.error_sleep)
                else:
                    self.__do(task)
            except Exception:
                import traceback
                time.sleep(self.error_sleep)
                self.logger.error(traceback.format_exc())

    def _pull_task_start(self):
        for th in self.pull_task_threads:
            th.start()

    def run(self):
        if self.running:
            self.logger.info(self.name + " is running")
            return
        self.running = True
        self._pull_task_start()
        self.logger.info(self.name + " is running")


class Robot(object):
    def __init__(self, name, agent, airline, max_workers=1, logger=None):
        self.logger = logger or robot_logger
        self.threadPool = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.name = name
        self.agent = agent
        self.airline = airline
        self.error_sleep = 10
        self.max_workers = max_workers
        self.addTaskThread = threading.Thread(target=self.add_task)

    def get_curr_thread_num(self):
        return len(getattr(self.threadPool, "_threads"))

    def get_cache_work_num(self):
        return getattr(self.threadPool, "_work_queue").qsize()

    def add_task(self):
        while self.running:
            try:
                print('add_task', self.get_cache_work_num())
                if self.get_cache_work_num() <= 0:
                    task = self.get_task()
                    if not task:
                        print("no task")
                        time.sleep(10)
                    else:
                        self.logger.info(f"submit task:{json.dumps(task)}")
                        self.push_result(task)
                    task = self.get_task(taskType="shuapiao")
                    if not task:
                        time.sleep(10)
                    else:
                        self.logger.info(f"submit task:{json.dumps(task)}")
                        self.push_result(task)
                else:
                    time.sleep(1)
            except Exception:
                import traceback
                time.sleep(10)
                self.logger.error(traceback.format_exc())

    def get_task(self, taskType="paodan"):
        try:
            return get_hold_task(self.airline, taskType)
        except Exception as e:
            self.logger.error(f'获取任务失败 {traceback.format_exc()}')
        return None

    def run(self):
        if self.running:
            self.logger.info(self.name + " is running")
            return
        # if getattr(self.threadPool, "_shutdown", False):
        #     self.threadPool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.running = True
        # self.addTaskThread.start()
        self.logger.info(self.name + " is running ")
        # self.addTaskThread.join()
        ths = []
        for _ in range(self.max_workers):
            th = threading.Thread(target=self.add_task)
            ths.append(th)
            th.start()

    def stop(self):
        self.running = False
        self.addTaskThread.join()
        self.threadPool.shutdown()
        self.logger.info(self.name + " is stop")

    def do(self, task: dict) -> dict:
        pass

    def push_result(self, task):
        try:
            task_str = json.dumps(task)
            task_md5 = md5(task_str.encode("utf-8")).hexdigest()
            self.logger.info(f"task_start: {task_md5}, task: {task_str}")
            result = self.do(task)
            self.logger.info(f"task_over: {task_md5} result {json.dumps(result)}")
            rep = submit_hold(result)
            self.logger.info(f"task_result_submit: {task_md5} submit hold result: {rep}")
        except Exception as e:
            import traceback
            self.logger.error(traceback.format_exc())


class HoldRobotAgent(Robot):

    def get_task(self, taskType="paodan") -> HoldTask or None:
        task = super().get_task(taskType=taskType)
        if not task:
            return None
        return HoldTask.from_dict(task, infer_missing=True)

    def do(self, task: HoldTask) -> HoldResult:
        pass

    def push_result(self, task: HoldTask):
        try:
            task_str = task.to_json()
            task_md5 = md5(task_str.encode("utf-8")).hexdigest()
            self.logger.info(f"task_md5: {task_md5}, task: {task_str}")
            result = self.do(task)
            self.logger.info(f"task: {task_md5} result {result.to_json()}")
            if task.taskType == "PAO_DAN":
                rep = submit_hold(result.to_dict())
            else:
                rep = submit_hold(result.to_dict())
            self.logger.info(f"task: {task_md5} submit hold result: {rep}")
        except Exception as e:
            import traceback
            self.logger.error(traceback.format_exc())

    def add_task(self):
        while self.running:
            try:
                if self.get_cache_work_num() <= 0:
                    task = self.get_task()
                    if not task:
                        time.sleep(self.error_sleep)
                    else:
                        self.logger.info(f"submit task:{task.to_json()}")
                        self.threadPool.submit(self.push_result, task)
                    task = self.get_task(taskType="shuapiao")
                    if not task:
                        time.sleep(self.error_sleep)
                    else:
                        self.logger.info(f"submit task:{task.to_json()}")
                        self.threadPool.submit(self.push_result, task)
                else:
                    time.sleep(1)
            except:
                import traceback
                time.sleep(self.error_sleep)
                self.logger.error(traceback.format_exc())


class PayRobot(Robot):
    def __init__(self, name, agent, airline, max_workers=1, logger=pay_logger):
        super().__init__(name, agent, airline, max_workers)
        self.logger = logger

    def get_task(self, taskType=""):
        try:
            ret = get_pay_task(self.airline)
            # self.logger.info(f"get_task: {ret}")
            if ret and ret != "":
                return json.loads(ret)
        except Exception as e:
            self.logger.error(f'获取任务失败 {e}')
        return None

    def submit_pay(self, task_md5, result):
        count = 0
        while True:
            try:
                rep = submit_pay(result)
                return rep
            except Exception as e:
                if count > 30:
                    raise Exception(f'回填失败 {str(e)}')
                self.logger.info(f"task_md5: {task_md5} 回填失败 等待10s重试")
                count += 1
                time.sleep(10)

    def push_result(self, task):
        try:
            self.logger.info("push_result start")
            task_str = json.dumps(task)
            task_md5 = md5(task_str.encode("utf-8")).hexdigest()
            self.logger.info(f"task_md5: {task_md5}, task: {task_str}")
            result = self.do(task)
            self.logger.info(f"task: {task_md5} result {json.dumps(result, ensure_ascii=False)}")
            rep = self.submit_pay(task_md5, result)
            self.logger.info(f"task: {task_md5} submit hold result: {rep}")
        except Exception as e:
            import traceback
            self.logger.error(traceback.format_exc())


class NotHoldPayRobot(PayRobot):

    def get_task(self, taskType=""):
        try:
            ret = get_no_hold_pay_task(self.airline)

            if ret and ret != '':
                return json.loads(ret)
        except Exception as e:
            self.logger.error(f'获取任务失败 {e}')
        return None


class BaseBagRobot(BaseRobot, ABC):

    def __init__(self, name, task_pool_name, result_cache_name=None, max_workers=1, proxies_type=None):
        super().__init__(f"{name}_bag_robot", spider_bag_log, max_workers)
        self.result_cache_name = result_cache_name or f"{self.name}_result"
        self.task_pool_name = task_pool_name
        self.proxies_type = proxies_type

    def get_task(self, *args, **kwargs) -> Optional[HoldTask]:
        task = redis_53.spop(self.task_pool_name)
        if task:
            depAirport, arrAirport, depDate, flightNo = task.split(',')
            return HoldTask.from_bag_task(depAirport, arrAirport, depDate, flightNo)

    def push_result(self, result: dict):
        redis_53.sadd(self.result_cache_name, json.dumps(result))


class NoShowRobot(BaseRobot, ABC):
    def __init__(self, name, task_pool_name, result_cache_name=None, max_workers=1, proxies_type=None):
        super().__init__(f"{name}_no_show_robot", spider_bag_log, max_workers)
        self.result_cache_name = result_cache_name or f"{self.name}_result"
        self.task_pool_name = task_pool_name
        self.proxies_type = proxies_type

    def get_task(self, *args, **kwargs) -> Optional[Tuple[str, str]]:
        task = redis_53.spop(self.task_pool_name)
        if task:
            pnr, ln = task.split(',', 1)
            ln = ln.split('/', 1)[0]
            return pnr, ln

    def push_result(self, result: dict):
        redis_53.sadd(self.result_cache_name, json.dumps(result))


class BookingService(metaclass=ABCMeta):

    def __init__(self, task: dict, logger: Logger):
        self.process = {
            'outTicket': self.outTicket,
            'refundPnr': self.refundPnr
        }
        self.logger = logger
        self.task: Dict = task
        self.holdTask: HoldTask = HoldTask.from_pay_task_v2(self.task)
        self.repaymentProcess: List = self.task.get('repaymentProcess', list())
        self.needRefundPnrs: List[RefundTaskV2] = RefundTaskV2.from_pay_task(self.task)

    def _call_proces(self, proces):
        try:
            call_do = self.process.get(proces['type'], None)
        except Exception:
            self.logger.error(f'[{self.holdTask.orderCode}][{proces}][{traceback.format_exc()}]')

    def do(self):
        if self.repaymentProcess:
            for p in self.repaymentProcess:
                self._call_proces(p)
        else:
            self.outTicket()

    @abstractmethod
    def outTicket(self) -> Tuple[int, Dict]:
        pass

    @abstractmethod
    def refundPnr(self) -> Tuple[int, Dict]:
        pass


class RefundBot(BaseRobot, ABC):
    def get_task(self, *args, **kwargs) -> Optional[RefundTaskV2]:
        task = get_refund_task(self.name)
        if task:
            self.logger.info(f'[获取任务成功][{task}]')
            return RefundTaskV2.from_dict(task)
        else:
            return None

    def push_result(self, result: RefundTaskV2):
        self.logger.info(f'[{result.otaId}][开始回填任务]')
        if send_refund_task(result.to_dict()):
            self.logger.info(f'[{result.otaId}][回填任务成功]')
        else:
            self.logger.info(f'[{result.otaId}][回填任务失败]')

    @abstractmethod
    def do(self, task: RefundTaskV2) -> RefundTaskV2:
        pass

    def __init__(self, name, logger, max_workers=1, proxies_type=None):
        super().__init__(name, logger, max_workers)
        self.proxies_type = proxies_type