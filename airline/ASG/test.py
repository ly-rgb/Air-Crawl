import os, json
import urllib3
os.chdir("../../")

from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.ASG.ASGWeb import api_search

    from airline.A6J import PayRobot6J

    task = 'AJA,DEL,AMD,2022-09-09,,5,,,AFARE,0,,CRAWlLCC2'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=8)
    print(code, req)
    # for x in req:
    #     print(x)
        # for y in x["fromSegments"]:
        #     print(y)

