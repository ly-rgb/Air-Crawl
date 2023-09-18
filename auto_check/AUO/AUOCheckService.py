from utils.log import check_UO_logger
from auto_check.AUO.AUOCheckApi import AUOCheckWeb
import traceback
from datetime import datetime


class AUOCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(self, last_name, first_name, pnr):
        result = None
        app = AUOCheckWeb(proxies_type=7)
        try:
            app.manage_booking(last_name=last_name, first_name=first_name, pnr=pnr)
            app.check()
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
    def show_check_part_info(cls, last_name, first_name, pnr):
        result = None
        app = AUOCheckWeb(proxies_type=7)
        try:
            app.manage_booking(last_name=last_name, first_name=first_name, pnr=pnr)
            app.check()
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
            check_UO_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def show_check_agent_info(cls, pnr: str):
        """
        UO代理人账户质检
        :param pnr: PNR
        :return:
        """
        result = None
        app = AUOCheckWeb(proxies_type=0)
        try:
            app.agent_check(pnr)
            if app.error_code == "1":
                result = cls.__data_agent_extract(app.agent_check_response.json())
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
            check_UO_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def __data_extract(cls, all_info: dict):
        result = None
        print(all_info)
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

            journeys = all_info["journeys"]

            # 提取乘客信息
            for passenger in all_info["passengers"]:
                passenger_name = (passenger["lastName"] + "/" + passenger["firstName"]).replace(" ", "")
                passenger_sex = "F" if passenger["gender"] == "Female" or passenger["title"] == "mrs" else "M"
                passenger_birth = datetime.strptime(passenger["dateOfBirth"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": "",
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": passenger_birth,
                    "nationality": passenger["nationality"],
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_UO_logger.info(f"乘客信息为: {leave_passengers_list}")

            # 航班信息
            for index, flight in enumerate(journeys[0]["segments"]):
                flight_number = flight["carrierCode"] + flight["flightNumber"].strip()
                depart_date = datetime.strptime(flight["std"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                arrive_date = datetime.strptime(flight["sta"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

                flight_number_list.append(flight_number)
                origin_list.append(flight["originIata"])
                destination_list.append(flight["destinationIata"])
                depart_date_list.append(depart_date)
                arrive_date_list.append(arrive_date)
            check_UO_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 提取行李信息
            for index, passenger in enumerate(all_info["passengers"]):
                # 行李重量初始化,最终还是要转为str
                baggageWeight = 0
                if len(passenger["paxAncillaries"]) != 0:
                    for baggage in passenger["paxAncillaries"]:
                        if baggage["code"] == "BULK":
                            check_UO_logger.info(f"BULK(散装)暂时不处理")
                            continue
                        baggageWeight += int(baggage["bookingFeeId"][-2:])

                baggageMessageDOs = {
                    "passengerName": passenger_name_list[index],
                    "depCity": origin_list[0],
                    "arrCity": destination_list[-1],
                    "baggageWeight": str(baggageWeight)
                }
                leave_bags_list.append(baggageMessageDOs)
            check_UO_logger.info(f"行李信息为: {leave_bags_list}")

            # PNR状态信息
            pnr_status = "true" if all_info["bookingInfo"]["status"] == "Confirmed" else "false"

            # Noshow信息
            for index, paxSegment in enumerate(journeys[0]["segments"][0]["paxSegments"]):
                lift_status = {"status": paxSegment["liftStatus"],
                               "passenger_name": passenger_name_list[index]}

                lift_status_list.append(lift_status)

            check_UO_logger.info(f"Noshow 信息为: {lift_status_list}")

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
            check_UO_logger.error(f"check数据解析失败")
            check_UO_logger.error(f"{traceback.print_exc()}")

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
            journeys = all_info["booking"]["journeys"]["journey"][0]

            # 提取航班信息
            for flight in journeys["segments"]["segment"]:
                origin = flight["departureStation"]
                destination = flight["arrivalStation"]
                depart_date = datetime.fromtimestamp(flight["std"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                arrive_date = datetime.fromtimestamp(flight["sta"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                flight_number = (flight["flightDesignator"]["carrierCode"] + flight["flightDesignator"][
                    "flightNumber"]).replace(" ", "")

                origin_list.append(origin)
                destination_list.append(destination)
                depart_date_list.append(depart_date)
                arrive_date_list.append(arrive_date)
                flight_number_list.append(flight_number)
            check_UO_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            # 提取乘客信息与行李信息
            for passenger in all_info["booking"]["passengers"]["passenger"]:
                passenger_id = str(passenger["passengerID"])
                passenger_name = (passenger["names"]["bookingName"][0]["lastName"] + "/" +
                                  passenger["names"]["bookingName"][0]["firstName"]).replace(
                    " ", "")
                passenger_sex = "F" if passenger["names"]["bookingName"][0]["title"] == "MS" else "M"

                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": passenger_id,
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": "",
                    "nationality": passenger["passengerInfo"]["nationality"],
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })

                # 提取行李信息
                baggageWeight = 0
                if passenger["passengerFees"]["passengerFeeSpecified"] is False:
                    baggageMessageDOs = {
                        "passengerName": passenger_name,
                        "depCity": origin_list[0],
                        "arrCity": destination_list[-1],
                        "baggageWeight": str(baggageWeight)
                    }
                    leave_bags_list.append(baggageMessageDOs)
                else:
                    for passengerFee in passenger["passengerFees"]["passengerFee"]:

                        baggageWeight += 0 if passengerFee["feeCode"] == "BULK" else int(passengerFee["feeCode"][-2:])

                        baggageMessageDOs = {
                            "passengerName": passenger_name,
                            "depCity": origin_list[0],
                            "arrCity": destination_list[-1],
                            "baggageWeight": str(baggageWeight)
                        }
                        leave_bags_list.append(baggageMessageDOs)

            check_UO_logger.info(f"乘客信息: {leave_passengers_list}")
            check_UO_logger.info(f"行李信息: {leave_bags_list}")

            # PNR状态信息
            pnr_status = "true" if (all_info["booking"]["bookingInfo"]["bookingStatus"]["value"] == "Confirmed" and
                                    all_info["booking"]["bookingInfo"]["paidStatus"]["value"] == "PaidInFull") else "false"

            # Noshow信息
            check_UO_logger.info(f"PNR 状态信息: {pnr_status}")
            check_UO_logger.info("noshow信息暂时不写")

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
            check_UO_logger.error(f"{traceback.print_exc()}")

        return result



