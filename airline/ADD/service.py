import traceback
from utils.log import spider_DD_logger, booking_DD_logger
from airline.ADD.ADDWeb import ADDWeb
from robot import HoldTask
from airline.base import pay_error_result
from native.api import AutoApplyCard, can_pay, pay_order_log


def api_search(taskItem, proxies_type=6):
    result = None
    code = 0

    try:
        app = ADDWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result and isinstance(result, list):
            code = -1
            spider_DD_logger.info("当天无航班")

    except Exception:
        code = -1
        spider_DD_logger.error(f"{traceback.format_exc()}")

    return code, result


def no_hold_pay(task, proxies_type=None):
    code = -1
    booking_DD_logger.info(f'最开始的任务{task}')
    payOrder: dict = task['payOrderDetail']['payOrder']
    try:
        holdTask: HoldTask = HoldTask.from_pay_task_v2(task)
        username = task['paymentAccount']['account']
        password = task['paymentAccount']['password']
        price = task['guidePriceList'][0]['totalPrice']
        app = ADDWeb(proxies_type=proxies_type, holdTask=holdTask, totalprice=price,password=password,username=username)
        app.login()
        app.select_flight()
        app.find_flight()
        if "IgnoreFlightChange" not in payOrder.get("tags", ""):
            app.flight_check(payOrder)
        app.prebook()
        app.AssessPaymentMethodFees()
        card = {'id': task['paymentMethod']['id']}
        can = can_pay(task, card)
        if not can:
            return -1, pay_error_result(payOrder, "支付取消", 302)
        try:
            app.create()
            app.pay()
            pay_order_log(payOrder['apiSystemUuid'], '票号', 'Trident', f"{app.pnr} {app.webBookingId}")
            result = app.convert_hold_pay(task, card['id'])
            return code, result
        except Exception:
            booking_DD_logger.error(traceback.format_exc())
            result = pay_error_result(payOrder, "支付异常", 203)
            return code, result
    except Exception:
        traceback.print_exc()
        booking_DD_logger.error(traceback.format_exc())
        result = pay_error_result(payOrder, "出票异常", 302)
        return code, result
