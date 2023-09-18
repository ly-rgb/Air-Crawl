import json
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_FY_logger
import traceback
from spider.model import Segment


class AFYWeb(AirAgentV3Development):
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
                pass
                # end_date = (datetime.strptime(searchParam.date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
                # spider_FY_logger.info(f"取多天数据, start_date: {start_date} -> end_date: {end_date}")

            url = "https://booking.fireflyz.com.my/Search.aspx"

            payload = {"__EVENTARGUMENT": "", "__EVENTTARGET": "", "pageToken": "", "Page": "Select",
                       "ControlGroupSearchView$ButtonSubmit": "Search",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListFareTypes": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarketStructure": "OneWay",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1": searchParam.dep,
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1": searchParam.arr,
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDateRange1": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay1": start_date[
                                                                                                          -2:],
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth1": start_date[
                                                                                                            :7],
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDateRange2": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay2": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth2": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_ADT": searchParam.adt,
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_INFANT": "0",
                       "test": "", "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxPromotionCode": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListCurrency": "",
                       "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListSearchBy": "columnView"}
            headers = {
                'Host': 'booking.fireflyz.com.my',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
            }
            search_response = self.post(url=url, headers=headers, data=payload, allow_redirects=False)
            url_2 = "https://booking.fireflyz.com.my/Select.aspx"
            select_response = self.get(url=url_2, headers=headers)
            # print(select_response.cookies)
            self.select_response = select_response
            # print(self.select_response.text)
            if select_response.status_code == 200:
                spider_FY_logger.info(f"请求参数： {payload}")
                spider_FY_logger.info(f"请求结果长度为: {len(search_response.text)}")
        except Exception:
            spider_FY_logger.error(f"请求失败, 失败结果：{self.search_response.text}")
            spider_FY_logger.error(f"{traceback.format_exc()}")

    def convert_search(self):
        result = []
        try:
            soup = BeautifulSoup(self.select_response.text, 'lxml')
            tbody = soup.select('table')[13]
            trs = tbody.find_all('tr', attrs={'style': 'background-color:#ffffff;'})
            infos = [[tr.find_next('td'), *tr.find_next('td').find_next_siblings('td')] for tr in trs]
            for info in infos:
                flight = {
                    'childPrice': 0,
                    'childTax': 0,
                    'promoPrice': 0,
                    'adultTaxType': 0,
                    'childTaxType': 0,
                    'priceType': 0,
                    'applyType': 0,
                    'limitPrice': True
                }
                flight['productClass'] = 'ECONOMIC'
                for j, i in enumerate(info):
                    fromSegments = []
                    tmp = i.getText().split()
                    if j == 0:
                        flight['data'] = '/'.join(tmp) if len(i) > 1 else tmp[0]
                    # if j == 1:
                    #     flight['data'] = '/'.join(tmp) if len(i) > 1 else tmp[0]
                    if j == 2:
                        flight['cur'] = tmp[1]
                        flight['adultPrice'] = float(tmp[2]) - 1
                        flight['adultTax'] = 1
                        if 'seat' in tmp:
                            flight['max'] = int(tmp[tmp.index('seat') - 1])
                        elif 'seat' in tmp:
                            flight['max'] = int(tmp[tmp.index('seat') - 1])
                        else:
                            flight['max'] = 0
                        key = i.select_one('div > div > input')
                        key = key['value']
                        flight['info'] = key
                        seg = Segment.from_flight_key(journey_key=key.split('|')[1], fare_key=key.split('|')[0])
                        fromSegments.append(seg[0].to_dict())
                    flight['fromSegments'] = fromSegments
                result.append(flight)
            # print(result)
            return result

        except Exception:
            spider_FY_logger.error("解析数据失败，请查看json结构")
            spider_FY_logger.error(f"{traceback.format_exc()}")
