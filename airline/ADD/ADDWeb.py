import json
import random
import re
import math
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_DD_logger, booking_DD_logger
import traceback
from datetime import datetime, timedelta
from native.api import register_email, AutoApplyCard, can_pay, pay_order_log, get_exchange_rate_carrier


class ADDWeb(AirAgentV3Development):
    '''

    '''

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None, totalprice=None, password=None,
                 username=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.search_response = None
        self.promo_code = None
        if self.holdTask:
            if self.holdTask.orderCode[:3] in ['DRC', 'CTR']:
                self.promo_code = ""
            else:
                self.promo_code = "AMZTH300"
        self.totalprice = totalprice
        self.phone = '18611715578'
        self.email = 'nevergiveup17apr04@qq.com'
        self.password = password
        self.username = username

    def random_char(self):
        '''
        s = function(e) {
                for (var t = "", n = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", r = 0; r < e; r++)
                    t += n.charAt(Math.floor(Math.random() * n.length));
                return t
            }
        '''
        t = ''
        for i in range(8):
            n = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            t += n[math.floor(random.random() * len(n))]
        return t

    def search(self, searchParam: SearchParam):
        # spider_DD_logger.info(f"开始任务{searchParam.args}")
        self.number = searchParam.adt
        try:
            start_date = searchParam.date
            end_date = searchParam.date
            if "CRAWlLCC" in searchParam.args:
                end_date = str(datetime.date(datetime.strptime(start_date, "%Y-%m-%d")) + timedelta(days=7))
            get_apikey_url = "https://booking.nokair.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            }
            spider_DD_logger.info(f"开始请求{get_apikey_url}")
            res_ = self.post(url=get_apikey_url, headers=headers)
            # spider_DD_logger.info(res_.text)
            if res_.status_code == 200:
                apikey_ = re.findall(r"window.runtimeConfig =(.*?)\s+window.version.+?</script>", res_.text, re.S)[0]
                apikey = json.loads(apikey_)['apiKey']
            else:
                raise Exception('apikey获取失败..')

            ticket_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/Availability/SearchShop'
            headers = {
                'X-UserIdentifier': "OZdDOl6WVIG9omZHUuQ7JW8CyjUaeM",
                'Tenant-Identifier': apikey,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            }
            data = {"passengers": [{"code": "ADT", "count": searchParam.adt}, {"code": "CHD", "count": 0},
                                   {"code": "INF", "count": 0}], "routes": [
                {"fromAirport": searchParam.dep, "toAirport": searchParam.arr, "departureDate": searchParam.date,
                 "startDate": start_date,
                 "endDate": end_date}],
                    "currency": "THB", "fareTypeCategories": '',
                    "isManageBooking": 'false', "languageCode": "zh-cn"}
            ticket_res = self.post(url=ticket_url, headers=headers, data=json.dumps(data))
            ticket_res.encoding = 'gbk'
            if ticket_res.status_code == 200:
                self.ticket_info = ticket_res.json()
            else:
                raise Exception('ticket_info获取失败..')
        except Exception as e:
            spider_DD_logger.error(f"请求失败, 失败结果：{e}")
            spider_DD_logger.error(f"{traceback.format_exc()}")

    def parse_info(self):
        result = []
        flights = self.ticket_info['routes'][0]['flights']
        booking_DD_logger.info(f"抓取结果:{flights}")
        for f in flights:
            ep_data = {
                'data': '',
                'productClass': 'ECONOMIC',
                'fromSegments': [],
                'cur': '',
                'adultPrice': 999999,
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
            sg = {
                'carrier': '',
                'flightNumber': '',
                'depAirport': '',
                'depTime': '',
                'arrAirport': '',
                'arrTime': '',
                'codeshare': False,
                'cabin': 'Y',
                'num': 0,
                'aircraftCode': '',
                'segmentType': 0
            }
            tmp = [fare['price'] for fare in f['fares'] if fare['soldOut'] != True]
            if len(tmp) > 0:
                min_price = min(tmp)
            else:
                continue
            ep_data['adultPrice'] = (min_price / self.number) - 1
            # ep_data['max'] = [fare['seatCount'] for fare in f['fares'] if fare['name'] == "NOK LITE"][0]
            ep_data['max'] = [fare['seatCount'] for fare in f['fares'] if fare['price'] == min_price][0]
            ep_data['productClass'] = [fare['cabin'] for fare in f['fares'] if fare['price'] == min_price][0]
            ep_data['info'] = f['key']
            ep_data['cur'] = self.ticket_info['routes'][0]['from']['currency']

            s = []
            for l in f['legs']:
                sg['carrier'] = l['carrierCode']
                sg['flightNumber'] = l['carrierCode'] + l['flightNumber']
                sg['depAirport'] = l['from']['code']
                sg['arrAirport'] = l['to']['code']
                sg['depTime'] = datetime.strptime(l['departureDate'], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                sg['arrTime'] = datetime.strptime(l['arrivalDate'], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                sg['cabin'] = [fare['code'] for fare in f['fares'] if fare['price'] == min_price][0]
                sg['aircraftCode'] = l['equipmentType']
                s.append(sg)
                ep_data['fromSegments'] = s
            ep_data['data'] = '/'.join([i['flightNumber'] for i in s])
            result.append(ep_data)
        return result

    def convert_search(self):
        spider_DD_logger.info('开始解析')
        try:
            result = self.parse_info()
            return result

        except Exception:
            spider_DD_logger.error("解析数据失败，请查看json结构")
            spider_DD_logger.error(f"{traceback.format_exc()}")

    def login(self):
        get_apikey_url = "https://booking.nokair.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }
        booking_DD_logger.info(f"开始请求{get_apikey_url}")
        res_ = self.post(url=get_apikey_url, headers=headers)
        if res_.status_code == 200:
            apikey_ = re.findall(r"window.runtimeConfig =(.*?)\s+window.version.+?</script>", res_.text, re.S)[0]
            self.apikey = json.loads(apikey_)['apiKey']
            booking_DD_logger.info(f"apikey获取成功{self.apikey}")
        else:
            raise Exception('apikey获取失败..')
        login_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/TravelAgent/Login'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'X-UserIdentifier': 'kAJkEIqAF7wyyyoZly4YmZsKAl9lUR',
            'Host': 'api-production-nokair-booksecure.ezyflight.se',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Access-Control-Allow-Origin': '*',
            'Tenant-Identifier': self.apikey,
            'Origin': 'https://booking.nokair.com',
            'Referer': 'https://booking.nokair.com/en/ta',
        }
        data = {"username": self.username, "password": self.password, "languageCode": "en-us"}
        booking_DD_logger.info(f'账户，密码{data}')
        res = self.post(url=login_url, headers=headers, data=json.dumps(data))
        booking_DD_logger.info(f"登陆成功Authorization:{res.json()}")
        if res.status_code == 200:
            self.Authorization = res.headers.get('X-AuthorizationToken')
            self.iata_code = res.json()['travelAgent']['agency']['iataCode']
            self.first_name = res.json()['travelAgent']['firstName']
            booking_DD_logger.info(f"登陆成功Authorization:{self.Authorization}")
        else:
            booking_DD_logger.error(f"登陆失败。。。")
            raise Exception('登陆失败。。。')

    def flight_check(self, payOrder):
        depTime = datetime.strptime(self.flight['departureDate'], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M')
        if self.holdTask.departTime != depTime:
            pay_order_log(payOrder['apiSystemUuid'], '航变', 'Trident', f"old:{self.holdTask.departTime} new:{depTime}")
            raise Exception(f'{self.holdTask.orderCode} 航变 old:{self.holdTask.departTime} new:{depTime}')

    def find_flight(self):
        flights = self.ticket_info['routes'][0]['flights']
        booking_DD_logger.info(f"抓取结果:{flights}")
        fs = []
        for f in flights:
            flight_number = f['carrierCode'] + f['flightNumber']
            departureDate = datetime.strptime(f['departureDate'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            tmp = [fare['price'] for fare in f['fares'] if fare['soldOut'] != True]
            if len(tmp) <= 0:
                continue
            this_er = get_exchange_rate_carrier('DD', self.currency)
            min_ = this_er * min(tmp)
            if self.holdTask.flightNumber == flight_number and self.holdTask.departDate == departureDate and (
                    self.holdTask.targetPrice + 5) * (self.holdTask.adt_count + self.holdTask.chd_count) >= min_:
                fs.append(f)
        if len(fs) == 0:
            raise Exception('未找到相应航班！')
        else:
            dict_ = {}
            for fl in fs:
                tmp = [fare['price'] for fare in fl['fares'] if fare['soldOut'] != True]
                dict_[min(tmp)] = fl
            prices = list(dict_.keys())
            self.min_price = min(prices)
            self.flight = dict_[self.min_price]

    def select_flight(self):
        select_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/Availability/SearchShop'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'X-UserIdentifier': 'kAJkEIqAF7wyyyoZly4YmZsKAl9lUR',
            'Host': 'api-production-nokair-booksecure.ezyflight.se',
            'Content-Type': 'application/json;charset=UTF-8',
            'Tenant-Identifier': self.apikey,
            'Origin': 'https://booking.nokair.com',
            'Referer': 'https://booking.nokair.com/en/',
            'Authorization': 'bearer ' + self.Authorization,
            'languageCode': 'en-us',
        }
        data = {"passengers": [{"code": "ADT", "count": self.holdTask.adt_count},
                               {"code": "CHD", "count": self.holdTask.chd_count},
                               {"code": "INF", "count": 0}], "routes": [
            {"fromAirport": self.holdTask.origin, "toAirport": self.holdTask.destination,
             "departureDate": self.holdTask.departDate,
             "startDate": str(
                 datetime.date(datetime.strptime(self.holdTask.departDate, "%Y-%m-%d"))),
             # self.holdTask.departDate,
             "endDate": str(
                 datetime.date(datetime.strptime(self.holdTask.departDate, "%Y-%m-%d")))}],
                "currency": "THB", "fareTypeCategories": '',
                "isManageBooking": 'false', "promoCode": self.promo_code, "languageCode": "zh-cn"}
        booking_DD_logger.info(f"开始请求{select_url}")
        ticket_res = self.post(url=select_url, headers=headers, data=json.dumps(data))
        # ticket_res.encoding = 'gbk'
        if ticket_res.status_code == 200:
            self.ticket_info = ticket_res.json()
            self.currency = self.ticket_info['currency']
        else:
            booking_DD_logger.error('ticket_info获取失败..')
            raise Exception('ticket_info获取失败..')

    def get_pre_data(self):
        try:
            passengers = []
            passengerFares = []
            selectedFare = [i for i in self.flight['fares'] if i['price'] == self.min_price][0]
            fare_id = selectedFare['id']
            fareTypes = [i for i in self.flight['fareTypes'] if i['fares'][0]['id'] == fare_id][0]
            fare = fareTypes['fares'][0]
            legs = self.flight['legs'][0]
            for p in self.holdTask.current_passengers:
                baggage = int(p.baggageMessageDO.baggageWeight) if p.baggageMessageDO else 0
                if baggage > 0:
                    services = [{
                        'code': "BG" + str(baggage),
                        'flightId': self.flight['id'],
                        'isFareBundle': False,
                        'isFromServiceBundle': False,
                        'isServiceBundleSsr': False,
                    }]
                else:
                    services = []
                person = {}
                if p.passenger_type == 'ADT':
                    firstname = p.first_name
                    lastname = p.last_name
                    person['passengerTypeCode'] = p.passenger_type
                    person['id'] = "ADT_" + self.random_char()
                    person['passengerTypeNamePlural'] = "adults"
                    if p.sex == 'M':
                        person['title'] = 'MR'
                    else:
                        person['title'] = 'MISS'
                else:
                    person['passengerTypeCode'] = p.passenger_type
                    person['id'] = "CHD_" + self.random_char()
                    person['passengerTypeNamePlural'] = "children"
                    if p.sex == 'M':
                        person['title'] = 'MSTR'
                    else:
                        person['title'] = 'MISS'
                tmp = {"passengerTypeCode": p.passenger_type, "id": person['id'], "associateWithPassengerId": '',
                       "selectedTravelCompanionId": '', "title": person['title'], "firstName": p.first_name,
                       "middleName": "",
                       "lastName": p.last_name, "dateOfBirth": p.birthday_format('%Y-%m-%d'), "gender": p.sex,
                       "mobileNumber": "",
                       "email": "", "frequentFlyerNumber": "", "documentNumber": "", "redressNumber": "",
                       "knownTravelerNumber": "", "height": "", "weight": "", "seats": [],
                       "services": services,
                       "contactInformation": {"address": "", "address2": "", "city": "", "country": "",
                                              "state": "", "phoneNumber": "+8618611715578",
                                              "workPhoneNumber": "", "postal": "",
                                              "email": "nevergiveup17apr04@qq.com", "fax": ""},
                       "apisInfo": {"nationality": "", "residenceCountry": "", "documentNumber": "",
                                    "issuedBy": "", "passportExpireDate": "", "destinationCountry": "",
                                    "destinationPostal": "", "destinationState": "", "destinationCity": "",
                                    "destinationAddress": "", "documentNumber2": "", "documentType2": "",
                                    "document2IssuedBy": "", "document2ExpireDate": ""}}
                tmp_ = {"passengerId": person['id'], "passengerTypeCode": p.passenger_type,
                        "passengerTypeName": p.passengerType.lower(),
                        "passengerTypeNamePlural": person['passengerTypeNamePlural'], "fareName": fareTypes['name'],
                        "farePrice": fare['price'],
                        "farePriceWithoutTax": fare['priceWithoutTax'], "fareDiscount": fare['discount']}
                passengers.append(tmp)
                passengerFares.append(tmp_)
            data = {"contact": {"address": "Missing Address", "address2": "Missing Address2", "city": "Missing City",
                                "country": "TH", "state": "NA", "phoneNumber": "+8618611715578", "workPhoneNumber": "",
                                "postal": "00000", "email": "nevergiveup17apr04@qq.com", "fax": ""},
                    "emergencyContact": {"firstName": firstname, "lastName": lastname,
                                         "reference": "+8618611715578",
                                         "referenceType": 0}, "flights": [
                    {"route": 0, "key": self.flight['key'], "id": self.flight['id'], "carrierCode": "DD",
                     "flightNumber": self.flight['flightNumber'],
                     "selectedFare": selectedFare,
                     "fareId": fare['id'], "fareBasis": fare['fareBasis'],
                     "departureDate": self.flight['departureDate'], "arrivalDate": self.flight['arrivalDate'],
                     "from": self.flight['from'], "to": self.flight['to'],
                     "isInternational": 'false', "passengerFares": passengerFares,
                     "price": fare['price'], "priceWithoutTax": fare['priceWithoutTax'],
                     "legs": [
                         {"id": legs['id'], "departureDate": legs['departureDate'], "flightTime": legs['flightTime'],
                          "flightNumber": legs['flightNumber'],
                          "equipmentType": legs['equipmentType'], "carrierCode": "DD", "legType": legs['legType']}],
                     "cabin": self.flight['cabin']}],
                    "passengers": passengers,
                    "currency": self.currency,
                    "fareTypeCategories": '', "promoCode": self.promo_code, "tracking": {},
                    "isExternallyPriced": 'false',
                    "invoiceDetails": '', "languageCode": "en-us"}
            return data
        except Exception as e:
            raise Exception('prebook fail{}'.format(e))

    def prebook(self):
        prebook_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/Booking/PreBook'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'X-UserIdentifier': 'kAJkEIqAF7wyyyoZly4YmZsKAl9lUR',
            'Host': 'api-production-nokair-booksecure.ezyflight.se',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Access-Control-Allow-Origin': '*',
            'Tenant-Identifier': self.apikey,
            'Origin': 'https://booking.nokair.com',
            'Authorization': 'bearer ' + self.Authorization,
            'languageCode': 'en-us',
        }
        data = self.get_pre_data()
        booking_DD_logger.info(f"开始请求{prebook_url}{data}")
        prebook_res = self.post(url=prebook_url, headers=headers, data=json.dumps(data))
        # ticket_res.encoding = 'gbk'
        booking_DD_logger.info(f"prebook_res结果：{prebook_res.status_code}{prebook_res.json()}")
        if prebook_res.status_code == 200:
            self.prebook_res = prebook_res.json()
            self.SessionToken = prebook_res.headers['SessionToken']
            self.endprice = self.prebook_res['totalPrice']
        else:
            booking_DD_logger.error(f'prebook_res获取失败..')
            raise Exception('prebook_res获取失败..')

    def AssessPaymentMethodFees(self):
        AssessPaymentMethodFees_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/Payment/AssessPaymentMethodFees'
        headers = {
            'Host': 'api-production-nokair-booksecure.ezyflight.se',
            'X-UserIdentifier': 'kAJkEIqAF7wyyyoZly4YmZsKAl9lUR',
            'Access-Control-Allow-Origin': '*',
            'Authorization': 'bearer ' + self.Authorization,
            'Content-Type': 'application/json;charset=UTF-8',
            'AppContext': 'ibe',
            'Accept': 'text/plain',
            'SessionToken': self.SessionToken,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'Tenant-Identifier': self.apikey,
            'languageCode': 'en-us',
            'Origin': 'https://booking.nokair.com',
            'Referer': 'https://booking.nokair.com/en/payment',
        }
        data = {"providerId": "invoice", "paymentMethodId": "internal:invoice", "amount": self.endprice,
                "currency": self.currency, "areSeatsCached": False,
                "routes": [{"origin": self.holdTask.origin, "destination": self.holdTask.destination}],
                "isModified": False, "languageCode": "en-us"}
        booking_DD_logger.info(f"开始请求{AssessPaymentMethodFees_url}{data}")
        AssessPaymentMethodFees_res = self.post(url=AssessPaymentMethodFees_url, headers=headers, data=json.dumps(data))
        # ticket_res.encoding = 'gbk'
        booking_DD_logger.info(
            f"AssessPaymentMethodFees_res结果：{AssessPaymentMethodFees_res.status_code}{AssessPaymentMethodFees_res.json()}")
        if AssessPaymentMethodFees_res.status_code == 200:
            self.prebook_res = AssessPaymentMethodFees_res.json()
        else:
            booking_DD_logger.error(f'AssessPaymentMethodFees_res获取失败..')
            raise Exception('AssessPaymentMethodFees_res获取失败..')

    def create(self):
        create_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/Booking/Create'
        headers = {
            'Host': 'api-production-nokair-booksecure.ezyflight.se',
            'X-UserIdentifier': 'kAJkEIqAF7wyyyoZly4YmZsKAl9lUR',
            'Access-Control-Allow-Origin': '*',
            'Authorization': 'bearer ' + self.Authorization,
            'Content-Type': 'application/json;charset=UTF-8',
            'AppContext': 'ibe',
            'Accept': 'text/plain',
            'SessionToken': self.SessionToken,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'Tenant-Identifier': self.apikey,
            'languageCode': 'en-us',
            'Origin': 'https://booking.nokair.com',
            'Referer': 'https://booking.nokair.com/en/payment',
        }
        data = self.get_pre_data()
        booking_DD_logger.info(f"开始请求{create_url}{data}")
        create_res = self.post(url=create_url, headers=headers,
                               data=json.dumps(data), is_retry=False)
        # ticket_res.encoding = 'gbk'
        booking_DD_logger.info(f"create_res结果：{create_res.status_code}{create_res.json()}")
        if create_res.status_code == 200:
            self.prebook_res = create_res.json()
            self.pnr = self.prebook_res['confirmationNumber']
            self.webBookingId = self.prebook_res['webBookingId']
        else:
            booking_DD_logger.error(f'create_res获取失败..')
            raise Exception('create_res获取失败..')

    def pay(self):
        pay_url = 'https://api-production-nokair-booksecure.ezyflight.se/api/v1/Payment/Process'
        headers = {
            'Host': 'api-production-nokair-booksecure.ezyflight.se',
            'X-UserIdentifier': 'kAJkEIqAF7wyyyoZly4YmZsKAl9lUR',
            'Access-Control-Allow-Origin': '*',
            'Authorization': 'bearer ' + self.Authorization,
            'Content-Type': 'application/json;charset=UTF-8',
            'AppContext': 'ibe',
            'Accept': 'text/plain',
            'SessionToken': self.SessionToken,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'Tenant-Identifier': self.apikey,
            'languageCode': 'en-us',
            'Origin': 'https://booking.nokair.com',
            'Referer': 'https://booking.nokair.com/en/payment',
        }
        data_order = self.get_pre_data()
        last_name = data_order['emergencyContact']['lastName']
        if not self.pnr:
            raise Exception('pay获取失败..')
        data = {"card": {"cardHolder": "", "cardNumber": "", "cvc": "", "expiryMonth": "05", "expiryYear": "2020"},
                "address": "", "address2": "", "city": "", "postal": "", "state": "", "country": "CN",
                "firstName": self.first_name, "lastName": "-", "email": "", "mobileNumber": "",
                "confirmationNumber": self.pnr, "amount": self.endprice, "paymentMethodId": "internal:invoice",
                "providerId": "invoice", "metaData": {}, "currency": self.currency, "bookingLastName": last_name,
                "iataCode": self.iata_code, "basePaymentAmount": self.endprice, "baseCurrency": self.currency,
                "exchangeRate": 1, "isModifyPayment": True, "hasPaymentFee": True, "signUpToNewsletter": False,
                "areSeatsCached": False, "receiptLanguageCode": "en-us", "firebaseCloudMessagingToken": "",
                "successUrl": "https://booking.nokair.com/en/confirmation?confirmationNumber=" + self.pnr + "&digest=9D5CCC13D39A77FE65E023B55CAC45E7964C48D8076EF1364EC200D3F81651BB",
                "failureUrl": "https://booking.nokair.com/en/payment?failed=true", "vouchers": [],
                "languageCode": "en-us"}
        booking_DD_logger.info(f"开始请求{pay_url}{data}")
        pay_res = self.post(url=pay_url, headers=headers,
                            data=json.dumps(data), is_retry=False)
        # ticket_res.encoding = 'gbk'
        booking_DD_logger.info(f"pay_res结果：{pay_res.status_code}{pay_res.json()}")
        if pay_res.status_code == 200:
            if pay_res.json()['success']:
                return
            else:
                raise Exception('pay_res获取失败..')
        else:
            booking_DD_logger.error(f'pay_res获取失败..')
            raise Exception('pay_res获取失败..')

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
                "payTicketPrice": self.endprice,
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
                "bookingId": self.webBookingId
            },
            "code": 0,
            "type": 1,
            "address": '',
            "taskstep": "login"
        }
