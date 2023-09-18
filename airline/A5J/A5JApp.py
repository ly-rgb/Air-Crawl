import base64
import random
import re
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Any, Dict, Optional

import execjs

from airline.A5J.A5JAppOA import *
from airline.A5J.currency import currency_map
from airline.A5J.international_routes import inte_routes
from airline.baggage import Baggage
from airline.base import AirAgentV3Development, pay_error_result, convert_voucher_pay, convert_hold_pay
from config import config
from native.api import register_email, pay_order_log, get_exchange_rate_carrier, submit_shupiao, AutoApplyCard, can_pay, \
    check_pay, update_pnr_accountInfo
from native.db.weelfly_email.api import find_email_by_recv_address_and_subject
# from requests_curl import CURLAdapter
from robot.model import TargetPassenger, HoldResult, HoldTask, HoldPassenger
from utils.A5J_key import decode, encode
from utils.date_tools import get_age_by_birthday
from utils.func_helper import func_retry
from utils.log import spider_5j_logger, robot_5j_logger, check_5J_logger
from utils.phone_number import random_phone
from utils.redis import redis_53, redis_81, redis_82
from utils.searchparser import SearchParam
from urllib.parse import urlparse, parse_qs

token_cache_key = '5J_token_cache'
gender_map = {'F': 'Female',
              'M': 'Male'}
title_map = {'F': 'MS',
             'M': 'MR'}

js = '''
const getRandomValues = require('get-random-values');
const CryptoJS = require("crypto-js");
const encrypt = (word, key) => {
    let encrypted = CryptoJS.AES.encrypt(word, key);
    return encrypted.toString()
};


const decrypt = (word, key) => {
    let decrypt = CryptoJS.AES.decrypt(word, key)
    let decryptedStr = decrypt.toString(CryptoJS.enc.Utf8)
    return decryptedStr
};

function generateUniqueId() {
    let n = new Uint8Array(20);
    return getRandomValues(n),Array.from(n, generateHexaDecimal).join("")
};
function generateHexaDecimal(n) {
    return n.toString(16).padStart(2, "0")
};

function generateCode(n) {
    const e = [];
    for (let t = 48; t <= 57; ++t)
        e.push(String.fromCharCode(t));
    for (let t = 65; t <= 90; ++t)
        e.push(String.fromCharCode(t));
    for (let t = 97; t <= 122; ++t)
        e.push(String.fromCharCode(t));
    const l = [];
    for (let t = 0; t < n; t++)
        l.push(e[Math.floor(Math.random() * e.length)]);
    return l.join("")
}
'''
js_exec = execjs.compile(js)


