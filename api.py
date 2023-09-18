import time
from flask import Flask
from flask import request
from airline.A5J import add_on as _5j_add_on
from airline.AVB import add_on as _VB_add_on
from airline.AXY import add_on as _XY_add_on
from airline.AG8 import add_on as _G8_add_on
from airline.AFZ import add_on as _FZ_add_on
from airline.AZ9.service import add_on as _Z9_add_on


from airline.A6J import api_search as _6j_search
from airline.AV7 import api_search as _v7_search
from airline.AH2 import api_search as _h2_search
from airline.ASG import api_search as _SG_search
from airline.A2I import api_search as _2I_search
from airline.AGQ import api_search as _GQ_search
from airline.ATO import api_search as _TO_search
from airline.AWS import api_search as _WS_search
from airline.ATS import api_search as _TS_search
from airline.AT3 import api_search as _T3_search
from airline.AXP import api_search as _XP_search
from airline.AN0 import api_search as _N0_search
from airline.ABZ import api_search as _BZ_search
from airline.AY9 import api_search as _Y9_search
from airline.ATL import api_search as _TL_search
from airline.AFY import api_search as _FY_search
from airline.AJ9 import api_search as _J9_search
from airline.AHD import api_search as _HD_search
from airline.ABF import api_search as _BF_search
from airline.ADD import api_search as _DD_search
from airline.AYQ import api_search as _YQ_search
from airline.AOV import api_search as _OV_search
from airline.AFO import api_search as _FO_search
from airline.AZ9 import api_search as _Z9_search
from airline.AAE import api_search as _AE_search
from airline.AB7 import api_search as _B7_search

import traceback
import json
from flask_restful import Resource, Api

from robot import HoldTask
from utils.log import verification_log, add_on_logger
from utils.searchparser import parser_from_task
from utils.security import md5

app = Flask(__name__)
api = Api(app)

api_map = {
    'A6J': _6j_search,
    'AV7': _v7_search,
    'AH2': _h2_search,
    # 'AG8': _G8_search,
    "ASG": _SG_search,
    "A2I": _2I_search,
    "AGQ": _GQ_search,
    "ATO": _TO_search,
    "AWS": _WS_search,
    "ATS": _TS_search,
    "AT3": _T3_search,
    "AXP": _XP_search,
    "AN0": _N0_search,
    "ABZ": _BZ_search,
    "AY9": _Y9_search,
    "ATL": _TL_search,
    "AFY": _FY_search,
    "AJ9": _J9_search,
    "AHD": _HD_search,
    "ABF": _BF_search,
    # "ADD": _DD_search,
    "AYQ": _YQ_search,
    "AOV": _OV_search,
    "AFO": _FO_search,
    "AZ9": _Z9_search,
    "AAE": _AE_search,
    "AB7": _B7_search,
}


proxy_config = {'AU2': 6,
                "ATS": 6}

add_on_api_map = {
    'CB': _5j_add_on,
    'FVB': _VB_add_on,
    'FXY': _XY_add_on,
    'FG8': _G8_add_on,
    'FFZ': _FZ_add_on,
    'FZ9': _Z9_add_on,
}

add_on_proxy_config = {
    'FVB': 7,
    'FXY': 7,
    'FG8': 7,
    'FFZ': 7,
}


class Search(Resource):

    def post(self):
        """
        request.data: {"postData": 'AJA,YYC,YYJ,2022-06-24,,1,,,AFARE,0,,READTIMELCC'}
        爬虫测试接口
        :return: response.body
        """
        try:
            st = time.time()
            body = request.json
            _id = md5(json.dumps(body))
            verification_log.info(f"task_id:{_id} task:{json.dumps(body)}")
            taskItem = body['postData']
            url = taskItem.split(',')[0]
            taskItem = parser_from_task(body['postData'])
            _api = api_map.get(url, None)
            if not api:
                verification_log.error(f"task_id:{id} not has api {url}")
                return {"errorCode": -1}
            code, ret = _api(taskItem)
            verification_log.info(f"task_id:{id} time:{str(time.time() - st)} result:{json.dumps(ret)}")
            if not ret:
                return {"errorCode": -1}
            if code == 0:
                return {"errorCode": 0, "content": json.dumps(ret)}
            else:
                return {"errorCode": -1}
        except Exception as e:
            verification_log.error(traceback.format_exc())
            return {"errorCode": -1}


class AddonServices(Resource):

    def post(self):
        code = -1
        result = []
        st = time.time()
        body = request.json
        try:
            airline = body['postData'].split(',')[0]

            _api = add_on_api_map.get(airline)
            if not _api:
                raise Exception(f"[不支持航司][{airline}]")
            proxy_type = add_on_proxy_config.get(airline, None)
            if proxy_type is not None:
                code, result = _api(HoldTask.from_add_on_task(body['postData']),
                                    proxy_type)
            else:
                code, result = _api(HoldTask.from_add_on_task(body['postData']))
            add_on_logger.info(f"[任务开始][{body}]")
        except Exception as e:
            add_on_logger.error(f'[任务异常][{body}][{traceback.format_exc()}]')
        add_on_logger.info(f'[任务结束][耗时:{round(time.time() - st, 2)}s][{body}][{result}]')
        if not result:
            return {"errorCode": -1}
        if code == 0:
            return {"errorCode": 0, "content": json.dumps(result)}
        else:
            return {"errorCode": -1}


api.add_resource(Search, "/curl")
api.add_resource(AddonServices, "/AddonServices")
