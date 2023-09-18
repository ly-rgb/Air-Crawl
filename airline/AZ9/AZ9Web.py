# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AZ9Web.py
@effect: "请填写用途"
@Date: 2022/11/29 14:33
"""
import math
import random

from airline.base import AirAgentV3Development
from robot import HoldTask, Dict
from utils.searchparser import SearchParam
from datetime import datetime
import traceback
from utils.log import booking_Z9_logger, spider_Z9_logger
from native.api import get_exchange_rate_carrier, pay_order_log


class AZ9Web(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None, totalprice=None, username=None,
                 password=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.search_url = "https://api.myairline.my/api/v1/flight/searchflight"
        self.search_response = None
        self.adult_num = None

        self.promo_code = None
        if self.holdTask:
            if self.holdTask.orderCode[:3] in ['DRC', 'CTR']:
                self.promo_code = ""
            else:
                self.promo_code = ""
        self.username = username
        self.password = password
        self.totalprice = totalprice
        self.phone = '18611715578'
        self.email = 'nevergiveup17apr01@qq.com'

    @property
    def base_headers(self):
        headers = {
            'authority': 'api.myairline.my',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://booking.myairline.my',
            'pragma': 'no-cache',
            'referer': 'https://booking.myairline.my/',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        return headers

    def random_char(self):

        t = ''
        n = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        for i in range(8):
            t += n[math.floor(random.random() * len(n))]

        return t

    def search(self, searchParam: SearchParam):
        body = None
        depart_date = datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00.000Z")

        if "READTIMELCC" in searchParam.args:
            body = self.json.dumps({
                "searchFlightRequest": {
                    "OriginAirport": searchParam.dep,
                    "DestinationAirport": searchParam.arr,
                    "DepartDate": depart_date,
                    "ReturnDate": depart_date,
                    "Adults": searchParam.adt,
                    "Childrens": "0",
                    "Infants": "0",
                    "IsReturn": False,
                    "TripType": "One Way",
                    "Currency": "MYR",
                    "PromoCode": ""
                }
            })

        if "CRAWlLCC" in searchParam.args:
            body = self.json.dumps({
                "searchFlightRequest": {
                    "OriginAirport": searchParam.dep,
                    "DestinationAirport": searchParam.arr,
                    "DepartDate": depart_date,
                    "ReturnDate": depart_date,
                    "Adults": searchParam.adt,
                    "Childrens": "0",
                    "Infants": "0",
                    "IsReturn": False,
                    "TripType": "One Way",
                    "Currency": "MYR",
                    "PromoCode": ""
                }
            })

        try:

            response = self.post(url=self.search_url, headers=self.base_headers, data=body)
            if response.status_code == 200:
                is_error = list(response.json().keys())
                if "error" in is_error:
                    spider_Z9_logger.error("请求失败, 此次请求没有行程数据(当天没有航班)")
                    spider_Z9_logger.error(f"请求参数: {body}")
                    spider_Z9_logger.error(f"请求结果: {response.text}")
                    raise Exception(f"返回的错误信息为: {is_error}")

                spider_Z9_logger.info(f"请求成功，请求接口地址: {self.search_url}")
                spider_Z9_logger.info(f"请求参数: {body}")
                spider_Z9_logger.info(f"请求结果: {response.text}")
                self.search_response = response
                self.adult_num = int(searchParam.adt)

            else:
                spider_Z9_logger.error(f"请求失败，请检查ip，UA等参数是否正常")
                raise Exception(f"请求失败，状态码: {response.status_code}")
        except Exception:
            spider_Z9_logger.error(f"{traceback.print_exc()}")

    def convert_search(self):
        result = []

        try:
            if not self.search_response.json()["result"]["success"]:
                return result
            flights = self.search_response.json()["result"]["searchFlightResponse"]["flightResult"]["outboundSegment"]
            for flight in flights:
                flight_num_list = []
                from_segment_list = []
                # 判断是否为中转航班
                legs_count = flight["legCount"]
                if legs_count == 1:
                    spider_Z9_logger.info("此次航班为直达航班")

                    # 提取航班信息
                    carrier = flight["segmentDetail"]["carrierCode"]
                    flight_num = flight["segmentDetail"]["flightNum"]
                    dep = flight["segmentDetail"]["origin"]
                    arr = flight["segmentDetail"]["destination"]
                    dep_time = datetime.strptime(flight["segmentDetail"]["departureDate"],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                    arr_time = datetime.strptime(flight["segmentDetail"]["arrivalDate"],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                    from_segment = {
                        'carrier': carrier,
                        'flightNumber': (carrier + flight_num).replace(" ", ""),
                        'depAirport': dep,
                        'depTime': dep_time,
                        'arrAirport': arr,
                        'arrTime': arr_time,
                        'codeshare': False,
                        'cabin': "Y",
                        'num': 0,
                        'aircraftCode': '',
                        'segmentType': 0
                    }
                    flight_num_list.append(f"{carrier}{flight_num}".replace(" ", ""))
                    from_segment_list.append(from_segment)
                    spider_Z9_logger.info(f"提取的航班信息: {from_segment}")

                    data = {
                        'data': "/".join(flight_num_list),
                        'productClass': 'ECONOMIC',
                        'fromSegments': from_segment_list,
                        'cur': 'MYR',
                        'adultPrice': flight["adultPriceTotal"] / self.adult_num - 1,
                        'adultTax': 1,
                        'childPrice': 0,
                        'childTax': 0,
                        'promoPrice': 0,
                        'adultTaxType': 0,
                        'childTaxType': 0,
                        'priceType': 0,
                        'applyType': 0,
                        'max': 0,
                        'limitPrice': True,
                        'info': ""
                    }

                    spider_Z9_logger.info(f"data信息: {data}")
                    result.append(data)

                else:
                    spider_Z9_logger.info("此次航班为中转航班")
                    raise Exception(f"请添加中转航班: {flight}")

        except Exception:
            result = None
            spider_Z9_logger.error(f"数据解析错误")
            spider_Z9_logger.error(f"{traceback.print_exc()}")

        return result

    def login(self, username, password):

        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'languageCode': 'en-us'
        }

        data = {
            'UserName': username,
            'Password': password,
            'languageCode': 'en-us',
        }
        sign_in_url = 'https://myairline-api.ezycommerce.sabre.com/api/v1/TravelAgent/Login'
        booking_Z9_logger.info(f"开始登录账户， 登录接口: {sign_in_url}")
        response = self.post(url=sign_in_url, headers=headers, json=data)

        if response.status_code == 200:
            self.authorizationtoken = "bearer " + response.headers.get('x-authorizationtoken')
            self.iata_code = response.json()['travelAgent']['agency']['iataCode']
            self.first_name = response.json()['travelAgent']['firstName']
            self.session_token = response.headers.get("sessiontoken")
            booking_Z9_logger.info(f"登录成功!!!请求结果: {response.text}")
            booking_Z9_logger.info(f"set-cookie: {response.cookies}")
            booking_Z9_logger.info(f"sessionToken: {self.session_token}")
            booking_Z9_logger.info(f"x-authorizationtoken: {self.authorizationtoken}")

        else:
            booking_Z9_logger.error(f"登录失败,状态码: {response.status_code}")
            booking_Z9_logger.error(f"data: {data}")
            raise Exception(f"登录失败...")

    def select_flight(self):
        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'languageCode': 'en-us',
            'Authorization': self.authorizationtoken
        }
        select_flight_url = "https://myairline-api.ezycommerce.sabre.com/api/v1/Availability/SearchShop"

        json_data = {
            'passengers': [
                {
                    'code': 'ADT',
                    'count': self.holdTask.adt_count,
                },
                {
                    'code': 'CHD',
                    'count': self.holdTask.chd_count,
                },
                {
                    'code': 'INF',
                    'count': 0,
                },
            ],
            'routes': [
                {
                    'fromAirport': self.holdTask.origin,
                    'toAirport': self.holdTask.destination,
                    'departureDate': self.holdTask.departDate,
                    'startDate': self.holdTask.departDate,
                    'endDate': self.holdTask.departDate
                },
            ],
            'currency': 'MYR',
            'fareTypeCategories': None,
            'isManageBooking': False,
            'languageCode': 'en-us',
        }

        booking_Z9_logger.info(f"开始请求: {select_flight_url}")

        response = self.post(url=select_flight_url, headers=headers, json=json_data)

        if response.status_code == 200:
            self.ticket_info = response.json()
            self.currency = self.ticket_info['currency']
            booking_Z9_logger.info(f"ticket_info获取成功，{response.json()}")
        else:
            booking_Z9_logger.error("ticket_info获取失败...")
            raise Exception('ticket_info获取失败..')

    def find_flight(self):

        flights = self.ticket_info["routes"][0]["flights"]
        booking_Z9_logger.info(f"抓取航班结果: {flights}")
        fs = []
        for flight in flights:
            flight_number = flight["carrierCode"] + flight["flightNumber"]
            departure_date = datetime.strptime(flight["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            tmp = [fare["price"] for fare in flight["fares"] if fare["soldOut"] != True]

            if len(tmp) <= 0:
                continue

            this_er = get_exchange_rate_carrier('Z9', self.currency)
            min_ = this_er * min(tmp)

            if flight_number == self.holdTask.flightNumber and departure_date == self.holdTask.departDate and (
                    (self.holdTask.targetPrice + 5) * (self.holdTask.adt_count + self.holdTask.chd_count) >= min_
            ):
                fs.append(flight)
        if len(fs) == 0:
            booking_Z9_logger.error("未找到相应航班...")
        else:
            dict_ = {}
            for fl in fs:
                tmp = [fare["price"] for fare in fl["fares"] if fare["soldOut"] != True]
                dict_[min(tmp)] = fl
            prices = list(dict_.keys())
            self.min_price = min(prices)
            self.flight = dict_[self.min_price]
            booking_Z9_logger.info(f"提取到的航班最低价格: {self.min_price} => flight: {self.flight}")

    def flight_check(self, payOrder):
        depTime = datetime.strptime(self.flight["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M")
        if self.holdTask.departTime != depTime:
            pay_order_log(payOrder["apiSystemUuid"], "航变", "Trident", f"old: {self.holdTask.departTime} new: {depTime}")
            raise Exception(f"{self.holdTask.orderCode} 航变 old:{self.holdTask.departTime} new: {depTime}")

    def get_pre_data(self):
        """
        拼接Probook接口的data
        :return: data
        """
        try:
            passengers = []
            passengerFares = []
            selectedFare = [fare for fare in self.flight["fares"] if fare["price"] == self.min_price][0]
            # add field
            selectedFare.update({"selected": True, "serviceBundles": []})
            fare_id = selectedFare["id"]
            fareTypes = [i for i in self.flight["fareTypes"] if i["fares"][0]["id"] == fare_id][0]
            fare = fareTypes['fares'][0]
            legs = self.flight["legs"][0]

            for idx, p in enumerate(self.holdTask.current_passengers):
                baggage = int(p.baggageMessageDO.baggageWeight) if p.baggageMessageDO else 0
                if baggage > 0:
                    service = [{
                        "code": "BG" + str(baggage),
                        "flightId": self.flight["id"],
                        "isFareBundle": False,
                        "isFromServiceBundle": False,
                        "isServiceBundleSsr": False
                    }]
                else:
                    service = []
                person = {}
                if p.passenger_type == "ADT":
                    first_name = p.first_name
                    last_name = p.last_name
                    person["passengerTypeCode"] = p.passenger_type
                    person["id"] = "ADT_" + self.random_char()
                    person["passengerTypeNamePlural"] = "Adult"
                    if p.sex == "M":
                        person["title"] = "MR"
                    else:
                        person["title"] = "MRS"
                else:
                    person["passengerTypeCode"] = p.passenger_type
                    person["id"] = "CHD_" + self.random_char()
                    person["passengerTypeNamePlural"] = "Children"
                    if p.sex == "M":
                        person["title"] = "Mstr"
                    else:
                        person["title"] = "Ms"

                contactInformation = {
                    'address': '',
                    'address2': '',
                    'city': '',
                    'country': '',
                    'state': '',
                    'phoneNumber': '',
                    'workPhoneNumber': '',
                    'postal': '',
                    'email': '',
                    'fax': '',
                }
                if idx == 0:
                    contactInformation = {
                        "address": "beijing",
                        "address2": "beijing",
                        "city": "beijing",
                        "country": "CN",
                        "state": "beijing",
                        "phoneNumber": "18611715578",
                        "workPhoneNumber": "",
                        "postal": "100000",
                        "email": "nevergiveup17apr01@qq.com",
                        "fax": ""
                    }

                tmp = {
                    "passengerTypeCode": p.passenger_type,
                    "id": person["id"],
                    "associateWithPassengerId": None,
                    "selectedTravelCompanionId": None,
                    "title": person["title"],
                    "firstName": p.first_name,
                    "middleName": "",
                    "lastName": p.last_name,
                    "dateOfBirth": p.birthday_format("%Y-%m-%d"),
                    "gender": p.sex,
                    "mobileNumber": "",
                    "email": "",
                    "frequentFlyerNumber": "",
                    "documentNumber": "",
                    "redressNumber": "",
                    "knownTravelerNumber": "",
                    "height": "",
                    "weight": "",
                    "seats": [

                    ],
                    "services": service,
                    "contactInformation": contactInformation,
                    "apisInfo": {
                        "nationality": "",
                        "residenceCountry": "",
                        "documentNumber": "",
                        "issuedBy": "",
                        "passportExpireDate": "",
                        "destinationCountry": "",
                        "destinationPostal": "",
                        "destinationState": "",
                        "destinationCity": "",
                        "destinationAddress": "",
                        "documentNumber2": "",
                        "documentType2": "",
                        "document2IssuedBy": "",
                        "document2ExpireDate": ""
                    }
                }

                tmp_ = {
                    "passengerId": person["id"],
                    "passengerTypeCode": person["passengerTypeCode"],
                    "passengerTypeName": person["passengerTypeNamePlural"],
                    "passengerTypeNamePlural": person["passengerTypeNamePlural"],
                    "fareName": fareTypes["name"],
                    "farePrice": fare["price"],
                    "farePriceWithoutTax": fare["priceWithoutTax"],
                    "fareDiscount": fare["discount"]
                }
                passengers.append(tmp)
                passengerFares.append(tmp_)

            data = {
                "contact": {
                    "address": "beijing",
                    "address2": "beijing",
                    "city": "beijing",
                    "country": "CN",
                    "state": "beijing",
                    "phoneNumber": "18611715578",
                    "workPhoneNumber": "",
                    "postal": "100000",
                    "email": "nevergiveup17apr01@qq.com",
                    "fax": ""
                },
                "emergencyContact": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "reference": "18611715578",
                    "referenceType": 0
                },
                "flights": [
                    {
                        "route": 0,
                        "key": self.flight["key"],
                        "id": self.flight["id"],
                        "carrierCode": "Z9",
                        "flightNumber": self.flight["flightNumber"],
                        "selectedFare": selectedFare,
                        "fareId": fare_id,
                        "fareBasis": fare["fareBasis"],
                        "departureDate": self.flight["departureDate"],
                        "arrivalDate": self.flight["arrivalDate"],
                        "from": self.flight["from"],
                        "to": self.flight["to"],
                        "isInternational": False,
                        "passengerFares": passengerFares,
                        "price": fare["price"],
                        "priceWithoutTax": fare["priceWithoutTax"],
                        "legs": [
                            {
                                "id": legs["id"],
                                "departureDate": legs["departureDate"],
                                "flightTime": legs["flightTime"],
                                "flightNumber": legs["flightNumber"],
                                "equipmentType": legs["equipmentType"],
                                "carrierCode": "Z9",
                                "legType": legs["legType"]
                            }
                        ],
                        "cabin": self.flight["cabin"],
                        "scheduleInformation": self.flight["scheduleInformation"]
                    }
                ],
                "passengers": passengers,
                "currency": self.currency,
                "fareTypeCategories": None,
                "promoCode": self.promo_code,
                "tracking": {},
                "isExternallyPriced": False,
                "invoiceDetails": None,
                "languageCode": "en-us"
            }
            return data
        except Exception as e:
            raise Exception(f"probook fail {e}")

    def pre_book(self):
        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'Authorization': self.authorizationtoken,
            'SessionToken': self.session_token,
            'languageCode': 'en-us'
        }
        pre_book_url = "https://myairline-api.ezycommerce.sabre.com/api/v1/Booking/PreBook"
        data = self.get_pre_data()
        booking_Z9_logger.info(f"开始请求: {pre_book_url}")
        response = self.post(url=pre_book_url, headers=headers, json=data)
        if response.status_code == 200:
            self.prebook_res = response.json()
            self.SessionToken = response.headers['SessionToken']
            self.endprice = self.prebook_res["totalPrice"]
            self.baggage_price()
            booking_Z9_logger.info(f"在prebook中提取 => end_price: {self.endprice} bagggage: {self._baggage_price}")
        else:
            booking_Z9_logger.error(f"prebook获取失败...")
            raise Exception("prebook获取失败...")

    def baggage_price(self):
        self._baggage_price = 0
        passengers = self.prebook_res["passengers"]
        for passenger in passengers:
            services = passenger["flights"][0]["services"]
            for service in services:
                if "BG" in service["code"]:
                    self._baggage_price += service["price"]

    def create(self):

        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'Authorization': self.authorizationtoken,
            'SessionToken': self.SessionToken,
            'languageCode': 'en-us'
        }
        create_url = 'https://myairline-api.ezycommerce.sabre.com/api/v1/Booking/Create'
        data = self.get_pre_data()
        booking_Z9_logger.info(f"开始请求 :  {create_url} ")
        booking_Z9_logger.info(f"请求参数data: {data}")
        response = self.post(url=create_url, headers=headers,
                             json=data, is_retry=False)
        booking_Z9_logger.info(f"create_res结果: {response.status_code} {response.json()}")
        if response.status_code == 200:
            self.prebook_res = response.json()
            self.SessionToken = response.headers["sessiontoken"]
            self.pnr = self.prebook_res["confirmationNumber"]
            self.__digest = self.prebook_res["digest"]
            self.webBookingId = self.prebook_res["webBookingId"]
        else:
            booking_Z9_logger.error(f"create_res获取失败")
            raise Exception("create_res 获取失败...")

    def pay(self):

        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'Authorization': self.authorizationtoken,
            'SessionToken': self.SessionToken,
            'languageCode': 'en-us'
        }

        pay_url = "https://myairline-api.ezycommerce.sabre.com/api/v1/Payment/Process"
        data_order = self.get_pre_data()
        last_name = data_order["emergencyContact"]["lastName"]

        data = {
            'card': {
                'cardHolder': '',
                'cardNumber': '',
                'cvc': '',
                'expiryMonth': '05',
                'expiryYear': '2020',
            },
            'address': 'ROOM 601, A5, NO.14, JIUXIANQIAO',
            'address2': 'ROAD, CHAOYANG DISTRICT,',
            'city': 'BEIJINg',
            'postal': '',
            'state': 'BEIJINg',
            'country': 'CN',
            'firstName': 'QIAn',
            'lastName': 'SULIN',
            'email': 'sulin.qian@darana.cn',
            'mobileNumber': '',
            'confirmationNumber': self.pnr,
            'amount': int(self.endprice),
            'paymentMethodId': 'internal:invoice',
            'providerId': 'invoice',
            'metaData': {},
            'currency': self.currency,
            'bookingLastName': last_name,
            'iataCode': self.iata_code,
            'basePaymentAmount': int(self.endprice),
            'baseCurrency': self.currency,
            'exchangeRate': 1,
            'isModifyPayment': False,
            'hasPaymentFee': False,
            'signUpToNewsletter': False,
            'areSeatsCached': False,
            'receiptLanguageCode': 'en-us',
            'firebaseCloudMessagingToken': '',
            'successUrl': 'https://mybooking.myairline.my/en/confirmation?confirmationNumber=' + self.pnr + '&digest=' + self.__digest,
            'failureUrl': 'https://mybooking.myairline.my/en/payment?failed=true',
            'vouchers': [],
            'languageCode': 'en-us',
        }

        booking_Z9_logger.info(f"开始请求: {pay_url}")
        booking_Z9_logger.info(f"pay_data: {data}")

        response = self.post(url=pay_url, headers=headers, json=data, is_retry=False)
        booking_Z9_logger.info(f"pay_res请求结果: {response.status_code}{response.text}")
        if response.status_code == 200:
            if response.json()["success"]:
                return

        else:
            booking_Z9_logger.error(f"pay_res获取失败")
            raise Exception(f"pay_res获取失败...")

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
                "payPrice": self.endprice,
                "payTicketPrice": self.endprice - self._baggage_price,
                "payBaggagePrice": self._baggage_price,
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
                "bookingId": self.webBookingId
            },
            "code": 0,
            "type": 1,
            "address": '',
            "taskstep": "login"
        }
