import os
from utils import ConfigParser

config_path = os.path.abspath(os.path.join(os.getcwd(),
                                           'flight.cfg'))
db_config_path = os.path.abspath(os.path.join(os.getcwd(), './db.cfg'))
apd_config_path = os.path.abspath(os.path.join(os.getcwd(),
                                               './apd.cfg'))


class Config(object):

    def __init__(self, cfg: ConfigParser):
        self.agent_master_service_endpoint = cfg.get("agentMasterServiceEndpoint")
        self.pppoe_redialing = cfg.get_boolean("pppoe_redialing")
        self.agent_sleeping_time = cfg.get_int("agent_sleeping_time")
        self.agent = cfg.get("agent")
        self.http_svr_port = cfg.get_int("http_svr_port")
        self.http_svr_addr = cfg.get("http_svr_addr")
        self.cookie_redis_url = cfg.get("cookie_redis_url")
        self.cookie_redis_pwd = cfg.get("cookie_redis_pwd")
        self.read_redis_key = cfg.get("read_redis_key")
        self.version = "1.0"
        self.log_path = './log'
        self.log_count = cfg.get_int("log_count")
        self.log_type = cfg.get("log_type", "time")
        self.proxy_type = 35
        self.max_booking = 5
        self.use_proxy = True
        self.spider_count_expiration_time = 60 * 60 * 5
        self.request_before_pay_pnr = "http://47.104.182.61:5454/robot/canPay",
        self.get_hold_task_url = "http://120.27.16.108:8882/api/GetTask"
        self.get_no_hold_pay_task_url = "http://47.104.182.61:5454/order/getAutomaticPayOrder"
        self.get_exchange_rate_carrier_url = "http://47.104.182.61:5454/order/getExchangeRateCarrier"
        self.get_apply_card_url = "http://47.104.182.61:5454/order/autoApplyCard"
        self.submit_hold_url = "http://120.27.14.84:8882/api/common/savePaoDanResult"
        self.submit_shupiao_url = "http://120.27.16.108:8882/api/AddResult"

        self.get_pay_task_url = "http://47.104.182.61:5454/order/getPnrAutomaticPayOrder"
        self.submit_pay_url = "http://47.104.182.61:5454/order/automaticBackfillPnr"
        self.can_pay_url = "http://47.104.182.61:5454/robot/canPay"
        self.get_auto_check_pay_order_url = "http://47.104.182.61:5454/order/getAutoCheckPayOrder"
        self.get_flight_search_url = "http://118.190.156.204:8881/api/search"


class DBConfig:
    def __init__(self, cfg: ConfigParser):
        self.host = cfg.get("host")
        self.port = cfg.get("port")
        self.user = cfg.get("user")
        self.passwd = cfg.get("passwd")
        self.db = cfg.get("db")


class APDConfig:
    def __init__(self, cfg: ConfigParser):
        self.apd_strategy_redis_host = cfg.get("apd_strategy_redis_host")
        self.apd_strategy_redis_port = cfg.get("apd_strategy_redis_port")
        self.apd_strategy_redis_passwd = cfg.get("apd_strategy_redis_passwd")
        self.apd_strategy_save_url = cfg.get("apd_strategy_save_url")
        self.ota_testing_url = cfg.get('ota_testing_url')
        self.trip_search_url = cfg.get('trip_search_url')
        self.local_redis_host = cfg.get('local_redis_host')
        self.local_redis_port = cfg.get_int('local_redis_port')
        self.local_redis_passwd = cfg.get('local_redis_passwd', None)
        self.offer_data_decode_url = cfg.get('offer_data_decode_url')
        self.adp_mysql_host = cfg.get('adp_mysql_host')
        self.adp_mysql_port = cfg.get('adp_mysql_port')
        self.adp_mysql_user = cfg.get('adp_mysql_user')
        self.adp_mysql_passwd = cfg.get('adp_mysql_passwd')
        self.apd_mysql_db = cfg.get('apd_mysql_db')


config = Config(ConfigParser(config_path))
db_config = DBConfig(ConfigParser(db_config_path))
apd_config = APDConfig(ConfigParser(apd_config_path))
