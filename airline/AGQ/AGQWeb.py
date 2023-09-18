import collections
import re
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_GQ_logger
from utils.searchparser import SearchParam
import json


class AGQWeb(AirAgentV3Development):
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._headers = {
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
        }

    def search_body(self, searchParam):
        """https://www.skyexpress.gr/el"""
        date2 = searchParam.date
        if 'CRAWlLCC' in searchParam.args:
            date2 = (datetime.strptime(searchParam.date, "%Y-%m-%d")
                     + timedelta(days=5)).strftime('%Y-%m-%d')
        body = {
            "interline": False,
            "fromCityCode": searchParam.dep,
            "toCityCode": searchParam.arr,
            "departureDateString": searchParam.date,
            "returnDateString": date2,
            "startDateStringOutbound": searchParam.date,
            "endDateStringOutbound": date2,
            "adults": searchParam.adt,
            "children": 0,
            "infants": 0,
            "roundTrip": False,
            "useFlexDates": True,
            "isOutbound": True,
            "filterMethod": "100",
            "currency": "EUR",
            "languageCode": "el-GR",
            "fareTypeCategory": 1,
        }
        return json.dumps(body, indent=1)

    def search(self, searchParam: SearchParam):
        response = self.post(url="https://bookings.skyexpress.gr/Api/AvailablityRequest/Post",
                             data=self.search_body(searchParam), headers=self._headers)
        self.search_response = response

    def convert_search(self):
        results = []
        for flight in self.search_response.json()["Availability"]["OutboundSegments"]:
            fromsegments = []
            flight_numbers = []

            fare_obj = list(filter(lambda x:x["Fares"][0]["SeatCount"] > 0,  flight["FaresTypes"]))
            if fare_obj:
                fare_obj = fare_obj[0]["Fares"][0]
            else:
                continue

            for leg in flight["Legs"]:
                flight_number = leg["Carrier"]["Code"] + str(int(leg["FlightNumber"]))
                flight_numbers.append(flight_number)
                fromsegment = {
                    'carrier': leg["Carrier"]["Code"],
                    'flightNumber': flight_number,
                    'depAirport': leg["Origin"]['Code'],
                    'depTime': datetime.strptime(leg["Departure"], '%Y-%m-%dT%H:%M:%S').strftime("%Y%m%d%H%M"),
                    'arrAirport': leg["Destination"]['Code'],
                    'arrTime': datetime.strptime(leg["Arrival"], '%Y-%m-%dT%H:%M:%S').strftime("%Y%m%d%H%M"),
                    'codeshare': False,
                    'cabin': "Y",
                    'num': 0,
                    'aircraftCode': flight["AirCraftDescription"],
                    'segmentType': 0
                }
                fromsegments.append(fromsegment)
            data = {
                'data': "/".join(flight_numbers),
                'productClass': "ECONOMIC",
                'fromSegments': fromsegments,
                'cur': flight["FaresTypes"][0]["Fares"][0]["Currency"],
                'adultPrice': fare_obj["Amount"],
                'adultTax': fare_obj["AmountIncludingTax"] - fare_obj["Amount"],
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': fare_obj["SeatCount"],
                'limitPrice': True,
                'info': ""
            }
            results.append(data)
        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AGQWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_GQ_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
