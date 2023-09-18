# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AEWCheckService.py
@effect: "EW质检业务层"
@Date: 2022/11/2 15:09
"""
import json

from utils.log import check_EW_logger
from datetime import datetime
import traceback
import re
from lxml import etree
import execjs
from auto_check.AEW.AEWCheckApi import AEWCheckWeb


class AEWCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, pnr, gender):
        result = None
        app = AEWCheckWeb(proxies_type=7)
        try:
            app.front_check(last_name=last_name, pnr=pnr)
            app.check_redirect(last_name=last_name, pnr=pnr, gender=gender)
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
    def show_check_part_info(cls, last_name, pnr, gender):
        result = None
        app = AEWCheckWeb(proxies_type=7)
        try:
            app.front_check(last_name=last_name, pnr=pnr)
            app.check_redirect(last_name=last_name, pnr=pnr, gender=gender)
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
    def __data_extract(cls, all_info: str):
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

        # 定义行李类型对应的重量
        baggage_type_weight = {
            "Kleines Handgepäck": 0,
            "Großes Handgepäck": 8,
            "Aufgabegepäck": 23
        }

        try:
            html = etree.HTML(all_info)
            info_json = cls.__transformation_object(html)
            info_list = json.loads(info_json)["1"]

            for leg in info_list:
                origin = leg["departureAirport"]["threeLetterCode"]
                destination = leg["arrivalAirport"]["threeLetterCode"]
                depart_date = datetime.strptime(leg["departureDate"]["dateTime"], "%Y-%m-%d %H:%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S")
                arrive_date = datetime.strptime(leg["arrivalDate"]["dateTime"], "%Y-%m-%d %H:%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S")
                flight_number = leg["carrierCode"] + str(leg["flightNumber"])

                origin_list.append(origin)
                destination_list.append(destination)
                depart_date_list.append(depart_date)
                arrive_date_list.append(arrive_date)
                flight_number_list.append(flight_number)
            check_EW_logger.info(f"航班信息为: "
                                 f"航班号: {flight_number_list}"
                                 f"出发地: {origin_list}"
                                 f"目的地: {destination_list}"
                                 f"出发时间: {depart_date_list}"
                                 f"到达时间: {arrive_date_list}")

            for passenger in info_list[0]["passengers"]:
                passenger_name = (passenger["lastname"] + "/" + passenger["firstname"]).replace(" ", "")
                passenger_sex = "M" if passenger["salutation"] == "MR" else "F"

                passenger_name_list.append(passenger_name)
                leave_passengers_list.append({
                    "passengerId": "",
                    "name": passenger_name,
                    "sex": passenger_sex,
                    "birthday": "",
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_EW_logger.info(f"乘客信息: {leave_passengers_list}")

            # 行李信息
            # 判断有几个行李
            base_xpath = '//div[@class="baggage-card-passengers"]/div[@class="baggage-card-passenger"]'
            for i in range(1, len(html.xpath(base_xpath)) + 1):
                # 2. 提取行李类型
                baggage_type = html.xpath(f'//div[@class="baggage-card-passengers"]/div[{i}]/div[contains(@class,"baggage-card-item") and not(contains(@class,"baggage-card-item-not-included"))]/div[1]/span[@class="baggage-card-item-title"]/text()')

                # 3. 提取行李类型对应的数量
                baggage_number = html.xpath(f'//div[@class="baggage-card-passengers"]/div[{i}]/div[contains(@class,"baggage-card-item") and not(contains(@class,"baggage-card-item-not-included"))]/div[2]/span[@class="baggage-card-item-count"]/text()')
                baggage_weight = 0
                for index, value in enumerate(baggage_type):
                    baggage_weight += baggage_type_weight[value] * int(baggage_number[index])
                baggageMessageDOs = {
                    "passengerName": passenger_name_list[i-1],
                    "depCity": origin_list[0],
                    "arrCity": destination_list[-1],
                    "baggageWeight": str(baggage_weight)
                }
                leave_bags_list.append(baggageMessageDOs)

            check_EW_logger.info(f"行李信息: {leave_bags_list}")

            # PNR状态信息
            pnr_status = "true"

            # Noshow信息
            check_EW_logger.info(f"PNR 状态信息: 固定为true，没有找到标志")
            check_EW_logger.info("noshow信息暂时不写")

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


        except:
            result = {"result": "ERROR", "code": "-2"}
            check_EW_logger.error("解析数据失败")
            check_EW_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def __transformation_object(cls, html):
        """
        将html提取出指定script内容，并返回指定json
        :return:
        """

        # 提取质检信息，在js中提取
        scripts = html.xpath('//div[@class="flight-info-box"]/script[1]/text()')[0]
        check_EW_logger.info(f"提取的script信息为: {scripts}")
        all_info = re.match(
            r".*(window.Germanwings.Common.globalVariables.flightSegmentArray.*)window.Germanwings.Common.globalVariables.recordlocatorToSaveInApp",
            scripts,
            re.M | re.S).group(1).replace("window.Germanwings.Common.globalVariables.flightSegmentArray",
                                          "var flight_object") + "\n" + " return JSON.stringify(flight_object)"

        js_text = "function a(){" + all_info + "}"
        check_EW_logger.info(f"拼接的js代码为: {js_text}")
        js_object = execjs.compile(js_text)
        result = js_object.call("a")
        check_EW_logger.info(f"js执行结果(json类型)为: {result}")
        return result



