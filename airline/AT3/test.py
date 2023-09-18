import os, json
import urllib3
os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.AT3.AT3Web import api_search
    """
    AJA: 航司二字码
    LIM: 出发地
    CJA：目的地
    日期：起飞的日期
    READTIMELCC：
    CRAWlLCC 为采集任务， 如果为其他的则判定为扫价，需要删除多天采集条件， 多天搜索
    """
    task = 'AT3,SOU,DUB,2022-12-30,,1,,,AFARE,0,,CRAWlLCC'
    task_obj = parser_from_task(task)
    print(task_obj)
    code, req = api_search(task_obj, proxies_type=0)
    print(code, req)
    for x in req:
        print(x)
    # data = [["HND", "KMI"], ["HND", "KMJ"], ["HND", "NGS"], ["HND", "KOJ"], ["HND", "OIT"], ["HND", "OKA"],
    #         ["KMI", "HND"], ["KMI", "NGO"], ["KMI", "OKA"], ["KMJ", "HND"], ["NGS", "HND"], ["KOJ", "HND"],
    #         ["KOJ", "NGO"], ["KOJ", "OKA"], ["OIT", "HND"], ["FUK", "OKA"], ["NGO", "KMI"], ["NGO", "KOJ"],
    #         ["NGO", "OKA"], ["UKB", "OKA"], ["OKA", "HND"], ["OKA", "KMI"], ["OKA", "KOJ"], ["OKA", "FUK"],
    #         ["OKA", "NGO"], ["OKA", "UKB"], ["OKA", "ISG"], ["ISG", "OKA"]]
    #
    # print(','.join(map(lambda x:''.join(x), data)))
