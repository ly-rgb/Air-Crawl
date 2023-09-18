# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AVBCheckService.py
@effect: "请填写用途"
@Date: 2022/11/11 15:38
"""
import traceback

from auto_check.AVB.AVBCheckApi import AVBCheckWeb
from utils.log import check_VB_logger
from datetime import datetime


class AVBCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name: str, pnr: str):
        result = None
        app = AVBCheckWeb(proxies_type=7)
        try:
            app.check(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                result = {"result": app.check_response.json(), "code": app.error_code}
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
    def show_check_part_info(cls, last_name: str, pnr: str):
        result = None
        app = AVBCheckWeb(proxies_type=7)
        try:
            app.check(last_name=last_name, pnr=pnr)
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
            # 提取乘客信息
            for passenger in all_info["data"]["passengers"]:
                passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
                title = passenger["title"]
                gender = passenger["gender"]
                passenger_sex = cls.__sex_change(title, gender)
                passenger_birthday = datetime.strptime(passenger["dateOfBirth"], "%Y-%m-%dT%H:%M:%S").strftime(
                    "%Y-%m-%d")
                passenger_nationality = passenger["nationality"]

                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": "",
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": passenger_birthday,
                    "nationality": passenger_nationality,
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_VB_logger.info(f"乘客信息: {leave_passengers_list}")

            # 提取航班信息
            for flight in all_info["data"]["journeys"]:
                for segment in flight["segments"]:
                    origin = segment["origin"]['code']
                    destination = segment["destination"]['code']
                    depart_date = datetime.strptime(segment["departureDate"]['scheduled'], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    arrive_date = datetime.strptime(segment["arrivalDate"]['scheduled'], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    flight_number = (segment["operatingCarrier"] + segment['operatingCode']).replace(" ", "")

                    origin_list.append(origin)
                    destination_list.append(destination)
                    depart_date_list.append(depart_date)
                    arrive_date_list.append(arrive_date)
                    flight_number_list.append(flight_number)
            check_VB_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 提取行李信息
            for service in all_info["data"]["services"]["services"]:
                if service["category"] == "Baggage":
                    for index, option in enumerate(service["options"]):
                        baggage_weight = cls.__baggage_change(option)

                        baggageMessageDOs = {
                            "passengerName": passenger_name_list[index],
                            "depCity": origin_list[0],
                            "arrCity": destination_list[-1],
                            "baggageWeight": str(baggage_weight)
                        }
                        leave_bags_list.append(baggageMessageDOs)
            check_VB_logger.info(f"行李信息: {leave_bags_list}")

            # 提取PNR状态
            pnr_status = "true" if all_info["data"]["status"] == "Paid" and all_info["data"][
                "paidStatus"] == "PaidInFull" else "false"
            check_VB_logger.info(f"PNR状态: {pnr_status}")

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
            check_VB_logger.error("解析数据失败")
            check_VB_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def __sex_change(cls, title, gender):
        sex = ""
        if title == "Mr" or gender == "Male":
            sex = "M"
        else:
            sex = "F"
        return sex

    @classmethod
    def __baggage_change(cls, option):
        weight = 0

        if option["ssrCode"] == "VAAA":
            weight = 15
        elif option["ssrCode"] == "VAAB":
            weight = 20
        elif option["ssrCode"] == "VAAC":
            weight = 25
        else:
            check_VB_logger.error(f"没有判断该类型的行李: {option['ssrCode']}")

        return weight