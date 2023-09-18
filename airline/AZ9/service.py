# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: service.py
@effect: "请填写用途"
@Date: 2022/11/29 14:34
"""
from airline.base import pay_error_result, add_on_select_flight
from native.api import pay_order_log
from robot import HoldTask
from robot.model import AddOnResult
from utils.log import spider_Z9_logger, booking_Z9_logger, add_on_Z9_logger
import traceback
from airline.AZ9.AZ9Web import AZ9Web
from airline.AZ9.AZ9Baggage import AZ9Baggage


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0

    try:
        app = AZ9Web(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result and isinstance(result, list):
            code = -1
            result = None
            spider_Z9_logger.error(f"当天没有航班")
        if result is None:
            code = -1

    except Exception:
        code = -1
        spider_Z9_logger.error(f"{taskItem} {traceback.format_exc()}")

    return code, result


def no_hold_pay(task, proxies_type=None):
    code = -1
    booking_Z9_logger.info(f"最开始的任务: {task}")
    payOrder: dict = task['payOrderDetail']['payOrder']
    try:
        holdTask: HoldTask = HoldTask.from_pay_task_v2(task)
        username = task['paymentAccount']['account']
        password = task['paymentAccount']['password']
        price = task["guidePriceList"][0]["totalPrice"]

        app = AZ9Web(proxies_type=proxies_type, holdTask=holdTask, username=username, password=password,
                     totalprice=price)
        app.login(username=username, password=password)
        app.select_flight()
        app.find_flight()
        if "IgnoreFlightChange" not in payOrder.get("tags", ""):
            app.flight_check(payOrder)
        app.pre_book()
        card = {'id': task['paymentMethod']['id']}
        try:

            app.create()
            app.pay()
            pay_order_log(payOrder['apiSystemUuid'], '票号', 'Trident', f"{app.pnr} {app.webBookingId}")
            result = app.convert_hold_pay(task, card['id'])
            return code, result
        except Exception:
            traceback.print_exc()
            booking_Z9_logger.error(f"{traceback.print_exc()}")
            result = pay_error_result(payOrder, "支付异常", 203)
            return code, result

    except Exception:
        traceback.print_exc()
        booking_Z9_logger.error(f"{traceback.print_exc()}")
        result = pay_error_result(payOrder, "出票异常", 302)
        return code, result


def add_on(holdTask: HoldTask, proxies_type=0):
    result = []
    code = 0
    try:
        app = AZ9Baggage(proxies_type=proxies_type, task=holdTask)
        app.booking_availability()
        flight = app.convert_search()
        add_on_select_flight(holdTask, flight)
        app.select_flight()
        app.verify_flight()

        baggage_list = app.get_baggage_list()
        result = list(map(lambda x: AddOnResult.from_baggage(holdTask, x, 'Z9').to_dict(), baggage_list))
    except Exception:
        code = 3
        add_on_Z9_logger.error(traceback.print_exc())

    return code, result
