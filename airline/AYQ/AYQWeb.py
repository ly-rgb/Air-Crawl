import json
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_YQ_logger
import traceback
from spider.model import Segment


class AYQWeb(AirAgentV3Development):
    """
    该航司只有直达和经停，没有中转
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.search_response = None

    def search(self, searchParam: SearchParam):
        self.number = searchParam.adt
        try:
            start_date = searchParam.date.replace("-", '')
            # end_date = searchParam.date
            if "CRAWlLCC" in searchParam.args:
                pass
            get_sessionId_url = "https://booking.tarmexico.com/ibe/1.0/TAR/flow/create/session"
            payload = {
                "roundTrip": False, "origin": searchParam.dep, "destination": searchParam.arr,
                "departureDate": start_date,
                "returnDate": "", "adults": searchParam.adt, "minors": 0, "infants": 0, "currency": "MXN",
                "country": "US",
                "promotionalCode": ""
            }
            headers = {
                'Host': 'booking.tarmexico.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'content-type': 'application/json',
                'Origin': 'https://tarmexico.com',
                'Referer': 'https://tarmexico.com/',
                'Accept-Encoding': 'gzip, deflate, br',
            }
            sessUUid_response = self.post(url=get_sessionId_url, headers=headers, data=json.dumps(payload))
            if sessUUid_response.status_code == 200:
                uuid = sessUUid_response.json()['sessionUUID']
            else:
                raise Exception("uuid获取失败")
            ticket_url = f'https://booking.tarmexico.com/ibe/1.0/TAR/{uuid}/quote/day/from/{searchParam.dep}/to/{searchParam.arr}/when/{start_date}?return='
            ticket_response = self.get(url=ticket_url, headers=headers)
            if ticket_response.text:
                self.ticket_info = ticket_response.json()
            else:
                raise Exception("ticket_info获取失败")
        except Exception as e:
            spider_YQ_logger.error(f"请求失败, 失败结果：{e}")
            spider_YQ_logger.error(f"{traceback.format_exc()}")

    def convert_search(self):
        result = []
        try:
            try:
                if len(json.dumps(self.ticket_info)) < 220:
                    return result
                else:
                    familyOptions = self.ticket_info['flights'][0]['familyOptions']
            except:
                return result

            for option in ['BASICA', 'FLEXIBLE', 'STAR']:
                if familyOptions.get(option) and familyOptions[option]['airItinInformation'][0]['availableSeats'] > 0:
                    airItinInformation = familyOptions[option]['airItinInformation'][0]
                    option_info = familyOptions.get(option)
                    if airItinInformation['stops'] == 0:
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
                        sgs = []
                        sg = {'carrier': 'YQ', 'flightNumber': '', 'depAirport': '', 'depTime': '', 'arrAirport': '',
                              'arrTime': '', 'codeshare': False, 'cabin': '', 'num': 0, 'aircraftCode': '',
                              'segmentType': 0}
                        ep_data['data'] = airItinInformation['carrierCode'] + airItinInformation['flightNumber']
                        ep_data['productClass'] = option_info['fareInfo'][0]['cabin']
                        ep_data['cur'] = option_info['quotesDetail'][0]['equivCurrCode']
                        ep_data['adultPrice'] = option_info['quotesDetail'][0]['totalFareByPtc'] - 1
                        ep_data['max'] = familyOptions[option]['airItinInformation'][0]['availableSeats']
                        sg['carrier'] = airItinInformation['carrierCode']
                        sg['flightNumber'] = airItinInformation['carrierCode'] + airItinInformation['flightNumber']
                        sg['cabin'] = option_info['fareInfo'][0]['rbd']
                        sg['depAirport'] = airItinInformation['originLocationCode']
                        sg['depTime'] = airItinInformation['departureDate'].replace("-", '') + airItinInformation[
                            'departureTime'].replace(':', '')
                        sg['arrAirport'] = airItinInformation['destinationLocationCode']
                        sg['arrTime'] = airItinInformation['departureDate'].replace("-", '') + airItinInformation[
                            'arrivalTime'].replace(':', '')
                        sgs.append(sg)
                        ep_data['fromSegments'] = sgs
                        result.append(ep_data)
                        break
                    else:
                        continue
                else:
                    continue
            return result

        except Exception:
            spider_YQ_logger.error("解析数据失败，请查看json结构")
            spider_YQ_logger.error(f"{traceback.format_exc()}")
