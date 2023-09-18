import json
import re
import time
from datetime import datetime, timedelta
from typing import Any, Union, Dict
from lxml import etree
from requests.models import Response
from airline.base import AirAgentV3Development, pay_error_result
from robot import HoldTask
from utils.log import spider_LS_logger
from utils.redis import redis_52
from utils.searchparser import SearchParam


class ALSWeb(AirAgentV3Development):
    """https://www.jet2.com/"""
    search_response: Response

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}
        self._headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
        }

        self.maps = {'ABZ': 'aberdeen', 'BYF': 'albert', 'ALC': 'alicante', 'LEI': 'almeria', 'AMS': 'amsterdam', 'AYT': 'antalya', 'ATH': 'athens', 'AVN': 'avignon-provence', 'BCN': 'barcelona', 'BFS': 'belfast', 'EGC': 'bergerac', 'BER': 'berlin', 'SXF': 'berlinsxf', 'BHX': 'birmingham', 'BLK': 'blackpool', 'BJV': 'bodrum', 'BOJ': 'bourgas', 'BRS': 'bristol', 'BUD': 'budapest', 'CMF': 'chambery', 'CGN': 'cologne', 'CPH': 'copenhagen', 'CFU': 'corfu', 'CHQ': 'crete-chania', 'HER': 'crete', 'DLM': 'dalaman', 'BVE': 'dordogne-valley-brive', 'DBV': 'dubrovnik', 'DUS': 'dusseldorf', 'EMA': 'east-midlands', 'EDI': 'edinburgh', 'FAO': 'faro', 'FDH': 'friedrichshafen', 'FUE': 'fuerteventura', 'GVA': 'geneva', 'GRO': 'girona', 'GLA': 'glasgow', 'LPA': 'gran-canaria', 'GNB': 'grenoble', 'HRG': 'hurghada', 'IBZ': 'ibiza', 'INN': 'innsbruck', 'IST': 'istanbul', 'ADB': 'izmir', 'JER': 'jersey', 'KLX': 'kalamata', 'EFL': 'kefalonia', 'KGS': 'kos', 'KRK': 'krakow', 'LRH': 'la-rochelle', 'ACE': 'lanzarote', 'LCA': 'larnaca', 'LBA': 'leeds-bradford', 'MJT': 'lesvos', 'LIS': 'lisbon', 'LPL': 'liverpool', 'ILD': 'lleida-andorra', 'STN': 'london-stansted', 'LYS': 'lyon', 'FNC': 'madeira', 'PMI': 'majorca', 'AGP': 'malaga', 'MLA': 'malta', 'MAN': 'manchester', 'RAK': 'marrakech', 'MAH': 'menorca', 'BGY': 'milan', 'MUC': 'munich', 'RMU': 'murcia-corvera', 'MJV': 'murcia-san-javier', 'JMK': 'mykonos', 'NAP': 'naples', 'EWR': 'new-york', 'NCL': 'newcastle', 'NQY': 'newquay', 'NCE': 'nice', 'NUE': 'nuremberg', 'PFO': 'paphos', 'CDG': 'paris', 'PSA': 'pisa', 'PRG': 'prague', 'PVK': 'preveza', 'PUY': 'pula', 'REU': 'reus', 'KEF': 'reykjavik', 'RHO': 'rhodes', 'FCO': 'rome', 'SZG': 'salzburg', 'JTR': 'santorini', 'OLB': 'sardinia', 'SSH': 'sharm-el-sheikh', 'CTA': 'sicily-catania', 'JSI': 'skiathos', 'SOF': 'sofia', 'SPU': 'split', 'LED': 'st-petersburg', 'SXB': 'strasbourg', 'TFS': 'tenerife', 'SKG': 'thessaloniki', 'TIV': 'tivat', 'TLS': 'toulouse', 'NBE': 'tunisia', 'TRN': 'turin', 'VCE': 'venice', 'VRN': 'verona', 'VIE': 'vienna', 'ZAD': 'zadar', 'ZTH': 'zante', 'MIR': 'zztunisia-monastir'}
        self.redis_cookie = None

    def get_abck(self):
        # localdate = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
        localdate = (datetime.now()).strftime("%Y_%m_%d")
        cookie = redis_52.srandmember(f'LS_abck_1.75_{localdate}')
        return cookie

    def search(self, searchParam: SearchParam):
        url = f"https://www.jet2.com/en/cheap-flights/{self.maps.get(searchParam.dep)}/{self.maps.get(searchParam.arr)}?" \
              f"from={searchParam.date}&adults={searchParam.adt}&children&infants=0&preselect=true"
        cookie = self.get_abck()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0"
                      ".9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": self.get_abck(),
            "referer": "https://www.jet2.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) A"
                          "ppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
        }
        response = self.get(url=url, headers=headers)
        ele = etree.HTML(text=response.text)
        textid = re.findall('var j2ContextId = "(.*?)";', response.text)[0]
        flight_id = ele.xpath(f"//td[@data-date='{searchParam.date}']/@data-cheapest-flight-id")[0]
        if flight_id:
            dsid = ele.xpath("//div[@class='flight-results__wrapper clearfix']/@data-dsid")[0]
            url = f"https://www.jet2.com/api/search/flightsearchresults/update?scid={textid}"
            body = {"isCalendarSelection": True, "flightId": int(flight_id), "date": searchParam.date,
                    "isOutbound": True,
                    "isFull": False, "datasource": dsid,
                    "containsPofAndNonPofFlights": False}
            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-length": "183",
                "content-type": "application/json; charset=UTF-8",
                "cookie": cookie,
                "origin": "https://www.jet2.com",
                "referer": "https://www.jet2.com/en/cheap-flights/leeds-bradford/bergerac?from=2022-07-30&adults=1&children&infants=0&preselect=true",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "x-dtpc": "3$398529257_719h18vSRHQTUROGWHTTUMHJVROBRFQRLUVVPSW-0e0",
                "x-requested-with": "XMLHttpRequest"
            }
            self.search_response = self.post(url=url, headers=headers, data=json.dumps(body))

    def convert_search(self):
        results = []
        for x in self.search_response.json()["Gtm"]["ecommerce"]["click"]["products"]:
            Segment = {
                'carrier': x["dimension6"][:2],
                'flightNumber': x["dimension6"],
                'depAirport': x["dimension4"],
                'depTime': datetime.strptime(x["dimension2"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M%S"),
                'arrAirport': x["dimension9"],
                'arrTime': datetime.strptime("Dept_2022-07-30T12:40:00_Arr_2022-07-30T15:40:00".split("_Arr_")[1],
                                             "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M%S"),
                'codeshare': False,
                'cabin': "",
                'num': 0,
                'aircraftCode': None,
                'segmentType': 0
            }
            data = {
                'data': x["dimension6"],
                'productClass': 'ECONOMIC',
                'fromSegments': [Segment],
                'cur': x["dimension17"],
                'adultPrice': x["price"],
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
                'info': str(self.search_response.cookies.get_dict())
            }
            if data.get("adultPrice") != "NULL":
                results.append(data)
        return results


def api_search(taskItem, proxies_type=35):
    result = None
    code = 0
    try:
        app = ALSWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_LS_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
