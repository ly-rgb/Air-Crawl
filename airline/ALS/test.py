import os, json
import urllib3
os.chdir("../../")
from utils.searchparser import parser_from_task

urllib3.disable_warnings()

if __name__ == '__main__':
    from airline.ALS.ALSWeb import api_search
    task = 'AJA,LBA,EGC,2022-09-16,,1,,,AFARE,0,,READTIMELCC'
    task_obj = parser_from_task(task)
    code, req = api_search(task_obj, proxies_type=35)
    print(code, req)
    for x in req:
        print(x)
#     # print(','.join(map(lambda x:''.join(x), data)))
# https://www.jet2.com/en/cheap-flights/leeds-bradford/bergerac?from=2022-07-16&adults=1&children&infants=0&preselect=true
# https://www.jet2.com/en/cheap-flights/leeds-bradford/bergerac?from=2022-07-16&adults=1&children&infants=0&preselect=true