import time
import uuid
import random
from datetime import datetime

from robot import HoldTask
from airline.baggage import Baggage
from utils.log import robot_VB_logger
from airline.AVB.cookies_pool import cookies_pool
from airline.base import AirAgentV3Development
from concurrent.futures import ThreadPoolExecutor


class AVBApp(AirAgentV3Development):
    urls = {
        'ceb_omnix_proxy': 'https://api.vivaaerobus.com/web/v1/availability'
                           '/search'
    }

    def __init__(self, proxies_type=0, retry_count=10, timeout=120):
        super().__init__(proxies_type, retry_count, timeout,
                         logger=robot_VB_logger)

    @staticmethod
    def get_headers():
        cookie = cookies_pool.get(random.randint(0, 162))
        headers = {
            'Cookie': cookie,
            'Origin': 'https://www.vivaaerobus.com',
            'x-api-key': 'zasqyJdSc92MhWMxYu6vW3hqhxLuDwKog3mqoYkf'
        }
        return headers

    def bookingAvailability(self, holdTask: HoldTask):
        self.holdTask = holdTask
        self.currencyCode = "MXN"

        data = {
            "currencyCode": "MXN",
            "language": "en-US",
            "routes": [
                {
                    "date": holdTask.departDate,
                    "origin": {
                        "code": holdTask.origin,
                        "type": "Airport"
                    },
                    "destination": {
                        "code": holdTask.destination,
                        "type": "Airport"
                    }
                }
            ],
            "passengers": [
                {
                    "code": "ADT",
                    "count": len(holdTask.adt_with_age(12))
                }, {
                    "code": "CHD",
                    "count": len(holdTask.chd_with_age(12, inf_age=2))
                }, {
                    "code": "INFT",
                    "count": len(holdTask.chd_with_age(12, inf_age=2))
                }
            ],
            "deviceId": str(uuid.uuid4())
        }
        url = self.urls['ceb_omnix_proxy']
        headers = self.get_headers()
        resp = self.post(url, headers=headers, json=data)
        self.logger.info(f'抓数的响应状态码为{resp.status_code}')
        time.sleep(3.2)
        if resp.status_code >= 300:
            raise Exception(f"[resp] ==> {resp.status_code}")

        self.availability_result = resp.json()
        self.logger.info(f'抓到的所有结果为{self.availability_result}')
        self.currencyCode = resp.json()['data']['currencyCode']

    def convert_search(self):

        self.flights = {}
        result = []

        def func(journey):
            flight_no = []
            fromSegments = []
            for segment in journey['segments']:
                flightNumber = segment['flightNumber']
                flight_no.append(flightNumber)
                fromSegments.append({
                    "carrier": segment['operatingCarrier'],
                    "flightNumber": flightNumber,
                    "depAirport": segment['origin']['code'],
                    "depTime": datetime.strptime(segment['departureDate'],
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "arrAirport": segment['destination']['code'],
                    "arrTime": datetime.strptime(segment['arrivalDate'],
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "codeshare": False,
                    "cabin": segment['cabinAmenities'] or "Y",
                    "num": 0,
                    "aircraftCode": "",
                    "segmentType": 0
                })
            self.flights["/".join(flight_no)] = journey
            try:
                adultPrice = journey['fares'][0]['fare']['amount']
            except:
                adultPrice = journey['fares']
            try:
                max = journey['fares'][0]['availableCount']
            except:
                max = 0

            item = {
                'data': '/'.join(flight_no),
                'productClass': 'ECONOMIC',
                'fromSegments': fromSegments,
                'cur': self.currencyCode,
                'adultPrice': adultPrice,
                'adultTax': 0,
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': max,
                'limitPrice': True,
                'info': ''
            }
            result.append(item)

        ths = ThreadPoolExecutor(max_workers=10)
        list(ths.map(func,
                     self.availability_result['data']['routes'][0]['journeys']))
        self.logger.info(f'抓到的所有航班为{result}')
        return result

    def selectFlight(self, holdTask: HoldTask):
        self.flight = self.flights.get(holdTask.flightNumber, None)
        if not self.flight:
            raise Exception(
                f"未找到航班: {holdTask.flightNumber}, 当前航班: {self.flights}")

    def get_basket_id(self):
        url = 'https://api.vivaaerobus.com/web/v1/basket/create'
        headers = {
            'x-api-key': 'zasqyJdSc92MhWMxYu6vW3hqhxLuDwKog3mqoYkf'
        }
        data = {
            "currencyCode": "MXN",
            "language": "en-US",
            "currentStep": "Flights",
            "customFields": {
                "tij2TjxSwitch": False,
                "checkInPassengers": [],
                "checkInNextView": "",
                "bookingSeats": None,
                "checkInPaidCharges": None,
                "passengerChanges": None,
                "availabilityJourneyKeys": [],
                "availabilitySearchType": None,
                "bfHotelsOfferAvailable": False,
                "Boxever": {
                    "trackingId": "",
                    "browserId": ""
                },
                "preSelectedServices": []
            },
            "referralDetails": {
                "code": ""
            },
            "bookingType": None,
            "engine": {
                "deviceId": str(uuid.uuid4())
            },
            "device": "desktop",
            "location": {
                "country": "MX",
                "city": "DALLAS",
                "lat": "31.2624899",
                "long": "120.63212"
            }
        }
        basket_id = \
            self.post(url=url, headers=headers, json=data).json()['data'][
                'basketId']
        time.sleep(2)
        self.logger.info(f'获取到的basketId为{basket_id}')
        return basket_id

    def get_journeys(self, basket_id):
        url = 'https://api.vivaaerobus.com/web/v1/booking/journeys'
        headers = {
            'x-api-key': 'zasqyJdSc92MhWMxYu6vW3hqhxLuDwKog3mqoYkf'
        }
        data = {
            "basketId": basket_id,
            "journeys": [
                {
                    "journeyKey": self.flight['key'],
                    "fareAvailabilityKey": self.flight['lowestFareKey'],
                    "origin": {
                        "code": self.flight['origin']['code'],
                        "type": "Airport"
                    },
                    "destination": {
                        "code": self.flight['destination']['code'],
                        "type": "Airport"
                    }
                }
            ],
            "passengers": [
                {
                    "code": "ADT",
                    "count": 1
                }
            ],
            "isVivaFan": False
        }
        self.post(url=url, headers=headers, json=data).json()
        time.sleep(1.46)

    def get_bag_list(self, basket_id):
        # false = False
        # true = True
        # null = None
        url = 'https://api.vivaaerobus.com/web/v1/booking/availableservices'
        headers = {
            'x-api-key': 'zasqyJdSc92MhWMxYu6vW3hqhxLuDwKog3mqoYkf'
        }
        params = {
            'basketId': basket_id
        }
        resp = self.get(url=url, headers=headers, params=params)
        try:
            resp.status_code != 200
        except:
            self.logger.info(f'行李请求的状态码为{resp.status_code}')
        bag_data = resp.json()['data']['services'][1]['options']
        self.logger.info(f'bag为{bag_data}')
        bag_list = []
        for i in bag_data:
            weight = i['name'].split(' ')[0]
            if weight == 'Sport':
                break
            if weight == 'Music':
                break
            # if 'Kg' not in weight:
            #     break
            price = i['price']['amount']
            bag_list.append(
                Baggage(weight, price, self.flight, price, self.currencyCode))
        self.logger.info(f'获取到的bag_list为{bag_list}')
        return bag_list
