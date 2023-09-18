# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: ATKCheckService.py
@effect: "请填写用途"
@Date: 2022/11/30 15:58
"""
import traceback
from datetime import datetime
from utils.log import check_TK_logger
from auto_check.ATK.ATKCheckApi import ATKCheckWeb


class ATKCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr):
        result = None
        app = ATKCheckWeb(proxies_type=0)
        try:
            app.check(last_name=last_name, pnr=pnr)
            if app.error_code == "1":
                print(app.check_response.json())
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
        app = ATKCheckWeb(proxies_type=0)
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

        try:
            for index, flight in enumerate(all_info["data"]["trips"]):
                # 定义出发地等列表，当航班为中转的时候方便拼接
                origin_list = []
                destination_list = []
                depart_date_list = []
                arrive_date_list = []
                flight_number_list = []

                passengers_list = []
                passengers_name_list = []
                bags_list = []

                # 提取航班信息
                for segment in flight["flightInfo"]["segments"]:
                    origin = segment["originAirport"]["code"]
                    destination = segment["destinationAirport"]["code"]
                    depart_date = datetime.strptime(segment["departureDateTimeISO"]["customDateTimeMinutesLocal"], "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:00")
                    arrive_date = datetime.strptime(segment["arrivalDateTimeISO"]["customDateTimeMinutesLocal"], "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:00")
                    flight_number = segment["flightNumber"]

                    origin_list.append(origin)
                    destination_list.append(destination)
                    depart_date_list.append(depart_date)
                    arrive_date_list.append(arrive_date)
                    flight_number_list.append(flight_number)
                check_TK_logger.info(f"提取到的航班{'去程信息-->' if index == 0 else '回程信息-->'}" +
                                     f"航班号: {flight_number_list}"
                                     f"出发地: {origin_list}"
                                     f"目的地: {destination_list}"
                                     f"出发时间: {depart_date_list}"
                                     f"到达时间: {arrive_date_list}")

                # 提取乘客信息
                for passenger in flight["flightInfo"]["passengers"]:
                    passenger_name = (passenger["apiInfo"]["surname"] + "/" + passenger["apiInfo"]["name"]).replace(
                        " ", "")
                    passenger_sex = "M" if passenger["apiInfo"]["gender"] == "M" else "F"
                    passenger_birthday = datetime.strptime(passenger["apiInfo"]["birthday"], "%d-%m-%Y").strftime("%Y-%m-%d")
                    passenger_nationality = passenger["personalInfo"]["nationality"]
                    passengers_name_list.append(passenger_name)
                    passengers_list.append({
                        "passengerId": "",
                        "name": passenger_name,
                        "sex": passenger_sex,
                        "birthday": passenger_birthday,
                        "nationality": passenger_nationality,
                        "cardIssuePlace": "",
                        "cardExpired": "",
                        "certificateInformation": ""
                    })
                check_TK_logger.info(f"提取到的乘客{'去程信息-->' if index == 0 else '回程信息-->'}{passengers_list}")

                # 提取行李信息, 先设置为0
                for name in passengers_name_list:
                    baggageMessageDOs = {
                        "passengerName": name,
                        "depCity": origin_list[0],
                        "arrCity": destination_list[-1],
                        "baggageWeight": str(0)
                    }
                    bags_list.append(baggageMessageDOs)
                check_TK_logger.info(f"提取到的行李{'去程信息-->' if index == 0 else '回程信息-->'}{bags_list}")

                pnr_status = "true" if all_info["data"]["paid"] else "false"
                check_TK_logger.info(f"pnr_status: {pnr_status}")

                result = {
                    "code": "1",
                    "isFind": "true",
                    "isBusiness": "false",
                    "payStatus": pnr_status,
                    "liftStatus": ""
                }
                if index == 0:
                    result["Leave"] = {
                        "taskType": "SHUA_PIAO",
                        "origin": "|".join(origin_list),
                        "destination": "|".join(destination_list),
                        "targetPassengers": passengers_list,
                        "departDate": "|".join(depart_date_list),
                        "arriveDate": "|".join(arrive_date_list),
                        "flightNumber": "|".join(flight_number_list),
                        "baggageMessageDOs": bags_list,
                        "freeBaggageWeight": "0"
                    }

                elif index == 1:
                    result["Backhaul"] = {
                        "taskType": "SHUA_PIAO",
                        "origin": "|".join(origin_list),
                        "destination": "|".join(destination_list),
                        "targetPassengers": passengers_list,
                        "departDate": "|".join(depart_date_list),
                        "arriveDate": "|".join(arrive_date_list),
                        "flightNumber": "|".join(flight_number_list),
                        "baggageMessageDOs": bags_list,
                        "freeBaggageWeight": "0"
                    }
                else:
                    raise Exception(f"index = {index}, 请检查数据")

        except Exception:
            result = {"result": "ERROR", "code": "-2"}
            check_TK_logger.error("解析数据失败")
            check_TK_logger.error(f"{traceback.print_exc()}")

        return result

