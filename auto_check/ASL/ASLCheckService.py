# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: ASLCheckService.py
@effect: "请填写用途"
@Date: 2022/12/16 15:47
"""
import traceback

from utils.log import check_SL_logger
from auto_check.ASL.ASLCheckApi import ASLCheckWeb
from lxml import etree
import json


class ASLCheckService(object):

    def __init__(self):
        pass

    @classmethod
    def show_check_all_info(cls, last_name, first_name, pnr, otaid):
        result = None
        app = ASLCheckWeb(proxies_type=0, otaid=otaid)
        try:
            app.front_check(last_name=last_name,first_name=first_name, pnr=pnr)
            app.redirect_1()
            app.redirect_2()
            app.check()
            if app.error_code == "1":
                app.get_baggage_redirect1()
                app.get_baggage_html()
                result = {
                    "flight_text": app.flight_response.text,
                    "baggage_text": app.baggage_response.text,
                    "code": app.error_code
                }
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
            check_SL_logger.error(traceback.print_exc())

        return result

    @classmethod
    def show_check_part_info(cls, last_name, first_name, pnr):
        result = None
        app = ASLCheckWeb(proxies_type=0)
        try:
            app.front_check(last_name=last_name, first_name=first_name, pnr=pnr)
            app.redirect_1()
            app.redirect_2()
            app.check()
            if app.error_code == "1":
                app.get_baggage_redirect1()
                app.get_baggage_html()
                result = cls.__data_extract(app.flight_response.text, app.baggage_response.text)
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
            check_SL_logger.error(f"{traceback.print_exc()}")
            result = {"result": "ERROR", "code": app.error_code}

        return result

    @classmethod
    def __data_extract(cls, flight_text, baggage_text):
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

        passengers_list = []
        bags_list = []

        try:
            # 提取航班信息
            # flight_html = etree.HTML(flight_text)
            # flight_number_list = flight_html.xpath("//table[@id='tblflightdetails']/tbody/tr/td[@class='tab-2']/text()")
            # flight_number_list = list(filter(cls.flight_number_change, flight_number_list))
            #
            # date_list = flight_html.xpath("//table[@id='tblflightdetails']/tbody/tr/td[@class='tab-3']/span/text()")
            #
            # print(flight_number_list)
            # print(date_list)
            pass
        except Exception:
            result = {"result": "ERROR", "code": "-2"}
            check_SL_logger.error("解析数据失败")
            check_SL_logger.error(f"{traceback.print_exc()}")

        return result

    @classmethod
    def flight_number_change(cls, flight_number):
        if "SL" in flight_number:
            return True
        return False
