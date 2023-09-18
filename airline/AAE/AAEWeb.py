import parsel
from typing import Dict
from robot import HoldTask
from utils.log import spider_AE_logger
from utils.searchparser import SearchParam
from airline.base import AirAgentV3Development


class AAEWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60,
                 holdTask=None):
        super().__init__(proxies_type, retry_count, timeout,
                         logger=spider_AE_logger)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}

    @property
    def base_headers(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/94.0.4606.81 Safari/537.36'
        }
        return headers

    def search(self, searchParam: SearchParam):
        self.searchParam = searchParam

        params = {
            'departureCity': searchParam.dep,
            'arrivalCity': searchParam.arr,
            'passengerNo': 1,
            'infantNo': 0
        }
        data = {
            'depstn': searchParam.dep,
            'arrstn': searchParam.arr,
            'itinType': 'oneway',
            'departureDate': searchParam.date.replace('-', '/'),
            'returnDate': '',
            'adult': '1',
            'child': '0',
            'lang': 'zh_CN',
            # 'currentdate': '111-12-27',
            'currentCalForm': 'dep',
            'recaptcharesult':
                '03AD1IbLBW6hrLQQyrjTltlpcHB8nMAkZcpy6JUqGbinhnbO'
                '-V5QpOyAzTdFnKJKCT793RigzpdQ5pyfKtPNHBwwc5gH38r6lKHQbc7aVcxuAKTQEZrUHeR_EDcGfXWN644uvGW4Kqv4CWRyYOC0l88ixaTwC8xVa49qhd38hvmEJs3nXXmEYa1m_7mbroCvX8ccOabuj-VQajMTOqG_qDKeFv5IifBCphFFdbaoeaUqm-JO-bGCrzE7JVKUffwzNJj4ZMpdX2fgNKxbfWrm9NF1D2sGqKWISiqkpn_tcdXitW9K6iGbdVDUV47u_iIx0GKjzbsUa0Uiay-r9mV-v-gteWGDIG2xyJsasS3qwpO2owWH-pyQrFrtgaTl5q7J8kPljYA3vsdc2gu6C3nHkPgwPS9t_RffWyk7GVfl_U3_4hdywDWj-3G3rlcIQa8Shn1VAXrAWoGgh9NP4Xpz1VjtpgFqwp_0HJTKtnvsx4Etc4O7-JqzsnGT7sl_SE2NUo73VpE8kskLL3P8GOm779QuEggnkuaTXJDQ '
        }
        resp = self.post(
            'https://b2c.mda-knh.com/DomesticSelectFlightNFareGoNew.html',
            headers=self.base_headers, params=params, data=data)
        self.logger.info(f'抓数的状态码为{resp.status_code}')
        self.search_response = resp

    def convert_search(self):
        result = []
        selector = parsel.Selector(self.search_response.content.decode('utf8'))
        flight_divs = selector.css(
            '#bookingForm tr:nth-child(2) tr:nth-child(3) tr tr:nth-child(4) '
            'table tr')
        year = selector.css(
            '#bookingForm tr:nth-child(2) tr:nth-child(3) tr tr:nth-child(4) '
            'table tr td:nth-child(4)::text').get()[:4]
        month = selector.css(
            '#bookingForm tr:nth-child(2) tr:nth-child(3) tr tr:nth-child(4) '
            'table tr td:nth-child(4)::text').get()[5:].split('月')
        date = selector.css(
            '#bookingForm tr:nth-child(2) tr:nth-child(3) tr tr:nth-child(4) '
            'table tr td:nth-child(4)::text').get()[5:].split('月')[1].replace(
            '日', '').strip()
        if len(month[0]) == 2:
            month = month[0]
        else:
            month = '0' + month[0]
        if len(date) == 1:
            date = '0' + date
        for flight_div in flight_divs:
            flight_number = flight_div.css('table .flightno::text').get()
            if flight_number is None:
                continue
            dep_css = '#deptime_' + flight_number + '::text'
            deptime = year + month + date + flight_div.css(
                dep_css).get().replace(':', '')
            arrtime = year + month + date + flight_div.css(
                'td:nth-child(3)::text').get().replace(':', '')
            price = flight_div.css('td:nth-child(5)::text').get()
            pro_price = flight_div.css('td:nth-child(6)::text').get()
            # seat = selector.css('td:nth-child(8)::text').get()
            fromSegments = {
                "carrier": "AE",
                "flightNumber": "AE" + flight_number,
                "depAirport": self.searchParam.dep,
                "depTime": deptime.replace(' ', ''),
                "arrAirport": self.searchParam.arr,
                "arrTime": arrtime.replace(' ', ''),
                "codeshare": False,
                "cabin": "Y",
                "num": 0,
                "aircraftCode": "",
                "segmentType": 0
            }
            if pro_price:
                price = pro_price.replace('起', '')
                item = {
                    "data": "AE" + flight_number,
                    "productClass": "ECONOMIC",
                    "fromSegments": [fromSegments],
                    "cur": 'TWD',
                    "adultPrice": price.replace('$', ''),
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
                    "info": ''
                }
                result.append(item)
            elif price is None and pro_price is None:
                continue
            else:
                item = {
                    "data": "AE" + flight_number,
                    "productClass": "ECONOMIC",
                    "fromSegments": [fromSegments],
                    "cur": 'TWD',
                    "adultPrice": price.replace('$', ''),
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
                    "info": ''
                }
                result.append(item)
        self.logger.info(f'result为{result}')
        return result
