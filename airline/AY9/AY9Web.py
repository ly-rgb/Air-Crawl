import json
from datetime import datetime, timedelta

from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_Y9_logger
import traceback


class AY9Web(AirAgentV3Development):

    """
    该航司只有直达和经停，没有中转
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.search_response = None

    def search(self, searchParam: SearchParam):

        try:
            start_date = searchParam.date
            end_date = searchParam.date

            if "CRAWlLCC" in searchParam.args:
                end_date = (datetime.strptime(searchParam.date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
                spider_Y9_logger.info(f"取多天数据, start_date: {start_date} -> end_date: {end_date}")

            url = "https://api-production-lynxair-booksecure.ezyflight.se/api/v1/Availability/SearchShop"

            payload = json.dumps({'passengers': [{'code': 'ADT', 'count': searchParam.adt},
                                                 {'code': 'CHD', 'count': searchParam.chd},
                                                 {'code': 'INF', 'count': 0}],
                                  'routes': [{'fromAirport': searchParam.dep,
                                              'toAirport': searchParam.arr,
                                              'departureDate': searchParam.date,
                                              'startDate': start_date,
                                              'endDate': end_date}],
                                  'currency': 'CAD',
                                  'fareTypeCategories': None,
                                  'isManageBooking': False,
                                  'languageCode': 'en-us'})
            headers = {
                'authority': 'api-production-lynxair-booksecure.ezyflight.se',
                'access-control-allow-origin': '*',
                'content-type': 'application/json;charset=UTF-8',
                'languagecode': 'en-us',
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'tenant-identifier': 'cQuYv9mLXHbhDLgXzZmPRspmm4gz6TmrF8kaZ9uLsZCJTLvvKhuLMfRdBCvM9pbt',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                'x-useridentifier': 'MIZAeBFVx9Ye8Zk6o8XhhoTp2EuEJm'
            }

            response = self.post(url=url, headers=headers, data=payload)
            self.search_response = response
            if response.status_code == 200:
                spider_Y9_logger.info(f"请求参数： {payload}")
                spider_Y9_logger.info(f"请求结果为: {response.text}")
        except Exception:

            spider_Y9_logger.error(f"请求失败, 失败结果：{self.search_response.text}")
            spider_Y9_logger.error(f"{traceback.format_exc()}")

    def convert_search(self):
        result = []
        try:

            all_info = json.loads(self.search_response.text)["routes"][0]["flights"]
            for flight in all_info:
                # 初始化航段信息
                from_segment_list = []
                flight_number_list = []
                # 初始化最低价格信息
                lowest_price = {
                    "adultPrice": 100000,
                    "adultTax": 0,
                    "max": 0,
                    "cabin": "",
                    "info": ""
                }

                if len(flight["legs"]) > 1:
                    # 过滤经停
                    is_stop_list = [num['carrierCode'] + num['flightNumber'] for num in flight['legs']]
                    is_stop_time = [time['departureDate'] + "||" + time['arrivalDate'] for time in flight['legs']]
                    if is_stop_list[0] != is_stop_list[1]:
                        spider_Y9_logger.warning(f"这个是中转航班，请注意：多段航班号为{is_stop_list}, 时间：{is_stop_time}")

                    else:
                        spider_Y9_logger.info(f"经停过滤：多段航班号为{is_stop_list}, 时间：{is_stop_time}")
                        continue
                if flight["soldOut"]:
                    spider_Y9_logger.info(f"该航线已经售罄, "
                                          f"航班号：{flight['carrierCode'] + flight['flightNumber']}"
                                          f"到达时间：{flight['arrivalDate']}"
                                          f"价格：{flight['lowestPriceTotal']}")
                    continue

                # 提取价格信息
                for price_info in flight["fares"]:
                    if price_info["price"] < lowest_price["adultPrice"]:
                        lowest_price.update({
                            "adultPrice": price_info["priceWithoutTax"],
                            "adultTax": sum([tax["price"] for tax in price_info["taxes"]]),
                            "max": price_info["seatCount"],
                            "cabin": 'E' if price_info["cabin"] == "ECONOMY" else 'Y',
                            "info": ""
                        })
                spider_Y9_logger.info(f"最低价格信息：{lowest_price}")

                # 提取航段信息
                for leg in flight["legs"]:
                    carrier = leg["carrierCode"]
                    flight_number = carrier + leg["flightNumber"]
                    flight_number_list.append(flight_number)
                    dep = leg["from"]["code"]
                    dep_time = datetime.strptime(leg["departureDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                    arr = leg["to"]["code"]
                    arr_time = datetime.strptime(leg["arrivalDate"], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                    from_segment = {
                        'carrier': carrier,
                        'flightNumber': flight_number,
                        'depAirport': dep,
                        'depTime': dep_time,
                        'arrAirport': arr,
                        'arrTime': arr_time,
                        'codeshare': False,
                        'cabin': lowest_price["cabin"],
                        'num': 0,
                        'aircraftCode': '',
                        'segmentType': 0
                    }
                    from_segment_list.append(from_segment)
                spider_Y9_logger.info(f"航班信息为：{from_segment_list}")

                data = {
                    'data': "/".join(flight_number_list),
                    'productClass': 'ECONOMIC',
                    'fromSegments': from_segment_list,
                    'cur': 'CAD',
                    'adultPrice': lowest_price["adultPrice"],
                    'adultTax': lowest_price["adultTax"],
                    'childPrice': 0,
                    'childTax': 0,
                    'promoPrice': 0,
                    'adultTaxType': 0,
                    'childTaxType': 0,
                    'priceType': 0,
                    'applyType': 0,
                    'max': lowest_price["max"],
                    'limitPrice': True,
                    'info': lowest_price["info"]
                }

                spider_Y9_logger.info(f"data: {data}")
                result.append(data)

            return result

        except Exception:
            spider_Y9_logger.error("解析数据失败，请查看json结构")
            spider_Y9_logger.error(f"{traceback.format_exc()}")

        return result

