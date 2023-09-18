import os, json
import urllib3
os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.AWS.AWSWeb import api_search
    task = 'AJA,ATL,YYG,2022-09-26,,1,,,AFARE,0,,READTIMELCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=8)
    print(len(req))
    for x in req:
        print(x)
        # print(x["fromSegments"])
        # print(x["data"], x['adultPrice'], x['adultTax'])
    # print(','.join(map(lambda x:''.join(x), data)))
