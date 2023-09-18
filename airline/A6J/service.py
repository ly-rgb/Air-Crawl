import traceback

from airline.A6J.A6JWeb import A6JWeb
from airline.base import pay_error_result
from native.api import AutoApplyCard, can_pay, pay_order_log
from robot import HoldTask
from utils.log import spider_6J_logger, booking_6J_logger


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = A6JWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_6J_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result


def no_hold_pay(task, proxies_type=None):
    code = -1
    payOrder: dict = task['payOrderDetail']['payOrder']
    try:
        holdTask: HoldTask = HoldTask.from_pay_task_v2(task)
        app = A6JWeb(proxies_type=proxies_type, holdTask=holdTask)
        app.vacant_dispatch()
        app.vacant_result()
        if "IgnoreFlightChange" not in payOrder.get("tags", ""):
            app.flight_check(payOrder)
        app.selected_flight_review()
        app.reservation_pax_information_input()
        app.reservation_detail_review()
        card = AutoApplyCard.getCardNoHold(task, '6J', app.currency, app.total_amount)
        cardexpired = card['cardexpired']
        year = int(cardexpired.split("/")[-1]) + 2000
        month = int(cardexpired.split("/")[0])
        can = can_pay(task, card)
        if not can:
            payOrder = task['payOrderDetail']['payOrder']
            result = pay_error_result(payOrder, "支付取消", 302)
            return code, result
        app.token_4g(card['paynumber'], year, month, card['CVV'])
        try:
            app.settlement_input(year, month, card['CVV'])
            pay_order_log(payOrder['apiSystemUuid'], '票号', 'Trident', f"{app.pnr} {app.confirm_nb_number}")
            result = app.convert_hold_pay(task, card['id'])
            return code, result
        except Exception:
            booking_6J_logger.error(traceback.format_exc())
            result = pay_error_result(payOrder, "支付异常", 203)
            return code, result
    except Exception:
        traceback.print_exc()
        booking_6J_logger.error(traceback.format_exc())
        result = pay_error_result(payOrder, "出票异常", 302)
        return code, result


def refund_tax(task, proxies_type=None):
    pass
    return task


def refund_full(task, proxies_type=None):
    pass
    return task


def refund_check(task, proxies_type=None):
    pass
    return task
