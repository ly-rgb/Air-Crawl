# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AXYCheckService.py
@effect: "XY质检Service层"
@Date: 2022/11/9 14:13
"""

from utils.log import check_XY_logger
from auto_check.AXY.AXYCheckApi import AXYCheckWeb
import json
import traceback
from datetime import datetime


class AXYCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr):
        result = None
        app = AXYCheckWeb(proxies_type=7)
        try:
            app.retrieve_booking(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                app.check()
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
    def show_check_part_info(cls, last_name, pnr):
        result = None
        app = AXYCheckWeb(proxies_type=0)
        try:
            app.session_create()
            app.retrieve_booking(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                app.check()
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
            check_XY_logger.error(f"{traceback.print_exc()}")
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
            for passenger in all_info["passengersInput"]["passengers"]:
                passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
                title = passenger["title"]
                pax_type = passenger["paxType"]
                passenger_sex = cls.__sex_change(title, pax_type)
                passenger_birthday = datetime.strptime(passenger["dateOfBirth"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                passenger_nationality = passenger["travelDocument"]["nationality"]

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
            check_XY_logger.info(f"乘客信息: {leave_passengers_list}")

            # 提取航班信息
            for flight in all_info["bookingFlights"]["journeys"]:
                for segment in flight["segments"]:
                    origin = segment["origin"]
                    destination = segment["destination"]
                    depart_date = datetime.strptime(segment["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    arrive_date = datetime.strptime(segment["arrivalDate"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    flight_number = (segment["flightDesignator"]).replace(" ", "")

                    origin_list.append(origin)
                    destination_list.append(destination)
                    depart_date_list.append(depart_date)
                    arrive_date_list.append(arrive_date)
                    flight_number_list.append(flight_number)
            check_XY_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 提取行李信息
            service = all_info["baggageSsr"]["passengerServices"]
            for index, name in enumerate(passenger_name_list):
                baggage_weight = cls.__baggage_service(service[index])
                baggageMessageDOs = {
                    "passengerName": name,
                    "depCity": origin_list[0],
                    "arrCity": destination_list[-1],
                    "baggageWeight": str(baggage_weight)
                }
                leave_bags_list.append(baggageMessageDOs)
            check_XY_logger.info(f"行李信息: {leave_bags_list}")

            # PNR状态
            pnr_status = "true" if all_info["bookingDetails"]["status"] == "Confirmed" else "false"
            check_XY_logger.info(f"PNR状态: {pnr_status}")

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
            check_XY_logger.error("解析数据失败")
            check_XY_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def __sex_change(cls, title, pax_type):
        sex = ""
        if pax_type == "ADT":
            if title == "MS":
                sex = "F"
            elif title == "MRS":
                sex = "F"
            else:
                sex = "M"
        else:
            sex = "C"

        return sex

    @classmethod
    def __baggage_service(cls, baggage_service):
        weight = 0
        service_type = {
            "BULK": 15,
            "XB20": 20,
            "XB25": 25
        }
        services = baggage_service["flightPartServices"][0]["services"]
        for service in services:
            weight += service_type[service["feeCode"]] * int(service["count"])

        return weight

