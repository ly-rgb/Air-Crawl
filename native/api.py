import json
import string
import random
from typing import Optional

import requests
from config import config, apd_config
from datetime import datetime
from dateutil import rrule
from enumerate.hold import PassengerType
from utils.log import card_logger, api_logger
import time
from utils.func_helper import func_retry



def retry_decorator(*d_args, **d_kwargs):

    def wrapper(func):
        def process_wrap(*args, **kwargs):
            retry_num = 0
            while True:
                try:
                    ret = func(*args, **kwargs)
                    return ret
                except Exception as e:
                    retry_num += 1
                    import traceback
                    api_logger.error(f'{traceback.format_exc()}')
                    if retry_num > 10:
                        if d_args:
                            raise Exception(d_args[0])
                        else:
                            raise e
                    else:
                        time.sleep(0.2)
        return process_wrap
    return wrapper


def add_passenger_type(date, passenger):
    date = datetime.strptime(date, "%Y-%m-%d")
    if '-' in passenger['birthday']:
        birthday = datetime.strptime(passenger['birthday'], "%Y-%m-%d")
    else:
        birthday = datetime.strptime(passenger['birthday'], "%Y%m%d")
    year = rrule.rrule(rrule.YEARLY, dtstart=birthday, until=date).count()
    print(year)
    if year >= 16:
        passenger['passengerType'] = PassengerType.ADT
    else:
        passenger['passengerType'] = PassengerType.CHD


@retry_decorator('获取占座任务失败')
def get_hold_task(carrier, taskType="paodan"):
    url = config.get_hold_task_url
    body = {"taskType": taskType, "agent": config.agent, "airline": carrier}
    print(body)
    rep = requests.post(url, json=body, timeout=10)
    if rep.status_code != 200:
        api_logger.error(f"get_hold_task {carrier} {taskType} \n {rep.text}")
    print(rep.text)
    rep_json = rep.json()
    if rep_json['errorString'] == "OK":
        for p in rep_json['task']['targetPassengers']:
            add_passenger_type(rep_json['task']['departDate'], p)
        return rep_json['task']
    else:
        return None


@retry_decorator('获取不占座支付任务失败')
def get_no_hold_pay_task(carrier):
    url = config.get_no_hold_pay_task_url
    params = {
        'carrier': carrier,
        'client': config.agent
    }
    response = requests.get(url, params=params, timeout=10)
    return response.text


@retry_decorator('获取汇率失败')
def get_exchange_rate_carrier(carrier, currency):
    # for _ in range(5):
    #     try:
    url = config.get_exchange_rate_carrier_url
    rep = requests.get(url, params={'carrier': carrier, 'currency': currency}, timeout=5)
    return float(rep.text)
    #     except Exception as e:
    #         print(carrier, currency)
    # raise Exception('获取汇率失败')


@retry_decorator('提交占座结果失败')
def submit_hold(result):
    url = config.submit_hold_url
    params = {'orderLog': json.dumps(result)}
    rep = requests.get(url, params=params, timeout=60)
    return rep.text


@retry_decorator('获取支付任务失败')
def get_pay_task(carrier):
    url = config.get_pay_task_url
    params = {'carrier': carrier,
              'client': config.agent}
    rep = requests.get(url, params, timeout=10)
    return rep.text


@retry_decorator('回填失败')
def submit_pay(result):
    url = config.submit_pay_url
    rep = requests.post(url, json=result, timeout=60)
    if "success" not in rep.text:
        raise Exception("回填失败")
    return rep.text


@retry_decorator('获取虚拟卡能否支付失败')
def can_pay(task, card):
    if "notHoldAutomaticPayOrderResult" in task.keys():
        task = task['notHoldAutomaticPayOrderResult']
    taskNum = task['taskNum']
    uuid = task['payOrderDetail']['payOrder']['uuid']
    cardNumberId = card['id']
    robot = task['payOrderDetail']['payOrder']['userName']
    triptype = task['payOrderDetail']['payOrder']['tripType']
    url = config.can_pay_url
    params = {
        "uuid": uuid,
        "cardNumberId": cardNumberId,
        "robot": robot,
        "triptype": triptype,
        "taskNum": taskNum
    }
    rep = requests.get(url, params=params, timeout=60).json()
    api_logger.info("can_pay {} {}".format(json.dumps(params), json.dumps(rep)))
    if rep['code'] == "0":
        return True
    else:
        return False


@retry_decorator('获取自动检查支付订单失败')
def get_auto_check_pay_order(ota_id):
    url = config.get_auto_check_pay_order_url
    params = {'otaId': ota_id}
    rep = requests.get(url, params=params, timeout=60)
    return rep.json()


