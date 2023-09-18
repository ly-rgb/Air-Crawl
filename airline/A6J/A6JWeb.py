import re
import traceback
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from config import config
from native.api import register_email, AutoApplyCard, can_pay, pay_order_log, get_exchange_rate_carrier
from robot import HoldTask
from utils.log import spider_6J_logger, booking_6J_logger
from utils.phone_number import random_phone
from utils.searchparser import SearchParam


class A6JWeb(AirAgentV3Development):
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

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self.cookies.set("solaseedair_language_kbn", "en")

    @property
    def base_headers(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        }
        return headers

    def search(self, searchParam: SearchParam):
        self.searchParam = searchParam

        params = (
            ('segConditionForm.selectedDepApo', searchParam.dep),
            ('segConditionForm.selectedArrApo', searchParam.arr),
            ('segConditionForm.selectedEmbYear', searchParam.date.split('-')[0]),
            ('segConditionForm.selectedEmbMonth', searchParam.date.split('-')[1]),
            ('segConditionForm.selectedEmbDay', searchParam.date.split('-')[2]),
            ('segConditionForm.searchKind', '1'),
            ('segConditionForm.nowSegIndex', '1'),
            ('segConditionForm.seatKind', 'Y'),
            ('btnSubmit:mapping=success', ''),
            ('CONNECTION_KIND', 'TOP'),
            ('paxCountConditionForm.selectedAdultCount', searchParam.adt),
            ('paxCountConditionForm.selectedChildCount', '0'),
            ('paxCountConditionForm.selectedInfantCount', '0'),
        )

        response = self.get('https://resv.solaseedair.jp/dyc/snjapp/snjbe/be/pages/reserve/vacantDispatch.xhtml',
                            headers=self.base_headers, params=params)
        self.search_response = response

    def vacant_dispatch(self):
        params = (
            ('segConditionForm.selectedDepApo', self.holdTask.origin),
            ('segConditionForm.selectedArrApo', self.holdTask.destination),
            ('segConditionForm.selectedEmbYear', str(self.holdTask.depart_date.year)),
            ('segConditionForm.selectedEmbMonth', str(self.holdTask.depart_date.month)),
            ('segConditionForm.selectedEmbDay', str(self.holdTask.depart_date.day)),
            ('segConditionForm.searchKind', '1'),
            ('segConditionForm.nowSegIndex', '1'),
            ('segConditionForm.seatKind', 'Y'),
            ('btnSubmit:mapping=success', ''),
            ('CONNECTION_KIND', 'TOP'),
            ('paxCountConditionForm.selectedAdultCount', str(len(self.holdTask.adt))),
            ('paxCountConditionForm.selectedChildCount', str(len(self.holdTask.chd))),
            ('paxCountConditionForm.selectedInfantCount', '0'),
        )
        self.cookies.set("solaseedair_language_kbn", "en")
        response = self.get('https://resv.solaseedair.jp/dyc/snjapp/snjbe/be/pages/reserve/vacantDispatch.xhtml',
                            headers=self.base_headers, params=params)
        self.search_response = response
        self.snj_app = self.search_response.url.split('/')[4]
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][vacant_dispatch] ===> response {response.status_code} {response.url}")
        self.cid = response.url[-1]
        self.convert_search()

    def convert_search(self):
        result = []
        html = self.etree.HTML(self.search_response.content)
        dvi = html.xpath('//div[@class="c-tab-body-item js-tab-body-item is-active"]')
        if not dvi:
            return result
        dvi = dvi[0]
        tbody = dvi.xpath('.//tbody')
        if not tbody:
            return result
        tbody = tbody[0]
        tr_list = tbody.xpath('./tr')
        for tr in tr_list:
            td_list = tr.xpath('./td')
            time_info = td_list[0].xpath('.//div[@class="p-vacant-seat-table-body-outbound__date"]/text()')[0]
            flight_number = td_list[0].xpath('.//div[@class="p-vacant-seat-table-body-outbound__flight"]/text()')[0]
            price_status = td_list[1].xpath('.//img[@class="p-vacant-seat-table-info__remaining-item"]/@alt')
            if price_status:
                price_status = price_status[0]
                if price_status in ["Not set", "No seats available"]:
                    continue
                seat = 10
            else:
                seat = td_list[1].xpath(
                    './/span[@class="p-vacant-seat-table-info__remaining-item p-vacant-seat-table-info__remaining-number"]/text()')[
                    0]
            price = float(
                td_list[1].xpath('.//div[@class="p-vacant-seat-table-info__price"]/text()')[0].replace(',', ''))

            currency = td_list[1].xpath('.//span[@class="p-vacant-seat-table-info__price-small"]/text()')[0]

            date = re.findall("'(.*?)'", td_list[1].xpath('@onclick')[0])[-3].split('(')[0]
            date = datetime.strptime(date, '%b. %d, %Y ').strftime('%Y-%m-%d')
            dep_time = f"{date}T{time_info.split(' - ')[0]}"
            dep_time = datetime.strptime(dep_time, "%Y-%m-%dT%H:%M")
            arr_time = f"{date}T{time_info.split(' - ')[1]}"
            arr_time = datetime.strptime(arr_time, "%Y-%m-%dT%H:%M")
            data_value = td_list[1].xpath('./@data-value')[0]
            if dep_time > arr_time:
                arr_time = arr_time + timedelta(days=1)
            flight_number = flight_number.replace('SNA', '6J').replace(' ', '')
            fromSegments = {
                "carrier": "6J",
                "flightNumber": flight_number,
                "depAirport": html.xpath('//input[@name="vacantCondInputCompDepAirport"]/@value')[0],
                "depTime": dep_time.strftime("%Y%m%d%H%M"),
                "arrAirport": html.xpath('//input[@name="vacantCondInputCompArrAirport"]/@value')[0],
                "arrTime": arr_time.strftime("%Y%m%d%H%M"),
                "codeshare": False,
                "cabin": "Y",
                "num": 0,
                "aircraftCode": "",
                "segmentType": 0
            }
            item = {
                "data": flight_number,
                "productClass": "ECONOMIC",
                "fromSegments": [fromSegments, ],
                "cur": currency,
                "adultPrice": price,
                "adultTax": 0,
                "childPrice": 0,
                "childTax": 0,
                "promoPrice": 0,
                "adultTaxType": 0,
                "childTaxType": 0,
                "priceType": 0,
                "applyType": 0,
                "max": seat,
                "limitPrice": True,
                "info": data_value
            }
            result.append(item)
            self.flights[flight_number] = item
        return result

    def flight_check(self, payOrder):
        depTime = datetime.strptime(self.flight['fromSegments'][0]['depTime'], '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M')
        if self.holdTask.departTime != depTime:
            pay_order_log(payOrder['apiSystemUuid'], '航变', 'Trident', f"old:{self.holdTask.departTime} new:{depTime}")
            raise Exception(f'{self.holdTask.orderCode} 航变 old:{self.holdTask.departTime} new:{depTime}')

    def vacant_result(self):
        html = self.etree.HTML(self.search_response.content)
        self.flight = self.flights.get(self.holdTask.flightNumber, None)
        if not self.flight:
            raise self.Exception(f"{self.holdTask.flightNumber} 未找到, 当前航班 {list(self.flights.keys())}")
        this_er = get_exchange_rate_carrier("6J", self.flight['cur'])
        this_cny_fare = self.flight['adultPrice'] * this_er
        if this_cny_fare - float(self.holdTask.targetPrice) > 5:
            raise Exception(f"涨价 curr: {this_cny_fare},old: {self.holdTask.targetPrice}")
        booking_6J_logger.info(f'[{self.holdTask.orderCode}] ===> {self.holdTask.flightNumber} '
                               f'{self.flight["adultPrice"]} {self.flight["cur"]} cny:{this_cny_fare} targetPrice:{self.holdTask.targetPrice}')

        url = f'https://resv.solaseedair.jp/dyc/{self.snj_app}/snjbe/be/pages/reserve/vacantResult.xhtml?cid={self.cid}'
        data = {
            'fromPageName': 'Result of Seat Availability ',
            'commonWithSummaryNotResponsiveForm': 'commonWithSummaryNotResponsiveForm',
            'alc.transaction.token': html.xpath('//input[@name="alc.transaction.token"]/@value')[0],
            'currentNumber': self.flight['info'],
            'selectedDateValue': html.xpath('//input[@name="selectedDateValue"]/@value')[0],
            'selectedFlightInformationFlightNumber': '',
            'selectedTab': 'vacant.result.tab.recommend',
            'javax.faces.ViewState': html.xpath('//input[@name="javax.faces.ViewState"]/@value')[0],
            'nextPageButton': 'nextPageButton',
            'fromButtonName': 'To confirmation page'
        }
        headers = self.base_headers
        headers['origin'] = 'https://resv.solaseedair.jp'
        headers['referer'] = self.search_response.url
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][vacant_result] ===> 选择航班 {self.holdTask.flightNumber} {self.flight['info']}")
        response = self.post(url, data=data, headers=self.base_headers)
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][vacant_result] ===> response {response.status_code} {response.url}")
        self.vacant_result_response = response

    def selected_flight_review(self):
        html = self.etree.HTML(self.vacant_result_response.content)
        url = f"https://resv.solaseedair.jp" + html.xpath('//form[@name="headerAreaForm"]/@action')[0]
        data = {
            'fromPageName': 'Flight Confirmation',
            'selectedFlightReviewForm': 'selectedFlightReviewForm',
            'alc.transaction.token': html.xpath('//input[@name="alc.transaction.token"]/@value')[0],
            'displayFlightInfo': html.xpath('//input[@name="displayFlightInfo"]/@value')[0],
            'javax.faces.ViewState': html.xpath('//input[@name="javax.faces.ViewState"]/@value')[0],
            'slectedFlightReviewGeneralButton': 'slectedFlightReviewGeneralButton',
            'fromButtonName': 'For general customers'
        }
        headers = self.base_headers
        headers['referer'] = f'https://resv.solaseedair.jp/dyc/{self.snj_app}/' \
                             f'snjbe/be/pages/reserve/vacantResult.xhtml?cid={self.cid}'
        response = self.post(url, data=data, headers=self.base_headers)
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][selected_flight_review] ===> response {response.status_code} {response.url}")

        self.selected_flight_review_response = response

    def reservation_pax_information_input(self):
        self.phone = "".join(random_phone(type_coed=self.holdTask.current_passengers[0].nationality, phone_len=10))
        self.email = register_email()
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}] ===> phone: {self.phone}, email: {self.email}")
        html = self.etree.HTML(self.selected_flight_review_response.content)
        url = f"https://resv.solaseedair.jp" + html.xpath('//form[@name="headerAreaForm"]/@action')[0]
        data = {
            'fromPageName': 'Enter Passenger Information',
            'reservationPaxInformationInputForm': 'reservationPaxInformationInputForm',
            'alc.transaction.token': html.xpath('//input[@name="alc.transaction.token"]/@value')[0],
            'consentConfirmFlag': 'on',
            'javax.faces.ViewState': html.xpath('//input[@name="javax.faces.ViewState"]/@value')[0],
            'reservationButton': 'reservationButton',
            'fromButtonName': 'Reserve'
        }
        index = 0
        for targetPassenger in self.holdTask.current_passengers:
            booking_6J_logger.info(
                f"[{self.holdTask.orderCode}][reservation_pax_information_input] ===> 添加乘客 {targetPassenger.to_json()} {targetPassenger.age} {targetPassenger.sex}")
            if index > 0:
                data[f'paxInfoListLoop:{index}:paxLastName2'] = targetPassenger.lastName
                data[f'paxInfoListLoop:{index}:paxFirstName2'] = targetPassenger.firstName
                data[f'paxInfoListLoop:{index}:age2'] = targetPassenger.age
                data[f'paxInfoListLoop:{index}:sexCode2'] = targetPassenger.sex
            else:
                data[f'paxInfoListLoop:{index}:paxLastName'] = targetPassenger.lastName
                data[f'paxInfoListLoop:{index}:paxFirstName'] = targetPassenger.firstName
                data[f'paxInfoListLoop:{index}:age'] = targetPassenger.age
                data[f'paxInfoListLoop:{index}:sexCode'] = targetPassenger.sex
            if index == 0:
                data[f'paxInfoListLoop:{index}:telephoneNumberKind'] = 'H'
                data[f'paxInfoListLoop:{index}:telephoneNumber'] = self.phone
                data[f'paxInfoListLoop:{index}:mailAddless'] = self.email
                data[f'paxInfoListLoop:{index}:confirmMailAddless'] = self.email
                data[f'paxInfoListLoop:{index}:mailWishFlag'] = 'on'
            index += 1
        response = self.post(url, data=data, headers=self.base_headers)
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][reservation_pax_information_input] ===> response {response.status_code} {response.url}")
        self.reservation_pax_information_input_response = response

    def reservation_detail_review(self):
        html = self.etree.HTML(self.reservation_pax_information_input_response.content)
        self.pnr = html.xpath('//div[@class="p-reservation-flight-number"]//dd/text()')[0].replace(' ', '').replace('\n', '')
        self.total_amount = float(html.xpath('//p[@class="p-booking-info-list-box-number"]/text()')[0].replace(',', '').replace(' ', ''))
        self.currency = html.xpath('//span[@class="p-booking-info-list-box-number--small"]/text()')[0].replace(',', '')
        booking_6J_logger.info(f"[{self.holdTask.orderCode}] ===> pnr: {self.pnr}, total_amount: {self.total_amount}, currency: {self.currency}")
        data = {
            'fromPageName': 'Reservation Completed',
            'reservationDetailReviewForm': 'reservationDetailReviewForm',
            'alc.transaction.token': html.xpath('//input[@name="alc.transaction.token"]/@value')[0],
            'javax.faces.ViewState': html.xpath('//input[@name="javax.faces.ViewState"]/@value')[0],
            'purchaseProcedure3columnsHead': html.xpath('//input[@name="purchaseProcedure3columnsHead"]/@value')[0],
            'fromButtonName': 'To Purchasing'
        }
        url = f"https://resv.solaseedair.jp" + html.xpath('//form[@name="headerAreaForm"]/@action')[0]
        response = self.post(url, data=data, headers=self.base_headers)
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][reservation_detail_review] ===> response {response.status_code} {response.url}")
        if 'settlementInput' not in response.url:
            raise self.Exception(f'[{self.holdTask.orderCode}][reservation_detail_review] response {response.status_code} {response.url}')
        self.reservation_detail_review_response = response

    def token_4g(self, card, year, month, cvv):
        if month < 10:
            month = f'0{month}'
        else:
            month = f'{month}'
        token_api_key = re.findall(r"token_api_key = '(.*?)'", self.reservation_detail_review_response.text)
        if not token_api_key:
            raise self.Exception(f'token_4g cant find token_api_key')
        url = 'https://api.veritrans.co.jp/4gtoken'
        headers = {
            'User-Agent': self.base_headers['user-agent'],
            'Origin': 'https://resv.solaseedair.jp',
            'Referer': 'https://resv.solaseedair.jp/'
        }
        json = {"token_api_key": token_api_key[0],
                "card_number": card,
                "card_expire": f"{str(month)}/{str(year)[-2:]}",
                "security_code": cvv,
                "lang": "en"}
        response = self.post(url, headers=headers, json=json)
        booking_6J_logger.info(
            f"[{self.holdTask.orderCode}][token_4g] ===> response {response.status_code} {response.text}")
        self.token_4g_result = response.json()

    def settlement_input(self, year, month, cvv):
        html = self.etree.HTML(self.reservation_detail_review_response.content)
        total_amount = html.xpath('//*[@id="settlementInputForm"]/div/div/dl/dd/p/span/span[2]/text()')
        if not total_amount:
            raise self.Exception(f'[{self.holdTask.orderCode}][settlement_input] 获取支付价格失败')
        self.total_amount = float(total_amount[0].replace(',', ''))
        booking_6J_logger.info(f"[{self.holdTask.orderCode}][total_amount] ===> {self.total_amount}")
        url = f"https://resv.solaseedair.jp" + html.xpath('//form[@name="headerAreaForm"]/@action')[0]
        headers = self.base_headers
        data = {
            'fromPageName': 'Fare Amount Confirmation / Select Payment Method',
            'j_idt123': 'j_idt123',
            'alc.transaction.token': html.xpath('//form[@name="headerAreaForm"]//input[@name="alc.transaction.token"]/@value')[0],
            'cvvInput': '',
            'creditCardCheck': '0',
            'creditCardNumber': '',
            'j_idt158': '',
            'expirationMonth': str(month),
            'expirationYear': str(year),
            'expirationMonth1': '',
            'expirationMonthInput': '',
            'expirationYear1': '',
            'expirationYearInput': '',
            'j_idt179': '',
            'cvv': str(cvv),
            'consentConfirmFlag': 'on',
            'vtsHttpStatus': '200',
            'vtsToken': self.token_4g_result['token'],
            'vtsTokenExpireDate': self.token_4g_result['token_expire_date'],
            'vtsReqCardNumber': self.token_4g_result['req_card_number'],
            'vtsStatus': self.token_4g_result['status'],
            'vtsCode': self.token_4g_result['code'],
            'vtsMessage': self.token_4g_result['message'],
            'javax.faces.ViewState': html.xpath('//form[@name="headerAreaForm"]//input[@name="javax.faces.ViewState"]/@value')[0],
            'executeCreditCard': 'executeCreditCard',
            'fromButtonName': 'Purchase'
        }
        response = self.post(url, headers=headers, data=data)
        self.settlement_input_response = response
        booking_6J_logger.info(f"[{self.holdTask.orderCode}][settlement_input] ===> response {response.status_code} {response.url}")
        if 'confirmNumberReview' not in self.settlement_input_response.url:
            raise self.Exception(f'[{self.holdTask.orderCode}][settlement_input] response {response.status_code} {response.url}')
        if 'p-confirm-nb-numbe' not in response.text:
            raise self.Exception(f'[{self.holdTask.orderCode}][settlement_input] response {response.status_code} \n {response.text} \n')
        html = self.etree.HTML(response.content)
        self.confirm_nb_number = html.xpath('//p[@class="p-confirm-nb-number"]/text()')[0]
        booking_6J_logger.info(f"[{self.holdTask.orderCode}][confirm-nb-number] ===> {self.confirm_nb_number}")

    def convert_hold_pay(self, task, card_id):
        payOrder: dict = task['payOrderDetail']['payOrder']
        noPayedUnitList: list = task['payOrderDetail'].get('noPayedUnitList', [])
        noPayedUnitBagList: list = task['payOrderDetail'].get('noPayedUnitBagList', [])
        payOrderInfoIds = list(map(lambda x: x['payOrderInfoIds'], noPayedUnitList))
        payBaggageIds = list(map(lambda x: x['payOrderInfoIds'], noPayedUnitBagList))
        return {
            "pnr": {
                "otaId": payOrder['otaId'],
                "payOrderUuid": payOrder['uuid'],
                "pnr": self.pnr,
                "payPrice": self.total_amount,
                "payTicketPrice": self.total_amount,
                "payBaggagePrice": 0,
                "payCurrency": self.currency,
                "payPhone": self.phone,
                "payEmail": self.email,
                "payRoute": task['paymentAccount']['account'],
                "payType": card_id,
                "client": "system_wh",
                "payOrderInfoIds": payOrderInfoIds,
                "payBaggageIds": payBaggageIds,
                "userName": "Trident",
                "cabin": "",
                "payBillCode": 1,
                "payBagCode": 1,
                "bookingId": self.confirm_nb_number
            },
            "code": 0,
            "type": 1,
            "address": config.agent,
            "taskstep": "login"
        }
