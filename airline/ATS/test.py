import os, json
import urllib3
os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.ATS.ATSWeb import api_search
    task = 'AJA,CUN,YYZ,2022-09-09,,1,,,AFARE,0,,READTIMELCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=0)
    for x in req:
        print(x["data"], x['adultPrice'], x['adultTax'], x["cur"])
        # for y in x["fromSegments"]:

