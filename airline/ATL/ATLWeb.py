import re
from datetime import datetime
import requests
import traceback
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_TL_logger


class ATLWeb(AirAgentV3Development):

    """
    注意：
    1.不使用chrome开发者工具抓包，抓的包是错的，用charles抓的包与chrome抓的包不一样
    2.没有中转，只有直达和经停
    3.暂时没有数据有当天有两次航班
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.session = requests.session()

        self.__front_search_url = "https://secure.airnorth.com.au/AirnorthB2C/Booking/AvailProcessing"
        self.__search_url = "https://secure.airnorth.com.au/AirnorthB2C/Booking/Select"
        self.__front_search_cookie = {
            'AWSALB': 'TJ1le7qSlKTCH4mF3KpmFFjJuPm+TfI69sL9NliyDFK04TWdB9ZU9j/ajarLB5PNxNx4Bf+x79bRL7nfS5/ts8l6E5bDLN8ktQ7ZkPlYmUaV3y2q+36cYzfCyijq'
        }

        self.__place = ['Alice Springs', 'Broome', 'Cairns', 'Darwin', 'Dili', 'Elcho Island', 'Gove', 'Groote Eylandt', 'Katherine', 'Kununurra', 'Maningrida', 'McArthur River', 'Milingimbi', 'Mount Isa', 'Perth', 'Tennant Creek', 'Toowoomba (Brisbane-West)', 'Townsville']
        self.__code = ['ASP', 'BME', 'CNS', 'DRW', 'DIL', 'ELC', 'GOV', 'GTE', 'KTR', 'KNX', 'MNG', 'MCV', 'MGT', 'ISA', 'PER', 'TCA', 'WTB', 'TSV', '', 'ASP', 'BME', 'CNS', 'DRW', 'DIL', 'ELC', 'GOV', 'GTE', 'KTR', 'KNX', 'MNG', 'MCV', 'MGT', 'ISA', 'PER', 'TCA', 'WTB', 'TSV']
        self.search_response = None

    @property
    def base_headers(self):
        headers = {
            'Host': 'secure.airnorth.com.au',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'https://www.airnorth.com.au/',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        return headers

    @property
    def code_place_dict(self):
        place = dict(zip(self.__code, self.__place))
        print(place)
        return place

    @property
    def place_code_dict(self):
        code = dict(zip(self.__place, self.__code))
        print(code)
        return code

    def front_search(self, searchParam: SearchParam):

        try:

            if searchParam.dep not in list(self.__code) or searchParam.arr not in list(self.__code):
                spider_TL_logger.error(f"dep: {searchParam.dep}或者arr: {searchParam.arr}不在__code列表中")

            payload = {
                "triptype": 'o',
                'search_departing': self.code_place_dict[searchParam.dep],
                'port.0': searchParam.dep,
                'search_arriving': self.code_place_dict[searchParam.arr],
                'port.1': searchParam.arr,
                'date.0': datetime.strptime(searchParam.date, "%Y-%m-%d").strftime("%d%b"),
                'search_passengers': f'{searchParam.adt} Passenger',
                'pax.0': searchParam.adt,
                'pax.1': '0',
                'pax.2': '0',
                'corpCode': '',
                'assist': 'No'
            }

            response = self.session.get(url=self.__front_search_url, headers=self.base_headers, params=payload,
                                        cookies=self.__front_search_cookie, allow_redirects=False)

            if response.status_code == 302:
                spider_TL_logger.info(f"请求参数为: {payload}, 此请求状态码为: {response.status_code}")

        except Exception:

            spider_TL_logger.error(f"请求失败，请检查接口: {self.__front_search_url}")
            spider_TL_logger.error(f"{traceback.format_exc()}")

    def search(self):
        try:
            response = self.session.get(url=self.__search_url, headers=self.base_headers)
            if response.status_code == 200:
                self.search_response = response
                spider_TL_logger.info(f"请求成功")

        except Exception:
            if self.search_response is None:
                spider_TL_logger.error(f"请求失败，请检查接口: {self.__search_url}")
                spider_TL_logger.error(f"{traceback.format_exc()}")

    def convert_search(self):
        result = []
        from_segment_list = []

        try:
            html = self.etree.HTML(self.search_response.text)
            # 判断当天是否有航班
            is_empty = False if len(html.xpath('//*[@id="select-form"]/div[2]/section[2]/div/button[7]/div[2]/text()')) > 0 else True
            if is_empty:
                spider_TL_logger.info(f"当天无航班")
                return result
            # 是否为经停，如果是过滤掉
            is_stop = False if html.xpath('//div[@class="body"]/div[@class="details"]/div[@class="body"]/span[@class="stops"]/text()')[0] == "0 Stop" else True
            if is_stop:
                spider_TL_logger.info(f"经停航班，过滤")
                return result

            # 解析
            flight_number = \
            html.xpath('//div[@class="body"]/div[@class="details"]/div/span[@class="flight"]/span/text()')[0].replace(
                " ", "")
            # Darwin to Elcho Island 19 September 2022
            _date_and_place = html.xpath('//section[@class="fwSect heading"]/div[@class="container"]/h6/text()')[0]
            _time = html.xpath('//div[@class="f-body"]//h5/text()')

            dep_arr_dict = self.handle_date_place(_date_and_place, _time)

            from_segment = {
                'carrier': "TL",
                'flightNumber': flight_number,
                'depAirport': dep_arr_dict["dep"],
                'depTime': dep_arr_dict["dep_time"],
                'arrAirport': dep_arr_dict["arr"],
                'arrTime': dep_arr_dict["arr_time"],
                'codeshare': False,
                'cabin': 'Y',
                'num': 0,
                'aircraftCode': '',
                'segmentType': 0
            }
            spider_TL_logger.info(f"航段信息为: {from_segment}")
            from_segment_list.append(from_segment)

            lowest_price = html.xpath('//button[7]/div[@class="price"]/text()')[0].replace(" ", "").replace("$", "")
            data = {
                'data': flight_number,
                'productClass': 'ECONOMIC',
                'fromSegments': from_segment_list,
                'cur': 'USD',
                'adultPrice': float(lowest_price) - 1,
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
                'info': ""
            }

            result.append(data)

        except Exception:
            result = None
            spider_TL_logger.error(f"解析失败，修改xpath")
            spider_TL_logger.error(f"{traceback.format_exc()}")

        return result

    def handle_date_place(self, _date_and_place: str, _time: list):
        """
        对解析出来的时间字符串进行拆分处理，并且对时间进行格式化处理
        :param _date_and_place: 包含地点与时间的字符串
        :param _time: 出发时间与到达时间列表
        :return: dict{"dep": "出发地点"， "arr": "到达地点", "dep_time": "出发时间（格式化）", "arr_time": "到达时间（格式化）"}
        """
        date_place_dict = {}
        try:

            for idx in range(len(_date_and_place)):
                if _date_and_place[idx].isdigit():
                    __place = _date_and_place[:idx]
                    __date = _date_and_place[idx:].replace(" ", "")
                    __time = [t.replace(" ", "") for t in _time]
                    print(__time)
                    spider_TL_logger.info(f"handle_date_place函数初步切分结果: "
                                          f"__place: {__place}, "
                                          f"__date: {__date}")

                    dep_place = __place.split("to")[0].strip()
                    date_place_dict["dep"] = self.place_code_dict[dep_place]

                    arr_place = __place.split("to")[1].strip()
                    date_place_dict["arr"] = self.place_code_dict[arr_place]

                    dep_time = datetime.strptime(__date + __time[0], "%d%B%Y%H:%M").strftime("%Y%m%d%H%M")
                    date_place_dict["dep_time"] = dep_time

                    arr_time = datetime.strptime(__date + __time[1], "%d%B%Y%H:%M").strftime("%Y%m%d%H%M")
                    date_place_dict["arr_time"] = arr_time

                    if dep_place not in list(self.place_code_dict.keys()) or arr_place not in list(self.place_code_dict.keys()):
                        spider_TL_logger.error(f"请检查dep: {dep_place}, arr: {arr_place} 是否在place_code_dict中")

                    break
            spider_TL_logger.info(f"handle_date_place函数解析得到的最终结果为: {date_place_dict}")
            return date_place_dict
        except Exception:
            spider_TL_logger.error(f"handle_date_place函数解析数据：{date_place_dict}")
            spider_TL_logger.error(f"{traceback.format_exc()}")








