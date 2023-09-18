# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AZ9Baggage.py
@effect: "请填写用途"
@Date: 2023/1/5 10:20
"""
from airline.baggage import Baggage
from airline.base import AirAgentV4
from native.api import get_exchange_rate_carrier
from utils.log import add_on_Z9_logger
from robot.model import HoldTask
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal


class AZ9Baggage(AirAgentV4):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=add_on_Z9_logger, task=None):
        super(AZ9Baggage, self).__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout,
                                         logger=logger, task=task)

        self.search_url = 'https://api.myairline.my/api/v1/flight/searchflight'
        self.get_baggage_url = 'https://api.myairline.my/api/v1/checkout/verifyflight'
        self.currency = "MYR"
        self.promo_code = ""
        self._key = dict()
        self._flight_price = dict()

    @property
    def base_header(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        return headers

    def booking_availability(self):

        depart_time = datetime.strptime(self.task.departDate, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00.000Z")

        json_data = {
            'searchFlightRequest': {
                'OriginAirport': self.task.origin,
                'DestinationAirport': self.task.destination,
                'DepartDate': depart_time,
                'ReturnDate': depart_time,
                'Adults': self.task.adt_count,
                'Childrens': self.task.chd_count,
                'Infants': '0',
                'IsReturn': False,
                'TripType': 'One Way',
                'Currency': self.currency,
                'PromoCode': self.promo_code,
            },
        }

        self.logger.info(f"开始请求: {self.search_url}")
        response = self.post(url=self.search_url, headers=self.base_header,
                             json=json_data)
        if response.status_code == 200:
            is_error = list(response.json().keys())
            if "error" not in is_error:
                self.availability_result = response.json().get("result", None)
                self.logger.info(f"所有航班信息: {self.availability_result}")
        else:
            self.logger.error(f"查找航班失败... data: {json_data}\n"
                              f" url: {self.search_url}")
            raise Exception("查找航班失败...")

    def convert_search(self):

        result = []

        def func(flight):
            from_segment_list = []

            # 提取航班信息
            carrier = flight["segmentDetail"]["carrierCode"]
            flight_num = flight["segmentDetail"]["flightNum"]
            dep = flight["segmentDetail"]["origin"]
            arr = flight["segmentDetail"]["destination"]
            dep_time = datetime.strptime(flight["segmentDetail"]["departureDate"],
                                         "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
            arr_time = datetime.strptime(flight["segmentDetail"]["arrivalDate"],
                                         "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
            adult_price = flight["adultPriceTotal"] / (self.task.adt_count + self.task.chd_count) -1
            self.flights[f"{carrier}{flight_num}"] = flight
            self._key[f"{carrier}{flight_num}"] = {"LFID": flight["lfid"],
                                                   "FBCode": flight["fbCode"]}
            self._flight_price.update({
                f"{carrier}{flight_num}": str(Decimal(adult_price + 1).quantize(Decimal("0.00")))
            })

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
            from_segment_list.append(from_segment)
            self.logger.info(f"提取的航班信息: {from_segment}")
            self.logger.info(f"提取到的_key: {self._key}")
            self.logger.info(f"提取到的_flight_price: {self._flight_price}")

            data = {
                'data': carrier + flight_num,
                'productClass': 'ECONOMIC',
                'fromSegments': from_segment_list,
                'cur': self.currency,
                'adultPrice': adult_price,
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

            self.logger.info(f"data信息: {data}")
            result.append(data)

        ths = ThreadPoolExecutor(max_workers=10)
        list(ths.map(func, self.availability_result['searchFlightResponse']["flightResult"]["outboundSegment"]))
        return result

    def select_flight(self):
        self.logger.info("select flight")
        self.flight = self.flights.get(self.task.flightNumber, None)
        if not self.flight:
            raise Exception(f"未找到该航班...")

    def verify_flight(self):
        self.logger.info("进入verify")
        depart_time = datetime.strptime(self.task.departDate, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00.000Z")

        json_data = {
            'flightVerifyRequest': {
                'OriginAirport': self.task.origin,
                'DestinationAirport': self.task.destination,
                'DepartDate': depart_time,
                'ReturnDate': depart_time,
                'Adults': len(self.task.adt_with_age(12)),
                'Childrens': len(self.task.chd_with_age(12, inf_age=12)),
                'Infants': '0',
                'IsReturn': False,
                'TripType': 'One Way',
                'Currency': self.currency,
                'PromoCode': self.promo_code,
                'TotalAmount': self._flight_price[self.task.flightNumber],
                'OutboundFares': [
                    self._key[self.task.flightNumber]
                ],
                'InboundFares': [],
            },
        }

        add_on_Z9_logger.info(f"开始获取行李信息: {self.get_baggage_url}")
        response = self.post(url=self.get_baggage_url, headers=self.base_header,
                             json=json_data)
        if response.status_code == 200:
            is_error = list(response.json().keys())
            if "error" not in is_error:
                self.baggage_result = response.json().get("result", None)
                self.logger.info("获取行李信息成功...")
        else:
            self.logger.error(f"查找行李信息失败... data: {json_data}\n"
                              f" url: {self.search_url}\n"
                              f"baggage_response: {response.text}")
            raise Exception("查找航班失败...")

    def get_baggage_list(self):
        bag_list = []
        er = get_exchange_rate_carrier('Z9', self.currency)
        for x in sorted(list(map(lambda a: a, self.baggage_result["flightSSR"]["baggageGroup"]["outbound"])),
                        key=lambda a: a["ssrCode"]):
            if x["ssrCode"] == "NOSELECT":
                continue
            else:
                weight = int(str(x["ssrCode"].replace("BG", "")))
                basic_price = round(x["amount"] + x['applicableTaxes'][0]["taxAmount"], 2)
                price = round(er * basic_price, 2)
                bag_list.append(Baggage(weight, price, x, basic_price, self.currency))

        self.logger.info(f"提取到的行李列表: {bag_list}")

        return bag_list

