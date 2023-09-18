# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AFDCheckService.py
@effect: "FD质检业务类"
@Date: 2022/10/15 17:17
"""
from auto_check.AFD.AFDCheckApi import AFDCheckWeb


class AFDCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, account: str, password: str, pnr: str):
        result = None
        app = AFDCheckWeb(proxies_type=7)

        try:
            app.login("THTHYUTOP", "2020Sh_yy")
            app.agent_user()
            app.booking1("THTHYUTOP")
            app.booking2("FZCZNV")

            if app.error_code == "1":
                result = app.booking1_response.json()
            elif app.error_code == "0":
                result = {
                    "code": app.error_code,
                    "isFind": "false",
                    "isBusiness": "false",
                    "Leave": {
                        "taskType": "",
                        "origin": "",
                        "destination": "",
                        "targetPassengers": "",
                        "departDate": "",
                        "arriveDate": "",
                        "flightNumber": "",
                        "baggageMessageDOs": "",
                        "freeBaggageWeight": "0"
                    },
                    "payStatus": "false",
                    "liftStatus": ""
                }
            elif app.error_code == "-3":
                result = {"result": "ERROR", "code": app.error_code}
            else:
                result = {"result": "ERROR", "code": app.error_code}

        except Exception:
            result = {"result": "ERROR", "code": app.error_code}

        return result