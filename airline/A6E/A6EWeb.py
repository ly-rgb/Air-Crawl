import re
from typing import Any, Union, Dict
from requests.models import Response

from utils.func_helper import func_retry
from utils.log import refund_6E_logger
from utils.searchparser import SearchParam
from airline.base import AirAgentV3Development


class A6EWeb(AirAgentV3Development):
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

    @func_retry(3)
    def get_session_id(self, task):
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0]["pnr"]
        email = 'nevergiveup17apr05@qq.com'
        url = 'https://book.goindigo.in/Booking/RetrieveAEM'
        headers = {
            'Origin': 'https://www.goindigo.in',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36'
        }
        data = {
            'indiGoRetrieveBooking.RecordLocator': pnr,
            'polymorphicField': email,
            'typeSelected': 'SearchByPNR',
            'indiGoRetrieveBooking.IndiGoRegisteredStrategy':
                'Nps.IndiGo.Strategies.IndiGoValidatePnrEmailStrategy, '
                'Nps.IndiGo',
            'indiGoRetrieveBooking.IsToEmailItinerary': 'false',
            'indiGoRetrieveBooking.EmailAddress': email,
            'indiGoRetrieveBooking.LastName': ''
        }
        resp = self.post(url=url, headers=headers, data=data)
        session_id = resp.cookies.get_dict()['ASP.NET_SessionId']
        return session_id

    def get_amount(self, session_id):
        url = 'https://book.goindigo.in/Booking/AddTaxRefund'
        headers = {
            'Origin': 'https://www.goindigo.in',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36'
        }
        cookies = {
            'ASP.NET_SessionId': session_id
        }
        data = {'indigoTaxRefund.taxQueueFlag': 'true'}
        refund_info = self.post(url=url, headers=headers, cookies=cookies,
                                    data=data).content.decode('utf-8')
        amount = \
            re.findall('.*?refundAmount":(.*?),"response.*?', refund_info,
                       re.S)[0]
        return amount

