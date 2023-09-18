# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: ADDCheckService.py
@effect: "DD航司业务层"
@Date: 2022/10/18 11:58
"""
from utils.log import check_DD_logger
from datetime import datetime
from auto_check.ADD.ADDCheckApi import ADDCheckWeb
from utils.AgentDb import select_agent_db
import traceback


class ADDCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr):

        result = None
        app = ADDCheckWeb(proxies_type=7)
        try:
            agent_account = select_agent_db(pnr=pnr, logger=check_DD_logger)
            app.agent_login(account=agent_account["user_name"], password=agent_account["password"])
            app.check(last_name=last_name, pnr=pnr)
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
    def show_check_part_info(cls, last_name, pnr):
        """
        官网质检
        :param last_name:
        :param pnr:
        :return:
        """
        pass

    @classmethod
    def show_check_agent_info(cls, last_name, pnr):
        """
        代理人质检
        :param last_name:
        :param pnr:
        :return:
        """
        result = None
        app = ADDCheckWeb(proxies_type=7)
        try:
            agent_account = select_agent_db(pnr=pnr, logger=check_DD_logger)
            app.agent_login(account=agent_account["user_name"], password=agent_account["password"])
            app.check(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                result = cls.__data_agent_extract(app.check_response.json())

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
    def __data_agent_extract(cls, all_info: dict):
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
            for flight in all_info["flights"]:
                for leg in flight["legs"]:
                    origin = leg["from"]["code"]
                    destination = leg["to"]["code"]
                    depart_date = datetime.strptime(leg["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    arrive_date = datetime.strptime(leg["arrivalDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    flight_number = leg["carrierCode"] + leg["flightNumber"]

                    origin_list.append(origin)
                    destination_list.append(destination)
                    depart_date_list.append(depart_date)
                    arrive_date_list.append(arrive_date)
                    flight_number_list.append(flight_number)

            check_DD_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 提取乘客信息
            for passenger in all_info["passengers"]:
                passenger_id = str(passenger["id"])
                passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
                passenger_sex = "F" if passenger["title"] == "MISS" or passenger["title"] == "MS" or passenger[
                    "title"] == "MRS" else "M"
                passenger_birthday = datetime.strptime(passenger["dateOfBirth"], "%Y-%m-%dT%H:%M:%S").strftime(
                    "%Y-%m-%d")
                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": passenger_id,
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": passenger_birthday,
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })

                # 行李信息
                baggageWeight = 0
                services = passenger["flights"][0]["services"]
                for service in services:
                    if len(services) == 0:
                        break
                    if "BG" in service["code"]:
                        baggageWeight += int(service["code"].replace("BG", ""))
                baggageMessageDOs = {
                    "passengerName": passenger_name,
                    "depCity": origin_list[0],
                    "arrCity": destination_list[-1],
                    "baggageWeight": str(baggageWeight)
                }
                leave_bags_list.append(baggageMessageDOs)

                # NoShow信息
                for flight in passenger["flights"]:
                    lift_status = "NoShow" if len(flight["seats"]) == 0 else "Normal"

                    lift_status_list.append({
                        "status": lift_status,
                        "passenger_name": passenger_name
                    })

            # ticketNumber
            ticket_number = all_info["webBookingId"]

            check_DD_logger.info(f"行李信息: {leave_bags_list}")
            check_DD_logger.info(f"乘客信息列表 ==> {leave_passengers_list}")
            check_DD_logger.info(f"NOSHOW: {lift_status_list}")
            check_DD_logger.info(f"ticketNumber: {ticket_number}")

            # PNR 状态信息
            pnr_status = "true" if all_info["cancelled"] is False and all_info["hasCancelledSegments"] is False else "false"
            check_DD_logger.info(f"PNR状态: {pnr_status}")

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
                "liftStatus": lift_status_list,
                "ticketNumber": ticket_number
            }

        except Exception:
            result = {"result": "ERROR", "code": "-2"}
            check_DD_logger.error("解析错误")
            check_DD_logger.error(f"{traceback.print_exc()}")

        return result

