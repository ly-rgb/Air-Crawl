import dataclasses
import json
import os
import string
import uuid
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
import random
from typing import List, Dict, Union, Optional
from datetime import datetime

from marshmallow import fields

from native.api import get_exchange_rate_carrier
from utils.date_tools import get_age_by_birthday
from utils.searchparser import SearchParam

with open(os.path.abspath(os.path.join(os.getcwd(), './files/passenger.json')), 'r') as f:
    real_passengers = json.loads(f.read())


@dataclass_json
@dataclass
class BaggageMessageDO:
    orderId: str
    passengerName: str
    depCity: str
    arrCity: str
    baggageWeight: int
    baggagePirce: float = field(default=0)
    payOrderInfoIds: Optional[str] = field(default=None)


@dataclass_json
@dataclass
class TargetPassenger:
    passengerId: int
    orderCode: str
    name: str
    sex: str  # F or M
    birthday: str
    nationality: str
    cardIssuePlace: str
    cardExpired: Optional[str]
    certificateInformation: Optional[str]
    passengerType: str
    baggageMessageDO: Union[BaggageMessageDO, None] = field(default=None)
    retBaggageMessageDO: Optional[BaggageMessageDO] = field(default=None)
    payOrderInfoIds: Optional[str] = field(default=None)

    def gender(self, M, F) -> str:
        gender_map = {'F': F,
                      'M': M}
        return gender_map[self.sex]

    @property
    def firstName(self):
        return self.name.split('/')[-1]

    @property
    def first_name(self):
        return self.firstName

    @property
    def lastName(self):
        return self.name.split('/')[0]

    @property
    def last_name(self):
        return self.lastName

    @property
    def age(self):
        return int((datetime.now() - self.birthday_format()).days / 356)

    def age_with_dep_date(self, dep_date: datetime):
        return int((dep_date - self.birthday_format()).days / 356)

    def birthday_format(self, fmt=None) -> Union[datetime, str]:
        if '-' in self.birthday:
            birthday = datetime.strptime(self.birthday, '%Y-%m-%d')
        else:
            birthday = datetime.strptime(self.birthday, '%Y%m%d')
        if fmt:
            return birthday.strftime(fmt)
        else:
            return birthday
        #     return datetime.strptime(self.birthday, '%Y-%m-%d').strftime(fmt)
        # return datetime.strptime(self.birthday, '%Y%m%d').strftime(fmt)

    @staticmethod
    def real_random(count):
        ret = []
        passengers = random.choices(real_passengers, count)
        for i in passengers:
            tp = TargetPassenger(passengerId=i,
                                 orderCode="",
                                 name=i['name'],
                                 sex='M',
                                 birthday=i['birthday'],
                                 nationality="US",
                                 cardIssuePlace="",
                                 cardExpired="",
                                 certificateInformation="",
                                 passengerType='ADULT')
            ret.append(tp)
        return ret

    @staticmethod
    def random(count, nationality='US'):
        ret = []
        r_list = string.ascii_uppercase
        for i in range(count):
            ln = "".join(random.sample(r_list, random.randint(4, 6)))
            fn = "".join(random.sample(r_list, random.randint(4, 6)))
            name = f"{ln}/{fn}"
            birthday = f"{random.randint(1980, 2000)}-0{random.randint(1, 9)}-{random.randint(10, 28)}"
            tp = TargetPassenger(passengerId=i,
                                 orderCode="",
                                 name=name,
                                 sex='M',
                                 birthday=birthday,
                                 nationality=nationality,
                                 cardIssuePlace="",
                                 cardExpired="",
                                 certificateInformation="",
                                 passengerType='ADULT')
            ret.append(tp)
        return ret

    @property
    def passenger_type(self):
        if self.age >= 12:
            return 'ADT'
        else:
            return 'CHD'


@dataclass_json
@dataclass
class BaggageAllowance:
    isBaggageAllowance: bool = field(default=None)
    baggageAlloNum: int = field(default=None)
    baggageAlloWeight: int = field(default=None)


@dataclass_json
@dataclass
class RefundTask:
    orderCode: str
    pnr: str
    passengerName: str
    ticketPnrOid: Optional[int] = field(default=None)
    payRoute: Optional[str] = field(default=None)
    payType: Optional[str] = field(default=None)
    payTypeName: Optional[str] = field(default=None)
    payNumber: Optional[str] = field(default=None)
    needRefundPnr: Dict = field(default_factory=dict)
    taskType: str = field(default='Refund')
    baggagePnrOid: Optional[int] = field(default=None)
    refundReason: Optional[str] = field(default=None)

    @property
    def last_name(self):
        return self.passengerName.split('/')[0]

    @property
    def first_name(self):
        return self.passengerName.split('/')[1]

    @classmethod
    def from_pay_task(cls, task: dict) -> List:
        payOrder: dict = task['payOrderDetail']['payOrder']
        needRefundPnrs: list = task.get('needRefundPnrs', list())
        result = list()
        for x in needRefundPnrs:
            field_names = set(_field.name for _field in dataclasses.fields(cls))
            result.append(cls(needRefundPnr=x, taskType='Refund', orderCode=payOrder['apiSystemUuid'],
                              **{k: v for k, v in x.items() if k in field_names}))
        return result


