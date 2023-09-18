# -*- coding: UTF-8 -*-
from auto_check.AFZ.AFZCheckApi import AFZCheckWeb
import json
from datetime import datetime
from utils.log import check_FZ_logger


def show_check_all_info(last_name, pnr):
    result = None
    try:
        app = AFZCheckWeb(proxies_type=7)
        app.return_sign_api(last_name=last_name, pnr=pnr)
        response = app.fz_check_api()
        all_info = json.loads(response.text)

        result = all_info

    except Exception:
        import traceback
        traceback.print_exc()

    return result


def show_check_part_info(last_name, pnr):
    result = None
    try:
        app = AFZCheckWeb(proxies_type=7)
        app.return_sign_api(last_name=last_name, pnr=pnr)
        response = app.fz_check_api()

        result = data_extract(response)

    except Exception:
        import traceback
        traceback.print_exc()

    return result


def data_extract(check_response):
    try:

        # 首先判断是否找到PNR
        if check_response == "":
            code = "0"
            data = {
                "code": code,
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
                "payStatus": "false"

            }
            check_FZ_logger.error("没有找到PNR")
            return data

        if check_response is None:
            code = "-1"
            data = {"result": "ERROR", "code": code}
            check_FZ_logger.error("请求失败，请重试")
            return data

        all_info = json.loads(check_response.text)

        # 定义出发地等列表，当航班为中转的时候方便拼接
        orgin_list = []
        destination_list = []
        depart_date_list = []
        arrive_date_list = []
        fight_number_list = []

        # passenger_name_list的作用是帮助添加行李中乘客的名字
        passenger_name_list = []

        leave_passengers_list = []
        leave_bags_list = []

        # 提取乘客信息
        for passenger_info in all_info["passengerList"]:
            passenger_id = passenger_info["passengerId"]
            name = passenger_info["lastName"] + "/" + passenger_info["firstName"]
            name = name.replace(" ", "")
            sex = sex_extract(title=passenger_info["title"], gender=passenger_info["gender"])

            birthday = ""
            nationality = passenger_info["nationality"]
            card_issue_place = ""
            card_expired = ""
            certificate_information = ""

            passenger = {
                "passengerId": passenger_id,
                "name": name,
                "sex": sex,
                "birthday": birthday,
                "nationality": nationality,
                "cardIssuePlace": card_issue_place,
                "cardExpired": card_expired,
                "certificateInformation": certificate_information
            }

            passenger_name_list.append(name)
            leave_passengers_list.append(passenger)

        check_FZ_logger.info(f"乘客信息为: {leave_passengers_list}")

        # 提取行李信息
        for flight in all_info["selectedFlights"]:
            selected_baggage_quotes = flight["selectedBaggageQuotes"]

            route = flight["selectedFare"]["route"]
            dep = route.split("_")[0]
            arr = route.split("_")[1]

            for baggage_info in selected_baggage_quotes:

                if baggage_info == '' or baggage_info is None:
                    bag_weight = "0"

                    baggageMessageDOs = {
                        "passengerName": passenger_name_list[0],
                        "depCity": dep,
                        "arrCity": arr,
                        "baggageWeight": bag_weight
                    }

                    leave_bags_list.append(baggageMessageDOs)

                else:

                    for passenger in leave_passengers_list:
                        if passenger["passengerId"] == baggage_info["passengerId"]:
                            bag_weight = str(baggage_info["weight"])

                            baggageMessageDOs = {
                                "passengerName": passenger["name"],
                                "depCity": dep,
                                "arrCity": arr,
                                "baggageWeight": bag_weight
                            }

                            leave_bags_list.append(baggageMessageDOs)

        check_FZ_logger.info(f"行李信息为: {leave_bags_list}")

        # 提取出发地，出发时间等信息
        for flight in all_info["selectedFlights"]:
            # 如果为中转航班需要拼接信息，如果不是则直接取出来

            for leg in flight["legs"]:
                # 地点
                orgin_list.append(leg["origin"])
                destination_list.append(leg["destination"])

                # 时间
                depart_date = datetime.strptime(leg["departureTime"], "%m/%d/%Y %I:%M:%S %p").strftime(
                    "%Y-%m-%d %H:%M:%S")
                depart_date_list.append(depart_date)
                arrive_date = datetime.strptime(leg["arrivalTime"], "%m/%d/%Y %I:%M:%S %p").strftime(
                    "%Y-%m-%d %H:%M:%S")
                arrive_date_list.append(arrive_date)

                # 航班号
                fight_number = leg["marketingCarrier"] + leg["flightNumber"]
                fight_number_list.append(fight_number)

        check_FZ_logger.info(f"航班号: {fight_number_list}\n"
                             f"出发地: {orgin_list}\n"
                             f"目的地: {destination_list}\n"
                             f"出发时间: {depart_date_list}\n"
                             f"到达时间: {arrive_date_list}\n")

        # 提取订单状态，即PNR状态
        pay_status = all_info["pnrInformation"]["bookingStatus"]
        if pay_status == "Confirmed":
            pay_status = "true"
        else:
            pay_status = "false"

        check_FZ_logger.info(f"PNR状态: {pay_status}")

        code = "1"
        data = {
            "code": code,
            "isFind": "true",
            "isBusiness": "false",
            "Leave": {
                "taskType": "SHUA_PIAO",
                "origin": "|".join(orgin_list),
                "destination": "|".join(destination_list),
                "targetPassengers": leave_passengers_list,
                "departDate": "|".join(depart_date_list),
                "arriveDate": "|".join(arrive_date_list),
                "flightNumber": "|".join(fight_number_list),
                "baggageMessageDOs": leave_bags_list,
                "freeBaggageWeight": "0"
            },
            "payStatus": pay_status

        }

        return data

    except Exception:
        import traceback
        check_FZ_logger.error(f"{traceback.print_exc()}")


# 对性别的处理
def sex_extract(title, gender):
    if gender is None:
        if title is None:
            check_FZ_logger.error("乘客没有填写性别信息")
            return None
        elif title == "Mr":
            return "M"
        elif title == "Ms":
            return "F"
        else:
            check_FZ_logger.error("检查乘客性别信息，有未知的代表性别的信息没有判断")
            return None

    else:
        return gender





