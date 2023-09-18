from typing import List, Tuple, Optional

from . import execute_select, execute_select_first


def find_order_by_pnr(pnr: str):
    """
    :param pnr:
    :return List[Tuple][('出票单号', '平台', 'pnr', '航司', '起飞时间', '降落时间', '航段', '航班号', '乘客姓名', '出票渠道', '支付方式', '支付金额', '支付币种', '支付人民币金额', '生单仓位')]:
    """
    sql = f'''
    select DISTINCT otaId '出票单号',c.companyName '平台',pnr,pfs.carrier '航司',
substring_index(group_concat(DISTINCT concat(pfs.depDate,' ',pfs.depTime) order by flightType,sequence ),',',1) '起飞时间',
substring_index(group_concat(DISTINCT concat(pfs.arrDate,' ',pfs.arrTime) order by flightType,sequence ),',',-1) '降落时间',
group_concat(DISTINCT concat(pfs.depPort,'-',pfs.arrPort) order by flightType,sequence SEPARATOR '/' ) '航段',
group_concat(DISTINCT pfs.flightNum order by flightType,sequence SEPARATOR '/' ) '航班号',
group_concat(DISTINCT ppa.passengerName) '乘客姓名',
pa.short_name '出票渠道',pm.name '支付方式',
pp.payPrice '支付金额',pp.payCurrency '支付币种',round(pp.payPrice * pp.rate,2) '支付人民币金额',
SUBSTRING_INDEX(SUBSTRING_INDEX(substring_index(statement,(case group_concat(DISTINCT pfs.flightType order by flightType,sequence)  when '1' then '去程' when '2' then '返程' when '1,2' then '往返' end),-1),'","儿童价格',1),'舱位":"',-1) '生单仓位'
from pay_order po 
left join pay_order_info poi on po.uuid = poi.payOrderUuid 
left join pay_pnr pp on poi.payPnrOid = pp.oid 
left join payment_account pa on pp.payRoute = pa.id
left join payment_method pm on pp.payType = pm.id
left join pay_flight_segment pfs on poi.paySegmentFlightOid = pfs.oid
left join pay_passenger ppa on poi.payPassengerOid = ppa.oid
left join company c on po.otaCompany = c.oid
left join order_info o on po.apiSystemUuid = o.uuid
where po.status = 3 and adtCount > 0 and pp.status = 1
and pnr = '{pnr}'
group by otaId, pnr;
    '''
    return execute_select_first(sql)


def find_email_by_pnr(pnr: str) -> Optional[str]:
    sql = f"select payEmail from pay_pnr where pnr='{pnr}'"
    return execute_select_first(sql)