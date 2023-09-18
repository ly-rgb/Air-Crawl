import calendar
import datetime
from typing import Dict
from robot import HoldTask
from requests.models import Response
from utils.log import spider_G8_logger
from utils.searchparser import SearchParam
from airline.base import AirAgentV3Development


class AG8Web(AirAgentV3Development):
    search_response: Response
    """http://www.goair.in 不支持多天"""
    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}

    def search(self, searchParam: SearchParam):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/101.0.0.0 Safari/537.36"
        }
        params = (
            ('s', True),
            ('o1', searchParam.dep),
            ('d1', searchParam.arr),
            ('ADT', searchParam.adt),
            ('dd1', searchParam.date),
            ('mon', True),
            ('gl', 0),
            ('glo', 0),
            ('cc', 'USD'),
        )
        response = self.get(url="https://book.flygofirst.com/Flight/Select", headers=headers, params=params)
        self.search_response = response

    def convert_search(self):
        results = []
        for element in self.etree.HTML(self.search_response.text).xpath("//tr[@class='js-avail-row']"):
            if not element.xpath(".//span[@class='js-extract-text']/text()"):
                continue
            flightnumber = element.xpath(".//span[@class='flightdetails-number']/text()")[0]
            carrier = flightnumber.split()[0]
            flightnumber = "/".join(map(lambda x: x.split()[0] + str(int(x.split()[1])), flightnumber.split("/")))
            year = element.xpath("//input[@id='search_from_date']/@value")[0].split("/")[-1]
            dep_d_m, arr_d_m = element.xpath(".//span[@class='w-35per']/text()")
            mouth_list = list(calendar.month_abbr)
            dep_m, dep_d = mouth_list.index(dep_d_m.split()[1]), dep_d_m.split()[0]
            fromsegments_ele = element.xpath(".//div[@class='flight-info direct' or"
                                             " @class='flight-info ond']/p[contains(text(),' to ')]")
            # 记录每一站的出发日期
            start_date = datetime.datetime.strptime(year + (str(dep_m) if dep_m > 9 else f"0{dep_m}") + dep_d, "%Y%m%d")

            fromSegments = []
            for x_idn, direct_ele in enumerate(fromsegments_ele):
                # 出发和到达的信息
                dep_info, arr_info = direct_ele.xpath("./text()")[0].split("to")

                [dep_airport, dep_time], [arr_airport, arr_time] = dep_info.split(), arr_info.split()
                dep_datetime = start_date.strftime("%Y%m%d") + dep_time.strip("()").replace(":", "")

                # 如果到达时间早于出发时间，判定为过了一天 增加一天
                if datetime.datetime.strptime(dep_time.strip("()"), "%H:%M") > \
                        datetime.datetime.strptime(arr_time.strip("()"), "%H:%M"):
                    start_date += datetime.timedelta(days=1)
                arr_datetime = start_date.strftime("%Y%m%d") + arr_time.strip("()").replace(":", "")
                fromsegments_data = {
                    'carrier': carrier,
                    'flightNumber': flightnumber.split("/")[x_idn],
                    'depAirport': dep_airport,
                    'depTime': dep_datetime,
                    'arrAirport': arr_airport,
                    'arrTime': arr_datetime,
                    'codeshare': False,
                    'cabin': "",
                    'num': 0,
                    'aircraftCode': "",
                    'segmentType': 0
                }
                fromSegments.append(fromsegments_data)

            data = {
                'data': flightnumber,
                'productClass': 'ECONOMIC',
                'fromSegments': fromSegments,
                'cur': element.xpath(".//div[@class='currency-code']/text()")[0],
                'adultPrice': float(element.xpath(".//span[@class='js-extract-text']/text()")[0]) - 1,
                'adultTax': 1,
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': 0,
                'limitPrice': False,
                'info': self.search_response.url
            }
            if len(data["data"].split("/")) != len(set(data["data"].split("/"))):
                spider_G8_logger.info(f"{data['data']}经停过滤！")
            else:
                results.append(data)
        return results


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AG8Web(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_G8_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
