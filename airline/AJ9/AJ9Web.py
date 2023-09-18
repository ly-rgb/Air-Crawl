import json
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_J9_logger
import traceback
from spider.model import Segment
from utils import key_tools


class AJ9Web(AirAgentV3Development):
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
            get_authorization_url = "https://j9api.jazeeraairways.com/api/Postman/api/nsk/v1/token"
            res_authorization = self.post(url=get_authorization_url)
            if res_authorization.status_code == 201:
                authorization = res_authorization.json()['data']['token']
                spider_J9_logger.info(f"authorization获取成功:{authorization}")
            else:
                raise Exception("authorization获取失败")
            headers = {
                'authorization': authorization,
                'origin': 'https://booking.jazeeraairways.com',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'content-type': 'application/json',
                'Accept': '*/*',
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'deflate, gzip, br'
            }
            payload = {
                "passengers": {"types": [{"type": "ADT", "count": str(searchParam.adt)}], "residentCountry": ""},
                "criteria": [{
                    "stations": {
                        "destinationStationCodes": [searchParam.arr],
                        "originStationCodes": [searchParam.dep],
                        "searchDestinationMacs": 'true',
                        "searchOriginMacs": 'true'},
                    "dates": {
                        "beginDate": start_date},
                    "filters": {
                        "maxConnections": 10,
                        "compressionType": "CompressByProductClass",
                        "exclusionType": "Default"}}],
                "codes": {"promotionCode": "", "currencyCode": ""},
                "numberOfFaresPerJourney": 10
            }
            ticket_url = "https://j9api.jazeeraairways.com/api/jz/v1/Availability"
            ticket_response = self.post(url=ticket_url, data=json.dumps(payload), headers=headers)
            # print(ticket_response.text)
            if ticket_response.status_code == 200:
                self.ticket_response = ticket_response
            else:
                raise Exception("ticket_response获取失败")
        except Exception as e:
            spider_J9_logger.error(f"请求失败, 失败结果：{e}")
            spider_J9_logger.error(f"{traceback.format_exc()}")

    def parse_key(self, journeyKey, fareAvailabilityKey):
        j = key_tools.decode_key(journeyKey)
        f = key_tools.decode_key(fareAvailabilityKey)
        cabin = f.split('~')[1]
        sgs = Segment.from_flight_key(journey_key=j, cabin=cabin, fare_key=f)
        data = []
        fromSegments = []
        for i in sgs:
            sg = i.to_dict()
            data.append(sg['flightNumber'])
            fromSegments.append(sg)
        return '/'.join(data), fromSegments, f + "|" + j

    def convert_search(self):
        result = []
        try:
            data = self.ticket_response.json()['data']
            results = data['availabilityv4']['results']
            if len(results) == 0:
                return []
            values = results[0]['trips'][0]['journeysAvailableByMarket'][0]['value']
            for i in values:
                ep_data = {
                    'data': '',
                    'productClass': 'ECONOMIC',
                    'fromSegments': [],
                    'cur': '',
                    'adultPrice': 9999,
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
                ep_data['cur'] = data['availabilityv4']['currencyCode']
                ep_data['adultPrice'] = data['availabilityv4']['faresAvailable'][0]['value']['totals']['fareTotal'] - 1
                fareAvailabilityKey = i['fares'][0]['fareAvailabilityKey']
                journeyKey = i['journeyKey']
                parsed_keys = self.parse_key(journeyKey, fareAvailabilityKey)
                ep_data['data'] = parsed_keys[0]
                ep_data['fromSegments'] = parsed_keys[1]
                ep_data['info'] = parsed_keys[2]
                ep_data['max'] = i['fares'][0]['details'][0]['availableCount']
                result.append(ep_data)
            return result

        except Exception:
            spider_J9_logger.error("解析数据失败，请查看json结构")
            spider_J9_logger.error(f"{traceback.format_exc()}")