@dataclass_json
@dataclass
class HoldTask:
    taskType: Union[str] = field(default='')
    email: Union[str] = field(default='')
    orderCode: Union[str] = field(default='')
    origin: Union[str] = field(default='')
    destination: Union[str] = field(default='')
    transit: Union[str] = field(default='')
    retTransit: Optional[str] = field(default=None)
    departTime: Union[str] = field(default='')
    retDepartTime: Optional[str] = field(default=None)
    departDate: Union[str] = field(default='')
    retDepartDate: Optional[str] = field(default=None)
    flightNumber: Union[str] = field(default='')
    retflightNumber: Optional[str] = field(default=None)
    airlineCompany: Union[str] = field(default='')
    baggageAllowance: Union[BaggageAllowance, None] = field(default=None)
    targetCur: Union[str, None] = field(default=None)
    transitTime: Union[str, None] = field(default=None)
    retTransitTime: Optional[str] = field(default=None)
    freeBaggageWeight: Union[int, None] = field(default_factory=int)
    userName: Union[str, None] = field(default_factory=str)
    passwd: Union[str, None] = field(default_factory=str)
    info: Union[str, None] = field(default=None)
    targetPrice: Union[float, None] = field(default=None)
    taskId: Union[int, None] = field(default=None)
    targetPassengers: Union[List[TargetPassenger], None] = field(default_factory=list)
    baggageMessageDOs: Union[List[BaggageMessageDO], None] = field(default_factory=list)
    retBaggageMessageDOs: List[BaggageMessageDO] = field(default_factory=list)
    tripType: Union[int, None] = field(default=None)
    contactName: Union[str, None] = field(default=None)
    contactMobile: Union[str, None] = field(default=None)
    contactEmail: Union[str, None] = field(default=None)
    tags: Union[str, None] = field(default="")
    targetCabin: Optional[str] = field(default="")
    uuid: Optional[str] = field(default=None)

    @property
    def route(self):
        return f'{self.origin}_{self.destination}_{self.flightNumber}_{self.departDate}'

    def __post_init__(self):
        for targetPassenger in self.targetPassengers:
            if (datetime.now() - targetPassenger.birthday_format()).days >= 356 * 12:
                targetPassenger.passengerType = "ADULT"
            else:
                targetPassenger.passengerType = "CHILD"

            for baggageMessageDO in self.baggageMessageDOs:
                if baggageMessageDO.depCity == self.origin and baggageMessageDO.arrCity == self.destination and targetPassenger.name == baggageMessageDO.passengerName:
                    targetPassenger.baggageMessageDO = baggageMessageDO

            for baggageMessageDO in self.retBaggageMessageDOs:
                if baggageMessageDO.arrCity == self.origin and baggageMessageDO.depCity == self.destination and targetPassenger.name == baggageMessageDO.passengerName:
                    targetPassenger.retBaggageMessageDO = baggageMessageDO

    @property
    def current_passengers(self) -> List[TargetPassenger]:

        return self.targetPassengers

    @property
    def passengerCount(self):
        return len(self.targetPassengers)

    @property
    def adt(self):
        return self.adt_with_age(12)
        # return list(filter(lambda targetPassenger: targetPassenger.passengerType == "ADULT", self.targetPassengers))

    @property
    def chd(self):
        return self.chd_with_age(12)
        # return list(filter(lambda targetPassenger: targetPassenger.passengerType != "ADULT", self.targetPassengers))

    def adt_with_age(self, age: int):
        return list(
            filter(lambda x: get_age_by_birthday(x.birthday_format(), now=self.depart_date) >= age,
                   self.current_passengers))

    def yha_with_age(self, age: int, chd_age: int):
        return list(
            filter(lambda x: chd_age <= get_age_by_birthday(x.birthday_format(), now=self.depart_date) < age,
                   self.current_passengers))

    def chd_with_age(self, age: int, inf_age=0):
        if inf_age:
            return list(
                filter(lambda x: inf_age <= get_age_by_birthday(x.birthday_format(), now=self.depart_date) < age,
                       self.current_passengers))
        else:
            return list(
                filter(lambda x: get_age_by_birthday(x.birthday_format(), now=self.depart_date) < age,
                       self.current_passengers))

    def inf_with_age(self, age: int):
        return list(filter(lambda x: get_age_by_birthday(x.birthday_format(), now=self.depart_date) < age,
                           self.current_passengers))

    @property
    def adt_count(self):
        return len(self.adt)

    @property
    def chd_count(self):
        return len(self.chd)

    @classmethod
    def from_pay_task_v2(cls, task: dict):
        if task['type'] == 3:
            return cls.from_pay_return_task(task)
        payOrder: dict = task['payOrderDetail']['payOrder']
        payFlightSegments: list = task['payOrderDetail'].get('payFlightSegments', [])
        noPayedUnitList: list = task['payOrderDetail'].get('noPayedUnitList', [])
        noPayedUnitBagList: list = task['payOrderDetail'].get('noPayedUnitBagList', [])
        guidePrice: list = task['guidePriceList']
        segments = noPayedUnitList[0]['payFlightSplicedSegment']
        noPayedUnitList = list(
            filter(lambda x: x['payFlightSplicedSegment']['flightType'] == segments['flightType'], noPayedUnitList))
        if not noPayedUnitList:
            raise Exception(f'[任务解析失败] ===> {json.dumps(task)}')
        origin = noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')[0]
        destination = noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')[-1]
        transit = ""
        transitTime = ""

        payFlightSegments = sorted(list(filter(lambda x: x['flightType'] == segments['flightType'], payFlightSegments)),
                                   key=lambda x: x['sequence'])
        if len(noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')) == 3:
            transitTime = datetime.strptime(payFlightSegments[-1]['depDate'], "%b %d, %Y %I:%M:%S %p").strftime(
                "%Y-%m-%d")
            transitTime = f'{transitTime} {payFlightSegments[-1]["depTime"].split(":")[0]}:{payFlightSegments[-1]["depTime"].split(":")[1]}'
            transit = noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')[1]

        departDate = datetime.strptime(segments['depDate'], "%b %d, %Y %I:%M:%S %p").strftime("%Y-%m-%d")
        departTime = f'{departDate} {segments["depTime"].split(":")[0]}:{segments["depTime"].split(":")[1]}'
        targetCabin = '/'.join(map(lambda pfs: pfs['cabin'], payFlightSegments))

        flightNumber = segments['flightNum']
        airlineCompany = segments['carrier'].split('/')[0]
        noPayedUnitBagList = list(
            filter(lambda x: x['payFlightSplicedSegment']['flightType'] == segments['flightType'], noPayedUnitBagList))
        guidePrice = list(filter(lambda x: x['tripType'] == segments['flightType'], guidePrice))
        this_er = get_exchange_rate_carrier(airlineCompany, guidePrice[0]['currency'])
        targetPrice = this_er * guidePrice[0]['totalPrice']
        ret = {"taskType": "PAY_ORDER",
               "email": "",
               "orderCode": payOrder['apiSystemUuid'],
               "origin": origin,
               "destination": destination,
               "transit": transit,
               "departTime": departTime,
               "departDate": departDate,
               "flightNumber": flightNumber,
               "airlineCompany": airlineCompany,
               "transitTime": transitTime,
               "baggageAllowance": {"isBaggageAllowance": False,
                                    "baggageAlloNum": 0,
                                    "baggageAlloWeight": 0},
               "freeBaggageWeight": 0,
               "userName": "",
               "passwd": "",
               "info": "",
               "targetPrice": targetPrice,
               "targetCur": "CNY",
               "taskId": task['taskNum'],
               "targetPassengers": [],
               "baggageMessageDOs": [],
               "contactName": task.get('contactName', None),
               "contactMobile": task.get('contactMobile', None),
               "contactEmail": task.get('contactEmail', None),
               "tags": payOrder.get("tags", ""),
               "targetCabin": targetCabin,
               "uuid": payOrder.get("uuid", None)}
        index = 0
        for x in noPayedUnitList:
            payFlightSplicedSegment = x['payFlightSplicedSegment']
            payPassenger = x['payPassenger']
            if payFlightSplicedSegment['flightNum'] != ret["flightNumber"]:
                continue
            age = get_age_by_birthday(payPassenger['birthday'], "%b %d, %Y %I:%M:%S %p")
            if age >= 12:
                passengerType = "ADULT"
            else:
                passengerType = "CHILD"
            card_expired = payPassenger.get('cardTimeLimit', None)
            if card_expired is not None:
                card_expired = datetime.strptime(card_expired, "%b %d, %Y %I:%M:%S %p").strftime("%Y-%m-%d")
            ret["targetPassengers"].append({"passengerId": index,
                                            "orderCode": payPassenger['payOrderUuid'],
                                            "name": payPassenger['passengerName'],
                                            "sex": payPassenger['gender'],
                                            "birthday": datetime.strptime(payPassenger['birthday'],
                                                                          "%b %d, %Y %I:%M:%S %p").strftime("%Y%m%d"),
                                            "nationality": payPassenger['nationality'],
                                            "cardIssuePlace": payPassenger['certIssueCountry'],
                                            "cardExpired": card_expired,
                                            "certificateInformation": payPassenger['cardNo'],
                                            "passengerType": passengerType,
                                            "payOrderInfoIds": x['payOrderInfoIds']})
            index += 1
        for x in noPayedUnitBagList:
            payFlightSplicedSegment = x['payFlightSplicedSegment']
            if payFlightSplicedSegment['flightNum'] != ret["flightNumber"]:
                continue
            payPassengerBaggage = x['payPassengerBaggage']
            ret["baggageMessageDOs"].append({"orderId": payPassengerBaggage['payOrderUuid'],
                                             "passengerName": payPassengerBaggage['payPassengerName'],
                                             "depCity": ret['origin'],
                                             "arrCity": ret['destination'],
                                             "baggageWeight": payPassengerBaggage['baggageWeight'],
                                             "baggagePirce": payPassengerBaggage['baggagePrice'],
                                             "payOrderInfoIds": x['payOrderInfoIds']})
        ret["targetPassengers"] = sorted(ret["targetPassengers"], key=lambda p: p['birthday'])
        index = 0
        for p in ret["targetPassengers"]:
            p['passengerId'] = index
            index += 1
        return cls.from_dict(ret)

    @staticmethod
    def __get_info(task, flightType: int):
        payFlightSegments: list = task['payOrderDetail'].get('payFlightSegments', [])
        noPayedUnitList: list = task['payOrderDetail'].get('noPayedUnitList', [])
        noPayedUnitBagList: list = task['payOrderDetail'].get('noPayedUnitBagList', [])
        noPayedUnitList = list(
            filter(lambda x: x['payFlightSplicedSegment']['flightType'] == flightType, noPayedUnitList))
        segments = noPayedUnitList[0]['payFlightSplicedSegment']
        if not noPayedUnitList:
            raise Exception(f'[任务解析失败] ===> {json.dumps(task)}')
        origin = noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')[0]
        destination = noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')[-1]
        transit = ""
        transitTime = ""

        payFlightSegments = sorted(list(filter(lambda x: x['flightType'] == segments['flightType'], payFlightSegments)),
                                   key=lambda x: x['sequence'])
        if len(noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')) == 3:
            transitTime = datetime.strptime(payFlightSegments[-1]['depDate'], "%b %d, %Y %I:%M:%S %p").strftime(
                "%Y-%m-%d")
            transitTime = f'{transitTime} {payFlightSegments[-1]["depTime"].split(":")[0]}:{payFlightSegments[-1]["depTime"].split(":")[1]}'
            transit = noPayedUnitList[0]['payFlightSplicedSegment']['portSegment'].split('-')[1]

        departDate = datetime.strptime(segments['depDate'], "%b %d, %Y %I:%M:%S %p").strftime("%Y-%m-%d")
        departTime = f'{departDate} {segments["depTime"].split(":")[0]}:{segments["depTime"].split(":")[1]}'
        targetCabin = '/'.join(map(lambda pfs: pfs['cabin'], payFlightSegments))

        flightNumber = segments['flightNum']
        airlineCompany = segments['carrier'].split('/')[0]
        noPayedUnitBagList = list(
            filter(lambda _x: _x['payFlightSplicedSegment']['flightType'] == segments['flightType'],
                   noPayedUnitBagList))
        return {
            'airlineCompany': airlineCompany,
            'origin': origin,
            'destination': destination,
            'transit': transit,
            'departTime': departTime,
            'departDate': departDate,
            'flightNumber': flightNumber,
            'transitTime': transitTime,
            'targetCabin': targetCabin,
            'noPayedUnitBagList': noPayedUnitBagList
        }

    @classmethod
    def from_pay_return_task(cls, task: dict):
        payOrder: dict = task['payOrderDetail']['payOrder']
        payFlightSegments: list = task['payOrderDetail'].get('payFlightSegments', [])
        noPayedUnitList: list = task['payOrderDetail'].get('noPayedUnitList', [])
        noPayedUnitBagList: list = task['payOrderDetail'].get('noPayedUnitBagList', [])
        guidePrice: list = task['guidePriceList']

        to_trip = cls.__get_info(task, 1)
        ret_trip = cls.__get_info(task, 2)

        guidePrice = list(filter(lambda x: x['tripType'] == task['type'], guidePrice))
        this_er = get_exchange_rate_carrier(to_trip['airlineCompany'], guidePrice[0]['currency'])
        targetPrice = this_er * guidePrice[0]['totalPrice']
        ret = {"taskType": "PAY_ORDER",
               "email": "",
               "orderCode": payOrder['apiSystemUuid'],
               "origin": to_trip['origin'],
               "destination": to_trip['destination'],
               "transit": to_trip['transit'],
               "retTransit": ret_trip['transit'],
               "departTime": to_trip['departTime'],
               "retDepartTime": ret_trip['departTime'],
               "departDate": to_trip['departDate'],
               "retDepartDate": ret_trip['departDate'],
               "flightNumber": to_trip['flightNumber'],
               "retflightNumber": ret_trip['flightNumber'],
               "airlineCompany": to_trip['airlineCompany'],
               "transitTime": to_trip['transitTime'],
               "retTransitTime": ret_trip['transitTime'],
               "baggageAllowance": {"isBaggageAllowance": False,
                                    "baggageAlloNum": 0,
                                    "baggageAlloWeight": 0},
               "freeBaggageWeight": 0,
               "userName": "",
               "passwd": "",
               "info": "",
               "targetPrice": targetPrice,
               "targetCur": "CNY",
               "taskId": task['taskNum'],
               "targetPassengers": [],
               "baggageMessageDOs": [],
               "retBaggageMessageDOs": [],
               "contactName": task.get('contactName', None),
               "contactMobile": task.get('contactMobile', None),
               "contactEmail": task.get('contactEmail', None),
               "tags": payOrder.get("tags", ""),
               "targetCabin": to_trip['targetCabin'],
               "uuid": payOrder.get("uuid", None)}
        index = 0
        for x in noPayedUnitList:
            payFlightSplicedSegment = x['payFlightSplicedSegment']
            payPassenger = x['payPassenger']
            if payFlightSplicedSegment['flightNum'] != ret["flightNumber"]:
                continue
            age = get_age_by_birthday(payPassenger['birthday'], "%b %d, %Y %I:%M:%S %p")
            if age >= 12:
                passengerType = "ADULT"
            else:
                passengerType = "CHILD"
            ret["targetPassengers"].append({"passengerId": index,
                                            "orderCode": payPassenger['payOrderUuid'],
                                            "name": payPassenger['passengerName'],
                                            "sex": payPassenger['gender'],
                                            "birthday": datetime.strptime(payPassenger['birthday'],
                                                                          "%b %d, %Y %I:%M:%S %p").strftime("%Y%m%d"),
                                            "nationality": payPassenger['nationality'],
                                            "cardIssuePlace": payPassenger['certIssueCountry'],
                                            "cardExpired": "",
                                            "certificateInformation": "",
                                            "passengerType": passengerType,
                                            "payOrderInfoIds": x['payOrderInfoIds']})
            index += 1
        for x in noPayedUnitBagList:
            payFlightSplicedSegment = x['payFlightSplicedSegment']
            if payFlightSplicedSegment['flightNum'] != ret["flightNumber"]:
                continue
            depCity = payFlightSplicedSegment['portSegment'].split('-')[0]
            arrCity = payFlightSplicedSegment['portSegment'].split('-')[-1]
            payPassengerBaggage = x['payPassengerBaggage']
            ret["baggageMessageDOs"].append({"orderId": payPassengerBaggage['payOrderUuid'],
                                             "passengerName": payPassengerBaggage['payPassengerName'],
                                             "depCity": depCity,
                                             "arrCity": arrCity,
                                             "baggageWeight": payPassengerBaggage['baggageWeight'],
                                             "baggagePrice": payPassengerBaggage["baggagePrice"],
                                             "payOrderInfoIds": x['payOrderInfoIds']})

        for x in noPayedUnitBagList:
            payFlightSplicedSegment = x['payFlightSplicedSegment']
            if payFlightSplicedSegment['flightNum'] != ret["retflightNumber"]:
                continue
            depCity = payFlightSplicedSegment['portSegment'].split('-')[0]
            arrCity = payFlightSplicedSegment['portSegment'].split('-')[-1]
            payPassengerBaggage = x['payPassengerBaggage']
            ret["retBaggageMessageDOs"].append({"orderId": payPassengerBaggage['payOrderUuid'],
                                                "passengerName": payPassengerBaggage['payPassengerName'],
                                                "depCity": depCity,
                                                "arrCity": arrCity,
                                                "baggageWeight": payPassengerBaggage['baggageWeight'],
                                                "baggagePrice": payPassengerBaggage["baggagePrice"],
                                                "payOrderInfoIds": x['payOrderInfoIds']})

        ret["targetPassengers"] = sorted(ret["targetPassengers"], key=lambda p: p['birthday'])
        index = 0
        for p in ret["targetPassengers"]:
            p['passengerId'] = index
            index += 1
        return cls.from_dict(ret)

    @classmethod
    def from_pay_task(cls, task: dict):
        return cls.from_pay_task_v2(task)

    @classmethod
    def from_bag_task(cls, depAirport: str, arrAirport: str, depDate: str, flightNo: str):
        return cls(taskType="BAG_TASK",
                   orderCode=",".join([depAirport, arrAirport, depDate, flightNo]),
                   origin=depAirport,
                   destination=arrAirport,
                   departDate=depDate,
                   flightNumber=flightNo,
                   targetPrice=1000000,
                   targetPassengers=TargetPassenger.random(1))

    def select_key(self, ignore_departTime_check=False):
        if ignore_departTime_check:
            return self.flightNumber
        if self.transitTime:
            key = self.flightNumber + '_' + '/'.join([self.departTime, self.transitTime])
        else:
            key = self.flightNumber + '_' + self.departTime
        return key

    @property
    def depart_date(self) -> datetime:
        return datetime.strptime(self.departDate, '%Y-%m-%d')

    @classmethod
    def from_ah_task(cls, ah_task, passenger: int, is_real=False):
        if is_real:
            targetPassengers = TargetPassenger.real_random(passenger)
        else:
            targetPassengers = TargetPassenger.random(passenger)
        ret = {"taskType": "AHTask",
               "email": "",
               "orderCode": ah_task.cache_key,
               "origin": ah_task.dep,
               "destination": ah_task.arr,
               "transit": "",
               "departTime": "",
               "departDate": ah_task.date,
               "flightNumber": ah_task.flight_no,
               "airlineCompany": ah_task.flight_no[:2],
               "transitTime": "",
               "baggageAllowance": {"isBaggageAllowance": False,
                                    "baggageAlloNum": 0,
                                    "baggageAlloWeight": 0},
               "targetCur": "",
               "freeBaggageWeight": 0,
               "userName": "",
               "passwd": "",
               "info": "",
               "targetPrice": "",
               "taskId": ah_task.cache_key,
               "targetPassengers": targetPassengers,
               "baggageMessageDOs": []}
        return cls.from_dict(ret)

    @classmethod
    def from_search_param(cls, searchParam: SearchParam):
        return cls.from_dict({
            'taskType': 'SEARCH',
            'orderCode': searchParam.__str__(),
            'origin': searchParam.dep,
            'destination': searchParam.arr,
            'departDate': searchParam.date,
            'targetPassengers': TargetPassenger.random(searchParam.adt),
            'flightNumber': searchParam.flight_no
        })

    @classmethod
    def from_add_on_task(cls, task: str):
        task = task.split(',')
        if len(task) != 7:
            task.insert(2, '')
        return cls.from_dict({
            'taskType': 'ADDON',
            'orderCode': ','.join(task),
            'origin': task[1],
            'transit': task[2],
            'destination': task[3],
            'departDate': task[5],
            'targetPassengers': TargetPassenger.random(1),
            'targetPrice': 100000000
        })

    @classmethod
    def new_test(cls, origin, destination, departDate, flightNumber, retDepartDate, retflightNumber):
        return cls.from_dict({
            'taskType': 'SEARCH',
            'orderCode': str(uuid.uuid4()),
            'origin': origin,
            'destination': destination,
            'departDate': departDate,
            'targetPassengers': TargetPassenger.random(1),
            'flightNumber': flightNumber,
            'retDepartDate': retDepartDate,
            'retflightNumber': retflightNumber
        })

    @classmethod
    def new_test_one(cls, origin, destination, departDate, flightNumber, ):
        return cls.from_dict({
            'taskType': 'SEARCH',
            'orderCode': str(uuid.uuid4()),
            'origin': origin,
            'destination': destination,
            'departDate': departDate,
            'targetPassengers': TargetPassenger.random(1),
            'flightNumber': flightNumber
        })

    @classmethod
    def new_test_booking_one(cls, origin, destination, departDate, flightNumber, adt: int, targetPrice: float):
        return cls.from_dict({
            'taskType': 'PAY_ORDER',
            'orderCode': str(uuid.uuid4()),
            'origin': origin,
            'destination': destination,
            'departDate': departDate,
            'targetPassengers': TargetPassenger.random(adt),
            'flightNumber': flightNumber,
            'targetPrice': targetPrice
        })


@dataclass_json
@dataclass
class HoldPassenger:
    passengerName: str
    passengerNo: str


@dataclass_json
@dataclass
class HoldResult:
    orderUuid: str
    depCity: str
    arrCity: str
    flightNumber: str
    depTime: str
    pnr: str
    totalPrice: float
    ticketPrice: float
    baggagePrice: float
    currency: str
    expirationTime: str
    holdAccount: str
    imageUrl: str
    machineAddress: str
    statusCode: int
    tripType: int
    type: int
    holdRoute: str
    holdEmail: str
    cabin: str
    contact: str
    contactMobile: str
    holdTime: str
    passengerList: List[HoldPassenger] = field(default_factory=list)
    targetPrice: float = field(default=None)
    targetCurrency: str = field(default=None)
    # statusCode: str = field(default=None)


@dataclass_json
@dataclass
class PayOrder:
    uuid: str = field(default=None)
    otaId: str = field(default=None)
    otaCompany: int = field(default=None)
    groupCode: str = field(default=None)
    fromFlightNum: str = field(default=None)
    fromFlightSegment: str = field(default=None)
    fromFlightCarrier: str = field(default=None)
    depDate: str = field(default=None)
    ticketPrice: float = field(default=None)
    ticketTax: float = field(default=None)
    totalPrice: float = field(default=None)
    bookingTime: str = field(default=None)
    createTime: str = field(default=None)
    apiSystemUuid: str = field(default=None)
    depAirport: str = field(default=None)
    arrAirport: str = field(default=None)
    tripType: int = field(default=None)
    commissionPrice: float = field(default=None)
    remark: str = field(default=None)
    selPnr: str = field(default=None)
    adtCount: int = field(default=None)
    chidCount: int = field(default=None)
    infantCount: int = field(default=None)
    status: int = field(default=None)
    userId: int = field(default=None)
    userName: str = field(default=None)
    orderType: int = field(default=None)
    tags: str = field(default=None)
    cost: int = field(default=None)
    profit: int = field(default=None)
    totalBaggagePrice: float = field(default=None)
    baggageCommissionPrice: float = field(default=None)
    baggageCost: float = field(default=None)
    baggageProfit: float = field(default=None)
    checkinProfit: float = field(default=None)
    handleRank: int = field(default=None)
    releaseTime: str = field(default=None)
    firstPullTime: int = field(default=None)
    otaFillStatus: int = field(default=None)
    productId: str = field(default=None)
    priceId: str = field(default=None)
    quoteChannel: str = field(default=None)
    priceGroupId: str = field(default=None)
    shuaPiao: bool = field(default=False)


@dataclass_json
@dataclass
class payFlightSegment:
    oid: int = field(default=None)
    payOrderUuid: str = field(default=None)
    carrier: str = field(default=None)
    depCity: str = field(default=None)
    depPort: str = field(default=None)
    arrCity: str = field(default=None)
    arrPort: str = field(default=None)
    flightNum: str = field(default=None)
    flightNumPull: str = field(default=None)
    depDate: str = field(default=None)
    arrDate: str = field(default=None)
    cabin: str = field(default=None)
    depTime: str = field(default=None)
    arrTime: str = field(default=None)
    sequence: int = field(default=None)
    flightType: int = field(default=None)


@dataclass_json
@dataclass
class PayPassenger:
    oid: int = field(default=None)
    payOrderUuid: str = field(default=None)
    passengerName: str = field(default=None)
    ageType: int = field(default=None)
    birthday: str = field(default=None)
    cardNo: str = field(default=None)
    cardTimeLimit: str = field(default=None)
    cardType: str = field(default=None)
    gender: str = field(default=None)
    nationality: str = field(default=None)
    certIssueCountry: str = field(default=None)
    enNationality: str = field(default=None)
    enCertIssueCountry: str = field(default=None)
    enCardType: str = field(default=None)


@dataclass_json
@dataclass
class PayFlightSplicedSegment:
    splicedOid: str = field(default=None)
    carrier: str = field(default=None)
    citySegment: str = field(default=None)
    portSegment: str = field(default=None)
    flightNum: str = field(default=None)
    depDate: str = field(default=None)
    arrDate: str = field(default=None)
    flightType: int = field(default=None)
    depTime: str = field(default=None)
    arrTime: str = field(default=None)


@dataclass_json
@dataclass
class PayPassengerBaggage:
    oid: int = field(default=None)
    payOrderUuid: str = field(default=None)
    payPassengerOid: int = field(default=None)
    payFlightSegmentOid: int = field(default=None)
    baggageWeight: int = field(default=None)
    baggagePrice: float = field(default=None)
    payOrderInfoOid: int = field(default=None)
    payPassengerName: str = field(default=None)
    otaBaggageId: str = field(default=None)


@dataclass_json
@dataclass
class PayedUnit:
    payFlightSplicedSegment: PayFlightSplicedSegment = field(default=None)
    payPassenger: PayPassenger = field(default=None)
    payOrderInfoIds: str = field(default=None)
    type: str = field(default=None)


@dataclass_json
@dataclass
class PayedUnitBag:
    payFlightSplicedSegment: PayFlightSplicedSegment = field(default=None)
    payPassenger: PayPassenger = field(default=None)
    payPassengerBaggage: PayPassengerBaggage = field(default=None)
    payOrderInfoIds: str = field(default=None)
    type: str = field(default=None)


@dataclass_json
@dataclass
class PayFlightSegment:
    oid: int = field(default=None)
    payOrderUuid: str = field(default=None)
    carrier: str = field(default=None)
    depCity: str = field(default=None)
    depPort: str = field(default=None)
    arrCity: str = field(default=None)
    arrPort: str = field(default=None)
    flightNum: str = field(default=None)
    flightNumPull: str = field(default=None)
    depDate: str = field(default=None)
    arrDate: str = field(default=None)
    cabin: str = field(default=None)
    depTime: str = field(default=None)
    arrTime: str = field(default=None)
    sequence: int = field(default=None)
    flightType: int = field(default=None)


@dataclass_json
@dataclass
class PayOrderDetail:
    payOrder: PayOrder = field(default=None)
    payFlightSegments: List[PayFlightSegment] = field(default_factory=list)
    payPassengers: List[PayPassenger] = field(default_factory=list)
    payPassengerBaggages: List[PayPassengerBaggage] = field(default_factory=list)
    noPayedUnitList: List[PayedUnit] = field(default_factory=list)
    noPayedUnitBagList: List[PayedUnitBag] = field(default_factory=list)


@dataclass_json
@dataclass
class GuidePrice:
    totalPrice: float = field(default=None)
    currency: str = field(default=None)
    tripType: int = field(default=None)


@dataclass_json
@dataclass
class PaymentMethod:
    id: int = field(default=None)
    payment: int = field(default=None)
    paynumber: str = field(default=None)
    name: str = field(default=None)
    cardexpired: str = field(default=None)
    CVV: str = field(default=None)
    owner: str = field(default=None)
    password: str = field(default=None)
    status: int = field(default=None)


@dataclass_json
@dataclass
class PaymentAccount:
    id: int = field(default=None)
    carrier: str = field(default=None)
    short_name: str = field(default=None)
    account: str = field(default=None)
    password: str = field(default=None)
    status: int = field(default=None)


@dataclass_json
@dataclass
class NotHoldAutomaticPayOrderResult:
    payOrderDetail: PayOrderDetail = field(default=None)
    guidePriceList: List[GuidePrice] = field(default_factory=list)
    paymentMethod: PaymentMethod = field(default_factory=list)
    paymentAccount: PaymentAccount = field(default_factory=list)
    carrier: str = field(default=None)
    freeBaggageWeight: int = field(default=None)
    taskNum: str = field(default=None)
    contactName: str = field(default=None)
    contactMobile: str = field(default=None)
    contactEmail: str = field(default=None)
    type: int = field(default=None)
    code: int = field(default=None)


@dataclass_json
@dataclass
class HoldPnrProto:
    depCity: str = field(default=None)
    arrCity: str = field(default=None)
    flightNumber: str = field(default=None)
    depTime: str = field(default=None)
    pnr: str = field(default=None)
    totalPrice: float = field(default=None)
    ticketPrice: float = field(default=None)
    baggagePrice: float = field(default=None)
    currency: str = field(default=None)
    holdTime: str = field(default=None)
    expirationTime: str = field(default=None)
    holdAccount: str = field(default=None)
    password: str = field(default=None)
    statusCode: int = field(default=None)
    passengerNameList: str = field(default=None)
    tripType: int = field(default=None)
    holdEmail: str = field(default=None)
    cabin: str = field(default=None)


@dataclass_json
@dataclass
class HoldPayTask:
    notHoldAutomaticPayOrderResult: NotHoldAutomaticPayOrderResult = field(default=None)
    holdPnrProto: HoldPnrProto = field(default=None)
    code: int = field(default=None)


@dataclass_json
@dataclass
class RefundTaskV2:
    id: str
    otaId: str
    pnr: str
    carrier: str
    flightNumber: str
    passengerName: str
    email: str
    phone: str
    refundTicketType: str
    depTime: datetime = field(
        metadata=config(
            encoder=lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),
            decoder=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'),
            mm_field=fields.DateTime(format='%Y-%m-%d %H:%M:%S')
        )
    )
    applyType: Optional[int] = field(default=None)
    businessType: Optional[str] = field(default=None)
    handleResult: bool = field(default=False)
    caseNumber: Optional[str] = field(default=None)
    message: Optional[str] = field(default=None)
    flightSegment: Optional[str] = field(default=None)
    payRoutePassword: Optional[str] = field(default=None)
    payOrderUuid: Optional[str] = field(default=None)

    @property
    def last_name(self):
        return self.passengerName.split('/')[0]

    @property
    def first_name(self):
        return self.passengerName.split('/')[1]


@dataclass_json
@dataclass
class AddOnResult:
    carrier: str
    depAirport: str
    arrAirport: str
    flightNum: str
    scaleDesp: str
    price: float
    currency: str
    isAllWeight: int = field(default=0)
    rmRule: str = field(default='0000')
    type: int = field(default=11)
    transAirport: Optional[str] = field(default=None)
    uniCode: str = field(init=False)

    def __post_init__(self):
        self.uniCode = f'{self.carrier}{self.depAirport}{self.transAirport}{self.arrAirport}{self.scaleDesp}{self.type}'

    @classmethod
    def from_baggage(cls, task: HoldTask, baggage, carrier=None) -> 'AddOnResult':
        return cls(carrier=carrier or task.flightNumber[:2],
                   depAirport=task.origin,
                   transAirport=task.transit,
                   arrAirport=task.destination,
                   flightNum=task.flightNumber,
                   scaleDesp=str(baggage.weight),
                   price=baggage.base_price,
                   currency=baggage.base_currency,
                   type=baggage.type)
