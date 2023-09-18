from datetime import datetime
from typing import Dict

from lxml import etree
from requests.models import Response

from airline.base import AirAgentV3Development
from requests_curl import CURLAdapter
from robot import HoldTask
from utils.log import spider_TO_logger
from utils.redis import redis_53
from utils.searchparser import SearchParam


class ATOWeb(AirAgentV3Development):
    """https://www.transavia.com/"""
    search_response: Response

    def __init__(self, task, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)
        self.reese84 = None
        self.task: HoldTask = task
        self.flights: Dict = {}
        self.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        self.headers['Referer'] = 'https://www.transavia.com/en-EU/home/'
        self.html = None
        self.mount('https://', CURLAdapter(verbose=0, cookie=False))

    def set_reese84(self):
        reese84_cache = redis_53.spop('transavia_token_reese84')
        if reese84_cache:
            reese84_cache = self.json.loads(reese84_cache)
            self.reese84 = reese84_cache['reese84']
            self.headers['User-Agent'] = reese84_cache['User-Agent']
            self.cookies.set('reese84', self.reese84)
            self.logger.info(f'[{self.task.orderCode}][缓存reese84][{self.reese84}]')
            return

        request_body = redis_53.spop('transavia_token')
        if not request_body:
            raise Exception(f'[{self.task.orderCode}][获取 reese84 失败]')
        url = 'https://www.transavia.com/rgeonseart-Cawdor-mine-no-our-selfe-Wife-comfort?d=www.transavia.com'
        request_body = self.json.loads(request_body)
        self.headers['User-Agent'] = request_body['User-Agent']
        json = self.json.loads(request_body['requestBody'])
        response = self.post(url, json=json)
        if response.status_code != 200:
            raise Exception(f'[{self.task.orderCode}][reese84 提交失败][{response.status_code}]')
        self.reese84 = response.json()['token']
        self.logger.info(f'[{self.task.orderCode}][reese84][{self.reese84}]')
        self.cookies.set('reese84', self.reese84)

    def flights_search(self):
        self.set_reese84()
        url = 'https://www.transavia.com/en-EU/book-a-flight/flights/search/'
        for _ in range(5):
            response = self.get(url, allow_redirects=False)
            if 'Request unsuccessful' in response.text:
                self.refresh_proxy()
                continue
            if response.status_code != 200 or 'Request unsuccessful' in response.text:
                raise Exception(f'[{self.task.orderCode}][flights_search 初始化失败][{response.status_code}]')
            self.html = self.etree.HTML(response.text)
            return
        else:
            response = self.get(url, allow_redirects=False)
            if response.status_code != 200 or 'Request unsuccessful' in response.text:
                raise Exception(f'[{self.task.orderCode}][flights_search 初始化失败][{response.status_code}][{response.text}]')
            self.html = self.etree.HTML(response.text)

    def multi_day_availability(self):
        __RequestVerificationToken = self.html.xpath('//*[@id="flights"]/input[@name="__RequestVerificationToken"]/@value')
        if not __RequestVerificationToken:
            raise Exception(f'[{self.task.orderCode}][multi_day_availability __RequestVerificationToken 获取失败]')

        url = "https://www.transavia.com/fr-FR/reservez-un-vol/vols/multidayavailability/"
        data = {
            "selectPassengersCount.AdultCount": self.task.adt_count,
            "selectPassengersCount.ChildCount": "0",
            "selectPassengersCount.InfantCount": "0",
            "routeSelection.DepartureStation": self.task.origin,
            "routeSelection.ArrivalStation": self.task.destination,
            "dateSelection.OutboundDate.Day": str(self.task.depart_date.day),
            "dateSelection.OutboundDate.Month": str(self.task.depart_date.month),
            "dateSelection.OutboundDate.Year": str(self.task.depart_date.year),
            "dateSelection.InboundDate.Day": "",
            "dateSelection.InboundDate.Month": "",
            "dateSelection.InboundDate.Year": "",
            "dateSelection.IsReturnFlight": "false",
            "flyingBlueSearch.FlyingBlueSearch": "false",
            "__RequestVerificationToken": __RequestVerificationToken[0]
        }
        response = self.post(url=url, data=data)
        if response.status_code != 200 or 'Request unsuccessful' in response.text:
            raise Exception(f'[{self.task.orderCode}][multidayavailability 查询失败][{response.url}]')
        self.html = self.etree.HTML(response.json()['multiDayAvailabilityOutbound'])

    def single_day_availability(self):
        __RequestVerificationToken = self.html.xpath('//div[@class="current-view"]//input[@name="__RequestVerificationToken"]/@value')
        if not __RequestVerificationToken:
            raise Exception(f'[{self.task.orderCode}][single_day_availability __RequestVerificationToken 获取失败]')

        url = "https://www.transavia.com/fr-FR/reservez-un-vol/vols/SingleDayAvailability/"

        data = {
            "selectSingleDayAvailability.JourneyType": "OutboundFlight",
            "selectSingleDayAvailability.Date.DateToParse": self.task.depart_date.strftime('%Y-%m-%d'),
            "selectSingleDayAvailability.AutoSelect": "true",
            "__RequestVerificationToken": __RequestVerificationToken
        }
        response = self.post(url, data=data)
        if response.status_code != 200 or 'Request unsuccessful' in response.text:
            raise Exception(f'[{self.task.orderCode}][SingleDayAvailability 查询失败][{response.text}]')
        result = self.convert_search(response.json())
        redis_53.sadd('transavia_token_reese84', self.json.dumps({'reese84': self.reese84, 'User-Agent': self.headers['User-Agent']}))
        return result

    def convert_search(self, data):
        elemet = etree.HTML(data["SingleDayOutbound"])
        results = []
        for flight in data["TagMan"]["eventData"]["day_view_outbound_flights"]:
            flight_label = flight["flight_label"]
            flight_number = flight["flight_number"]
            depdatetime = elemet.xpath(f"//button[@class='flight-result-button' and contains(@value,"
                                       f"'{flight_label}~{flight_number}~')]/@value")[0].split("|")[-1].split("~")[5]
            arrdatetime = elemet.xpath(f"//button[@class='flight-result-button' and contains(@value,"
                                       f"'{flight_label}~{flight_number}~')]/@value")[0].split("|")[-1].split("~")[7]
            flightnumber = flight["flight_label"] + str(int(flight["flight_number"].strip()))
            segments = [{
                'carrier': flight["flight_label"],
                'flightNumber': flightnumber,
                'depAirport': flight["departure"],
                'depTime': datetime.strptime(depdatetime, "%m/%d/%Y %H:%M").strftime("%Y%m%d%H%M"),
                'arrAirport': flight["arrival"],
                'arrTime': datetime.strptime(arrdatetime, "%m/%d/%Y %H:%M").strftime("%Y%m%d%H%M"),
                'codeshare': False,
                'cabin': "",
                'num': 0,
                'aircraftCode': '',
                'segmentType': 0
            }]
            item = {
                "data": "/".join(map(lambda x: x["flightNumber"], segments)),
                "productClass": "ECONOMIC",
                "fromSegments": segments,
                "cur": 'EUR',
                "adultPrice": float(flight["flight_cost"]),
                "adultTax": 0,
                "childPrice": 0,
                "childTax": 0,
                "promoPrice": 0,
                "adultTaxType": 0,
                "childTaxType": 0,
                "priceType": 0,
                "applyType": 0,
                "max": 0,
                "limitPrice": True,
                "info": "/".join(map(lambda x: x["flightNumber"], segments))
            }
            results.append(item)
        return results


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0
    try:
        app = ATOWeb(HoldTask.from_search_param(taskItem), proxies_type=proxies_type)
        app.flights_search()
        app.multi_day_availability()
        result = app.single_day_availability()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_TO_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result

