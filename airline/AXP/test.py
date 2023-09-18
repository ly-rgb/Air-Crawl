import os, json
import urllib3
from threading import Thread

os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()


if __name__ == '__main__':
    from airline.AXP.AXPWeb import api_search

    task = 'AXP,RDM,BUR,2022-09-15,,1,,,AFARE,0,,CRAWlLCC'
    task_obj = parser_from_task(task)

    code, req = api_search(task_obj, proxies_type=8)
    print(code, req)
    for x in req:
        print(x)
    # test_results(req[0], test_body)
    print("测试通过")

