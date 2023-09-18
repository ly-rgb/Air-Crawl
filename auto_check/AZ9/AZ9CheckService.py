# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AZ9CheckService.py
@effect: "请填写用途"
@Date: 2022/12/30 12:01
"""
from auto_check.AZ9.AZ9CheckApi import AZ9CheckWeb
from utils.log import check_Z9_logger
import traceback
from datetime import datetime


class AZ9CheckService(object):
    empty_result = {
        "code": "0",
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

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr):
        result = None

        app = AZ9CheckWeb()
        try:
            app.login(pnr=pnr)
            try:
                app.login2()
                app.check(last_name=last_name, pnr=pnr)
                if app.error_code == "1":
                    result = {"result": app.check_response.json(), "code": app.error_code}
                elif app.error_code == "0":
                    result = cls.empty_result
                else:
                    result = {"result": "ERROR", "code": app.error_code}
            except Exception:
                result = {"result": "ERROR", "code": app.error_code}
        except Exception:
            result = cls.empty_result

        return result

    @classmethod
    def show_check_part_info(cls, last_name, pnr):
        result = None

        app = AZ9CheckWeb()
        try:
            app.login(pnr=pnr)
            try:
                app.login2()
                app.check(last_name=last_name, pnr=pnr)
                if app.error_code == "1":
                    result = cls.__data_extract(all_info=app.check_response.json())
                elif app.error_code == "0":
                    result = cls.empty_result
                elif result is None:
                    result = {"result": "ERROR", "code": "2"}
            except Exception:
                check_Z9_logger.error(f"{traceback.print_exc()}")
                result = {"result": "ERROR", "code": app.error_code}
        except Exception:
            result = cls.empty_result

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

        for passenger in all_info["passengers"]:
            # 提取乘客信息
            passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
            passenger_sex = "M" if passenger["gender"] == "M" else "F"
            passenger_birthday = datetime.strptime(passenger["dateOfBirth"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

            # 提取行李信息
            dep = passenger["flights"][0]["from"]["code"]
            arr = passenger["flights"][0]["to"]["code"]
            services = passenger["flights"][0]["services"]
            baggage_weight = cls.__baggage_change(services)

            leave_bags_list.append({
                "passengerName": passenger_name,
                "depCity": dep,
                "arrCity": arr,
                "baggageWeight": str(baggage_weight)
            })

            leave_passengers_list.append({
                "passengerId": "",
                "name": passenger_name,
                "sex": passenger_sex,
                "birthday": passenger_birthday,
                "nationality": "",
                "cardIssuePlace": "",
                "cardExpired": "",
                "certificateInformation": ""
            })
        check_Z9_logger.info(f"乘客信息: {leave_passengers_list}")
        check_Z9_logger.info(f"行李信息: {leave_bags_list}")

        # 提取航班信息
        for leg in all_info["flights"][0]["legs"]:
            origin = leg["from"]["code"]
            destination = leg["to"]["code"]
            depart_date = datetime.strptime(leg["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")
            arrive_date = datetime.strptime(leg["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S")
            flight_number = leg["carrierCode"] + leg["flightNumber"]

            origin_list.append(origin)
            destination_list.append(destination)
            depart_date_list.append(depart_date)
            arrive_date_list.append(arrive_date)
            flight_number_list.append(flight_number)
        check_Z9_logger.info(f"航班信息为: "
                             f"航班号: {flight_number_list}"
                             f"出发地: {origin_list}"
                             f"目的地: {destination_list}"
                             f"出发时间: {depart_date_list}"
                             f"到达时间: {arrive_date_list}")

        # 提取pnr状态信息
        pnr_status = "false" if all_info["cancelled"] or all_info["hasCancelledSegments"] else "true"
        check_Z9_logger.info(f"pnr_status: {pnr_status}")

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

        return result

    @classmethod
    def __baggage_change(cls, services: list):
        weight = 0
        for service in services:
            if "BG" in service["code"]:
                weight += int(service["code"].replace("BG", ""))
        return weight