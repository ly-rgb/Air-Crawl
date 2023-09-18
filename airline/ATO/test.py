import os, json
import urllib3
os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.ATO.ATOWeb import api_search
    task = 'AJA,FEZ,ORY,2022-12-30,,1,,,AFARE,0,,READTIMELCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=6)
    print(code, req)
    for x in req:
        print(x)
    # print(','.join(map(lambda x:''.join(x), data)))
