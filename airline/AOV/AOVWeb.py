import json
import re
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_OV_logger
import traceback
from datetime import datetime, timedelta


class AOVWeb(AirAgentV3Development):
    '''
    proxies_type=7 该代理失败率高，可以尝试不挂
    '''

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.search_response = None

    def search(self, searchParam: SearchParam):
        self.number = searchParam.adt
        try:
            start_date = searchParam.date
            if "CRAWlLCC" in searchParam.args:
                pass
            get_sess_token_url = "https://api.salamair.com/api/session"
            sess_token_res = self.post(url=get_sess_token_url)
            if sess_token_res.status_code == 204:
                sess_token = sess_token_res.headers['X-Session-Token']
            else:
                raise Exception('sess_token获取失败..')
            ticket_info_url = "https://api.salamair.com/api/flights"
            headers = {
                'X-Session-Token': sess_token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            }
            params = {
                'TripType': '1',
                'OriginStationCode': searchParam.dep,
                'DestinationStationCode': searchParam.arr,
                'DepartureDate': start_date,
                'AdultCount': str(searchParam.adt),
                'ChildCount': '0',
                'InfantCount': '0',
                'extraCount': '0',
                'days': '7',
                'currencyCode': ''
            }
            ticket_info_res = self.get(url=ticket_info_url, headers=headers, params=params)
            if ticket_info_res.status_code == 200:
                self.ticket_info = ticket_info_res.json()
            else:
                raise Exception('ticket_info获取失败..')


        except Exception as e:
            spider_OV_logger.error(f"请求失败, 失败结果：{e}")
            spider_OV_logger.error(f"{traceback.format_exc()}")

    def parse_info(self, markets, cur):
        result = []
        cabin = 'Y'
        for market in markets:
            ep_data = {
                'data': '',
                'productClass': 'ECONOMIC',
                'fromSegments': [],
                'cur': '',
                'adultPrice': 999999,
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
            ep_data['cur'] = cur
            if market['flights'] == None:
                continue
            for fare in market['flights'][0]['fares']:
                if fare['fareInfos'][0]['seatsAvailable'] > 0:
                    ep_data['adultPrice'] = fare['fareInfos'][0]['fareWithTaxes']-1
                    cabin = fare['fareInfos'][0]['fareClassCode']
                    break
                else:
                    continue
            segments = market['flights'][0]['segments']
            sgs = []
            for leg in segments[0]['legs']:
                sg = {
                    'carrier': '',
                    'flightNumber': '',
                    'depAirport': '',
                    'depTime': '',
                    'arrAirport': '',
                    'arrTime': '',
                    'codeshare': False,
                    'cabin': '',
                    'num': 0,
                    'aircraftCode': '',
                    'segmentType': 0
                }
                sg['carrier'] = leg['carrierCode']
                sg['flightNumber'] = leg['carrierCode'] + leg['flightNumber']
                sg['aircraftCode'] = leg['aircraftType']
                sg['depAirport'] = leg['origin']
                sg['depTime'] = datetime.strptime(leg['departureDate'], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                sg['arrAirport'] = leg['destination']
                sg['arrTime'] = datetime.strptime(leg['arrivalDate'], "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
                ep_data['max'] = market['flights'][0]['seatsAvailable']
                sg['cabin'] = cabin
                sgs.append(sg)
            ep_data['fromSegments'] = sgs
            ep_data['data'] = '/'.join([i['flightNumber'] for i in sgs])
            if ep_data['adultPrice'] !=999999:
                result.append(ep_data)
        return result

    def convert_search(self):
        try:
            cur = self.ticket_info['searchRequest']['currencyCode']
            markets = self.ticket_info['trips'][0]['markets']
            result = self.parse_info(markets, cur)
            return result

        except Exception:
            spider_OV_logger.error("解析数据失败，请查看json结构")
            spider_OV_logger.error(f"{traceback.format_exc()}")
