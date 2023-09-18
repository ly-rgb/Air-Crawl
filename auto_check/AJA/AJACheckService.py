# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AJACheckService.py
@effect: "JA质检业务层"
@Date: 2022/11/18 14:57
"""
from utils.log import check_JA_logger
from datetime import datetime
import traceback
import html
import re
from auto_check.AJA.AJACheckApi import AJACheckWeb
import json


class AJACheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr):
        result = None
        app = AJACheckWeb(proxies_type=7)
        try:
            app.retrieve_check(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                app.check()
                result = {"result": app.check_response.text, "code": app.error_code}
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
        app = AJACheckWeb(proxies_type=7)
        try:
            app.retrieve_check(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                app.check()
                result = cls.__data_extract(app.check_response.text)
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
            # 1. 解析html中的booking-data属性
            html_text = html.unescape(all_info)
            booking_dict = cls.__booking_extract(html_info=html_text)
            model_dict = cls.__state_extract(html_info=html_text)

            # 2. 提取航班信息
            origin = booking_dict["data"]["OutboundJourney"]["DepartureStationCode"]
            destination = booking_dict["data"]["OutboundJourney"]["ArrivalStationCode"]
            depart_date = booking_dict["data"]["OutboundJourney"]["DepartureDate"]
            arrive_date = booking_dict["data"]["OutboundJourney"]["ArrivalDate"]
            flight_number = booking_dict["data"]["OutboundJourney"]["FlightNumber"].replace(" ", "")

            origin_list.append(origin)
            destination_list.append(destination)
            depart_date_list.append(depart_date)
            arrive_date_list.append(arrive_date)
            flight_number_list.append(flight_number)
            check_JA_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 3.提取乘客信息
            for passenger in model_dict["data"]["Passengers"]:
                passenger_name = (passenger["LastName"] + "/" + passenger["FirstName"]).replace(" ", "")
                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": "",
                    "name": passenger_name,
                    "sex": "",
                    "birthday": "",
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_JA_logger.info(f"乘客信息列表 ==> {leave_passengers_list}")

            # 提取行李信息，暂时设置为0
            for index, passenger_name in enumerate(passenger_name_list):
                baggageMessageDOs = {
                    "passengerName": passenger_name_list[index],
                    "depCity": origin_list[0],
                    "arrCity": destination_list[-1],
                    "baggageWeight": str(0)
                }
                leave_bags_list.append(baggageMessageDOs)
            check_JA_logger.info(f"行李信息列表 ==> {leave_bags_list}")

            # noshow 信息
            check_JA_logger.info(f"noShow信息暂不提取")

            # PNR状态
            pnr_status = "true" if model_dict["data"]["IsCancelled"] is False and model_dict["data"]["ShowPaymentErrorWarning"] is False else "false"
            check_JA_logger.info(f"pnr状态信息: {pnr_status}")

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
            check_JA_logger.error("解析错误")
            check_JA_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def __booking_extract(cls, html_info):

        pattern = ".*?booking-data=(.*?)\n"
        booking_data = re.match(pattern, html_info, re.M | re.S).groups(0)[0]
        booking_data = booking_data[1:booking_data.rfind("\"")].replace("`", "{")
        return json.loads(booking_data)

    @classmethod
    def __state_extract(cls, html_info) -> dict:
        """
        提取
        :param html_info:
        :return:
        """
        pattern = ".*?model=(.*data.*?)has-balance-due"
        model_data = re.match(pattern, html_info, re.M | re.S).groups(0)[0]
        model_data = model_data[1:model_data.rfind("\"")].replace("`", "{")
        return json.loads(model_data)

