import time
from datetime import datetime

from robot import HoldTask
from airline.baggage import Baggage
from utils.log import robot_XY_logger
from airline.base import AirAgentV3Development
from concurrent.futures import ThreadPoolExecutor


class AXYApp(AirAgentV3Development):
    urls = {
        'ceb_omnix_proxy': 'https://booking.flynas.com/api/SessionCreate'
    }

    def __init__(self, proxies_type=0, retry_count=10, timeout=120):
        super().__init__(proxies_type, retry_count, timeout,
                         logger=robot_XY_logger)

    def get_session(self):
        data = {'session': {'channel': "web"}}
        url = self.urls['ceb_omnix_proxy']
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'close',
            'Content-Length': '29',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': '',
            'Host': 'booking.flynas.com',
            'Origin': 'https://booking.flynas.com',
            'Pragma': 'no-cache',
            'Referer': 'https://booking.flynas.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
            'X-Culture': 'en-US'
        }
        resp = self.post(url, headers=headers, json=data)
        self.logger.info(f'请求会话的响应状态码为{resp.status_code}')
        if resp.status_code >= 300:
            raise Exception(f"[resp] ==> {resp.status_code}")
        token = resp.headers.get('X-Session-Token')
        time.sleep(1.3)
        return token

    def bookingAvailability(self, holdTask: HoldTask, token):
        self.holdTask = holdTask
        self.currencyCode = "SAR"

        data = {
            "flightSearch": {
                "flights": [
                    {
                        "origin": holdTask.origin,
                        "destination": holdTask.destination,
                        "date": holdTask.departDate
                    }
                ],
                "adultCount": "1",
                "childCount": "0",
                "infantCount": "0",
                "selectedCurrencyCode": "SAR",
                "promoCode": "",
                "reference": "",
                "specialDiscount": "NONE",
                "flightMode": "oneway",
                "clickId": ""
            }
        }
        url = 'https://booking.flynas.com/api/FlightSearch'
        headers = {
            'Connection': 'close',
            'Cookie': '',
            'Host': 'booking.flynas.com',
            'Origin': 'https://booking.flynas.com',
            'Referer': 'https://booking.flynas.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',

            'X-Session-Token': token
        }
        resp = self.post(url=url, headers=headers, json=data)
        self.logger.info(f'抓数的响应状态码为{resp.status_code}')
        time.sleep(3.2)
        if resp.status_code >= 300:
            raise Exception(f"[resp] ==> {resp.status_code}")

        self.availability_result = resp.json()
        self.logger.info(f'抓到的所有结果为{self.availability_result}')
        self.currencyCode = resp.json()['flightsAvailability']['currencyCode']

    def convert_search(self):

        self.flights = {}
        result = []

        def func(journey):
            flight_no = []
            fromSegments = []
            for segment in journey['legs']:
                flightNumber = 'XY' + str(segment['flightNumber'])
                flight_no.append(flightNumber)
                fromSegments.append({
                    "carrier": segment['carrierCode'],
                    "flightNumber": str(flightNumber),
                    "depAirport": segment['origin'],
                    "depTime": datetime.strptime(segment['departureDate'],
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "arrAirport": segment['destination'],
                    "arrTime": datetime.strptime(segment['arrivalDate'],
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "codeshare": False,
                    "cabin": "Y",
                    "num": 0,
                    "aircraftCode": "",
                    "segmentType": 0
                })
            self.flights["/".join(flight_no)] = journey
            item = {
                'data': '/'.join(flight_no),
                'productClass': 'ECONOMIC',
                'fromSegments': fromSegments,
                'cur': self.currencyCode,
                'adultPrice':
                    journey['fares'][0]['bundleSet']['bundleOffers'][0][
                        'priceTotal'],
                'adultTax': journey['fares'][0]['bundleSet']['bundleOffers'][0][
                    'taxTotal'],
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': journey['fares'][0]['remainingSeats'],
                'limitPrice': True,
                'info': journey['journeyKey']
            }
            result.append(item)

        ths = ThreadPoolExecutor(max_workers=10)
        list(ths.map(func,
                     self.availability_result['flightsAvailability']['trips'][
                         0]['flights']))
        self.logger.info(f'抓到的所有航班为{result}')
        return result

    def selectFlight(self, holdTask: HoldTask):
        self.flight = self.flights.get(holdTask.flightNumber, None)
        if not self.flight:
            raise Exception(
                f"未找到航班: {holdTask.flightNumber}, 当前航班: {self.flights}")

    def get_flight(self, token):
        url = 'https://booking.flynas.com/api/FlightSell'
        fareKey = self.flight["fares"][0]['fareKey']
        journeyKey = self.flight["journeyKey"]
        bundleCode = self.flight["fares"][0][
            "bundleSet"][
            "bundleOffers"][0]["bundleCode"]
        key = fareKey + '|' + journeyKey + '|' + bundleCode + '|' + str(0)
        headers = {
            'Host': 'booking.flynas.com',
            'Origin': 'https://booking.flynas.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36',
            'X-Session-Token': token,
            'Connection': 'close'
        }
        json = {
            "marketSell": {
                "keys": [
                    key
                ],
                "lockPrice": 'false'
            }
        }
        resp = self.post(url=url, headers=headers, json=json)
        print(resp)
        try:
            resp.status_code != 201
        except:
            self.logger.info(f'选择航班的状态码为{resp.status_code}')

    def get_passengers(self, token):
        url = 'https://booking.flynas.com/api/BookingContacts'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'close',
            'Cookie': '',
            'Host': 'booking.flynas.com',
            'Pragma': 'no-cache',
            'Referer': 'https://booking.flynas.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
            'X-Culture': 'en-US',
            'X-Session-Token': token
        }
        json = {
            "contactInput": {
                "contactItemInfo": {
                    "mobilePhone": {
                        "code": "SA",
                        "number": "13520092394"
                    },
                    "workPhone": {
                        "code": "",
                        "number": "",
                        "phone": ""
                    },
                    "contactName": {
                        "title": "MR",
                        "first": "yong",
                        "last": "li"
                    },
                    "emailAddress": "1502143197@qq.com",
                    "smsCharged": True,
                    "notificationPreference": False
                }
            }
        }
        resp = self.post(url=url, headers=headers, json=json)
        self.logger.info(f'发送乘客的状态码为{resp.status_code}')

    def get_bag_list(self, token):
        url = 'https://booking.flynas.com/api/Baggage'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'close',
            'Cookie': '',
            'Host': 'booking.flynas.com',
            'Pragma': 'no-cache',
            'Referer': 'https://booking.flynas.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
            'X-Culture': 'en-US',
            'X-Session-Token': token
        }
        resp = self.get(url=url, headers=headers)
        bag_data = \
        resp.json()["baggageSsr"]["passengerServices"][0]["flightPartServices"][
            0]["services"]
        bag_list = []
        weight_dict = {
            'XB30': 30,
            'PDBG': 30,
            'FRAG': 25,
            'XBAG': 20,
            'NSSW': 30,
            'NSSA': 20,
            'CBBG': 10,
            'BULK': 15
        }
        for i in bag_data:
            code = i['code']
            weight = weight_dict.get(code)
            price = i['price']

            bag_list.append(
                Baggage(weight, price, self.flight, price, self.currencyCode))
        self.logger.info(f'获取到的bag_list为{bag_list}')
        return bag_list