class A5JApp(AirAgentV3Development):
    setPaymentBody: Dict[Any, Any]
    ssrs: object
    vouchernumber: str
    psp_info: dict
    voucher: dict
    _payment_data: dict
    account: dict
    __payment: Dict[Any, Any]
    __init_token: str
    __hmac: str
    __nonce: str
    holdTask: HoldTask
    holdOptions: dict
    phone_number: str
    contact_country: dict
    contact: str
    ticketPrice: float
    addOns: dict
    booking_info: dict
    email: str
    phone: str
    trip_info: dict
    flight: dict
    flights: dict
    availability_result: dict
    currencyCode: str
    has_bag: bool
    park = 'VwxG&vJSrS-3*?7z'
    lssk = "d1e41c1b-1f01-4905-aaad-454ece559c6b"
    urls = {
        'ceb_omnix_proxy': 'https://soar.cebupacificair.com/ceb-omnix_proxy'
    }
    x_auth_token: str
    ua = 'Cebu Pacific/3.23.1 (com.navitaire.nps.5j; build:8; iOS 14.5.0) Alamofire/3.23.1'

    def __init__(self, proxies_type=0, retry_count=3, timeout=120):
        super().__init__(proxies_type, retry_count, timeout, logger=robot_5j_logger)
        self.account_amount: float = 0
        self.searchParam: Optional[SearchParam] = None
        self.has_bag = False
        self.rule_sets = {}
        self.authorization = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55IjoiQ0VCVSBBaXIgSW5jLiIsIm5hbWUiOiJvbW5pWCIsInZlcnNpb24iOjEsImNvZGVWZXJzaW9uIjoiUHRFRHNWNVA1QUhMb0FoWnk3eHE1SW5XbGZOTW9WaDkifQ.rJdOfwQPOLGObQUkZOX0eEfpXmqHtAkeXNLjorQvQj4"
        # self.visitor_id = get_visitor_id()
        self.promoCode = ""
        self.x_auth_token = ""
        self.currencyCode = "PHP"
        self.expiration = None
        self.is_login = False
        self.user: Optional[str] = None
        self.is_black = False
        # self.mount('https://', CURLAdapter(verbose=0, cookie=False))

    def decrypt(self, plain_text):
        return js_exec.call("decrypt", plain_text, self.authorization)

    def encrypt(self, plain_text: str, passwd: Optional[str] = None) -> str:
        result = js_exec.call("encrypt", plain_text,
                              passwd or self.authorization + self.x_auth_token + self.park)
        if plain_text != 'accessToken':
            result = result + self.authorization + self.x_auth_token
        return result

    @property
    def unique_id(self):
        return str(uuid.uuid4())

    def get_headers(self):
        headers = {
            'authority': 'soar.cebupacificair.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en',
            'authorization': f'Bearer {self.authorization}',
            'cache-control': 'no-cache',
            'content-length': '0',
            'dnt': '1',
            'origin': 'https://www.cebupacificair.com',
            'pragma': 'no-cache',
            'referer': 'https://www.cebupacificair.com/',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'uniqueid': js_exec.call('generateCode', 10),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Content-Type': 'application/json'
        }
        if self.x_auth_token:
            headers['X-Auth-Token'] = self.x_auth_token
        return headers

    def get_body(self, data):
        body = {
            'content': self.encrypt(self.json.dumps(data, ensure_ascii=False, separators=(',', ': ')))
        }
        return body

    def cache_token(self):
        redis_53.sadd(token_cache_key, json.dumps(
            {'authorization': self.authorization, 'x_auth_token': self.x_auth_token,
             'expiration': self.expiration or int(time.time()) + 60 * 3}))

    def init(self, use_cache=False):
        if use_cache:
            cache_token = redis_53.spop(token_cache_key)
            if cache_token:
                cache_token = json.loads(cache_token)
                expiration = cache_token['expiration']
                if expiration > time.time():
                    self.expiration = expiration
                    self.authorization = cache_token['authorization']
                    self.x_auth_token = cache_token['x_auth_token']
                    return
        url = 'https://soar.cebupacificair.com/ceb-omnix_proxy'
        params = {
            'content': self.encrypt('accessToken', self.park)
        }
        headers = self.get_headers()
        # headers['uniqueId'] = js_exec.call('generateCode', 10)
        response = self.post(url, params=params, headers=headers)
        self.cookies.clear()
        if "Resource Not Found" in response.text or '429' in response.text:
            return self.init()
        try:
            data = response.json()
            self.authorization = data['Authorization']
            self.x_auth_token = data['X-Auth-Token']
        except Exception:
            raise Exception(f"[init_error][response] ==> {response.text}")

    def account_login(self, user, passwd):
        params = {
            'content': self.encrypt("account/login")
        }
        data = {"username": user, "password": passwd}
        body = self.get_body(data)
        url = 'https://soar.cebupacificair.com/ceb-omnix_proxy'
        headers = self.get_headers()
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(f"[account_login][response] ==> {response.text}")
        try:
            data = response.json()
            self.authorization = data['Authorization']
            self.x_auth_token = data['X-Auth-Token']
            redis_53.set('A5J_login_cache',
                         json.dumps({'authorization': self.authorization, 'x_auth_token': self.x_auth_token}),
                         ex=60 * 2)
            self.is_login = True
            self.user = user
        except Exception:
            raise Exception(f"[account_login][response] ==> {response.text}")

    def availability(self, searchParam: SearchParam, currencyCode=None):
        self.searchParam = searchParam
        self.currencyCode = currencyCode or currency_map.get(searchParam.dep, 'PHP')
        params = {
            'content': self.encrypt("availability")
        }
        if self.currencyCode in ['HKD']:
            ssrs = []
        else:
            ssrs = ["WAFI"]
        data = {"lffMode": False,
                "ssrs": ssrs,
                "routes": [{"origin": searchParam.dep,
                            "destination": searchParam.arr,
                            "beginDate": searchParam.date,
                            }],
                "daysToLeft": 3,
                "daysToRight": 3,
                "adultCount": searchParam.adt,
                "childCount": 0,
                "infantCount": {"lap": 0, "seat": 0},
                "promoCode": self.promoCode,
                "currency": self.currencyCode}
        body = self.get_body(data)
        url = 'https://soar.cebupacificair.com/ceb-omnix_proxy'
        headers = self.get_headers()
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(f"[availability_error][response] ==> {response.text}")
        self.availability_result = response.json()
        self.currencyCode = self.availability_result['currencyCode']

    def bookingAvailability(self, holdTask: HoldTask, ssrs, currencyCode=None):
        # if holdTask.origin in ['HKG','SEL', 'TYO', 'OSA', 'SIN', 'DXB', 'NGO', 'KUL', 'FUK', 'CAN', 'TPE']:
        #     self.ssrs = []
        # else:
        #     self.ssrs =
        self.holdTask = holdTask
        self.currencyCode = currency_map.get(holdTask.origin, 'PHP')
        if self.currencyCode in ['HKD', 'AUD']:
            ssrs = []
        self.ssrs = ssrs
        self.currencyCode = currencyCode or currency_map.get(holdTask.origin, 'PHP')
        params = {
            'content': self.encrypt("availability")
        }
        data = {"lffMode": False,
                "ssrs": self.ssrs,
                "routes": [{"origin": holdTask.origin,
                            "destination": holdTask.destination,
                            "beginDate": holdTask.departDate,
                            }],
                "daysToLeft": 5,
                "daysToRight": 1,
                "adultCount": len(holdTask.adt_with_age(12)),
                "childCount": len(holdTask.chd_with_age(12, inf_age=2)),
                "infantCount": {"lap": len(holdTask.inf_with_age(2)), "seat": 0},
                "promoCode": self.promoCode,
                "currency": self.currencyCode}
        body = self.get_body(data)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(f"[availability_error][response] ==> {response.text}")
        self.availability_result = response.json()
        self.currencyCode = self.availability_result['currencyCode']

    def convert_search(self, is_booking=False):
        # php_er = get_exchange_rate_carrier("5J", 'PHP')
        # current_er = get_exchange_rate_carrier("5J", self.currencyCode)
        self.flights = {}
        result = []

        # b2b_price_list = dict()
        # if self.currencyCode != 'PHP':
        #     b2b_price_list = b2b_lower_price_search(self.searchParam)

        def func(journey):
            data_price = None
            # if not is_booking:
            #     if self.searchParam.flight_no == self.getFlightNumberFromJourneyKey(decode(journey['journeyKey']), ignore_departTime_check=True):
            #         data_price = go_search(self.searchParam, journey['journeyKey'], use_cache=False)
            #     else:
            #         data_price = go_search(self.searchParam, journey['journeyKey'])
            #
            #     # if not data_price:
            #     #     data_price = b2b_price_list.get(decode(journey['journeyKey']), None)
            #     #     if data_price:
            #     #         data_price = data_price * php_er / current_er
            #
            #     if data_price and 0 < data_price < float(journey['fareTotal']):
            #         discount = 1 - data_price / float(journey['fareTotal'])
            #         if discount < 0.06:
            #             journey['fareClass'] = f"{journey['fareClass']}2"
            #         elif 0.06 <= discount < 0.1:
            #             journey['fareClass'] = f"{journey['fareClass']}3"
            #         elif 0.1 <= discount < 0.15:
            #             journey['fareClass'] = f"{journey['fareClass']}4"
            #         elif 0.15 <= discount < 0.20:
            #             journey['fareClass'] = f"{journey['fareClass']}5"
            #         elif 0.20 <= discount < 0.23:
            #             journey['fareClass'] = f"{journey['fareClass']}6"
            #         elif 0.23 <= discount < 0.26:
            #             journey['fareClass'] = f"{journey['fareClass']}7"
            #         elif 0.26 <= discount < 0.29:
            #             journey['fareClass'] = f"{journey['fareClass']}8"
            #         elif 0.29 <= discount < 0.32:
            #             journey['fareClass'] = f"{journey['fareClass']}9"
            #         elif 0.32 <= discount < 0.35:
            #             journey['fareClass'] = f"{journey['fareClass']}10"
            #         elif 0.35 <= discount < 0.38:
            #             journey['fareClass'] = f"{journey['fareClass']}11"
            #         elif 0.38 <= discount:
            #             journey['fareClass'] = f"{journey['fareClass']}12"
            flight_no = []
            fromSegments = []
            for segment in journey['segments']:
                flightNumber = f"{segment['identifier']['carrierCode'].strip()}{segment['identifier']['identifier'].strip()}"
                flight_no.append(flightNumber)
                fromSegments.append({
                    "carrier": segment['identifier']['carrierCode'],
                    "flightNumber": flightNumber,
                    "depAirport": segment['designator']['origin'],
                    "depTime": datetime.strptime(segment['designator']['departure'],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                    "arrAirport": segment['designator']['destination'],
                    "arrTime": datetime.strptime(segment['designator']['arrival'],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                    "codeshare": False,
                    "cabin": journey['fareClass'],
                    "num": 0,
                    "aircraftCode": "",
                    "segmentType": 0
                })
            self.flights["/".join(flight_no)] = journey

            er = redis_53.get(f'exchange_rate_5J_{self.currencyCode}')
            if not er:
                er = get_exchange_rate_carrier("5J", self.currencyCode)
                redis_53.set(f'exchange_rate_5J_{self.currencyCode}', str(er), ex=60 * 60 * 24)
            else:
                er = float(er)
            tax = 90 / er
            if tax >= float(journey['fareTotal']):
                tax = 45 / er
            adultPrice = float(journey['fareTotal']) - tax
            tax = round(tax, 2)
            adultPrice = round(adultPrice, 2)
            if data_price == -1:
                adultPrice = round(2 * data_price, 2)
            item = {
                "data": "/".join(flight_no),
                "productClass": "ECONOMIC",
                "fromSegments": fromSegments,
                "cur": self.currencyCode,
                "adultPrice": adultPrice,
                "adultTax": tax,
                "childPrice": 0,
                "childTax": 0,
                "promoPrice": 0,
                "adultTaxType": 0,
                "childTaxType": 0,
                "priceType": 0,
                "applyType": 0,
                "max": str(journey['availableCount']),
                "limitPrice": True,
                "info": f"{decode(journey['fareAvailabilityKey'])}|{decode(journey['journeyKey'])}"
            }
            result.append(item)

        for route in self.availability_result['routes']:
            ths = ThreadPoolExecutor(max_workers=10)
            list(ths.map(func, route['journeys']))
        if result and not is_booking:
            self.cache_token()
        return result

    def selectFlight(self, holdTask: HoldTask, check_class=False):
        self.flight = self.flights.get(holdTask.flightNumber, None)
        if not self.flight:
            raise Exception(f"未找到航班: {holdTask.flightNumber}, 当前航班: {self.flights}")
        if self.flight['fareClass'] != 'PD' and check_class:
            raise Exception(f"非 PD 舱, 当前: {self.flight['fareClass']}")
        er = get_exchange_rate_carrier("5J", self.currencyCode)
        cny_fare = self.flight['fareTotal'] * er
        # self.ticketPrice = self.flight['fareTotal']
        if holdTask.taskType != 'PAO_DAN' and cny_fare - float(holdTask.targetPrice) > 5:
            raise Exception(
                f"涨价 curr: {cny_fare},old: {holdTask.targetPrice}, {self.flight['fareTotal']} {self.currencyCode}")

    def use_black(self):
        return False
        if 'ignoreBlackTechnology' in self.holdTask.tags:
            return False
        if self.is_login:
            return False
        if datetime.now() + timedelta(days=60) < self.holdTask.depart_date:
            return False
        if 'PKFARE' in self.holdTask.orderCode:
            return True
        if 'BSZHL' in self.holdTask.orderCode:
            return True
        if 'CTR' in self.holdTask.orderCode:
            return True
        if 'DRCP' in self.holdTask.orderCode:
            return True
        return False

    def reset_journey_key(self, journey_key):
        pass

    def search_trip(self, journey_key, searchParam):
        self.searchParam = searchParam
        self.currencyCode = currency_map.get(searchParam.dep, 'PHP')
        if f"{self.searchParam.dep},{self.searchParam.arr}" in inte_routes:
            fare_kye = encode('0~GO~X~5J~GOGETINT~4610~~0~0~~X!0')
        else:
            fare_kye = encode('0~GO~X~5J~GOGETDOM~4610~~0~0~~X!0')
        body = {"ssrs": ["MAFI", ], "routes": [
            {"journeyKey": journey_key,
             "fareAvailabilityKey": fare_kye}],
                "adultCount": self.searchParam.adt,
                "childCount": 0,
                "infantCount": {"lap": 0, "seat": 0},
                "promoCode": "",
                "currency": self.currencyCode,
                "bundles": [
                    {"journeyKey": journey_key,
                     "bundles": []}, {"bundles": []}]}
        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("trip")
        }
        response = self.post(url, headers=headers, params=params, json=body, timeout=30)
        self.cookies.clear()
        if response.status_code >= 300:
            redis_81.set(journey_key, journey_key, ex=2 * 60 * 60)
            self.logger.error(f"{decode(journey_key)} {response.text}")
            redis_82.delete(decode(journey_key))
            return None
        self.logger.info(
            f"{decode(journey_key)} {response.json()['bookingSummary']['balanceDue'] / int(searchParam.adt)}")
        redis_82.set(decode(journey_key), str(response.json()['bookingSummary']['balanceDue'] / int(searchParam.adt)),
                     ex=60 * 60 * 4)
        return response.json()['bookingSummary']['balanceDue'] / int(searchParam.adt)

    def trip(self, holdTask, use_black=True):
        self.bookingReset()
        base_fare_key = self.flight['fareAvailabilityKey']

        """"""
        """黑科技"""
        if use_black and self.use_black():
            self.logger.info(f'[{self.holdTask.orderCode}][使用黑科技]')
            if f"{self.holdTask.origin},{self.holdTask.destination}" in inte_routes:
                fare_key = encode('0~GO~X~5J~GOGETINT~4610~~0~0~~X!0')
            else:
                fare_key = encode('0~GO~X~5J~GOGETDOM~4610~~0~0~~X!0')
            self.flight['fareAvailabilityKey'] = fare_key
            self.is_black = True

        else:
            self.is_black = False
            self.logger.info(f'[{self.holdTask.orderCode}][不满足使用黑科技条件]')

        body = {"ssrs": self.ssrs, "routes": [
            {"journeyKey": self.flight['journeyKey'],
             "fareAvailabilityKey": self.flight['fareAvailabilityKey']}],
                "adultCount": len(
                    list(filter(lambda x: (self.holdTask.depart_date - x.birthday_format()).days >= 12 * 365,
                                self.holdTask.current_passengers))),
                "childCount": len(
                    list(filter(lambda x: (self.holdTask.depart_date - x.birthday_format()).days < 12 * 365,
                                self.holdTask.current_passengers))),
                "infantCount": {"lap": 0, "seat": 0},
                "promoCode": "",
                "currency": self.currencyCode,
                "bundles": [
                    {"journeyKey": self.flight['journeyKey'],
                     "bundles": []}, {"bundles": []}],
                "isRebookEnable": False}

        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("trip")
        }
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            if self.is_black:
                self.flight['fareAvailabilityKey'] = base_fare_key
                redis_82.delete(decode(self.flight['journeyKey']))
                raise self.Exception(f'[{self.holdTask.orderCode}][低价使用失败][{response.text}]')
                # return self.trip(holdTask, use_black=False)
            raise Exception(response.text)
        self.trip_info = response.json()
        self.ticketPrice = self.trip_info['bookingSummary']['balanceDue']
        # if 'Authorization' in self.trip_info.keys():
        #     self.authorization = self.trip_info['Authorization']

    def guestdetails(self, task: HoldTask):
        targetPassengers = task.current_passengers
        if task.taskType == 'ADDON':
            self.email = f'{random.randint(1000000, 99999999)}@qq.com'
        elif self.is_login:
            self.email = register_email(["jescw.com", ])
            # pass
            # self.email = self.user
        elif self.is_black:
            name = f'{self.holdTask.current_passengers[0].firstName}{self.holdTask.current_passengers[0].birthday_format("%m%d")}'.replace(
                ' ', '').lower()
            self.email = register_email(["tazget.com", ], black=True, name=name)
        else:
            self.email = register_email(["tgbnx.com", ])
        area_code, phone = random_phone(type_coed=targetPassengers[0].nationality)
        self.phone_number = phone
        self.phone = f'{area_code}{phone}'
        self.phone = "".join(random_phone(type_coed=targetPassengers[0].nationality))
        passengers = []
        targetPassenger: TargetPassenger
        for targetPassenger, tripPassenger in zip(targetPassengers, self.trip_info['passengers']):
            passenger = {"passengerKey": tripPassenger['passengerKey'], "isInfant": False,
                         "name": {"title": title_map[targetPassenger.sex],
                                  "first": targetPassenger.firstName,
                                  "middle": "", "last": targetPassenger.lastName, "suffix": ""},
                         "info": {"gender": gender_map[targetPassenger.sex],
                                  "dateOfBirth": targetPassenger.birthday_format("%Y-%m-%d"),
                                  "nationality": targetPassenger.nationality,
                                  "residentCountry": targetPassenger.nationality}, "travelDocuments": [],
                         "ssrs": []}
            if get_age_by_birthday(targetPassenger.birthday_format(), now=task.depart_date) < 2:
                passenger['isInfant'] = True

            # if targetPassenger.baggageMessageDO:
            #     passenger['ssrs'].append({
            #         "journeyKey": self.flight['journeyKey'],
            #         "ssrCode": ""
            #     })

            passengers.append(passenger)

        body = {"passengers": passengers,
                "contacts": [{"contactTypeCode": "P",
                              "name": {"title": title_map[targetPassengers[0].sex],
                                       "first": targetPassengers[0].firstName,
                                       "middle": "",
                                       "last": targetPassengers[0].lastName,
                                       "suffix": ""},
                              "emailAddress": self.email, "address": None,
                              "phoneNumbers": [{"type": "Home", "number": f"+{self.phone}"}]}]}
        self.contact = targetPassengers[0].name
        self.contact_country = countryList[targetPassengers[0].nationality]
        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("guestdetails")
        }

        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.trip_info = response.json()
        self.addOns = response.json()['addOns']

    def cancelAddons(self, addons):
        body = {"addons": addons, "passengers": []}
        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("selladdons")
        }
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)

    def cancelInsurance(self):
        body = {"addons": "insurance", "passengers": []}
        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("selladdons")
        }
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.trip_info = response.json()

    def cancelMeal(self):
        if not self.addOns['meal']:
            return
        passengers = []
        for passenger in self.trip_info["passengers"]:
            passengers.append({
                "passengerKey": passenger['passengerKey'],
                "ssrs": [{"legKey": self.addOns['meal'][0]['legKey'], "ssrCode": ""},
                         {"legKey": self.addOns['meal'][0]['legKey'], "ssrCode": ""}, ]
            })

        body = {"addons": "meal",
                "passengers": passengers}
        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("selladdons")
        }
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.trip_info = response.json()

    def get_bag_list(self):
        er = get_exchange_rate_carrier("U2", self.currencyCode)
        bag_list = []
        for x in sorted(list(map(lambda a: a, self.addOns['baggage'][0]['ssrs'])), key=lambda a: a['ssrCode']):

            weight = int(str(x['ssrCode'].replace('BG', '')))
            price = round(x['price'] * er, 2)
            bag_list.append(Baggage(weight, price, x, x['price'], self.currencyCode))
        return bag_list

    def get_bag_code(self, weight):
        bag_info = sorted(list(map(lambda a: a['ssrCode'], self.addOns['baggage'][0]['ssrs'])))
        for x in bag_info:
            if int(x.replace("BG", "")) >= weight:
                return x
        raise Exception(f"不支持行李重量：{weight}")

    def addBaggage(self, targetPassengers):
        passengers = []
        self.has_bag = False
        for targetPassenger, tripPassenger in zip(targetPassengers, self.trip_info['passengers']):
            if targetPassenger.baggageMessageDO:
                passengerKey = tripPassenger['passengerKey']
                journeyKey = self.flight['journeyKey']
                if targetPassenger.baggageMessageDO.baggageWeight == 52:
                    passenger = {
                        "passengerKey": passengerKey,
                        "ssrs": [{
                            "journeyKey": journeyKey,
                            "ssrCode": self.get_bag_code(20)
                        },
                            {
                                "journeyKey": journeyKey,
                                "ssrCode": self.get_bag_code(32)
                            }
                        ]
                    }
                else:
                    passenger = {
                        "passengerKey": passengerKey,
                        "ssrs": [{
                            "journeyKey": journeyKey,
                            "ssrCode": self.get_bag_code(targetPassenger.baggageMessageDO.baggageWeight)
                        }]
                    }
                self.has_bag = True
                passengers.append(passenger)
        if not passengers:
            return
        body = {"addons": "baggage",
                "passengers": passengers}
        body = self.get_body(body)
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {'content': self.encrypt("selladdons")}
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.trip_info = response.json()

    def bookingCommit(self):
        body = {"holdExpiration": f"{(datetime.utcnow() + timedelta(minutes=60)).isoformat()[:23]}z"}
        body = self.get_body(body)
        params = {
            'content': self.encrypt("booking/commit")
        }
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.booking_info = response.json()
        self.authorization = self.booking_info['Authorization']
        pay_order_log(self.holdTask.orderCode, '占座成功', 'Trident',
                      f"{self.booking_info['recordLocator']} {self.email} {self.booking_info['balanceDue']} {self.booking_info['currencyCode']}")
        self.logger.info(f'[{self.holdTask.orderCode}][booking_info: {self.booking_info}]')

    def bookingReset(self):
        params = {
            'content': self.encrypt("booking/reset")
        }
        url = 'https://soar.cebupacificair.com/ceb-omnix_proxy'
        headers = self.get_headers()
        response = self.delete(url, headers=headers, params=params)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)

    def getFlightByBooking(self):
        depTime = self.trip_info['journeys'][0]["designator"]['departure']
        depTime = datetime.strptime(depTime, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M")
        segments = self.trip_info['journeys'][0]['segments']
        fn = "/".join(
            map(lambda s: f"{s['identifier']['carrierCode'].strip()}{s['identifier']['identifier'].strip()}", segments))
        return fn, depTime

    def hold_check(self, holdTask, ignore_departTime_check=True):
        fn, std = self.getFlightByBooking()
        if fn != holdTask.flightNumber:
            raise Exception(f"flightNumber error: {holdTask.flightNumber} {fn}")
        if not ignore_departTime_check:
            if std != holdTask.departTime:
                pay_order_log(holdTask.orderCode, '航变', 'Trident', f"Old:{holdTask.departTime}, Now: {std}")
                raise Exception(f'航变 Old:{holdTask.departTime}, Now: {std}')
        # for targetPassenger in holdTask.current_passengers:
        #     self.logger.info(f"[{holdTask.orderCode}] passengers {self.trip_info['passengers']}")
        #     for passenger in self.trip_info['passengers']:
        #         name = f"{passenger['name']['last']}/{passenger['name']['first']}"
        #         if targetPassenger.name == name:
        #             if gender_map[targetPassenger.sex] != passenger['info']['gender']:
        #                 raise Exception(
        #                     f"性别异常：{holdTask.orderCode} {targetPassenger.name} {gender_map[targetPassenger.sex]} {passenger['info']['gender']}")
        #
        #             dob = datetime.strptime(passenger['info']['dateOfBirth'], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d")
        #             if dob.replace('-', '') != targetPassenger.birthday.replace('-', ''):
        #                 raise Exception(f"生日异常：{holdTask.orderCode} {name} {targetPassenger.birthday} {dob}")
        #             if targetPassenger.baggageMessageDO:
        #                 if targetPassenger.baggageMessageDO.baggageWeight == 52:
        #                     ssrCode = self.get_bag_code(20)
        #                     if ssrCode not in list(map(lambda s: s['ssrCode'], passenger['ssrs'])):
        #                         raise Exception(f"行李异常：{holdTask.orderCode}, {targetPassenger.name} ")
        #                     ssrCode = self.get_bag_code(32)
        #                     if ssrCode not in list(map(lambda s: s['ssrCode'], passenger['ssrs'])):
        #                         raise Exception(f"行李异常：{holdTask.orderCode}, {targetPassenger.name} ")
        #                 else:
        #                     ssrCode = self.get_bag_code(targetPassenger.baggageMessageDO.baggageWeight)
        #                     if ssrCode not in list(map(lambda s: s['ssrCode'], passenger['ssrs'])):
        #                         raise Exception(f"行李异常：{holdTask.orderCode}, {targetPassenger.name} ")
        #             break
        #     else:
        #         raise Exception(f"乘客异常：{holdTask.orderCode} {targetPassenger.name} not found")

    def convert_booking(self, task: HoldTask):
        if self.has_bag:
            baggagePrice = self.booking_info['balanceDue'] - self.ticketPrice
        else:
            baggagePrice = 0

        holdPassengers = []
        for targetPassenger in task.targetPassengers:
            hp = HoldPassenger(passengerName=targetPassenger.name,
                               passengerNo=targetPassenger.certificateInformation)
            holdPassengers.append(hp)
        return HoldResult(orderUuid=task.orderCode.split('_')[0],
                          depCity=task.origin,
                          arrCity=task.destination,
                          flightNumber=task.flightNumber,
                          depTime=datetime.strptime(task.departTime, "%Y-%m-%d %H:%M").strftime(
                              "%b %d, %Y %I:%M:%S %p"),
                          pnr=self.booking_info['recordLocator'],
                          totalPrice=self.booking_info['balanceDue'],
                          ticketPrice=self.booking_info['balanceDue'] - baggagePrice,
                          baggagePrice=baggagePrice,
                          currency=self.currencyCode,
                          expirationTime=(datetime.now() + timedelta(minutes=15)).strftime("%b %d, %Y %I:%M:%S %p"),
                          holdAccount=self.email,
                          imageUrl="",
                          machineAddress=config.agent,
                          statusCode=0,
                          tripType=1,
                          type=2,
                          holdRoute="VCC",
                          holdEmail=self.email,
                          cabin=self.flight['fareClass'],
                          passengerList=holdPassengers,
                          contactMobile=self.phone,
                          holdTime=datetime.now().strftime("%b %d, %Y %I:%M:%S %p"),
                          contact=self.contact)

    def routes(self):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("routes")
        }
        response = self.get(url, headers=headers, params=params)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        return response.json()

    def bookings(self):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("bookings")
        }
        body = {'recordLocator': 'JL9EVX',
                'lastName': 'JIANG'}
        body = self.get_body(body)

        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)

    def accounts(self, email=None):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        if self.is_login:
            params = {
                'content': self.encrypt(f"accounts/{self.user}")
            }
        else:
            params = {
                'content': self.encrypt(f"accounts/{email or self.email}")
            }
        response = self.get(url, headers=headers, params=params)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.account: dict = response.json()
        return self.account

    def loadBusinessRules(self, code):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt(f'bre/{code}')
        }
        response = self.get(url, headers=headers, params=params)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        result = response.json()
        for rule_set in result['ruleSets']:
            rules = {}
            for rule in rule_set['rules']:
                rules[rule['code']] = rule
            self.rule_sets[rule_set['code']] = rules

    def account_register(self):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt('account/register')
        }
        title = {
            'MR': 'Mr.',
            'MS': 'Ms.'
        }
        contact = self.booking_info['contacts'][0]
        body = {"profile": {"title": title[contact['name']['title']],
                            "firstName": contact['name']['first'],
                            "lastName": contact['name']['last'],
                            "NofName": False,
                            "email": self.email,
                            "login": self.email,
                            "primaryPhone": f"(+{self.phone[:2]}){self.phone_number}",
                            "AlternatePhoneNo": "",
                            "ContactFname": contact['name']['first'],
                            "ContactLname": contact['name']['last'],
                            "ContactTitle": title[contact['name']['title']],
                            "AccompanyingAdult": None,
                            "PWDID": "",
                            "anonymous": True}}
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if 'already exists' in response.text:
            return
        if response.status_code >= 300:
            raise Exception(response.text)

    def account_real_register(self, firstName, lastName, email):

        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt('account/register')
        }
        body = {
            "profile": {
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "login": email,
                "NofName": False
            }
        }
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        print('account/register', (firstName, lastName, email), response.text)
        if 'already exists' in response.text:
            account = self.accounts(email)
        else:
            if response.status_code >= 300:
                raise Exception(response.text)
            account = response.json()

        params = {
            'content': self.encrypt(f'account/activation/{account["id"]}')
        }

        response = self.post(url, headers=headers, params=params)
        self.cookies.clear()
        print('account/activation', (firstName, lastName, email), response.text)
        if 'is already active' in response.text:
            return
        if response.status_code >= 300:
            raise Exception(response.text)

    def create_profile(self):
        headers = self.get_headers()
        headers['scope'] = 'omnix'
        profile = self.account['profile']
        profile['status'] = self.account['status']

        if self.is_login:
            profile['anonymous'] = False
            body = {"profile": profile}
        else:
            profile['anonymous'] = True
            body = {"profile": profile}
        url = 'https://soar.cebupacificair.com/ceb-omnix_proxy'
        params = {'content': self.encrypt(f"bre/{self.authorization}")}
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        print(response.text)

    def getRule(self, key_1, key_2):
        return self.rule_sets[key_1][key_2]['parameters']

    def getHoldOptions(self):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt('holdOptions')
        }
        response = self.get(url, headers=headers, params=params)
        self.cookies.clear()
        result = response.json()
        if response.status_code >= 300:
            raise Exception(response.text)
        self.holdOptions = result

    def __getTotalPricePerPassenger(self):
        ret = []
        contact = self.trip_info['contacts'][0]
        for journey in self.trip_info['bookingSummary']['journeys']:
            for passenger in journey['passengers']:
                name = passenger['name']
                ret.append({
                    'title': name['title'],
                    'first_name': name['first'],
                    'last_name': name['last'],
                    'contact_info': {
                        'email': contact['emailAddress'],
                        'mobile': {
                            'country_id': self.contact_country['cpdCountryId'],
                            'text': self.phone_number
                        },
                        'type': passenger['passengerTypeCode'],
                        'amount': float(passenger['totalAmount'])
                    }
                })
        return ret

    @staticmethod
    def __getOriginStationDetails(origin, destination, carrierCode):
        t = origin
        if "MNL" == origin:
            t = f"MNL_{carrierCode}"
        if "CEB" == origin:
            if originStationIsInternational[f'{origin}-{destination}']:
                t = 'CEB_INTERNATIONAL'
            else:
                t = 'CEB_DOMESTIC'
        return stationDetailsList[t]['details']

    @staticmethod
    def __getDestinationStationDetails(origin, destination, carrierCode):
        t = destination
        if 'MNL' == destination:
            t = f"MNL_{carrierCode}"
        if 'CEB' == destination:
            if destinationStationIsInternational[origin]:
                t = 'CEB_INTERNATIONAL'
            else:
                t = 'CEB_DOMESTIC'
        return stationDetailsList[t]['details']

    def __create_trips(self):
        ret = []
        journeys: list = self.trip_info['bookingSummary']['journeys']
        for journey in journeys:
            segments: list = journey['segments']
            for segment in segments:
                origin_iata = iataList[segment['designator']['origin']]
                destination_iata = iataList[segment['designator']['destination']]
                designator = segment['designator']
                osd = self.__getOriginStationDetails(designator['origin'], designator['destination'],
                                                     segment['identifier']['carrierCode'])
                dsd = self.__getDestinationStationDetails(designator['origin'], designator['destination'],
                                                          segment['identifier']['carrierCode'])
                ret.append({
                    'tag': str(journeys.index(journey) + 1),
                    'seq': str(segments.index(segment) + 1),
                    'origin': {
                        'country_id': origin_iata['cpdCountryId'],
                        'external_id': designator['origin'],
                        'text': osd['name'],
                        'time_zone': designator['departureTimeZone']
                    },
                    'destination': {
                        'country_id': destination_iata['cpdCountryId'],
                        'external_id': designator['destination'],
                        'text': dsd['name'],
                        'time_zone': designator['arrivalTimeZone']
                    },
                    'departure_time': segment['designator']['departureTimeUtc'],
                    'arrival_time': segment['designator']['arrivalTimeUtc'],
                    'booking_class': self.flight['fareClass'],
                    'service_level': 'Economy',
                    'transportation': {
                        'code': segment['identifier']['carrierCode'],
                        'id': '1',
                        'carriers': {
                            'carrier': [{
                                'type_id': '1',
                                'code': segment['identifier']['carrierCode'],
                                'number': segment['identifier']['identifier']
                            }]
                        }
                    }
                })
        return ret

    def __create_orderdata(self):
        description = f"{self.booking_info['journeys'][0]['designator']['origin']}-{self.booking_info['journeys'][0]['designator']['destination']}"

        trip = self.__create_trips()

        return {
            "order": {
                "line_items": {
                    "line_item": [{
                        "product": {
                            "sku": "product-ticket",
                            "name": "ONE WAY",
                            "description": description,
                            "airline_data": {
                                "profiles": {
                                    "profile": self.__getTotalPricePerPassenger()},
                                "trips": {
                                    "trip": trip}}},
                        "amount": str(self.booking_info['balanceDue']),
                        "quantity": "1",
                        "additional_data": {
                            "param": [{"name": "deviceFingerPrint",
                                       "text": self.authorization}]}}]}}}

    def __create_additionaldata(self, iata):
        return {
            'additional_data': {
                'param': [{
                    'name': 'session_token',
                    'text': self.authorization
                }, {
                    'name': 'hold_fee_amount',
                    'text': self.booking_info['holdFeeTotalAmount'],
                }, {
                    'name': 'hold_fee_currency_code',
                    'text': iata['cpdCurrencyId']
                }, {
                    'name': 'hold_period',
                    'text': self.holdOptions['PAYMENT_CENTER']
                }, {"name": "stepper",
                    "text": "1"}]
            }
        }

    @staticmethod
    def pay_request_headers(origin='https://www.cebupacificair.com',
                            referer='https://www.cebupacificair.com/',
                            content_type='application/x-www-form-urlencoded'):
        return {
            'content-type': content_type,
            'origin': origin,
            'referer': referer,
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }

    def cpd_hpp(self):
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        params = {
            'content': self.encrypt("cpd/hpp")
        }
        journeys = self.trip_info['bookingSummary']['journeys']
        iata = iataList[journeys[0]['designator']['origin']]
        body = {
            "account": default_rule['ACCOUNT'],
            "txnType": "1",
            "stepper": "1"
        }
        body = self.get_body(body)

        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        html = self.etree.HTML(response.text)
        data = {}
        for _input in html.xpath('//input'):
            data[_input.xpath("./@name")[0]] = _input.xpath("./@value")
        self.setPaymentBody = data
        print(response.text)

    def setPayment(self):
        # journeys = self.trip_info['bookingSummary']['journeys']
        # iata = iataList[journeys[0]['designator']['origin']]
        # nonce = f'{int(time.time() * 1000)}'
        self.__nonce = self.setPaymentBody['nonce'][0]
        # if '.' not in str(self.booking_info['balanceDue']):
        # if self.booking_info['currencyCode'] == 'KRW' or self.booking_info['currencyCode'] == 'JPY':
        #     _balanceDue = self.booking_info['balanceDue']
        # else:
        #     _balanceDue = self.booking_info['balanceDue'] * 100
        # # _balanceDue = self.booking_info['balanceDue']
        # hmac = sha512(f"{default_rule['CLIENT_ID']}"
        #               f"{self.booking_info['recordLocator']}"
        #               f"{str(round(_balanceDue))}"
        #               f"{str(iata['cpdCountryId'])}"
        #               f"{self.phone_number}"
        #               f"{self.contact_country['cpdCountryId']}"
        #               f"{self.email}"
        #               f"{default_rule['SK']}")
        self.__hmac = self.setPaymentBody['hmac'][0]
        # "10077cebuairRwSy$a7q6h1648452576335https://soar.cebupacificair.com/ceb-omnix/redirect-uri/z2Ume7h1mER9dSQCiVSdW6lPXM0C"
        # init_token = sha512(f"{default_rule['CLIENT_ID']}"
        #                     f"{default_rule['ITU']}"
        #                     f"{default_rule['ITP']}"
        #                     f"{nonce}"
        #                     f"https://soar.cebupacificair.com/ceb-omnix/redirect-uri/{self.authorization}")
        self.__init_token = self.setPaymentBody['init-token'][0]
        headers = self.pay_request_headers()
        data = self.setPaymentBody
        response = self.post('https://pop.cellpointdigital.net/views/web.php', headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(f'{self.holdTask.orderCode} setPayment {response.status_code} data: {data}')
        re.findall(r'sessionStorage.setItem\((.*)\)\n', response.text)
        self.__payment = {}
        for x in re.findall(r'sessionStorage.setItem\((.*)\)\n', response.text):
            if x:
                k = re.findall("'(.*)', '", x)[0]
                v: str = re.findall("', '(.*)'", x)[0]
                self.__payment[k] = v.replace(r'\/', '/')
        self.logger.info(f'[{self.holdTask.orderCode}][__payment][{self.__payment}]')

    def initialize(self):
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        headers['token'] = self.__payment['inittoken']
        headers['nonce'] = self.__payment['nonce']

        body = {"country": int(self.__payment['country']),
                "mobilecountry": int(self.__payment['mobilecountry']),
                "clientid": self.__payment['clientid'],
                "account": self.__payment['account'],
                "language": self.__payment['language'],
                "orderid": self.__payment['orderid'],
                "mobile": int(self.__payment['mobile']),
                "operator": int(self.__payment['operator']),
                "email": self.__payment['email'],
                "customerref": self.__payment['customerref'],
                "accounts": "",
                "markup": self.__payment['markup'],
                "amount": self.__payment['amount'],
                "fees": self.__payment['fees'],
                "accepturl": self.__payment['accepturl'],
                "cancelurl": self.__payment['cancelurl'],
                "callbackurl": self.__payment['callbackurl'],
                "orderdata": self.__payment['orderdata'],
                "sessionid": self.__payment['sessionid'],
                "currency": int(self.__payment['currency-code']),
                "authtoken": self.__payment['authtoken'],
                "deviceid": "",
                "hmac": self.__payment['hmac'],
                "additionaldata": self.__payment['additionaldata'],
                "initToken": self.__payment['inittoken'],
                "iframe": False,
                "nonce": self.__payment['nonce'],
                "txntype": self.__payment['txntype'],
                "locale": self.__payment['locale'],
                "hppAppVersion": '2.0.0',
                "logourl": self.__payment['logourl'],
                "cssurl": self.__payment['cssurl'],
                "assetsurl": self.__payment['assetsurl'],
                "profileid": self.__payment['profileid'],
                "gtmdata": None,
                "gtmid": self.__payment['gtm-id'],
                "responsecontenttype": self.__payment['responsecontenttype']}
        response = self.post('https://pop.cellpointdigital.net/api/initialize', headers=headers, json=body)
        if response.status_code != 200 or 'transaction' not in response.text:
            raise Exception(f'{self.holdTask.orderCode} initialize response {response.status_code} {response.text}')
        self._payment_data: dict = response.json()
        if self.is_login:
            fund_balance = self._payment_data['fund_balances']['fund_balance']
            if not fund_balance:
                raise self.Exception(f'[{self.holdTask.orderCode}][获取余额失败][{self._payment_data}]')
            fund_balance = fund_balance[0]['response']
            if fund_balance['status']['text'] != 'Success':
                raise self.Exception(f'[{self.holdTask.orderCode}][获取余额失败][{self._payment_data}]')
            balance = fund_balance['balance']
            amount = float(balance['amount'])
            self.account_amount = amount
            pay_order_log(self.holdTask.orderCode, '账户信息', 'Trident',
                          f"{self.user} 余额：{amount} {balance['currency']} 到期时间：{balance['expiration']}")
            # if self.booking_info['balanceDue'] > amount:
            #     raise self.Exception(f'[{self.holdTask.orderCode}][余额不足， 票价：{self.booking_info["balanceDue"]} {self.booking_info["currencyCode"]} 余额：{amount} {balance["currency"]}]')

    def voucherbalance(self, vouchernumber):
        self.logger.info(f'[{self.holdTask.orderCode}] 查询代金劵 {vouchernumber}')
        self.vouchernumber: str = vouchernumber
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        body = {"country": str(self.__payment['country']),
                "clientid": str(self.__payment['clientid']),
                "mobilecountry": str(self.__payment['mobilecountry']),
                "account": str(self.__payment['account']),
                "orderid": self.booking_info['recordLocator'],
                "mobile": self.phone_number,
                "operator": str(self.__payment['operator']),
                "email": self.email,
                "language": self.__payment['language'],
                "customerref": self.__payment['customerref'],
                "accounts": "",
                "markup": self.__payment['markup'],
                "amount": self.__payment['amount'],
                "transaction": self._payment_data['transaction']['id'],
                "currency": self.__payment['currency-code'],
                "additionaldata": self.__payment['additionaldata'],
                "vouchernumber": vouchernumber}
        response = self.post('https://pop.cellpointdigital.net/api/voucherbalance', headers=headers, json=body)
        if response.status_code != 200 and 'balance' not in response.json().keys():
            raise Exception(
                f'{self.holdTask.orderCode} voucherbalance status_code:{response.status_code} response:{response.text}')
        self.logger.info(
            f'{self.holdTask.orderCode} voucherbalance status_code:{response.status_code} response:{response.text}')
        self.voucher: dict = response.json()['balance']
        self.logger.info(f'[{self.holdTask.orderCode}] {vouchernumber} {self.voucher}')

    def fxlookup(self, cardNumber):
        this_card = card['Master Card']
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        body = {
            "country": str(self.__payment['country']),
            "clientid": str(self.__payment['clientid']),
            "mobilecountry": str(self.__payment['mobilecountry']),
            "account": str(self.__payment['account']),
            "orderid": self.booking_info['recordLocator'],
            "mobile": self.phone_number,
            "operator": str(self.__payment['operator']),
            "email": self.__payment['email'],
            "language": self.__payment['language'],
            "customerref": self.__payment['customerref'],
            "accounts": "",
            "markup": self.__payment['markup'],
            "amount": self.__payment['amount'],
            "transaction": self._payment_data['transaction']['id'],
            "currency": self.booking_info['currencyCode'],
            "cardNumber": cardNumber,
            "cardtypeid": str(this_card['id'])
        }
        response = self.post('https://pop.cellpointdigital.net/api/fxlookup', headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(
                f'{self.holdTask.orderCode} fxlookup status_code:{response.status_code} response:{response.text}')

    def pay(self, card_number):
        if card_number[0] == '5':
            this_card = card['Master Card']
        elif card_number[0] == '4':
            this_card = card['VISA']
        else:
            raise Exception(f'{self.holdTask.orderCode} 不支持卡类型 {card_number} ')
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        body = {
            'hppAppVersion': '2.0.0',
            'country': int(self.__payment['country']),
            'clientid': str(self.__payment['clientid']),
            'mobilecountry': int(self.__payment['mobilecountry']),
            'account': str(self.__payment['account']),
            'mobile': int(self.__payment['mobile']),
            'operator': int(self.__payment['operator']),
            'email': self.__payment['email'],
            'language': self.__payment['language'],
            'customerref': self.__payment['customerref'],
            'markup': self.__payment['markup'],
            'cardid': int(this_card['id']),
            'transaction': self._payment_data['transaction']['id'],
            'storecard': 'false',
            'paymenttype': int(this_card['payment_type']),
            'billingaddress': {
                'fullname': f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
                'email': "",
                'address1': 'beiijng',
                'address2': '',
                'street': 'beiijng',
                'countryid': 609,
                'city': 'beiijng',
                'state': '',
                'postalcode': '100000',
                'mobilecontrycode': 640,
                'mobilenumber': self.phone_number,
                'cardholderemail': self.email,
                'firstName': self.holdTask.current_passengers[0].firstName,
                'lastName': self.holdTask.current_passengers[0].lastName,
            },
            'issuerIdentification': int(str(card_number)[:6]),
            'token': '',
            'profileid': self.__payment['authtoken'],
            'authtoken': self.__payment['authtoken'],
            'fxservicetypeid': '12',
            'amount': self.__payment['amount'],
            'currency': int(self.__payment['currency-code']),
            'hmac': self.__payment['hmac']
        }
        self.logger.info(f'[{self.holdTask.orderCode}][body][{body}]')
        response = self.post('https://pop.cellpointdigital.net/api/pay', headers=headers, json=body)
        self.logger.info(f'[{self.holdTask.orderCode}][response][{response.text}]')
        if response.status_code != 200 and 'psp_info' not in response.text:
            raise Exception(
                f'{self.holdTask.orderCode} pay status_code:{response.status_code} response:{response.text}')
        self.psp_info: dict = response.json()['psp_info']

    def check_voucher(self):
        return round(float(self.voucher['amount']) * 100) >= int(self.__payment['amount'])

    def card_authorize(self, card_number, expiry, cvc):
        if card_number[0] == '5':
            this_card = card['Master Card']
        elif card_number[0] == '4':
            this_card = card['VISA']
        else:
            raise Exception(f'{self.holdTask.orderCode} 不支持卡类型 {card_number} ')
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        if self.is_black:
            billingaddress = {
                "fullname": f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
                "email": "",
                "address1": "Manila",
                "address2": "",
                "street": f"{random.randint(1000, 9999)} Liwasang Bonifacio",
                "countryid": 609,
                "city": "Manila",
                "state": "",
                "postalcode": "1000",
                "mobilecontrycode": int(self.__payment['mobilecountry']),
                "mobilenumber": int(self.__payment['mobile']),
                "cardholderemail": self.__payment['email'],
                "firstName": self.holdTask.current_passengers[0].firstName,
                "lastName": self.holdTask.current_passengers[0].lastName}
        else:
            billingaddress = {
                "fullname": f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
                "email": "",
                "address1": "beijing",
                "address2": "",
                "street": f"beijing",
                "countryid": 609,
                "city": "Manila",
                "state": "",
                "postalcode": "10000",
                "mobilecontrycode": int(self.__payment['mobilecountry']),
                "mobilenumber": int(self.__payment['mobile']),
                "cardholderemail": self.__payment['email'],
                "firstName": self.holdTask.current_passengers[0].firstName,
                "lastName": self.holdTask.current_passengers[0].lastName}

        body = {
            "account": str(self.__payment['account']),
            "accountconfirmpassword": "",
            "accountpassword": "",
            "accouontname": "",
            "additionaldata": [{"name": "cfx_status_code", "text": "103"}],
            "amount": str(int(self.__payment['amount'])),
            "authtoken": self.__payment['authtoken'],
            "billingaddress": billingaddress,
            "cardid": "",
            "cardname": f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
            "cardtypeid": int(this_card['id']),
            "checkouturl": "",
            "clientid": str(self.__payment['clientid']),
            "country": int(self.__payment['country']),
            "currency": int(self.__payment['currency-code']),
            "customerref": self.__payment['customerref'],
            "decktoken": base64.b64encode(card_number.encode()).decode(),
            "email": self.__payment['email'],
            "euaid": "-1",
            "externalCall": "true",
            "hmac": self.__payment['hmac'],
            "hppAppVersion": "2.0.0",
            "language": self.__payment['language'],
            "markup": self.__payment['markup'],
            "mobile": int(self.__payment['mobile']),
            "mobilecountry": int(self.__payment['mobilecountry']),
            "mvault": "false",
            "network": "",
            "operator": int(self.__payment['operator']),
            "paymenttype": False,
            "preferred": False,
            "profileid": self.__payment['authtoken'],
            "storecard": "false",
            "termination": base64.b64encode(expiry.encode()).decode(),
            "token": "",
            "transaction": self._payment_data['transaction']['id'],
            "typeid": self.psp_info['hidden_fields']['transaction_type'],
            "validfrom": "",
            "verificationcode": base64.b64encode(str(cvc).encode()).decode(),
            "verifier": ""
        }
        self.logger.info(f'[{self.holdTask.orderCode}][body][{body}]')
        response = self.post('https://pop.cellpointdigital.net/api/authorize', headers=headers, json=body,
                             allow_redirects=False, timeout=120)
        self.logger.info(f'[{self.holdTask.orderCode}][response][{response.text}]')
        if response.status_code != 200:
            raise Exception(
                f'{self.holdTask.orderCode} pay status_code:{response.status_code} response:{response.text}')

        if '2005' in response.text:
            self._3DS(response.text)
            return
        if 'Payment authorized' not in response.text:
            raise Exception(
                f'{self.holdTask.orderCode} pay status_code:{response.status_code} response:{response.text}')

    def _3DS(self, body):
        html = self.etree.HTML(body)
        url = html.xpath('//form/@action')[0]
        inputs = html.xpath('//input')
        data = {}
        for _input in inputs:
            data[_input.xpath('./@name')[0]] = _input.xpath('./@value')
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'}
        response = self.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(
                f'{self.holdTask.orderCode} status_code:{response.status_code} 银行验证第一步失败')

        html = self.etree.HTML(response.text)
        url = html.xpath('//form/@action')[0]
        inputs = html.xpath('//input')
        data = {}
        for _input in inputs:
            data[_input.xpath('./@name')[0]] = _input.xpath('./@value')
        response = self.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(
                f'{self.holdTask.orderCode} status_code:{response.status_code} 银行验证第二步失败')

    def voucher_authorize(self, card_number: str = "", expiry: str = "", cvc: str = ""):
        if card_number[0] == '5':
            this_card = card['Master Card']
        elif card_number[0] == '4':
            this_card = card['VISA']
        else:
            raise Exception(f'{self.holdTask.orderCode} 不支持卡类型 {card_number} ')
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        if self.check_voucher():
            body = {"account": str(self.__payment['account']),
                    "accountconfirmpassword": "",
                    "accountpassword": "",
                    "accouontname": "",
                    "additionaldata": {"param": [{"name": "session_token", "text": self.authorization}]},
                    "amount": self.__payment['amount'],
                    "authtoken": self.__payment['authtoken'],
                    "billingaddress": "",
                    "cardid": "",
                    "cardname": "",
                    "cardtypeid": "",
                    "checkouturl": "",
                    "clientid": str(self.__payment['clientid']),
                    "country": int(self.__payment['country']),
                    "currency": int(self.__payment['currency-code']),
                    "customerref": self.__payment['customerref'],
                    "decktoken": "",
                    "email": self.__payment['email'],
                    "euaid": "-1",
                    "externalCall": "true",
                    "hmac": self.__payment['hmac'],
                    "hppAppVersion": "2.0.0",
                    "language": self.__payment['language'],
                    "markup": self.__payment['markup'],
                    "mobile": int(self.__payment['mobile']),
                    "mobilecountry": int(self.__payment['mobilecountry']),
                    "mvault": "false",
                    "network": "",
                    "operator": int(self.__payment['operator']),
                    "paymenttype": "",
                    "profileid": self.__payment['authtoken'],
                    "storecard": "false",
                    "termination": "",
                    "token": "",
                    "transaction": self._payment_data['transaction']['id'],
                    "typeid": str(this_card['id']),
                    "validfrom": "",
                    "verificationcode": "",
                    "verifier": "",
                    "voucheramount": self.__payment['amount']}
        else:
            body = {
                "cardname": f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
                "decktoken": base64.b64encode(card_number.encode()).decode(),
                "termination": base64.b64encode(expiry.encode()).decode(),
                "validfrom": "",
                "verificationcode": base64.b64encode(str(cvc).encode()).decode(),
                "cardtypeid": int(this_card['id']),
                "paymenttype": False,
                "token": "",
                "network": "",
                "storecard": "false",
                "accountconfirmpassword": "",
                "accountpassword": "",
                "accouontname": "",
                "typeid": self.psp_info['hidden_fields']['transaction_type'],
                "preferred": False,
                "issplitpayment": True,
                "voucheramount": round(float(self.voucher['amount']) * 100),
                "additionaldata": [{"name": "cfx_status_code", "text": "103"}],
                "amount": str(int(self.__payment['amount']) - round(float(self.voucher['amount']) * 100)),
                "currency": int(self.__payment['currency-code']),
                "hmac": self.__payment['hmac'],
                "vouchernumber": self.vouchernumber,
                "country": int(self.__payment['country']),
                "clientid": str(self.__payment['clientid']),
                "mobilecountry": int(self.__payment['mobilecountry']),
                "account": str(self.__payment['account']),
                "mobile": int(self.__payment['mobile']),
                "operator": int(self.__payment['operator']),
                "email": self.__payment['email'],
                "language": self.__payment['language'],
                "customerref": self.__payment['customerref'],
                "markup": self.__payment['markup'],
                "profileid": self.__payment['authtoken'],
                "transaction": self._payment_data['transaction']['id'],
                "authtoken": self.__payment['authtoken'],
                "billingaddress": {
                    "fullname": f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
                    "email": "",
                    "address1": "beiijng",
                    "address2": "",
                    "street": "beiijng ",
                    "countryid": 609,
                    "city": "beiijng",
                    "state": "",
                    "postalcode": "10000",
                    "mobilecontrycode": int(self.__payment['mobilecountry']),
                    "mobilenumber": int(self.__payment['mobile']),
                    "cardholderemail": self.__payment['email'],
                    "firstName": self.holdTask.current_passengers[0].firstName,
                    "lastName": self.holdTask.current_passengers[0].lastName},
                "cardid": "",
                "checkouturl": "",
                "euaid": "-1",
                "mvault": "false",
                "verifier": "",
                "externalCall": "true",
                "hppAppVersion": "2.0.0"}
        self.logger.info(f'[{self.holdTask.orderCode}][body][{body}]')
        response = self.post('https://pop.cellpointdigital.net/api/authorize', headers=headers, json=body)
        self.cookies.clear()
        self.logger.info(f'[{self.holdTask.orderCode}][response][{response.text}]')
        if response.status_code != 200 and 'Payment authorized' not in response.text:
            raise Exception(
                f'{self.holdTask.orderCode} pay status_code:{response.status_code} response:{response.text}')

    def account_authorize(self, card_number: str = "", expiry: str = "", cvc: str = ""):
        if card_number[0] == '5':
            this_card = card['Master Card']
        elif card_number[0] == '4':
            this_card = card['VISA']
        else:
            raise Exception(f'{self.holdTask.orderCode} 不支持卡类型 {card_number} ')
        headers = self.pay_request_headers(origin='https://pop.cellpointdigital.net',
                                           referer='https://pop.cellpointdigital.net/',
                                           content_type='application/json')
        if self.booking_info['balanceDue'] > self.account_amount:
            body = {"account": str(self.__payment['account']),
                    "accountconfirmpassword": "",
                    "accountpassword": "",
                    "accouontname": "",
                    "additionaldata": {"param": [{"name": "session_token", "text": self.authorization}]},
                    "amount": str(int(self.__payment['amount']) - round(self.account_amount * 100)),
                    "authtoken": self.__payment['authtoken'],
                    "billingaddress": {
                        'fullname': f'{self.holdTask.current_passengers[0].firstName} {self.holdTask.current_passengers[0].lastName}',
                        'email': "",
                        'address1': 'beiijng',
                        'address2': '',
                        'street': 'beiijng',
                        'countryid': 609,
                        'city': 'beiijng',
                        'state': '',
                        'postalcode': '100000',
                        'mobilecontrycode': 640,
                        'mobilenumber': self.phone_number,
                        'cardholderemail': self.email,
                        'firstName': self.holdTask.current_passengers[0].firstName,
                        'lastName': self.holdTask.current_passengers[0].lastName,
                    },
                    "cardid": "",
                    "cardname": "",
                    "cardtypeid": str(this_card['id']),
                    "checkouturl": "",
                    "clientid": str(self.__payment['clientid']),
                    "country": int(self.__payment['country']),
                    "currency": int(self.__payment['currency-code']),
                    "customerref": self.__payment['customerref'],
                    "decktoken": base64.b64encode(card_number.encode()).decode(),
                    "email": self.__payment['email'],
                    "euaid": "-1",
                    "externalCall": "true",
                    "hmac": self.__payment['hmac'],
                    "hppAppVersion": "2.0.0",
                    "issplitpayment": True,
                    "language": self.__payment['language'],
                    "markup": self.__payment['markup'],
                    "mobile": int(self.__payment['mobile']),
                    "mobilecountry": int(self.__payment['mobilecountry']),
                    "mvault": "false",
                    "network": "",
                    "operator": int(self.__payment['operator']),
                    "paymenttype": "",
                    "profileid": self.__payment['authtoken'],
                    "storecard": "false",
                    "termination": base64.b64encode(expiry.encode()).decode(),
                    "token": "",
                    "transaction": self._payment_data['transaction']['id'],
                    "typeid": "3",
                    "validfrom": "",
                    "verificationcode": base64.b64encode(str(cvc).encode()).decode(),
                    "verifier": "",
                    "voucheramount": round(self.account_amount * 100)}
        else:
            body = {"account": str(self.__payment['account']),
                    "accountconfirmpassword": "",
                    "accountpassword": "",
                    "accouontname": "",
                    "additionaldata": {"param": [{"name": "session_token", "text": self.authorization}]},
                    "amount": self.__payment['amount'],
                    "authtoken": self.__payment['authtoken'],
                    "billingaddress": "",
                    "cardid": "",
                    "cardname": "",
                    "cardtypeid": "",
                    "checkouturl": "",
                    "clientid": str(self.__payment['clientid']),
                    "country": int(self.__payment['country']),
                    "currency": int(self.__payment['currency-code']),
                    "customerref": self.__payment['customerref'],
                    "decktoken": "",
                    "email": self.__payment['email'],
                    "euaid": "-1",
                    "externalCall": "true",
                    "hmac": self.__payment['hmac'],
                    "hppAppVersion": "2.0.0",
                    "language": self.__payment['language'],
                    "markup": self.__payment['markup'],
                    "mobile": int(self.__payment['mobile']),
                    "mobilecountry": int(self.__payment['mobilecountry']),
                    "mvault": "false",
                    "network": "",
                    "operator": int(self.__payment['operator']),
                    "paymenttype": "",
                    "profileid": self.__payment['authtoken'],
                    "storecard": "false",
                    "termination": "",
                    "token": "",
                    "transaction": self._payment_data['transaction']['id'],
                    "typeid": "3",
                    "validfrom": "",
                    "verificationcode": "",
                    "verifier": "",
                    "voucheramount": self.__payment['amount']}
        response = self.post('https://pop.cellpointdigital.net/api/authorize', headers=headers, json=body)
        self.cookies.clear()
        self.logger.info(f'[{self.holdTask.orderCode}][response][{response.text}]')
        if response.status_code != 200 or 'Payment authorized' not in response.text:
            raise Exception(
                f'{self.holdTask.orderCode} pay status_code:{response.status_code} response:{response.text}')

    def convert_voucher_pay(self, task, card_id):
        if self.has_bag:
            baggagePrice = self.booking_info['balanceDue'] - self.ticketPrice
        else:
            baggagePrice = 0
        voucher_amount = self.account_amount
        total_amount = self.booking_info['balanceDue']
        ticket_total_amount = self.booking_info['balanceDue'] - baggagePrice
        if voucher_amount >= total_amount:
            use_voucher_amount = total_amount
            card_amount = 0
            card_ticket_amount = 0
        else:
            use_voucher_amount = voucher_amount
            card_amount = total_amount - voucher_amount
            if voucher_amount >= ticket_total_amount:
                card_ticket_amount = 0
            else:
                card_ticket_amount = ticket_total_amount - voucher_amount
        return convert_voucher_pay(task, card_id, self.booking_info['recordLocator'], card_amount, card_ticket_amount,
                                   self.booking_info['currencyCode'], self.phone_number, self.email,
                                   use_voucher_amount, self.booking_info['currencyCode'], use_voucher_amount)

    def convert_pay(self, task, card_id):
        if self.has_bag:
            baggagePrice = self.booking_info['balanceDue'] - self.ticketPrice
        else:
            baggagePrice = 0
        total_amount = self.booking_info['balanceDue']
        ticket_total_amount = self.booking_info['balanceDue'] - baggagePrice
        if self.is_black:
            return convert_hold_pay(task, card_id, self.booking_info['recordLocator'], total_amount,
                                    ticket_total_amount,
                                    self.booking_info['currencyCode'], self.phone_number, self.email,
                                    pnrTags='5J-blackTechnology',
                                    payRoute='guanwang')
        else:
            return convert_hold_pay(task, card_id, self.booking_info['recordLocator'], total_amount,
                                    ticket_total_amount,
                                    self.booking_info['currencyCode'], self.phone_number, self.email,
                                    payRoute='guanwang')

    def convert_account_pay(self, task, card_id):
        if self.has_bag:
            baggagePrice = self.booking_info['balanceDue'] - self.ticketPrice
        else:
            baggagePrice = 0
        total_amount = self.booking_info['balanceDue']
        ticket_total_amount = self.booking_info['balanceDue'] - baggagePrice
        if self.is_black:
            return convert_hold_pay(task, card_id, self.booking_info['recordLocator'], total_amount,
                                    ticket_total_amount,
                                    self.booking_info['currencyCode'], self.phone_number, self.email,
                                    pnrTags='5J-blackTechnology',
                                    payRoute=self.user)
        else:
            return convert_hold_pay(task, card_id, self.booking_info['recordLocator'], total_amount,
                                    ticket_total_amount,
                                    self.booking_info['currencyCode'], self.phone_number, self.email,
                                    payRoute=self.user)

    def account_bookings(self, recordLocator: str, lastName: str):
        url = "https://soar.cebupacificair.com/ceb-omnix_proxy"
        headers = self.get_headers()
        params = {
            'content': self.encrypt("account/bookings")
        }
        body = {"recordLocator": recordLocator, "lastName": lastName}
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        return response.json()

    def account_booking(self, recordLocator: str, lastName: str):
        url = "https://soar.cebupacificair.com/ceb-omnix_proxy"
        headers = self.get_headers()
        params = {
            'content': self.encrypt("account/booking")
        }
        body = {"recordLocator": recordLocator, "lastName": lastName}
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        return response.json()

    def account_token_verify(self, token):
        url = "https://soar.cebupacificair.com/ceb-omnix_proxy"
        headers = self.get_headers()
        params = {
            'content': self.encrypt("account/token/verify")
        }
        body = {"token": token}
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        return response.json()

    def account_setpassword(self, emial, passwd, stateToken):
        url = "https://soar.cebupacificair.com/ceb-omnix_proxy"
        headers = self.get_headers()
        params = {
            'content': self.encrypt(f"account/setpassword/{emial}")
        }
        body = {"stateToken": stateToken, "newPassword": passwd}
        body = self.get_body(body)
        response = self.post(url, headers=headers, params=params, json=body)
        self.cookies.clear()
        if response.status_code >= 300:
            raise Exception(response.text)
        return response.json()


def api_search(taskItem: SearchParam, proxies_type=10, currencyCode=None):
    result = None
    code = 0
    for _ in range(3):
        try:
            app = A5JApp(proxies_type=proxies_type, timeout=30)
            app.init(use_cache=True)
            app.availability(taskItem, currencyCode)
            result = app.convert_search()
            if result:
                code = 0
            else:
                code = 2
            break
        except Exception:
            import traceback
            code = 3
            spider_5j_logger.error(traceback.format_exc())
    return code, result


def new_pay_init(holdTask: HoldTask, proxies_type=None, ignore_departTime_check=True, account=None,
                 password=None, currencyCode=None, check_class=False) -> A5JApp:
    for ssrs in [["MAFI"], []]:
        try:
            app = A5JApp(proxies_type=proxies_type)
            app.init()
            if account:
                app.account_login(account, password)
            app.bookingAvailability(holdTask, ssrs, currencyCode)
            app.convert_search(is_booking=True)
            app.selectFlight(holdTask, check_class=check_class)
            app.trip(holdTask)
            app.guestdetails(holdTask)
            app.cancelMeal()
            app.cancelInsurance()
            app.cancelAddons("seats")
            app.addBaggage(holdTask.current_passengers)
            app.hold_check(holdTask, ignore_departTime_check=ignore_departTime_check)
            app.bookingCommit()
            app.account_register()
            app.accounts()
            app.create_profile()
            app.getHoldOptions()
            app.cpd_hpp()
            app.setPayment()
            app.initialize()
            return app
        except Exception as e:
            robot_5j_logger.error(traceback.format_exc())
            if 'Admin fee validation' not in str(e):
                raise e
            if '非 PD 舱' in str(e):
                raise e
    raise Exception('占座失败')


def no_hold_pay(task: dict, proxies_type=None):
    code = -1
    payOrder = task['payOrderDetail']['payOrder']
    try:
        # voucherInfo = task.get('voucherInfo', None)
        # if voucherInfo:
        #     return voucher_pay(task, proxies_type)
        # # if 'PKFARE' in payOrder['apiSystemUuid'] or 'BSZHL' in payOrder['apiSystemUuid']:
        # #     return account_pay(task, proxies_type)
        # else:
        return card_pay(task, proxies_type)
    except Exception as e:
        robot_5j_logger.error(traceback.format_exc())
        if '非 PD 舱' in str(e):
            code = -2
        return code, pay_error_result(payOrder, str(e), 302)


def voucher_pay(task: dict, proxies_type=None):
    payOrder = task['payOrderDetail']['payOrder']
    voucherInfo = task.get('voucherInfo')
    holdTask: HoldTask = HoldTask.from_pay_task_v2(task)
    account = voucherInfo['loginUser']
    password = voucherInfo['loginPassword']
    app = new_pay_init(holdTask, proxies_type=proxies_type, account=account, password=password)
    vcc_card = {"id": 1008318, "payment": 90, "paynumber": "4725930003618901", "name": "kzyh8901",
                "cardexpired": "05/25", "CVV": "550", "owner": "", "password": "", "status": 0}
    # vcc_card = AutoApplyCard.getCardNoHold(task, '5J', app.booking_info['currencyCode'], app.booking_info['balanceDue'])
    expiry = vcc_card['cardexpired']
    cvc = vcc_card['CVV']
    card_number = vcc_card['paynumber']
    can = can_pay(task, vcc_card)
    if not can:
        return -1, pay_error_result(payOrder, "支付取消", 302)
    try:
        app.account_authorize(card_number, expiry, cvc)
        time.sleep(10)
        order_info = pnr_check(app.booking_info['recordLocator'], app.holdTask.current_passengers[0].lastName,
                               proxies_type=proxies_type)
        app.logger.info(f'[{holdTask.orderCode}][order_info][{order_info}]')
        if not order_info or order_info['info']['status'] != 'Confirmed':
            return -1, pay_error_result(payOrder,
                                        f"票号状态异常, 请核实票号:{app.booking_info['recordLocator']}  邮箱:{app.email}, 票号状态异常",
                                        203)
        return 0, app.convert_voucher_pay(task, vcc_card['id'])
    except Exception:
        app.logger.error(f'[{holdTask.orderCode}]{traceback.format_exc()}')
        return -1, pay_error_result(payOrder,
                                    f"支付异常，账户: {account} ,请核实票号:{app.booking_info['recordLocator']}, 邮箱:{app.email}",
                                    203)


def account_pay(task: dict, proxies_type=None):
    payOrder = task['payOrderDetail']['payOrder']
    holdTask: HoldTask = HoldTask.from_pay_task_v2(task)
    account = 'fangxin@1tct.com'
    password = 'Su1234560329@'
    app = new_pay_init(holdTask, proxies_type=proxies_type, account=account, password=password)
    pay_card = {'id': 1}
    can = can_pay(task, pay_card)
    if not can:
        return -1, pay_error_result(payOrder, "支付取消", 302)
    try:
        app.account_authorize()
        time.sleep(10)
        order_info = pnr_check(app.booking_info['recordLocator'], app.holdTask.current_passengers[0].lastName,
                               proxies_type=proxies_type)
        app.logger.info(f'[{holdTask.orderCode}][order_info][{order_info}]')
        if not order_info or order_info['info']['status'] != 'Confirmed':
            return -1, pay_error_result(payOrder,
                                        f"票号状态异常, 请核实票号:{app.booking_info['recordLocator']}  邮箱:{app.email}, 票号状态异常",
                                        203)
        return 0, app.convert_account_pay(task, pay_card['id'])
    except Exception:
        app.logger.error(f'[{holdTask.orderCode}]{traceback.format_exc()}')
        return -1, pay_error_result(payOrder,
                                    f"支付异常，账户: {account} ,请核实票号:{app.booking_info['recordLocator']}, 邮箱:{app.email}",
                                    203)


def card_pay(task: dict, proxies_type=None):
    payOrder = task['payOrderDetail']['payOrder']
    holdTask: HoldTask = HoldTask.from_pay_task_v2(task)
    app = new_pay_init(holdTask, proxies_type=proxies_type, check_class=task['paymentAccount']['account'] != 'guanwang')
    vcc_card = AutoApplyCard.getCardNoHold(task, '5J', app.booking_info['currencyCode'], app.booking_info['balanceDue'])
    expiry = vcc_card['cardexpired']
    cvc = vcc_card['CVV']
    card_number = vcc_card['paynumber']
    can = can_pay(task, vcc_card)
    if not can:
        return -1, pay_error_result(payOrder, "支付取消", 302)
    app.fxlookup(card_number)
    app.pay(card_number)
    try:

        app.card_authorize(card_number, expiry, cvc)
        time.sleep(20)
        order_info = pnr_check(app.booking_info['recordLocator'], app.holdTask.current_passengers[0].lastName,
                               proxies_type=proxies_type)
        app.logger.info(f'[{holdTask.orderCode}][order_info][{order_info}]')
        if not order_info or order_info['info']['status'] != 'Confirmed':
            return -1, pay_error_result(payOrder,
                                        f"票号状态异常, 请核实票号:{app.booking_info['recordLocator']}  邮箱:{app.email}, 票号状态异常",
                                        203)

        threading.Thread(target=account_register, args=(holdTask.orderCode,
                                                        holdTask.current_passengers[0].firstName,
                                                        holdTask.current_passengers[0].lastName,
                                                        app.email,
                                                        proxies_type,
                                                        payOrder['otaId'],
                                                        app.booking_info['recordLocator'])).start()
        return 0, app.convert_pay(task, vcc_card['id'])

        # if check_pay(payOrder['otaId'], card_number):
        #     threading.Thread(target=account_register, args=(
        #     holdTask.orderCode, holdTask.current_passengers[0].firstName, holdTask.current_passengers[0].lastName,
        #     app.email, proxies_type, payOrder['otaId'], app.booking_info['recordLocator'])).start()
        #     return 0, app.convert_pay(task, vcc_card['id'])
        # else:
        #     return -1, pay_error_result(payOrder,
        #                                 f"支付流水异常, 请核实票号:{app.booking_info['recordLocator']}  邮箱:{app.email}, 支付流水异常",
        #                                 203)

    except Exception as e:
        app.logger.error(f'[{holdTask.orderCode}]{traceback.format_exc()}')
        if '非 PD 舱' in str(e):
            code = -2
        return -1, pay_error_result(payOrder,
                                    f"支付异常, 请核实票号:{app.booking_info['recordLocator']}  邮箱:{app.email}, 错误:{e}",
                                    203)


def pnr_check(pnr, ln, proxies_type=None):
    for _ in range(5):
        try:
            app = A5JApp(proxies_type=proxies_type)
            app.init()
            app.account_login('amp8eugn@tgbnx.com', 'Su123456789@')
            return app.account_bookings(pnr, ln)
        except Exception:
            check_5J_logger.error(traceback.format_exc())
    return None


def go_search(taskItem, journey_key, proxies_type=7, use_cache=True):
    decode_journey_key = decode(journey_key)
    if 'DG' in decode_journey_key and '5J' in decode_journey_key:
        return None
    price = redis_82.get(decode_journey_key)
    if use_cache:
        robot_5j_logger.info(f'查询缓存 {decode_journey_key}')

        # price = redis_82.get(decode(journey_key))
        if price:
            robot_5j_logger.info(f'命中缓存 {decode_journey_key} {price}')
            return float(price)
        # else:
        #     return None
    if redis_81.get(journey_key):
        robot_5j_logger.info(f'黑名单 {decode_journey_key} ')
        return None

    try:
        app = A5JApp(proxies_type=proxies_type, timeout=20, retry_count=1)
        for _ in range(4):
            try:
                app.init()
                break
            except Exception:
                import traceback
                spider_5j_logger.error(traceback.format_exc())
        else:
            return None
        result = app.search_trip(journey_key=journey_key, searchParam=taskItem)
        # app.availability(taskItem)
        return result
    except Exception as e:
        import traceback
        spider_5j_logger.error(traceback.format_exc())
        if 'ClassNotAvailable' in str(e) and 'price':
            return -1
    return None


def lower_price_search(taskItem: SearchParam, proxies_type=37) -> str:
    for _ in range(3):
        try:
            app = A5JApp(proxies_type=proxies_type, timeout=20, retry_count=1)
            app.init()
            app.availability(taskItem)
            for route in app.availability_result['routes']:
                for journey in route['journeys']:
                    if taskItem.flight_no == app.getFlightNumberFromJourneyKey(decode(journey['journeyKey']), True):
                        return str(app.search_trip(journey_key=journey['journeyKey'],
                                                   searchParam=taskItem)) + ' ' + app.currencyCode
            return 'no filight'
        except Exception:
            import traceback
            spider_5j_logger.error(traceback.format_exc())
    return '服务异常'


@func_retry(3)
def account_register(orderCode, firstName, lastName, email, proxies_type=37, otaId=None, pnr=None):
    try:
        app = A5JApp(proxies_type=proxies_type, timeout=60, retry_count=1)
        app.init()
        app.account_real_register(firstName, lastName, email)
        for _ in range(120):
            body = find_email_by_recv_address_and_subject(email, 'Verify your Cebu Pacific Account')
            if body:
                html = app.etree.HTML(body[0])
                verifyEmailUrl = html.xpath('//a[contains(text(),"verifyEmail")]/text()')
                if verifyEmailUrl:
                    verifyEmailUrl = verifyEmailUrl[0]
                    print(verifyEmailUrl)
                    query = parse_qs(urlparse(verifyEmailUrl).query)
                    token = query["activationToken"][0]
                    token_verify = app.account_token_verify(token)
                    passwd = 'Su123456789@'
                    result = app.account_setpassword(email, passwd, token_verify['stateToken'])
                    if result == {}:
                        pay_order_log(orderCode, '注册邮箱成功', 'Trident', f"{email} {passwd} 注册成功")
                        print('注册邮箱成功')
                        app.account_login(email, passwd)
                        app.account_booking(pnr, lastName)
                        pay_order_log(orderCode, 'pnr关联成功', 'Trident', f"{pnr} {email} 关联成功")
                        if otaId:
                            update_pnr_accountInfo(otaId, pnr, email, passwd, f"{firstName} {lastName}")
                        return
                    else:
                        raise Exception(f'{email} 注册失败 {result}')
                else:
                    raise Exception(f'{email} 解析异常')

            else:
                time.sleep(1)
        else:
            raise Exception(f'{email} 读取邮件超时')
    except Exception:
        import traceback
        pay_order_log(orderCode, '注册失败', 'Trident', f"{email} 注册失败")
        robot_5j_logger.error(f'{(firstName, lastName, email)} 注册失败 {traceback.format_exc()}')


def account_token_verify(token, email, firstName, lastName, proxies_type=1087):
    app = A5JApp(proxies_type=proxies_type, timeout=60, retry_count=1)
    app.init()
    app.account_real_register(firstName, lastName, email)
    token_verify = app.account_token_verify(token)
    passwd = 'Ab123456789@'
    result = app.account_setpassword(email, passwd, token_verify['stateToken'])
    if result == {}:
        print('注册邮箱成功')
    else:
        raise Exception(f'{email} 注册失败 {result}')


def account_booking_add_booking(orderCode, firstName, lastName, email, proxies_type=37, otaId=None, pnr=None,
                                password=None):
    app = A5JApp(proxies_type=proxies_type, timeout=60, retry_count=1)
    app.init()
    app.account_login(email, password or 'Su123456789@')
    app.account_booking(pnr, lastName)
    pay_order_log(orderCode, 'pnr关联成功', 'Trident', f"{pnr} {email} 关联成功")
