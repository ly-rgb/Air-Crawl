import collections
import re
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_2I_logger
from utils.searchparser import SearchParam


class A2IWeb(AirAgentV3Development):
    """https://www.starperu.com/ 不支持多天"""
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded"
        }

    def search(self, searchParam: SearchParam):
        body = {
            "tipo_viaje": "O",
            "origen": searchParam.dep,
            "destino": searchParam.arr,
            "date_from": datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%d/%m/%Y"),
            "date_to": datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%d/%m/%Y"),
            "cant_adultos": searchParam.adt,
            "cant_ninos": "0",
            "cant_infantes": "0",
            "codigo_desc": ""
        }
        response = self.post(url="https://www.starperu.com/Booking1", data=body, headers=self._headers)
        self.search_response = response

    def fare(self, body):
        url = "https://www.starperu.com/Booking1/ObtenerTarifas"
        response = self.post(url=url, headers=self._headers, data=body)
        html = self.etree.HTML(response.text)
        adultprice = html.xpath("//div[@class='text-danger col-md-5']/text()")[0].split()[1]
        cur = html.xpath("//div[@class='text-danger col-md-5 h2']/text()")[0]
        tax = html.xpath("//div[@class='text-danger col-md-5']/text()")[1].split()[1]
        return adultprice, cur, tax

    def convert_search(self):
        results = []
        html = self.etree.HTML(self.search_response.content)
        dep = html.xpath("//input[@name='origen']/@value")[0]
        arr = html.xpath("//input[@name='destino']/@value")[0]
        for segment in html.xpath("//table[@class='table reservas']//tr"):
            value = segment.xpath(".//input[@id='exampleRadios2']/@value")
            if not value:
                continue
            value = value[0]
            value1 = value.split("|")
            deptime = re.sub("-| |:", "", value1[3])
            arrtime = re.sub("-| |:", "", value1[4])
            number = value1[2]
            flightnumber = "2I" + str(int(number))
            cabin = segment.xpath("normalize-space(substring-after(.//a[@class='dropdown-toggle']/text(),':'))")[0]
            fromSegments = {
                "carrier": "2I",
                "flightNumber": flightnumber,
                "depAirport": dep,
                "depTime": deptime,
                "arrAirport": arr,
                "arrTime": arrtime,
                "codeshare": False,
                "cabin": cabin,
                "num": 0,
                "aircraftCode": "",
                "segmentType": 0
            }
            body = {
                "cod_origen": dep,
                "cod_destino": arr,
                "cant_adl": "1",
                "cant_chd": "0",
                "cant_inf": "0",
                "codigo_desc": "",
                "fecha_ida": value1[4].split()[0],
                "fecha_retorno": value1[3].split()[0],
                "tipo_viaje": "O",
                "grupo_retorno": "",
                "grupo_ida": value
            }
            adultprice, cur, tax = self.fare(body)
            item = {
                "data": flightnumber,
                "productClass": "ECONOMIC",
                "fromSegments": [fromSegments],
                "cur": cur,
                "adultPrice": adultprice,
                "adultTax": tax,
                "childPrice": 0,
                "childTax": 0,
                "promoPrice": 0,
                "adultTaxType": 0,
                "childTaxType": 0,
                "priceType": 0,
                "applyType": 0,
                "max": 0,
                "limitPrice": True,
                "info": "data_value"
            }
            results.append(item)
        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = A2IWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_2I_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
