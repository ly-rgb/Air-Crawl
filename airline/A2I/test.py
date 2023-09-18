import os, json
import urllib3
os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.A2I.A2IWeb import api_search
    task = 'AJA,LIM,CJA,2022-09-17,,1,,,AFARE,0,,READTIMELCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=0)
    print(code, req)
    # for x in req:
    #     print(x)
    # data = [["HND", "KMI"], ["HND", "KMJ"], ["HND", "NGS"], ["HND", "KOJ"], ["HND", "OIT"], ["HND", "OKA"],
    #         ["KMI", "HND"], ["KMI", "NGO"], ["KMI", "OKA"], ["KMJ", "HND"], ["NGS", "HND"], ["KOJ", "HND"],
    #         ["KOJ", "NGO"], ["KOJ", "OKA"], ["OIT", "HND"], ["FUK", "OKA"], ["NGO", "KMI"], ["NGO", "KOJ"],
    #         ["NGO", "OKA"], ["UKB", "OKA"], ["OKA", "HND"], ["OKA", "KMI"], ["OKA", "KOJ"], ["OKA", "FUK"],
    #         ["OKA", "NGO"], ["OKA", "UKB"], ["OKA", "ISG"], ["ISG", "OKA"]]
    #
    # print(','.join(map(lambda x:''.join(x), data)))
