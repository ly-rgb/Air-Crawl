# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AG4CheckService.py
@effect: "G4质检Service"
@Date: 2022/9/29 16:24
"""

from auto_check.AG4.AG4CheckApi import AG4CheckWeb
from utils.log import check_G4_logger
import traceback
import json
from datetime import datetime


class AG4CheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name: str, first_name: str, pnr: str):
        result = None
        app = AG4CheckWeb(proxies_type=7)

        try:
            app.check(last_name=last_name, first_name=first_name, pnr=pnr)
            if app.error_code == "1":
                result = app.check_response.json()
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
    def show_check_part_info(cls, last_name: str, first_name: str, pnr: str):
        result = None
        app = AG4CheckWeb(proxies_type=7)

        try:
            app.check(last_name=last_name, first_name=first_name, pnr=pnr)
            if app.error_code == "1":
                result = cls.__data_extract(app.check_response.json())
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
    def __data_extract(cls, all_info: dict):
        result = None

        leave_passengers_list = []
        leave_bags_list = []

        back_passengers_list = []
        back_bags_list = []

        try:

            # 提取去程航班信息
            leave_origin = all_info["legs"]["departing"]["origin"]
            leave_destination = all_info["legs"]["departing"]["destination"]
            leave_depart_date = datetime.strptime(all_info["legs"]["departing"]["departs"].split(".")[0],
                                                  "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            leave_arrive_date = datetime.strptime(all_info["legs"]["departing"]["arrives"].split(".")[0],
                                                  "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            leave_flight_number = all_info["legs"]["departing"]["airline_code"] + all_info["legs"]["departing"]["flight_no"]

            check_G4_logger.info(f"去程航班信息: "
                                 f"航班号: {leave_flight_number}"
                                 f"出发地: {leave_origin}"
                                 f"目的地: {leave_destination}"
                                 f"出发时间: {leave_depart_date}"
                                 f"到达时间: {leave_arrive_date}")

            # 提取乘客信息
            for passenger in all_info["travellers"]:
                passenger_id = str(passenger["id"])
                passenger_name = (passenger["lastname"] + "/" + passenger["firstname"]).replace(" ", "")
                passenger_sex = "M" if passenger["gender"] == "male" else "F"
                passenger_birth = passenger["clean_dob"]

                # 判断是否有返程, departing: 去程，
                # 可能会有返程，，请注意 **********************************************************
                passenger_keys = list(passenger.keys())
                # 去程乘客信息
                leave_passengers_list.append({
                    "passengerId": passenger_id,
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": passenger_birth,
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
                check_G4_logger.info(f"去程乘客信息: {leave_passengers_list}")

                # 去程行李信息
                leave_bags_list.append({
                    "passengerName": passenger_name,
                    "depCity": leave_origin,
                    "arrCity": leave_destination,
                    "baggageWeight": cls.baggage_weight_change(passenger["departing"]["carry_on_bag"])
                })
                check_G4_logger.info(f"去程行李信息: {leave_bags_list}")

            result = {
                "code": "1",
                "isFind": "true",
                "isBusiness": "false",
                "Leave": {
                    "taskType": "SHUA_PIAO",
                    "origin": leave_origin,
                    "destination": leave_destination,
                    "targetPassengers": leave_passengers_list,
                    "departDate": leave_depart_date,
                    "arriveDate": leave_arrive_date,
                    "flightNumber": leave_flight_number,
                    "baggageMessageDOs": leave_bags_list,
                    "freeBaggageWeight": "0"
                },
                "payStatus": "true",
                "liftStatus": "改天写，呜呜"
            }

        except Exception:
            result = {"result": "ERROR", "code": "-2"}
            check_G4_logger.error(f"数据解析失败")
            check_G4_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def baggage_weight_change(cls, carrier_on_bag):
        weight = 0

        if isinstance(carrier_on_bag, dict):
            weight = 0
        else:
            weight = sum(carrier_on_bag) if len(carrier_on_bag) != 0 else 0

        return str(weight)


