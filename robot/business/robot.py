import time
import traceback
from abc import ABC
from logging import Logger
from typing import Dict, Optional

import requests

from robot import BaseRobot


class BusinessRobot(BaseRobot, ABC):

    def __init__(self, name: str, logger: Logger, carrier: str, _type: str, max_workers=1, operator="withholding_refund_ticket"):
        super().__init__(name, logger, max_workers)
        self._type = _type
        self._operator = operator
        self._carrier = carrier

    def get_task(self, *args, **kwargs) -> Optional[Dict]:
        try:
            #url = 'http://42.96.130.155:8086/task/get'
            url = 'http://82.156.172.154:8086/task/get'
            json = {
                "carrier": self._carrier,
                "businessType": {
                    "type": self._type,
                    "operator": self._operator
                }
            }
            response = requests.post(url, json=json, timeout=60)
            if response.status_code != 200:
                raise Exception(f'[获取任务异常][{response.text}]')
            response_json = response.json()
            if response_json['code'] == 200:
                return response_json['result']
            elif response_json['code'] == 201:
                return None
            else:
                raise Exception(f'[获取任务异常][{response.text}]')
        except Exception:
            self.logger.error(traceback.format_exc())
            return None

    def push_result(self, result: Dict):
        for _ in range(6):
            try:
                #url = 'http://42.96.130.155:8086/task/fill'
                url = 'http://82.156.172.154:8086/task/fill'
                json = result
                response = requests.post(url, json=json, timeout=60)
                self.logger.info(f'[回填][{json}][{response.text}]')
                if response.json()['code'] != 200:
                    self.logger.error(f'[回填异常][{json}][{response.text}]')
                return
            except Exception:
                self.logger.error(f'[回填失败][{result}][{traceback.format_exc()}]')
                time.sleep(10)
                continue


