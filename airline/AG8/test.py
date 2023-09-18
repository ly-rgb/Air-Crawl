import os, json
import urllib3
os.chdir("../../")

from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.AG8.AG8Web import api_search

    from airline.A6J import PayRobot6J

    # AG8, IXC, NAG, 2022 - 07 - 02,, 3,, , AFARE, 0,, CRAWlLCC
    task = 'G8,BOM,AUH,2022-09-16 ,,2,,,AFARE,0,,READTIMELCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=8)
    print(code, req)
    for x in req:
        print(x)
        # for y in x['fromSegments']:
        #     print(y)
    # data = [["HND", "KMI"], ["HND", "KMJ"], ["HND", "NGS"], ["HND", "KOJ"], ["HND", "OIT"], ["HND", "OKA"],
    #         ["KMI", "HND"], ["KMI", "NGO"], ["KMI", "OKA"], ["KMJ", "HND"], ["NGS", "HND"], ["KOJ", "HND"],
    #         ["KOJ", "NGO"], ["KOJ", "OKA"], ["OIT", "HND"], ["FUK", "OKA"], ["NGO", "KMI"], ["NGO", "KOJ"],
    #         ["NGO", "OKA"], ["UKB", "OKA"], ["OKA", "HND"], ["OKA", "KMI"], ["OKA", "KOJ"], ["OKA", "FUK"],
    #         ["OKA", "NGO"], ["OKA", "UKB"], ["OKA", "ISG"], ["ISG", "OKA"]]
    #
    # print(','.join(map(lambda x:''.join(x), data)))
