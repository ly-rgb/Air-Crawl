import os, json
import time

import urllib3
os.chdir("../../")

from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.AV7.AV7Web import api_search

    task = 'AV7,LCG,BIO,2022-09-02,,1,,,AFARE,0,,CRAWlLCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=7)
    for x in req:
        print(x)


