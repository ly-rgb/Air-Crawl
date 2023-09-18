import time
import parsel
from datetime import datetime

from robot import HoldTask
from airline.baggage import Baggage
from utils.log import robot_G8_logger
from airline.base import AirAgentV3Development


class AG8App(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=10, timeout=120):
        super().__init__(proxies_type, retry_count, timeout,
                         logger=robot_G8_logger)

    def bookingAvailability(self, holdTask: HoldTask):
        self.holdTask = holdTask
        self.currencyCode = "USD"

        url = 'https://book.flygofirst.com/Flight/Select'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'book.flygofirst.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.flygofirst.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
        }
        params = {
            's': True,
            'o1': holdTask.origin,
            'd1': holdTask.destination,
            'ADT': len(holdTask.adt_with_age(12)),
            'dd1': holdTask.departDate,
            'gl': '0',
            'glo': '0',
            'cc': 'USD',
            'mon': 'true',
        }
        resp = self.get(url=url, headers=headers, params=params)
        session_id = resp.cookies.get_dict()['ASP.NET_SessionId']
        self.logger.info(f'抓数的响应状态码为{resp.status_code}')
        time.sleep(3.2)
        if resp.status_code >= 300:
            raise Exception(f"[resp] ==> {resp.status_code}")

        self.availability_result = resp.text
        return session_id

    def convert_search(self):
        self.flights = {}
        result = []
        selector = parsel.Selector(self.availability_result)
        flight_divs = selector.css(
            '#js-avail-table0>tbody>tr[class="js-avail-row"]')

        def time_s_date(ts):
            dt = time.strftime("%Y-%m-%d %H:%M:%S",
                               time.localtime(int(float(ts))))
            return dt

        year = time_s_date(int(time.time()))[:4]
        month_dict = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12
        }
        i = 0
        for flight_div in flight_divs:
            flight_number = flight_div.css(
                'td.avail-table-vert.stops-cell > div:nth-child(1) > '
                'span.flightdetails-number::text').get().replace(
                ' ',
                '').replace(
                '\r\n', '')

            css = '.fare-price-text.no-bundle input[id=\"trip_0_date_0_flight_' + str(i) + '_fare_0\"]::attr(value)'
            info = flight_div.css(css).get()
            i += 1

            dep_mon = flight_div.css(
                'td.avail-table-vert.stops-cell > div:nth-child(3) > '
                'span:nth-child(1)::text').get().split(
                ' ')[1]
            dep_date = flight_div.css(
                'td.avail-table-vert.stops-cell > div:nth-child(3) > span:nth-child(1)::text').get().split(
                ' ')[0]
            dep_hour = flight_div.css(
                'td.avail-table-vert.stops-cell > div.flight-info-middle > '
                'span:nth-child(1)::text').get().split(' ')[1]
            depTime = year + '-' + str(
                month_dict.get(dep_mon)) + '-' + \
                      dep_date + 'T' + \
                      dep_hour + ':00'
            dep_airport = flight_div.css('td.avail-table-vert.stops-cell > div.flight-info-middle > span:nth-child(1)::text').get().split(' ')[0]

            arr_mon = flight_div.css(
                'td.avail-table-vert.stops-cell > div:nth-child(3) > '
                'span:nth-child(3)::text').get().split(
                ' ')[1]
            arr_date = flight_div.css(
                'td.avail-table-vert.stops-cell > div:nth-child(3) > '
                'span:nth-child(3)::text').get().split(
                ' ')[0]
            arr_hour = flight_div.css(
                'td.avail-table-vert.stops-cell > div.flight-info-middle > '
                'span:nth-child(3)::text').get().split(' ')[1]
            arrTime = year + '-' + str(
                month_dict.get(arr_mon)) + '-' + \
                      arr_date + 'T' + \
                      arr_hour + ':00'
            arr_airport = flight_div.css('td.avail-table-vert.stops-cell > div.flight-info-middle > span:nth-child(3)::text').get().split(' ')[0]

            stop_airport = flight_div.css(
                'td.avail-table-vert.stops-cell.withStops > div:nth-child(3) '
                '> span.w-30per > span.flight-info-conecting::text').get()
            if stop_airport is None:
                pass
            else:
                stop_deptime = flight_div.css(
                    'td.avail-table-vert.stops-cell.withStops > '
                    'div.view-details.connecting-flight-img.custom-connecting'
                    '-flight-img > span > div > div.flight-info.ond > '
                    'p:nth-child(2)::text').get().split(
                    ' ')[1].replace('(', '').replace(')', '')
                stop_deptime = year + '-' + str(
                    month_dict.get(dep_mon)) + '-' + \
                               dep_date + 'T' + \
                               stop_deptime + ':00'
                stop_arrtime = flight_div.css(
                    'td.avail-table-vert.stops-cell.withStops > '
                    'div.view-details.connecting-flight-img.custom-connecting'
                    '-flight'
                    '-img > span > div > div.flight-info.direct > p:nth-child('
                    '2)::text').get().split(' ')[-2].replace('(',
                                                                   '').replace(
                    ')', '')
                stop_arrtime = year + '-' + str(
                    month_dict.get(arr_mon)) + '-' + \
                               arr_date + 'T' + \
                               stop_arrtime + ':00'

            adultPrice = flight_div.css(
                'td:nth-child(2) > div.fare-price-text.no-bundle > label > '
                'span.price-text > span::text').get()
            if adultPrice is None:
                continue

            seat = flight_div.css(
                'td:nth-child(2) > div > label > '
                'span.mdl-typography--body-2.seats-count::text').get()
            if seat is None:
                seat = '1'
            else:
                seat = seat[0].split(' ')[0]

            fromSegments = []
            if '/' not in flight_number:
                flight_no = []
                flight_no.append(flight_number)
                fromSegments.append({
                    "carrier": "G8",
                    "flightNumber": flight_number,
                    "depAirport": dep_airport,
                    "depTime": datetime.strptime(depTime,
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "arrAirport": arr_airport,
                    "arrTime": datetime.strptime(arrTime,
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "codeshare": False,
                    "cabin": "Y",
                    "num": 0,
                    "aircraftCode": "",
                    "segmentType": 0
                })
            else:
                flight_no = []
                flight_no.append(flight_number.split('/')[0])
                flight_no.append(flight_number.split('/')[1])
                fromSegments.append({
                    "carrier": "G8",
                    "flightNumber": flight_number.split('/')[0],
                    "depAirport": dep_airport,
                    "depTime": datetime.strptime(depTime,
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "arrAirport": stop_airport,
                    "arrTime": datetime.strptime(stop_arrtime,
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "codeshare": False,
                    "cabin": "Y",
                    "num": 0,
                    "aircraftCode": "",
                    "segmentType": 0
                })
                fromSegments.append({
                    "carrier": "G8",
                    "flightNumber": flight_number.split('/')[1],
                    "depAirport": stop_airport,
                    "depTime": datetime.strptime(stop_deptime,
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "arrAirport": arr_airport,
                    "arrTime": datetime.strptime(arrTime,
                                                 "%Y-%m-%dT%H:%M:%S").strftime(
                        "%Y%m%d%H%M"),
                    "codeshare": False,
                    "cabin": "Y",
                    "num": 0,
                    "aircraftCode": "",
                    "segmentType": 0
                })
            item = {
                'data': '/'.join(flight_no),
                'productClass': 'ECONOMIC',
                'fromSegments': fromSegments,
                'cur': 'USD',
                'adultPrice': adultPrice,
                'adultTax': 0,
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': seat,
                'limitPrice': True,
                'info': info
            }
            self.flights["/".join(flight_no)] = item
            result.append(item)
        self.logger.info(f'抓到的所有航班为{result}')
        return result

    def selectFlight(self, holdTask: HoldTask):
        self.flight = self.flights.get(holdTask.flightNumber, None)
        if not self.flight:
            raise Exception(
                f"未找到航班: {holdTask.flightNumber}, 当前航班: {self.flights}")

    def get_select(self, sessionid):
        url = 'https://book.flygofirst.com/Flight/Select'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '215',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'ASP.NET_SessionId=' + sessionid,
            'Host': 'book.flygofirst.com',
            'Origin': 'https://book.flygofirst.com',
            'Pragma': 'no-cache',
            'Referer': 'https://book.flygofirst.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
        }
        data = {
            'goAirAvailability.BundleCodes[0]': '',
            'goAirAvailability.MarketFareKeys[0]': self.flight['info']
        }
        self.post(url=url, headers=headers, data=data)

    def get_booking(self, sessionid):
        url = 'https://book.flygofirst.com/Passengers/Edit'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'ASP.NET_SessionId=' + sessionid,
            'Host': 'book.flygofirst.com',
            'Pragma': 'no-cache',
            'Referer': 'https://book.flygofirst.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
        }
        resp = self.get(url=url, headers=headers)
        BookingInformation = resp.cookies.get_dict()['BookingInformation']
        return BookingInformation

    def get_bag_key(self, sessionid, BookingInformation):
        url = 'https://book.flygofirst.com/Extras/Add'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'ASP.NET_SessionId=' + sessionid +
                      ';BookingInformation=' + BookingInformation,
            'Host': 'book.flygofirst.com',
            'Pragma': 'no-cache',
            'Referer': 'https://book.flygofirst.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
        }
        resp = self.get(url=url, headers=headers).content.decode('utf-8')
        selector = parsel.Selector(resp)
        bag_data = selector.css('.checkboxes label::text').getall()[3:]
        self.logger.info(f'获取到的bag_data为{bag_data}')
        bag_key = selector.css(
            '.checkboxes label input ::attr(id)').getall()
        self.logger.info(f'获取到的bag_key为{bag_key}')
        return bag_data, bag_key

    def get_bag_price(self, sessionid, bag_key):
        price_list = []
        for i in bag_key:
            if 'XC' in i:
                key = i
                url = 'https://book.flygofirst.com/Ssrs/Apply'
                headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Content-Length': '182',
                    'Content-Type': 'application/x-www-form-urlencoded; '
                                    'charset=UTF-8',
                    'Cookie': 'ASP.NET_SessionId=' + sessionid,
                    'Host': 'book.flygofirst.com',
                    'Origin': 'https://book.flygofirst.com',
                    'Pragma': 'no-cache',
                    'Referer': 'https://book.flygofirst.com/',
                    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", '
                                 '"Google Chrome";v="108"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                  'x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/108.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                }
                data = {
                    'goAirSsr.SelectedJourneySsrs[0]': key
                }
                self.post(url=url, headers=headers, data=data,
                          allow_redirects=False)
                url = 'https://book.flygofirst.com/Ssrs/Reload'
                headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    # 'Connection': 'close',
                    'Cookie': 'ASP.NET_SessionId=' + sessionid,
                    'Host': 'book.flygofirst.com',
                    'Pragma': 'no-cache',
                    'Referer': 'https://book.flygofirst.com/',
                    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", '
                                 '"Google Chrome";v="108"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/108.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                }
                resp = self.get(url=url, headers=headers).content.decode(
                    'utf-8')
                selector = parsel.Selector(resp)
                price = selector.css(
                    '.pull-right.pull-right-change::text').get().replace(' ',
                                                                         '').replace(
                    '\r\n', '').replace('USD', '')
                price_list.append(price)
                url = 'https://book.flygofirst.com/Ssrs/Apply'
                headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; '
                                    'charset=UTF-8',
                    'Cookie': 'ASP.NET_SessionId=' + sessionid,
                    'Host': 'book.flygofirst.com',
                    'Origin': 'https://book.flygofirst.com',
                    'Pragma': 'no-cache',
                    'Referer': 'https://book.flygofirst.com/',
                    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", '
                                 '"Google Chrome";v="108"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                  'x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/108.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                }
                data = {
                    'goAirSsr.SelectedJourneySsrs[0]': key + '|XX-1'
                }
                self.post(url=url, headers=headers, data=data,
                          allow_redirects=False)
        self.logger.info(f'获取到的price_list为{price_list}')
        return price_list

    def get_bag_list(self, bag_data, price_list):
        bag_list = []
        j = 0
        for i in bag_data:
            if 'Pre' not in i:
                continue
            if 'INTL' in i:
                continue
            if 'Sports' in i:
                continue
            weight = i.split('-')[1].split(' ')[1]
            price = price_list[j]
            j += 1
            bag_list.append(
                Baggage(weight, price, self.flight, price, self.currencyCode))
        self.logger.info(f'获取到的bag_list为{bag_list}')
        return bag_list