class AutoApplyCard:
    AUTO_APPLY_CARD_TYPE_VCC = "VCC"
    AUTO_APPLY_CARD_TYPE_ENETT_MASTER_USD = "ENETT_MASTER_USD"
    AUTO_APPLY_CARD_TYPE_ENETT_MASTER_HKD = "ENETT_MASTER_HKD"
    AUTO_APPLY_CARD_TYPE_ENETT_VISA = "ENETT_VISA"
    AUTO_APPLY_CARD_TYPE_AMADEUS = "AMADEUS"
    AUTO_APPLY_CARD_TYPE_CTRIP = "XC"
    AUTO_APPLY_CARD_TYPE_TRIP = "TRIP"
    AUTOAPPLY_USETYPE_XPRODUCT = "xproduct"
    AUTOAPPLY_USETYPE_AFTERSALE = "aftersale"
    URL = config.get_apply_card_url
    TRIPLINK_CARD_TYPE_GWTTP = 'GWTTP'
    TRIPLINK_CARD_TYPE_B2B = 'B2B'
    TRIPLINK_CARD_TYPE_MCO = 'MCO'
    TRIPLINK_CARD_TYPE_USDVCC = 'USDVCC'
    TRIPLINK_CARD_LABEL_VISA = 'VISA'
    TRIPLINK_CARD_LABEL_MASTERCARD = 'MasterCard'
    TRIPLINK_CARD_BIN = {
        TRIPLINK_CARD_TYPE_GWTTP: ['222934', '519315', '522981', '558678', '222933', '539593'],
        TRIPLINK_CARD_TYPE_B2B: ['472205', '471440'],
        TRIPLINK_CARD_TYPE_MCO: ['557271', '222929', '222932']
    }

    @classmethod
    def getVccCard(cls, orderCode, carrier, currency, applyAmount, username,
                   triplinkCardType: Optional[str] = None,
                   triplinkCardLabel: Optional[str] = None,
                   triplinkSingleCard: Optional[bool] = None,
                   triplinkCardBin: Optional[str] = None):
        body = {
            "otaId": orderCode,
            "carrier": carrier,
            "applyAmount": str(applyAmount),
            "username": username,
            "currency": currency,
        }
        if triplinkCardType:
            body['triplinkCardType'] = triplinkCardType
        if triplinkCardLabel:
            body['triplinkCardLabel'] = triplinkCardLabel
        if triplinkSingleCard:
            body['triplinkSingleCard'] = triplinkSingleCard
        if triplinkCardBin:
            if len(triplinkCardBin) != 6 or not triplinkCardBin.isalnum():
                raise ValueError('无效参数， 请传入6位数字字符')
            body['triplinkCardBin'] = triplinkCardBin
        rep = requests.post(cls.URL, json=body, timeout=60).text
        api_logger.info(rep)
        card_logger.info(f"getVccCard {json.dumps(body)} {rep}")
        return json.loads(rep)

    @classmethod
    def getCard(cls, task, carrier, to_usd=False, **kwargs):
        if task['notHoldAutomaticPayOrderResult']['paymentMethod']['paynumber'] != 'N/A':
            return task['notHoldAutomaticPayOrderResult']['paymentMethod']

        # if "美运通" in task['notHoldAutomaticPayOrderResult']['paymentMethod']['name']:
        #     return task['notHoldAutomaticPayOrderResult']['paymentMethod']
        if to_usd:
            base_exchange = get_exchange_rate_carrier(currency=task['holdPnrProto']['currency'], carrier=carrier)
            usd_exchange = get_exchange_rate_carrier(currency='USD', carrier=carrier)
            usd_price = float(task['holdPnrProto']['totalPrice'] * base_exchange / usd_exchange + 5)
            return cls.getVccCard(task['notHoldAutomaticPayOrderResult']['payOrderDetail']['payOrder']['otaId'],
                                  carrier,
                                  "USD",
                                  usd_price,
                                  "Apollo", **kwargs)
        else:
            return cls.getVccCard(task['notHoldAutomaticPayOrderResult']['payOrderDetail']['payOrder']['otaId'],
                                  carrier,
                                  task['holdPnrProto']['currency'],
                                  task['holdPnrProto']['totalPrice'],
                                  "Apollo", **kwargs)

    @classmethod
    def getCardNoHold(cls, task, carrier, currency, totalPrice, **kwargs):
        if task['paymentMethod']['paynumber'] != 'N/A' and task['paymentMethod']['paynumber'] != '0000000000':
            return task['paymentMethod']
        if "美运通" in task['paymentMethod']['name']:
            return task['paymentMethod']
        return cls.getVccCard(task['payOrderDetail']['payOrder']['otaId'],
                              carrier,
                              currency,
                              totalPrice,
                              "Apollo",
                              **kwargs)


