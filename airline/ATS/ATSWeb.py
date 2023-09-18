import json
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_TS_logger
from utils.searchparser import SearchParam
from datetime import datetime


class ATSWeb(AirAgentV3Development):
    """https://www.airtransat.com/en-US/americas?search=flight&flightType=O
    W&gateway=AIRPORT_YUL-AIRPORT_CDG&pax=1-0-0-0"""
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
        }

    def search(self, searchParam: SearchParam):
        url = "https://bookings.airtransat.com/ts-next-gen-ux/air-lfs-external/?"
        response = self.get(url=url, headers=self._headers)
        url = "https://bookings.airtransat.com/tdprest-2/api/air/lfs?"
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json",
            "origin": "https://bookings.airtransat.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
        }
        jsn = {"originDestination": [
            {"origin": {"date": searchParam.date, "locationRef": {"uri": f"/geo/locations/A/{searchParam.dep}"}},
             "destination": {"locationRef": {"uri": f"/geo/locations/A/{searchParam.arr}"}}}],
            "preferences": {"flight": {"flexibleDates": False}, "cabin": {
                "cabinRef": {"uri": "/info/air/cabin-classes/Economy"}}},
            "pos": "TS-B2C-US", "languageCode": "en_US",
            "travelerComposition": [{"count": searchParam.adt, "typeRef": {
                "uri": "/info/traveler-types/AIR/ADT"}}]}
        self.search_response = self.post(url=url, headers=headers, json=jsn, cookies=response.cookies.get_dict())

    @staticmethod
    def get_min_price(datas, idx, airid):
        for data in datas:
            if f"/air/lfs/{airid}/itinerary-prices/{idx}" in data["uri"]:
                tax = data["totalPrice"]["baseFare"]["money"]["amount"]
                adultprice = data["totalPrice"]["tax"][0]["value"]["money"]["amount"]
                currency = data["totalPrice"]["tax"][0]["value"]["money"]["currency"]
                return adultprice, tax, currency

    def convert_search(self):
        results = []
        _json = self.search_response.json()
        for idx, itinerary in enumerate(_json["lowFareSearch"]["itinerary"]):
            segments = []
            for segment in itinerary["originDestination"][0]["flightSegment"]:
                _segment = {
                    'carrier': segment["id"].split("_")[0],
                    'flightNumber': segment["id"].split("_")[0] + segment["id"].split("_")[1],
                    'depAirport': segment["id"].split("_")[-2],
                    'depTime': datetime.strptime(segment["departure"]["date"],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                    'arrAirport': segment["id"].split("_")[-1],
                    'arrTime': datetime.strptime(segment["arrival"]["date"],
                                                 "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M"),
                    'codeshare': False,
                    'cabin': segment["bookingClassAvailability"][0]["cabinClass"],
                    'num': 0,
                    'aircraftCode': '',
                    'segmentType': 0
                }
                segments.append(_segment)
            adultTax, adultPrice, cur = self.get_min_price(_json["lowFareSearch"]["itineraryPrice"],
                                                           idx + 1, _json["lowFareSearch"]["id"])
            item = {
                "data": "/".join(list(map(lambda x: x["flightNumber"], segments))),
                "productClass": "ECONOMIC",
                "fromSegments": segments,
                "cur": cur,
                "adultPrice": adultPrice,
                "adultTax": adultTax,
                "childPrice": 0,
                "childTax": 0,
                "promoPrice": 0,
                "adultTaxType": 0,
                "childTaxType": 0,
                "priceType": 0,
                "applyType": 0,
                "max": 0,
                "limitPrice": True,
                "info": ""
            }
            results.append(item)
        return results


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0
    try:
        app = ATSWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_TS_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
