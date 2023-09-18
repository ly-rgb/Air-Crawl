import json
from dataclasses import dataclass

StationCodeMap = {"OSA": "KIX",
                  "SHA": "PVG",
                  "TYO": "NRT"}


class SearchParam:

    def __init__(self, *args):
        'CB,DGT,CEB,2021-12-11,,3,,,AFARE,0,,CRAWlLCC'
        dep = StationCodeMap.get(args[1], args[1])
        arr = StationCodeMap.get(args[2], args[2])
        self.airline = args[0]
        self.dep = dep
        self.arr = arr
        self.date = args[3]
        self.flight_no = args[-2]
        if args[5]:
            self.adt = int(args[5])
        else:
            self.adt = 1
        self.chd = 0
        self.currency = None
        self.args = args

    def __str__(self) -> str:
        return ','.join(self.args)


def parser_from_task(task: str):
    return SearchParam(*task.split(','))


def parser_from_apd_task(task: str):
    dep, arr, date, airlines = task.split('|')
    return SearchParam(json.loads(airlines), dep, arr, date, None, 1)
