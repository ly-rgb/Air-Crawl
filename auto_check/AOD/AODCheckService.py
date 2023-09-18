# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AODCheckService.py
@effect: "OD质检业务层"
@Date: 2022/11/8 15:02
"""

from utils.log import check_OD_logger
import traceback
from auto_check.AOD.AODCheckApi import AODCheckWeb
from datetime import datetime


class AODCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, pnr):
        result = None

        app = AODCheckWeb(proxies_type=0)

        try:
            app.api_check(pnr=pnr)
            if app.error_code == "1":
                result = app.api_check_response.json()
                check_OD_logger.info(f"请求结果: {result}")
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
            else:
                result = {"result": "ERROR", "code": app.error_code}

        except Exception:
            result = {"result": "ERROR", "code": app.error_code}

        return result

    @classmethod
    def show_check_part_info(cls, pnr):
        result = None

        app = AODCheckWeb(proxies_type=0)

        try:
            app.api_check(pnr=pnr)
            if app.error_code == "1":
                result = AODCheckService.__data_extract(app.api_check_response.json())
                check_OD_logger.info(f"请求结果: {result}")
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
            else:
                result = {"result": "ERROR", "code": app.error_code}

        except Exception:
            result = {"result": "ERROR", "code": app.error_code}

        return result

    @classmethod
    def __data_extract(cls, all_info):

        result = None
        # 定义出发地等列表，当航班为中转的时候方便拼接
        origin_list = []
        destination_list = []
        depart_date_list = []
        arrive_date_list = []
        flight_number_list = []

        # passenger_name_list的作用是帮助添加行李中乘客的名字
        passenger_name_list = []

        # lift_status noshow
        lift_status_list = []

        leave_passengers_list = []
        leave_bags_list = []

        try:

            # 提取航班信息
            origin = all_info["dep"]
            destination = all_info["arr"]
            depart_date = all_info["departDate"]
            arrive_date = all_info["arrDate"]
            flight_number = all_info["flightNumber"]

            origin_list.append(origin)
            destination_list.append(destination)
            depart_date_list.append(depart_date)
            arrive_date_list.append(arrive_date)
            flight_number_list.append(flight_number)

            check_OD_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 提取乘客信息
            for passenger in all_info["adults"]:
                passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
                passenger_sex = "M" if passenger["sex"] == "1" else "F"

                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": "",
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": "",
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            for passenger in all_info["children"]:
                passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
                passenger_sex = "C"

                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": "",
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": "",
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_OD_logger.info(f"乘客信息: {leave_passengers_list}")

            # 行李信息
            for name in passenger_name_list:
                baggageMessageDOs = {
                    "passengerName": name,
                    "depCity": origin_list[0],
                    "arrCity": destination_list[-1],
                    "baggageWeight": str(0)
                }
                leave_bags_list.append(baggageMessageDOs)
            check_OD_logger.info(f"行李信息: {leave_bags_list}")

            # PNR 状态
            pnr_status = "true" if all_info["status"] == "confirmed" else "false"

            # noshow 暂时不填
            check_OD_logger.info("noshow信息暂时不写")

            result = {
                "code": "1",
                "isFind": "true",
                "isBusiness": "false",
                "Leave": {
                    "taskType": "SHUA_PIAO",
                    "origin": "|".join(origin_list),
                    "destination": "|".join(destination_list),
                    "targetPassengers": leave_passengers_list,
                    "departDate": "|".join(depart_date_list),
                    "arriveDate": "|".join(arrive_date_list),
                    "flightNumber": "|".join(flight_number_list),
                    "baggageMessageDOs": leave_bags_list,
                    "freeBaggageWeight": "0"
                },
                "payStatus": pnr_status,
                "liftStatus": lift_status_list
            }

        except Exception:
            result = {"result": "ERROR", "code": "-2"}
            check_OD_logger.error("解析数据失败")
            check_OD_logger.error(f"{traceback.print_exc()}")

        return result

