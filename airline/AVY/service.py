from datetime import datetime
from airline.AVY.AVYWeb import AVYWeb
from utils.func_helper import func_retry
from airline.AVY.AVYWsApp import AVYWsApp
from airline.AVY.AVYMobile import AVYMobile
from airline.base import HttpRetryMaxException
from utils.log import refund_VY_logger


def api_search():
    pass


def no_hold_pay():
    pass


def refund_tax(task):
    task_type = judge_type(task)
    if task_type == "RUN_IS_FULL_REFUND":
        try:
            result = AVYWeb(proxies_type=8, retry_count=10).run_is_full(task)
        except (HttpRetryMaxException, KeyError):
            task["data"]['crawlerResp'] = {'handleResult': False,
                                           'fillType': {
                                               'type': 'IS_FULL_REFUND',
                                               'describe': '是否全退'},
                                           'handleMsg': '已达到最大重试次数，请走人工查询',
                                           'amount': None,
                                           'isFullRefund': False,
                                           'isRetry': False}
            return task
        return result
    elif task_type[0] == "RUN_CASE_NUMBER" or task_type[0] == "REFUND_TAX":
        describe = refund_run_describe(task_type[1], task_type[2], task_type[3])
        refund_VY_logger.info(f'获取到的个案号为：{describe}')
        if not describe:
            refund_VY_logger.info(f'出入境包含西班牙城市，需走人工退票')
            task["data"]['crawlerResp'] = {'handleResult': False,
                                           'fillType': {
                                               'type': 'REFUND_MONEY',
                                               'describe': '退钱'},
                                           'handleMsg':
                                               '获取个案号失败，可能是西班牙航班，需要人工退票',
                                           'amount': None,
                                           'caseNumber': describe,
                                           'isRetry': False}
            return task

        task["data"]['crawlerResp'] = {'handleResult': True,
                                       'fillType': {
                                           'type': 'CASE_NUMBER',
                                           'describe': '回填个案号'},
                                       'handleMsg': '获取个案号成功',
                                       'amount': None,
                                       'caseNumber': describe,
                                       'isRetry': False}
        return task
    elif task_type == "FULL_REFUND" or task_type == "NO_SHOW_FULL_REFUND":
        try:
            result = AVYMobile(proxies_type=8,
                               retry_count=10).full_refund(task)
        except HttpRetryMaxException:
            task["data"]['crawlerResp'] = {'handleResult': False,
                                           'fillType': {
                                               'type': 'FULL_REFUND',
                                               'describe':
                                                   '全退'},
                                           'handleMsg':
                                               '请求重试次数已达上限，请走人工',
                                           'amount': None,
                                           'isFullRefund': False,
                                           'isRetry': False}
            refund_VY_logger.info(f'回填信息为{task}')
            return task
        if result == 'success':
            task["data"]['crawlerResp'] = {'handleResult': True,
                                           'fillType': {
                                               'type': 'FULL_REFUND',
                                               'describe':
                                                   '全退'},
                                           'handleMsg': '全退回填成功',
                                           'amount': None,
                                           'isFullRefund': True,
                                           'isRetry': False}
            refund_VY_logger.info(f'回填信息为{task}')
            return task
        else:
            task["data"]['crawlerResp'] = {'handleResult': False,
                                           'fillType': {
                                               'type': 'FULL_REFUND',
                                               'describe':
                                                   '全退'},
                                           'handleMsg': '全退回填失败,需要走人工退票',
                                           'amount': None,
                                           'isFullRefund': False,
                                           'isRetry': False}
            refund_VY_logger.info(f'回填信息为{task}')
            return task


def refund_check(task):
    pass
    return task


@func_retry(3)
def refund_run_describe(pnr, airport, date):
    app = AVYWsApp()
    app.start(timeout=10, ping_interval=60, ping_timeout=5)
    app.get_started()
    app.click_code()
    app.send_pnr(pnr)
    app.send_airport(airport)
    value_str = app.send_date(date)
    if value_str:  # 回复的消息中存在乘客号码的话，需要走另一条线路
        app.send_passenger(value_str)
        app.send_email()
        describe = app.send_phone()
        app.close()
        return describe
    app.send_email()
    describe = app.send_phone()
    app.close()
    return describe


def judge_type(task):
    if task["data"]["businessData"]["businessOperatorType"][
        "type"] == "RUN_DATA" and \
            task["data"]["businessData"]["businessOperatorType"][
                "operator"] == "RUN_IS_FULL_REFUND":
        task_type = task["data"]["businessData"]["businessOperatorType"][
            "operator"]
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0][
            "pnr"]
        refund_VY_logger.info(f"pnr: {pnr}")
        refund_VY_logger.info(f"任务类型:判断是否为全退")
        return task_type

    elif (task["data"]["businessData"]["businessOperatorType"][
              "type"] == "RUN_DATA" and
          task["data"]["businessData"]["businessOperatorType"][
              "operator"] == "RUN_CASE_NUMBER") or (
            task["data"]["businessData"]["businessOperatorType"][
                "type"] == "REFUND" and
            task["data"]["businessData"]["businessOperatorType"][
                "operator"] == "REFUND_TAX"):
        task_type = task["data"]["businessData"]["businessOperatorType"][
            "operator"]
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0][
            "pnr"]
        airport = task["data"]["payOrderBasicInfo"]["payOrder"][
            "fromFlightSegment"].split('-')[0]
        year = \
            task["data"]["payOrderBasicInfo"]["payOrder"]["depDate"].split(
                ',')[
                1][1:5]
        month = \
            task["data"]["payOrderBasicInfo"]["payOrder"]["depDate"].split(
                ' ')[
                0]
        digital_month = str(datetime.strptime(month, '%b')).split('-')[1]
        day = \
            task["data"]["payOrderBasicInfo"]["payOrder"]["depDate"].split(
                ' ')[
                1][:2]
        date_list = [year, digital_month, day]
        date = '-'.join(date_list)
        refund_VY_logger.info(f"pnr: {pnr}")
        refund_VY_logger.info(f"任务类型:退税任务")
        return task_type, pnr, airport, date

    elif task["data"]["businessData"]["businessOperatorType"][
        "type"] == "NO_SHOW_REFUND" and \
            task["data"]["businessData"]["businessOperatorType"][
                "operator"] == "NO_SHOW_FULL_REFUND":
        task_type = task["data"]["businessData"]["businessOperatorType"][
            "operator"]
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0][
            "pnr"]
        refund_VY_logger.info(f"pnr: {pnr}")
        refund_VY_logger.info(f"任务类型:全退任务")
        return task_type

    elif task["data"]["businessData"]["businessOperatorType"][
        "type"] == "REFUND" and \
            task["data"]["businessData"]["businessOperatorType"][
                "operator"] == "FULL_REFUND":
        task_type = task["data"]["businessData"]["businessOperatorType"][
            "operator"]
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0][
            "pnr"]
        refund_VY_logger.info(f"pnr: {pnr}")
        refund_VY_logger.info(f"任务类型:全退任务")
        return task_type
