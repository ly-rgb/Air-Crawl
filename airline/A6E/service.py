from datetime import datetime
from airline.A6E.A6EWeb import A6EWeb
from utils.func_helper import func_retry
from airline.base import HttpRetryMaxException
from utils.log import refund_6E_logger


def api_search():
    pass


def no_hold_pay():
    pass


def refund_tax(task):
    app = A6EWeb(proxies_type=8, retry_count=10)
    session_id = app.get_session_id(task)
    refund_6E_logger.info(f"session_id为{session_id}")
    amount = app.get_amount(session_id)
    refund_6E_logger.info(f"退款金额为{amount}")
    task["data"]['crawlerResp'] = {'handleResult': True,
                                   'fillType': {
                                       'type': 'REFUND_MONEY',
                                       'describe': '6E自愿退'},
                                   'handleMsg': '此任务为自愿退任务',
                                   'amount': amount,
                                   'isFullRefund': True,
                                   'isRetry': False}
    return task


def refund_check(task):
    pass
    return task
