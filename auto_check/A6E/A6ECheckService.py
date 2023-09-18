# -*- coding: UTF-8 -*-
from utils.log import check_6E_logger
from auto_check.A6E.A6ECheckApi import A6ECheckWeb
import json
import traceback


class A6ECheckService(object):

    """
    注意：乘客名字不能去掉空格
    """

    @classmethod
    def show_check_all_info(cls, last_name: str, pnr: str):
        """
        返回所有数据
        :param last_name:
        :param pnr:
        :return:
        """
        result = None

        try:
            app = A6ECheckWeb(proxies_type=7)
            app.index_AEM()
            app.retrieve_AEM(last_name, pnr)
            if app.error_code == "1":
                response = app.view_AEM()
                result = json.loads(response.text)

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

                check_6E_logger.error("没有找到PNR")

            else:
                result = {"result": "ERROR", "code": app.error_code}
                check_6E_logger.error("请求失败，请重试")

        except Exception:

            check_6E_logger.error(f"{traceback.print_exc()}")

            result = {"result": "ERROR", "code": app.error_code}

        check_6E_logger.info(f"最后的结果为: {result}")
        return result

    @classmethod
    def show_check_part_info(cls, last_name: str, pnr: str):

        """
        返回客户端（java）需要的数据
        :param last_name:
        :param pnr:
        :return:
        """

        result = None

        try:
            app = A6ECheckWeb(proxies_type=7)
            app.index_AEM()
            app.retrieve_AEM(last_name, pnr)

            if app.error_code == "1":
                response = app.view_AEM()
                all_info = json.loads(response.text)
                result = cls.__data_extra(all_info)

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
                check_6E_logger.error("请求失败，请重试")

        except Exception:

            check_6E_logger.info(f"{traceback.print_exc()}")

            result = {"result": "ERROR", "code": app.error_code}

        return result

    @classmethod
    def __data_extra(cls, all_info: dict):

        """
        数据解析
        :param all_info: 返回的所有数据的dict类型
        :return: 解析后的数据
        """

        try:
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

            # 提取乘客信息
            for passenger in all_info["indiGoItineraryNavigation"]["bookingObject"]["passengers"]:

                for name in passenger["names"]:
                    passenger_name = (name["lastName"] + "/" + name["firstName"]).replace(" ", "")
                    passenger_name_list.append(passenger_name)

                    passenger_sex = A6ECheckService.extra_sex(name["title"],
                                                              passenger["passengerInfos"][0]["gender"])

                # passenger_birthday = passenger['passengerTypeInfos'][0]["dOB"].split(" ")[0]
                passenger_id = passenger["passengerID"]
                passenger_nationality = passenger["passengerInfos"][0]["nationality"]

                leave_passengers_list.append({
                    "passengerId": passenger_id,
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": "",
                    "nationality": passenger_nationality,
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })

            check_6E_logger.info(f"乘客信息列表: {leave_passengers_list}")

            # 提取出发地，出发时间等信息
            for flight in all_info["indiGoItineraryNavigation"]["bookingObject"]["journeys"]:

                for segment in flight["segments"]:
                    # 地点
                    origin_list.append(segment["departureStation"])
                    destination_list.append(segment["arrivalStation"])

                    # 时间
                    depart_date_list.append(segment["sTD"])
                    arrive_date_list.append(segment["sTA"])

                    # 航班号
                    for leg in segment["legs"]:
                        flight_number = (leg["flightDesignator"]["carrierCode"] + leg["flightDesignator"][
                            "flightNumber"]).replace(" ", "")

                        flight_number_list.append(flight_number)

            check_6E_logger.info(f"航班信息-> "
                                 f"航班号列表：{flight_number_list}"
                                 f"出发地列表:{origin_list}"
                                 f"目的地列表：{destination_list}"
                                 f"出发时间列表：{depart_date_list}"
                                 f"到达时间列表：{arrive_date_list}")

            # 提取行李信息， 以及noshow状态（Deflate：没到起飞时间，Boarded：已经起飞）
            for flight in all_info["indiGoItineraryNavigation"]["bookingObject"]["journeys"]:

                segment = flight["segments"][0]

                for index, paxSegment in enumerate(segment["paxSegments"]):

                    baggage_weight = str(paxSegment["baggageAllowanceWeight"])
                    baggageMessageDOs = {
                        "passengerName": passenger_name_list[index],
                        "depCity": origin_list[0],
                        "arrCity": destination_list[-1],
                        "baggageWeight": baggage_weight
                    }

                    lift_status = paxSegment["liftStatus"]
                    lift_status_list.append({
                        "status": lift_status,
                        "passenger_name": passenger_name_list[index]
                    })

                    leave_bags_list.append(baggageMessageDOs)


            check_6E_logger.info(f"行李信息列表：{leave_bags_list}")
            check_6E_logger.info(f"liftStatus列表: {lift_status_list}")

            # 提取PNR状态信息
            pnr_status_info = all_info["indiGoItineraryNavigation"]["bookingObject"]["bookingInfo"]["bookingStatus"]
            pnr_status = lambda x: "true" if x == "Confirmed" else "false"

            check_6E_logger.info(f"PNR状态：{pnr_status(pnr_status_info)}")

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
                "payStatus": pnr_status(pnr_status_info),
                "liftStatus": lift_status_list

            }

            return result
        except Exception:

            check_6E_logger.error(f"{traceback.format_exc()}")


    @staticmethod
    def extra_sex(title: str, gender: str):
        if title == "MR" or gender == "Male":
            return "M"
        else:
            return "F"








