# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AG4CheckApi.py
@effect: "G4质检Api"
@Date: 2022/9/29 15:14
"""

from airline.base import AirAgentV3Development
from utils.log import check_G4_logger
import traceback
import time


class AG4CheckWeb(AirAgentV3Development):

    def __init__(self, retry_count=3, timeout=60, proxies_type=0):
        super().__init__(retry_count=retry_count, timeout=timeout, proxies_type=proxies_type)

        self.check_response = None
        self.error_code = "-1"

        print("G4的漏洞太多，呜呜呜！！！，只要PNR正确，就不校验姓名，不知道咋想的，最垃圾的航司")

    def check(self, last_name: str, first_name: str,  pnr: str):

        url = "https://www.allegiantair.com/g4search/api/modify/" + pnr
        timestamp = int(time.time() * 1000)

        headers = {
            'AJSUI-Version': '311.0.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'G4-Client-Id': 'modify',
            'Referer': 'https://www.allegiantair.com/my-trips?confCode=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        params = {
            'sessionID': '1FvnkXMj-31DmUKthtTb7jX3BO1ZovMer9JkDBiwx4c',
            'transactionIdentifier': 'undefined',
            'abTest': 'A'
        }

        data = {
            'order': self.json.dumps(
                {'credentials': {'firstName': first_name,
                                 'lastName': last_name,
                                 'confCode': pnr,
                                 'type': 'confirmation'},
                 'meta': {
                     'sessionID': '1FvnkXMj-31DmUKthtTb7jX3BO1ZovMer9JkDBiwx4c',
                 },
                 'travellers': None,
                 'legs': None,
                 'vouchers': [],
                 'hotel': None,
                 'vehicle': None,
                 'promos': [],
                 'cache_endpoint': '/data/31',
                 'vehicle_search': None,
                 'shuttles': [],
                 'completion_history': [],
                 'upLift': {'initialized': False,
                            'iFramePresent': False,
                            'enabled': False,
                            'outOfFilter': False,
                            'selected': False,
                            'approved': False,
                            'rejected': False,
                            'paymentReady': False,
                            'paymentLastUpdated': 0,
                            'optionsLastUpdated': timestamp,
                            'options': {}},
                 'deal_filter': '',
                 'saveTriggerEvent': 'orderDataRequested',
                 'paymentDetails': {'tripflex': None,
                                    'terms_accepted': False,
                                    'instant_credit': False,
                                    'card_no': None,
                                    'ccv': None,
                                    'country': 'US',
                                    'opt_in_marketing': True,
                                    'payment_method': 'CC',
                                    'appliedPoints': False,
                                    'storeCard': False,
                                    'encryptionType': 'PIE',
                                    'dcd': False},
                 'shuttle': []
                 })
        }

        try:
            response = self.post(url=url, headers=headers, params=params, data=data)
            result = response.json()
            keys = list(result.keys())
            if "error" in keys:
                self.error_code = "0"
                if result["error"][0]["reswebCode"] == "2202":
                    check_G4_logger.error(f"没有找到PNR, ERROR: {result}")

                elif result["error"][0]["reswebCode"] in "2307,1905":
                    check_G4_logger.error(f"名字错误， ERROR: {result}")
                else:
                    check_G4_logger.error(f"其他错误, ERROR: {result}")
            else:
                is_cancelled = result["legs"]["departing"]["cancelled"]
                if is_cancelled:
                    self.error_code = "0"
                    check_G4_logger.error(f"PNR取消")
                else:
                    self.error_code = "1"
                    self.check_response = response
                    check_G4_logger.info("请求成功！！！")
                    check_G4_logger.info(f"params: {params}, data: {data}")
                    check_G4_logger.info(f"请求结果: {result}")

        except Exception:
            self.error_code = "-1"
            check_G4_logger.error(f"请求失败，params: {params}"
                                  f"data: {data}")
            check_G4_logger.error(f"{traceback.print_exc()}")

