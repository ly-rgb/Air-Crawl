import os, json
import urllib3

os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

test_body = {'data': 'GQ290', 'productClass': 'ECONOMY', 'fromSegments': [
    {'carrier': 'GQ', 'flightNumber': 'GQ290', 'depAirport': 'ATH', 'depTime': '202206160715',
     'arrAirport': 'AXD', 'arrTime': '202206150820', 'codeshare': False, 'cabin': 'ECONOMY', 'num': 0,
     'aircraftCode': 'ATR72 600 New', 'segmentType': 0}], 'cur': 'EUR', 'adultPrice': 66.99,
             'adultTax': 31.989999999999995, 'childPrice': 0, 'childTax': 0, 'promoPrice': 0, 'adultTaxType': 0,
             'childTaxType': 0, 'priceType': 0, 'applyType': 0, 'max': 2, 'limitPrice': True, 'info': ''}


def test_results(x1, x2):
    if type(x1) == dict:
        for x in x1.keys():
            if x1[x] != x2[x] and x != 'fromSegments':
                raise TypeError(x, x1[x], x2[x])
            else:
                test_results(x1[x], x2[x])


if __name__ == '__main__':
    from airline.AGQ.AGQWeb import api_search

    task = 'AJA,ATH,AXD,2022-09-08,,1,,,AFARE,0,,CRAWlLCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=8)
    for x in req:
        print(x)
    #     for y in x['fromSegments']:
    #         print(x['adultPrice'], y)
    # # test_results(req[0], test_body)
    # print("测试通过")

