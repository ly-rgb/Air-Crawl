import parsel
import urllib
import pprint
from typing import Dict
from robot import HoldTask
from utils.log import spider_B7_logger
from utils.searchparser import SearchParam
from airline.base import AirAgentV3Development


class AB7Web(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60,
                 holdTask=None):
        super().__init__(proxies_type, retry_count, timeout,
                         logger=spider_B7_logger)
        self.holdTask: HoldTask = holdTask
        self.flights: Dict = {}

    @property
    def base_headers(self):
        headers = {
            'authority': 'www.uniair.com.tw',
            'method': 'POST',
            'path': '/rwd/B2C/booking/ubk_select-itinerary.aspx',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-length': '1483',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': '_UNI_UserData=rAdD5+tkk5Fv0zUiXW'
                      '+IDmyqvJ4rggi69ZTYRZFlCJrIpD8aVd0XYlR6lFVhw9O6KXmCXSI5kI36Gis4+OS3Vj1aDa3LYFIKVgVgXvbUMwi1HT/741mXnd6iZ/K+P6T2mHB7dYRwjFdYAlsi27jxvw==',
            'origin': 'https://www.uniair.com.tw',
            'pragma': 'no-cache',
            'referer': 'https://www.uniair.com.tw/rwd/index.aspx',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
                         'Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36',
        }
        return headers

    def search(self, searchParam: SearchParam):
        self.searchParam = searchParam

        UDSS_DATA = {"LANG": "zh-tw", "MSG_KEY": "", "TRIP": "OW", "DEP": searchParam.dep,
                     "ARR": searchParam.arr,
                     "GO_DATE": searchParam.date.replace('-', '/'), "BACK_DATE": "", "PAX_NUM": "1",
                     "PAX_NUM_INF": "0",
                     "TRIP_TYPE": "GO", "IP": "211.75.42.136", "MCT": "",
                     "MCT_DATE": "",
                     "DATA": "", "ACTION": "", "SEG_1": "", "SEG_2": "",
                     "SEG_3": "", "SEG_4": "",
                     "SEG_5": "", "SEG_6": "", "MCT_DATEPRE": "",
                     "MCT_DATEAFTER": "",
                     "OFFICE_SEGMENT": "", "SELECTED_FARE": "",
                     "SELECTED_FLIGHT": "",
                     "PASSENGER_INFO": "", "CONTACT_INFO": "",
                     "UP_TOTAL_FARE": "0", "TRANS_ID": "",
                     "PNR": "", "INSPNR": "", "MODE": "", "MAIL_URL": "",
                     "MIN_DATE": searchParam.date.replace('-', '/'),
                     "MAX_DATE": "2023/12/23"}
        UDSS_DATA = urllib.parse.quote(str(UDSS_DATA).encode('gb2312'))
        data = {
            #'lfk': '154312822_TSA-KNH_1_0',
            'lfd': 'Index',
            'UDSS_DATA': UDSS_DATA
        }
        resp = self.post(
            'https://www.uniair.com.tw/rwd/B2C/booking/ubk_select-itinerary.aspx',
            headers=self.base_headers, data=data)
        self.logger.info(f'抓数的状态码为{resp.status_code}')
        self.search_response = resp
        selector = parsel.Selector(self.search_response.content.decode('utf8'))
        __ZIPSTATE = selector.css('#__ZIPSTATE::attr(value)').get()
        self.deptime = \
        selector.css('#CPH_Body_lb_TripType::text').get().replace('出發日期：',
                                                                  '').split(
            ' ')[0].replace('/', '')
        url = 'https://www.uniair.com.tw/rwd/B2C/booking/ubk_select-itinerary.aspx'
        headers = {
            # 'authority': 'www.uniair.com.tw',
            # 'method': 'POST',
            # 'path': '/rwd/B2C/booking/ubk_select-itinerary.aspx',
            # 'scheme': 'https',
            # 'accept': '*/*',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'zh-CN,zh;q=0.9',
            # 'cache-control': 'no-cache',
            # 'content-length': '28789',
            # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',

            # 'cookie': '_UNI_ViewPolicy_zh-TW=Y;
            # _ga=GA1.3.286917546.1672213359;
            # _SI_VID_1.0164247f20000101f92c16b1=e822f75bbb9cf8368bef0109;
            # _gid=GA1.3.84419114.1672305973;
            # ASP.NET_SessionId=v3hfo45aue1mgkinfh5iwlia;
            # session-WEBPROD-virtualname=38780818;
            # _SI_DID_1.0164247f20000101f92c16b1=7d763a76-97c0-3161-9f35
            # -5903553c4b87; _gat_UA-127196658-1=1;
            # _UNI_UserData=rAdD5+tkk5Fv0zUiXW
            # +IDmyqvJ4rggi69ZTYRZFlCJoZciKCUZiHUndBmqxMfBjmpDwNYArovS66NYyB0S405VY5+6VWV0aEDKhBpiUJ2PoaDipIHY7DyOPm5tMy3jH5equW+30AhuFdK+Q3iXHzzw==; TS0169f7e2=017d6d6fc5365d1e25411b7efaf55d74e7101dfb0f31ad6dfb0e2031fdac296c6d2b9aa8212a6bc4dbb60085ec6736e51202ac679ed3b61f3da36bc532297786a9e177e781bfe64f9e7f50b354d188072139a1ef8e408038c83a267c15057585e8970c0b5be517981ec8e33f42089399b63563c274; _SI_SID_1.0164247f20000101f92c16b1=c8dd205d145fb759ec4104bb.1672384095081.184005',
            'origin': 'https://www.uniair.com.tw',
            # 'pragma': 'no-cache',
            'referer': 'https://www.uniair.com.tw/rwd/B2C/booking/ubk_select-itinerary.aspx',
            # 'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"Windows"',
            # 'sec-fetch-dest': 'empty',
            # 'sec-fetch-mode': 'cors',
            # 'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            # 'x-microsoftajax': 'Delta=true',
            # 'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'ctl00$ScriptManager1': 'ctl00$CPH_Body$uc_SelectFlight$pnl_Flight'
                                    '|ctl00$CPH_Body$uc_SelectFlight$rpt_Flight$ctl00$btn_SelectFlightCheck',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__ZIPSTATE': __ZIPSTATE,
            '__VIEWSTATE': '',
            'ctl00$CPH_Body$uc_SelectFlight$rpt_Flight$ctl00$hi_MCT': '',
            'ctl00$CPH_Body$uc_SelectFlight$rpt_Flight$ctl00$hi_SelectData': '',
            'ctl00$CPH_Body$uc_SelectFlight$rpt_Flight$ctl00$hi_DepTime': '',
            'ctl00$CPH_Body$uc_SelectFlight$rpt_Flight$ctl00$hi_ArrTime': '',
            'ctl00$CPH_Body$hi_SELECTED_FLIGHT': '',
            'ctl00$CPH_Body$hi_SELECTED_FARE': '',
            'ctl00$CPH_Body$hi_MCT': '',
            'ctl00$CPH_Body$hi_TripType': '',
            'ctl00$CPH_Body$hi_PAX_NUM': '1',
            'ctl00$CPH_Body$hi_PAX_NUM_INF': '0',
            'ctl00$CPH_Body$hi_SelectedFareData': '',
            'ctl00$CPH_Body$hi_ScrollHeight': '',
            'ctl00$ud': '',
            #'ctl00$lfk': '150806747_TSA-KNH_1_0',
            'ctl00$lfd': 'UDSS_Ticket',
            'ctl00$hi_CookieExpire': '2023/01/29 15:08:12',
            '__VIEWSTATEENCRYPTED': '',
            '__ASYNCPOST': 'true',
            'ctl00$CPH_Body$uc_SelectFlight$rpt_Flight$ctl00$btn_SelectFlightCheck': '',
        }
        resp = self.post(url=url, headers=headers, data=data)
        selector = parsel.Selector(resp.content.decode('utf8'))
        try:
            self.full_price = selector.css(
            '#CPH_Body_rpt_FareType_rpt_FareInfo_0_lb_Fare_0::text').get().replace(
            ',', '')
        except(AttributeError):
            return

    def convert_search(self):
        result = []
        selector = parsel.Selector(self.search_response.content.decode('utf8'))
        flight_divs = selector.css(
            '#CPH_Body_uc_SelectFlight_pnl_Flight > span')
        i = 0
        for flight_div in flight_divs:
            flight_number = flight_div.css(
                '#CPH_Body_uc_SelectFlight_rpt_Flight_lb_FlightNumber_' + str(
                    i) + '::text').get()
            dep_time = flight_div.css(
                '#CPH_Body_uc_SelectFlight_rpt_Flight_lb_DepTime_' + str(
                    i) + '::text').get().replace(':', '')
            arr_time = flight_div.css(
                '#CPH_Body_uc_SelectFlight_rpt_Flight_lb_ArrTime_' + str(
                    i) + '::text').get().replace(':', '')
            price = flight_div.css(
                '#CPH_Body_uc_SelectFlight_rpt_Flight_lb_SubInfo_' + str(
                    i) + '> span::text').get()
            seat = flight_div.css(
                '#CPH_Body_uc_SelectFlight_rpt_Flight_lb_SubInfo_' + str(
                    i) + '::text').get()
            i += 1
            if not price:
                price = self.full_price
            if seat == '無可售機位':
                continue
            fromSegments = {
                "carrier": "B7",
                "flightNumber": flight_number.replace('-', ''),
                "depAirport": self.searchParam.dep,
                "depTime": self.deptime + dep_time,
                "arrAirport": self.searchParam.arr,
                "arrTime": self.deptime + arr_time,
                "codeshare": False,
                "cabin": "Y",
                "num": 0,
                "aircraftCode": "",
                "segmentType": 0
            }
            item = {
                    "data": flight_number.replace('-', ''),
                    "productClass": "ECONOMIC",
                    "fromSegments": [fromSegments],
                    "cur": 'TWD',
                    "adultPrice": price.replace(',', ''),
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
