from typing import Any, Union, Dict
from requests.models import Response
from utils.log import refund_VY_logger
from utils.searchparser import SearchParam
from airline.base import AirAgentV3Development


class AVYWeb(AirAgentV3Development):
    searchParam: SearchParam
    cid: str
    currency: str
    pnr: str
    snj_app: str
    total_amount: float
    confirm_nb_number: str
    settlement_input_response: Response
    token_4g_result: Dict
    reservation_detail_review_response: Response
    reservation_pax_information_input_response: Response
    email: Union[str, Any]
    phone: str
    selected_flight_review_response: Response
    vacant_result_response: Response
    flight: Dict
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)

    @property
    def base_headers(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/94.0.4606.81 Safari/537.36',
        }
        return headers

    def run_is_full(self, task):
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0][
            "pnr"]
        url = 'https://tickets.vueling.com/HomeContingencies.aspx'
        headers = {
            'referer': 'https://www.vueling.com/en',
            'sec-ch-ua-mobile': '?0'
        }
        params = {
            'email': 'nevergiveup17apr05@qq.com',
            'pnr': str(pnr),
            'event': 'change',
            'culture': 'en-GB'
        }
        resp = self.get(url=url, headers=headers, params=params)
        if 'Request a refund' in resp.text:
            refund_VY_logger.info(f"此任务为全退任务")
            task["data"]['crawlerResp'] = {'handleResult': True,
                                           'fillType': {
                                               'type': 'REFUND_MONEY',
                                               'describe': '是否全退'},
                                           'handleMsg': '此任务为全退任务',
                                           'amount': None,
                                           'isFullRefund': True,
                                           'isRetry': False}
            return task
        refund_VY_logger.info(f"此任务不可以全退")
        task["data"]['crawlerResp'] = {'handleResult': True,
                                       'fillType': {
                                           'type': 'IS_FULL_REFUND',
                                           'describe': '是否全退'},
                                       'handleMsg': '此任务不能全退',
                                       'amount': None,
                                       'isFullRefund': False,
                                       'isRetry': False}
        return task
