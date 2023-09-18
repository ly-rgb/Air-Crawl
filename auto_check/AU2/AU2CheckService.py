# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AU2CheckService.py
@effect: "请填写用途"
@Date: 2022/12/9 14:59
"""
import json
import traceback
from datetime import datetime
from utils.redis import u2_order_check_cache
import pymysql

from config import db_config
from utils.log import check_PNR_U2_logger
from auto_check.AU2.AU2CheckApi import AU2Web, AU2PnrWeb
from utils.dingtalk import f9_order_check_talk


class AU2CheckService(object):
    """
    质检业务层
    """
    pass


class AU2PnrService(object):
    """
    pnr状态质检
    """
    r = u2_order_check_cache
    date = None

    def __init__(self):
        pass

    @classmethod
    def check_pnr_status(cls):

        try:
            __error_message_tmp_list = set()  # 作为缓冲列表，如果长度超过一定数值方便重跑
            __error_message_list = set()

            cls.date, pnr_info = cls.__select_pnr_info()
            app = AU2PnrWeb()

            for data in pnr_info:
                if data[0] is None:
                    continue
                pnr_info_list = data[0].split("#")
                ota_id = pnr_info_list[0]
                pnr = pnr_info_list[1]
                dep_date = pnr_info_list[3]
                last_name = pnr_info_list[4].split("/")[0]

                # 发请求
                app.check(last_name=last_name, pnr=pnr)
                _error_order = f"{ota_id},{pnr},U2,{dep_date},{last_name}"
                _is_new_error = cls.r.sismember(f"u2_check_{cls.date}", _error_order)  # 判断是否在集合中
                # __reason = ""  # 票号异常原因, 暂时先不用写出来，有需要在放开
                if app.req_code == -1:
                    # __reason = "RequestsFail"
                    if not _is_new_error:
                        __error_message_tmp_list.add(_error_order)
                else:
                    result = app.check_response.json()
                    if (not _is_new_error) and (result["data"].get("errorMessage") or result.get("data") is None):
                        # __reason = "NotFindPnr"
                        __error_message_tmp_list.add(_error_order)

            cls.__retry_error(error_tmp_list=__error_message_tmp_list, error_list=__error_message_list, app=app)
            # 将结果推送到钉钉消息群
            total_error = "\n".join(__error_message_list)

            if len(__error_message_list) == 0:
                f9_order_check_talk.send_mag("U2暂无新增风险订单")
            else:
                f9_order_check_talk.send_mag(f"U2风险订单: \n"
                                             f"{total_error}")

        except Exception:
            check_PNR_U2_logger.error(f"{traceback.print_exc()}")

    @classmethod
    def __select_pnr_info(cls, logger=check_PNR_U2_logger):
        """
        查询pnr信息
        :return: date, result
        """
        result = None
        conn = pymysql.connect(host=db_config.host, user=db_config.user,
                               password=db_config.passwd, database=db_config.db, charset="utf8")
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")
        try:
            sql = f"""
                    SELECT CONCAT(po.otaId,'#',pp.pnr,'#',pfs.carrier,'#',pfs.depDate,'#',GROUP_CONCAT(DISTINCT ps.passengerName),'#', c.oid, '#', c.companyname,'#',pfs.depTime) FROM pay_flight_segment pfs
        LEFT JOIN pay_passenger ps ON pfs.payOrderUuid = ps.payOrderUuid
        LEFT JOIN pay_order_info poi ON pfs.oid = poi.paySegmentFlightOid
        LEFT JOIN pay_order po ON po.uuid = poi.payOrderUuid
        LEFT JOIN pay_pnr pp ON pp.oid = poi.payPnrOid 
        LEFT JOIN company c ON po.otaCompany = c.oid
        WHERE pfs.carrier in ('U2')
        AND pfs.depDate = '{date}'
        GROUP BY pp.pnr;
                    """
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) > 1:
                logger.info(f"pnr 查询成功, 查询到的总条数为: {len(result)}")

        except Exception:

            logger.info("SQL执行失败")
            logger.info(f"{traceback.print_exc()}")
        finally:
            if conn:
                conn.close()
            if cursor:
                cursor.close()

        return date, result

    @classmethod
    def __retry_error(cls, error_tmp_list: set, error_list: set, app):
        if len(error_tmp_list) > 10:
            check_PNR_U2_logger.info(f"error_tmp_list 错误订单: {len(error_tmp_list)}, 正在重跑.....")
            for error_tmp in error_tmp_list:
                pnr_info_list = error_tmp.split(",")
                ota_id = pnr_info_list[0]
                pnr = pnr_info_list[1]
                dep_date = pnr_info_list[3]
                last_name = pnr_info_list[4]

                app.check(pnr=pnr, last_name=last_name)
                if app.req_code == -1:
                    error_list.add(f"{ota_id},{pnr},U2,{dep_date},{last_name}")
                    cls.r.sadd(f"u2_check_{cls.date}", error_tmp)
                else:
                    result = app.check_response.json()
                    if result["data"].get("errorMessage") or result.get("data") is None:
                        error_list.add(f"{ota_id},{pnr},U2,{dep_date},{last_name}")
                        cls.r.sadd(f"u2_check_{cls.date}", error_tmp)

        else:
            # 添加到redis中
            for err in error_tmp_list:
                error_list.add(err)
                cls.r.sadd(f"u2_check_{cls.date}", err)
