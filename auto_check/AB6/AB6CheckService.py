# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AB6CheckService.py
@effect: "请填写用途"
@Date: 2022/12/7 15:54
"""
from utils.log import check_B6_logger
from auto_check.AB6.AB6CheckApi import AB6CheckWeb
from datetime import datetime
import traceback


class AB6CheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr):
        result = None
        app = AB6CheckWeb(proxies_type=7)
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
    def show_check_part_info(cls, last_name, pnr):
        result = None
        app = AB6CheckWeb(proxies_type=7)
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

        # 为了解决pnr分段支付的问题，可能出现多航段未支付的情况
        pnr_status_list = []

        try:
            # 解析航班信息
            flights = all_info["data"]["getMYBTripDetails"]["originalResponse"]["pnr"]["itinerary"]["itineraryParts"]
            for flight in flights:
                for segment in flight["segments"]:
                    flight_number = segment["flight"]["airlineCode"] + str(segment["flight"]["flightNumber"])
                    origin = segment["origin"]
                    destination = segment["destination"]
                    depart_date = datetime.strptime(segment["departure"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    arrive_date = datetime.strptime(segment["arrival"], "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y-%m-%d %H:%M:%S")

                    pnr_status_list.append(
                        "true" if segment["segmentStatusCode"]["segmentStatus"] == "CONFIRMED" else "false")

                    flight_number_list.append(flight_number)
                    origin_list.append(origin)
                    destination_list.append(destination)
                    depart_date_list.append(depart_date)
                    arrive_date_list.append(arrive_date)

                check_B6_logger.info(f"航班信息为: "
                                     f"航班号: {flight_number_list}"
                                     f"出发地: {origin_list}"
                                     f"目的地: {destination_list}"
                                     f"出发时间: {depart_date_list}"
                                     f"到达时间: {arrive_date_list}")
                check_B6_logger.info(f"PNR状态: {pnr_status_list}")

            passengers = all_info["data"]["getMYBTripDetails"]["originalResponse"]["pnr"]["passengers"]
            for passenger in passengers:
                passenger_name = cls.__name_change(passenger)
                passenger_sex = cls.__sex_change(passenger)
                passenger_birthday = passenger["passengerInfo"]["dateOfBirth"]

                passenger_name_list.append(passenger_name)
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
            check_B6_logger.info(f"乘客信息: {leave_passengers_list}")

            # 提取行李信息
            documents = all_info["data"]["getMYBTripDetails"]["originalResponse"]["pnr"]["travelPartsAdditionalDetails"]
            for document in documents:

                for idx, passenger in enumerate(passenger_name_list):
                    bags = document["passengers"][idx]
                    weight = 0
                    if "ancillaries" in list(bags.keys()):
                        for bag in bags["ancillaries"]:
                            weight += cls.__bag_change(code=bag["ancillaryCode"], num=bag["assignedQuantity"])

                        baggageMessageDOs = {
                            "passengerName": passenger_name_list[idx],
                            "depCity": origin_list[0],
                            "arrCity": destination_list[-1],
                            "baggageWeight": str(weight)
                        }
                        leave_bags_list.append(baggageMessageDOs)
            check_B6_logger.info(f"行李信息: {leave_bags_list}")

            # pnr 状态
            pnr_status = "false" if "false" in pnr_status_list else "true"

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
            check_B6_logger.error("解析数据失败")
            check_B6_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def __bag_change(cls, **kwargs) -> int:
        weight = 0
        code = kwargs.get("code")
        num = kwargs.get("num")
        if code == "0C3":
            weight += 23 * num
        elif code == "0GO":
            weight += 23 * num

        return weight

    @classmethod
    def __name_change(cls, passenger: dict) -> str:
        name = ""
        if "middleName" in list(passenger["passengerDetails"].keys()):
            name = (passenger["passengerDetails"]["lastName"] + "/" + passenger["passengerDetails"][
                "firstName"] + passenger["passengerDetails"]["middleName"]).replace(" ", "")

        else:
            name = passenger["passengerDetails"]["lastName"] + "/" + passenger["passengerDetails"][
                "firstName"]

        return name.replace(" ", "")

    @classmethod
    def __sex_change(cls, passenger: dict) -> str:
        sex = ""
        if "prefix" in list(passenger["passengerDetails"].keys()):
            sex = "M" if passenger["passengerDetails"]["prefix"] == "MR" else "F"
        else:
            sex = "M" if passenger["passengerInfo"]["gender"] == "MALE" else "F"

        return sex