def flight_search(depCity, arrCity, depDate, airline, num=1, passenger=1):
    params = {"depCity": depCity,
              "arrCity": arrCity,
              "depDate": depDate,
              "airline": airline,
              "type": "SEARCH",
              "num": num,
              "passenger": passenger,
              "priceSource": "AFARE",
              "stepType": "SEARCH",
              "isThrough": "false"}
    url = config.get_flight_search_url
    rep = requests.get(url, params=params, timeout=60)
    return rep.json()


def apd_flight_search(task: str):
    dep, arr, date, airlines = task.split('|')
    airlines = json.loads(airlines)
    ret = {}
    for airline in airlines:
        flights = flight_search(dep, arr, date, airline)
        if not flights:
            continue
        ret.update(flights['AFARE'][airline]['result'])
    return ret


def save_apd_strategy(key: str, key2: str, value: str, time: int):
    url = apd_config.apd_strategy_save_url
    body = {"key": key, "key2": key2, "value": value, "time": time, "timeUnit": "MINUTES"}

    print(body)
    rep = requests.post(url, json=body, timeout=30)
    api_logger.info(f'body {body} rep {rep.text}')
    return rep.text


def ota_testing(fromCity, toCity, fromDate, carrier):
    url = apd_config.ota_testing_url
    data = {
        'companyoid': "15",
        'tripType': "1",
        'fromCity': fromCity,
        'toCity': toCity,
        'fromDate': fromDate,
        'carrier': carrier
    }
    headers = {'content-Type': 'text/html'}
    rep = requests.post(url, data=data, headers=headers, timeout=60)
    return rep.text


def trip_Search(task):
    fromCity, toCity, fromDate, airlines = task.split('|')
    url = apd_config.trip_search_url
    headers = {'content-Type': 'text/plain'}
    data = {'cid': '',
            'tripType': '1',
            'fromCity': fromCity,
            'toCity': toCity,
            'fromDate': str(fromDate).replace('-', ''),
            'retDate': '',
            'adultNumber': 1,
            'childNumber': 0,
            'infantNumber': 0,
            'channel': '"E"',
            'source': 0}
    rep = requests.post(url, json=data, headers=headers, timeout=60)
    rep_json = rep.json()
    if rep_json['status'] != 0:
        return {}
    ret = []
    # bag_ret = {}
    if rep_json['shoppingResultList']:
        flightList = {}
        for x in rep_json['flightList']:
            flightList[x['flightRefNum']] = x
        for x in rep_json['shoppingResultList']:
            item = {
                'add_info': offer_data_decode(x['data'])['data']['fdata'],
                'date': fromDate,
                'dep': flightList[x['flightRefList'][0]['flightRefNum']]['depAirport'],
                'arr': flightList[x['flightRefList'][-1]['flightRefNum']]['arrAirport'],
                'flightNum': "/".join(map(lambda f: flightList[f['flightRefNum']]['flightNumber'], x['flightRefList']))
            }
            item.update(x['tuList'][0]['priceList'][0])
            item['baggageWeight'] = x['tuList'][0]['formatBaggageDetailList'][0]['baggageWeight']
            ret.append(item)
            # print(json.dumps(item))

    return ret


def offer_data_decode(data):
    url = apd_config.offer_data_decode_url
    body = {'body': data}
    rep = requests.post(url, json=body, timeout=60)
    return rep.json()


@retry_decorator('添加流水日志失败')
def pay_order_log(payOrderUuid, operation, userId, request):
    body = {
        'payOrderUuid': payOrderUuid,
        'operation': operation,
        'userId': userId,
        'request': request,
        'result': 'success',
    }
    url = "http://47.104.182.61:5454/order/addLog"
    res = requests.post(url, json=body, timeout=60)
    return res.text


def submit_shupiao(holdTask, realPrice, email, pnr, bag_price):
    names = []

    if type(holdTask) is dict:
        for x in holdTask['targetPassengers']:
            names.append(x['name'])
        data = {"taskId": holdTask['taskId'], "taskType": holdTask['taskType'], "targetPrice": holdTask['targetPrice'],
                "realPrice": realPrice, "email": email, "pnr": pnr, "orderCode": holdTask['orderCode'],
                "taskStatus": "SUCESS", "names": names, "data": "{\"image\":\"\",\"pay_url\":\"\"}",
                "remark": f"({realPrice * len(names)}+{bag_price})"}
    else:
        for x in holdTask.targetPassengers:
            names.append(x.name)
        data = {"taskId": holdTask.taskId, "taskType": holdTask.taskType, "targetPrice": holdTask.targetPrice,
                "realPrice": realPrice, "email": email, "pnr": pnr, "orderCode": holdTask.orderCode,
                "taskStatus": "SUCESS", "names": names, "data": "{\"image\":\"\",\"pay_url\":\"\"}",
                "remark": f"({realPrice * len(names)}+{bag_price})"}

    url = 'http://120.27.16.108:8882/api/AddResult'
    res = requests.post(url, json=data, timeout=60)
    api_logger.info(f"submit_shupiao {json.dumps(data, ensure_ascii=False)} {res.text}")
    print(res.text)


