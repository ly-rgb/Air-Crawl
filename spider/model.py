from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Segment:
    carrier: str
    flightNumber: str
    depAirport: str
    depTime: str
    arrAirport: str
    arrTime: str
    codeshare: bool
    cabin: str
    num: int
    aircraftCode: str
    segmentType: int

    @classmethod
    def from_flight_key(cls, journey_key: str, cabin: str = 'Y', fare_key: str = None):
        from datetime import datetime

        result = []
        if fare_key:
            if len(journey_key.split('^')) == len(fare_key.split('^')):
                for itme, itme_2 in zip(journey_key.split('^'), fare_key.split('^')):
                    info = itme.split('~')
                    fare_info = itme_2.split('~')

                    result.append(cls(carrier=info[0],
                                      flightNumber=f'{info[0]}{info[1].replace(" ", "")}',
                                      depAirport=info[4],
                                      depTime=datetime.strptime(info[5], '%m/%d/%Y %H:%M').strftime('%Y%m%d%H%M'),
                                      arrAirport=info[6],
                                      arrTime=datetime.strptime(info[7], '%m/%d/%Y %H:%M').strftime('%Y%m%d%H%M'),
                                      codeshare=False,
                                      cabin=fare_info[1],
                                      num=0,
                                      aircraftCode='',
                                      segmentType=0))
            else:
                for itme in journey_key.split('^'):
                    info = itme.split('~')
                    result.append(cls(carrier=info[0],
                                      flightNumber=f'{info[0]}{info[1].replace(" ", "")}',
                                      depAirport=info[4],
                                      depTime=datetime.strptime(info[5], '%m/%d/%Y %H:%M').strftime('%Y%m%d%H%M'),
                                      arrAirport=info[6],
                                      arrTime=datetime.strptime(info[7], '%m/%d/%Y %H:%M').strftime('%Y%m%d%H%M'),
                                      codeshare=False,
                                      cabin=fare_key.split('~')[1],
                                      num=0,
                                      aircraftCode='',
                                      segmentType=0))

        else:
            for itme in journey_key.split('^'):
                info = itme.split('~')
                result.append(cls(carrier=info[0],
                                  flightNumber=f'{info[0]}{info[1].replace(" ", "")}',
                                  depAirport=info[4],
                                  depTime=datetime.strptime(info[5], '%m/%d/%Y %H:%M').strftime('%Y%m%d%H%M'),
                                  arrAirport=info[6],
                                  arrTime=datetime.strptime(info[7], '%m/%d/%Y %H:%M').strftime('%Y%m%d%H%M'),
                                  codeshare=False,
                                  cabin=cabin,
                                  num=0,
                                  aircraftCode='',
                                  segmentType=0))
        return result

@dataclass_json
@dataclass
class Journey:
    data: str
    fromSegments: List[Segment]
    cur: str
    adultPrice: Union[float, int]
    adultTax: Union[float, int]
    productClass: str = field(default='ECONOMIC')
    childPrice: Union[float, int] = field(default=0)
    childTax: Union[float, int] = field(default=0)
    promoPrice: Union[float, int] = field(default=0)
    adultTaxType: int = field(default=0)
    childTaxType: int = field(default=0)
    priceType: int = field(default=0)
    applyType: int = field(default=0)
    limitPrice: bool = field(default=True)
    max: str = field(default='0')
    info: str = field(default='')
