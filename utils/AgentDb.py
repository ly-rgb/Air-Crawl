# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AgentDb.py
@effect: "通过PNR查询代理账号与密码，SQL操作"
@Date: 2022/10/20 16:40
"""
import pymysql
from config import db_config
import traceback


def select_agent_db(pnr: str, logger) -> dict:

    result = None
    conn = pymysql.connect(host=db_config.host, user=db_config.user,
                           password=db_config.passwd, database=db_config.db, charset="utf8")
    cursor = conn.cursor()
    try:
        sql = f"""
            select DISTINCT otaId '出票单号',pnr,pfs.carrier '航司',
        substring_index(group_concat(DISTINCT concat(pfs.depDate,' ',pfs.depTime) order by flightType,sequence ),',',1) '起飞时间',
        group_concat(DISTINCT concat(pfs.depPort,'-',pfs.arrPort) order by flightType,sequence SEPARATOR '/' ) '航段',
        group_concat(DISTINCT pfs.flightNum order by flightType,sequence SEPARATOR '/' ) '航班号',
        group_concat(DISTINCT ppa.passengerName) '乘客姓名',
        pa.short_name '出票渠道',pa.account 账户,pa.password 密码
        from pay_order po 
        left join pay_order_info poi on po.uuid = poi.payOrderUuid 
        left join pay_pnr pp on poi.payPnrOid = pp.oid 
        left join payment_account pa on pp.payRoute = pa.id
        left join pay_flight_segment pfs on poi.paySegmentFlightOid = pfs.oid
        left join pay_passenger ppa on poi.payPassengerOid = ppa.oid
        where po.status = 3 and adtCount > 0 and pp.status = 1
        and pp.pnr = '{pnr}'
        and po.payTime >= '2018-01-01'
        group by otaId, pnr;
            """
        cursor.execute(sql)
        data = cursor.fetchall()
        if data:
            user_name = data[0][-2]
            password = data[0][-1]
            result = {"user_name": user_name, "password": password}
            logger.info("Success: 成功找到账号与密码")
        else:
            logger.error(f"Fail: 没有查到PNR: {pnr}对应的账号和密码，请认真检查")
            result = {"user_name": None, "password": None}

        conn.close()
        cursor.close()
    except Exception:
        if conn:
            conn.close()
        if cursor:
            cursor.close()
        logger.info("SQL执行失败")
        logger.info(f"{traceback.print_exc()}")
    return result