def register_email(domain=None, name=None, length=None, black=False):
    if domain is None:
        domain = ['iugogo.cn',]
    if name:
        ran_str = name
    else:
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length or random.randint(8, 15))).lower()

    email = f"{ran_str}@{random.choice(domain)}".lower()
    if black is False:
        url = f'http://47.104.108.85:8868/api/email/createUserEmail?username={email}&password=1'
    else:
        url = f'http://120.27.13.99:9595/createEmail/insert?username={email}&password=1&forwardTo=fly'
    try:
        req = requests.get(url, timeout=30)
        if req.text == "success" or 'already exists' in req.text:
            return email
        else:
            return register_email(domain=domain, name=name)
    except Exception as e:
        return False


def airport_to_city(airport):
    url = f'http://120.27.14.84:8882/api/common/airport?code={airport}'
    req = requests.get(url, timeout=30)
    body = req.json()
    for x in body:
        if x['AirportCode'] == airport:
            return x['CityCode']
    return airport


@retry_decorator('添加订单标签失败')
def add_tag(pay_task: dict, tags: str):
    url = 'http://47.104.182.61:5454/order/updateTags'
    if 'uuid' in pay_task.keys():
        body = {
            'uuid': pay_task['uuid'].split('_')[0],
            'tags': tags
        }
    else:
        body = {
            'uuid': pay_task['payOrderDetail']['payOrder']['uuid'].split('_')[0],
            'tags': tags
        }
    response = requests.post(url=url, json=body, timeout=10)
    api_logger.info(f'{api_logger} {response.status_code} {response.text}')
    return response.text


def check_pay(ota_id, card):
    try:
        url = f"http://47.104.182.61:5454/order/queryTripVCC?cardNo={card}&username=Poseidon&otaId={ota_id}"
        res = requests.get(url, timeout=10)
        if not res.json()['authInfoResp']['authInfos']:
            return False
        for x in res.json()['authInfoResp']['authInfos']:
            if float(x['transCurrencyAmt']) < 0:
                return False
        return True
    except Exception:
        import traceback
        api_logger.error(f'{traceback.format_exc()}')
    return False

def get_refund_task(carrier):
    try:
        url = f'http://oss.bingtrip.cn:7799/aftersale/withholdingOrder/getTask?carrier={carrier}'
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            api_logger.error(f'获取退票任务失败 {res.text}')
            return None
        if res.text == 'null':
            return None
        return res.json()
    except Exception:
        import traceback
        api_logger.error(f'{traceback.format_exc()}')
        return None


def send_refund_task(task):
    for _ in range(60):
        try:
            url = 'http://oss.bingtrip.cn:7799/aftersale/withholdingOrder/fillTask'
            res = requests.post(url, json=task)
            if res.text == 'ok' or res.text == 'OK':
                return True
            else:
                time.sleep(1)
                continue
        except Exception:
            import traceback
            api_logger.error(f'{traceback.format_exc()}')
            time.sleep(1)
    else:
        return False


@func_retry(60)
def update_pnr_accountInfo(otaId, pnr, ticketAccount, accountPassword, accountUsername, address1="",
                           address2="", address3="", postcode=""):
    url = 'http://47.104.182.61:5454/order/updatePnrAccountInfo'
    body = {"otaId": otaId,
            "pnr": pnr,
            "ticketAccount": ticketAccount,
            "accountPassword": accountPassword,
            "accountUsername": accountUsername,
            "address1": address1,
            "address2": address2,
            "address3": address3,
            "postcode": postcode}
    res = requests.post(url, json=body, timeout=60)
    if res.status_code == 200:
        return
    else:
        raise Exception('update_pnr_accountInfo 失败')


def get_carrier_account(shortname):
    url = 'http://47.104.182.61:5454/order/getCarrierAccount'
    body = {
        'shortname': shortname
    }
    res = requests.post(url, json=body, timeout=60)
    if res.status_code != 200:
        raise Exception(f"{shortname} 获取失败")
    return res.json()