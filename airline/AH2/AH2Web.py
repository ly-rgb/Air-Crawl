import json
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_H2_logger


class AH2Web(AirAgentV3Development):
    """
    支持多天 无检测请求头
    https://www.skyairline.com/english
    """
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

    def search(self, searchParam: SearchParam):
        segments_ = [{"from": searchParam.dep, "to": searchParam.arr,
                      "depDate": (datetime.strptime(searchParam.date, "%Y-%m-%d") + timedelta(days=x)).strftime(
                          "%Y-%m-%d")} for x in
                     range(10)]
        if 'CRAWlLCC' not in searchParam.args:
            segments_ = segments_[:1]
        headers = {
            "Content-Type": "application/json",
            "market": "US",
            "Ocp-Apim-Subscription-Key": "7c5e268930684ab29cdefdd697439e0a"
        }

        body = {"segments": segments_,
                "passengers": {"adults": searchParam.adt, "children": 0, "babies": 0, "pets": 0},
                "currency": "USD", "filters": None}
        response = self.post(url="https://api.skyairline.com/shopping-fares/v1/fares-shop",
                             data=json.dumps(body),
                             headers=headers)
        self.search_response = response

    def convert_search(self):
        results = []
        if self.search_response.json().get('statusCode') == 400:
            return []
        for flight in self.search_response.json()["flights"]:
            Segments = []
            flightnumbers = []
            for flightLegDetails in flight["flightLegDetails"]:
                dep_time = datetime.strptime(flightLegDetails["departureDate"],
                                             "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                arr_time = datetime.strptime(flightLegDetails["arrivalDate"],
                                             "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                _flightnumber = flight["marketingCarrierCode"] + str(int(flightLegDetails["flightNumber"])).strip()
                flightnumbers.append(_flightnumber)
                Segment = {
                    'carrier': flight["marketingCarrierCode"],
                    'flightNumber': _flightnumber,
                    'depAirport': flightLegDetails["from"],
                    'depTime': dep_time,
                    'arrAirport': flightLegDetails["to"],
                    'arrTime': arr_time,
                    'codeshare': False,
                    'cabin': flight["fares"][0]["fareCode"],
                    'num': 0,
                    'aircraftCode': flightLegDetails["aircraftType"],
                    'segmentType': 0
                }
                Segments.append(Segment)

            data = {
                'data': "/".join(flightnumbers),
                'productClass': 'ECONOMIC',
                'fromSegments': Segments,
                'cur': self.search_response.json()['currency'],
                'adultPrice': float(flight["fares"][0]["fareAmount"]),
                'adultTax': float(flight["fares"][0]["fareAmountWithTaxes"]) - float(flight["fares"][0]["fareAmount"]),
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': flight["fares"][0]["seatsAvailable"],
                'limitPrice': True,
                'info': "/".join(flightnumbers)
            }
            if len(data["data"].split("/")) != len(set(data["data"].split("/"))):
                spider_H2_logger.info(f"{data['data']}经停过滤！")
            elif Segments:
                results.append(data)
        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AH2Web(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_H2_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
