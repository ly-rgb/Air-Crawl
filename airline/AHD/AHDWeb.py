from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_HD_logger
import traceback



class AHDWeb(AirAgentV3Development):
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
            # end_date = searchParam.date
            if "CRAWlLCC" in searchParam.args:
                pass
            get_ticket_url = "https://www.airdo.jp/ap/rsv/book/search"
            params = {'roundtrip': '0',
                      'destination': 'all',
                      'from': searchParam.dep,
                      'to': searchParam.arr,
                      'departureDate': start_date,
                      'returnDate': '',
                      'adult': searchParam.adt,
                      'child': '0',
                      'infant': '0',
                      'lang': 'zh-cn'}
            headers = {
                'Host': 'www.airdo.jp',
                'Referer': 'https://www.airdo.jp/zh-cn/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                'Cookie': 'JSESSIONID=9194D57CF5BE9682DE1087BEE95F1D1B'
            }
            res_ = self.get(url=get_ticket_url, headers=headers, params=params, allow_redirects=False)
            if res_.status_code == 302:
                ticket_url = 'https://www.airdo.jp' + res_.headers['Location']
            else:
                raise Exception("ticket_url获取失败")
            ticket_res = self.get(url=ticket_url)
            if ticket_res.status_code == 200:
                self.ticket_response = ticket_res
            else:
                raise Exception("ticket_response获取失败")

        except Exception as e:
            spider_HD_logger.error(f"请求失败, 失败结果：{e}")
            spider_HD_logger.error(f"{traceback.format_exc()}")

    def parse_infos(self, infos, departure, arrival):
        result = []
        for i in infos:
            ep_data = {
                'data': '',
                'productClass': 'ECONOMIC',
                'fromSegments': [],
                'cur': 'JPY',
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
            sg = {
                'carrier': 'ADO',
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
            info = i.split('_')
            sg['depAirport'] = departure
            sg['arrAirport'] = arrival
            ep_data['data'] = 'ADO' + info[1]
            sg['flightNumber'] = 'ADO' + info[1]
            sg['depTime'] = info[0] + info[-2]
            sg['arrTime'] = info[0] + info[-1]
            sg['cabin'] = info[2]
            ep_data['adultPrice'] = float(info[4]) - 1
            ep_data['fromSegments'].append(sg)
            ep_data['info'] = i
            result.append(ep_data)
        return result

    def convert_search(self):
        try:
            html = self.etree.HTML(self.ticket_response.text)
            departure = html.xpath('//*[@id="anc-s1"]/div[1]/div[2]/span[1]/@data-place-departure')[0]
            arrival = html.xpath('//*[@id="anc-s1"]/div[1]/div[2]/span[2]/@data-place-arrival')[0]
            if not (departure and arrival):
                raise Exception('departure,arrival提取错误')
            tables = html.xpath('//div[@class="pagenation-content"]/table')[0]
            infos_ = tables.xpath(
                ".//*[contains(@class,'status-few') or contains(@class,'status-some') or contains(@class,'status-many')]/@data-flight-code")
            infos = [info for info in infos_ if 'DV3' in info]
            result = self.parse_infos(infos, departure, arrival)
            return result

        except Exception:
            spider_HD_logger.error("解析数据失败，请查看json结构")
            spider_HD_logger.error(f"{traceback.format_exc()}")
