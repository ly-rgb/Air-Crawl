import random
import time

import redis
import requests

from config import config, apd_config
from datetime import datetime

from utils.astoip_proxy import get_astoip_proxy, get_astoip_http_proxy
from utils.astoip_proxy_2 import get_astoip_proxy as get_astoip_proxy_2, \
    get_astoip_http_proxy as get_astoip_http_proxy_2
from utils.ipidea_proxy import get_ipidea_proxy, get_ipidea_proxy_fr
from utils.proxy import get_ip_idea

local_cache = redis.Redis(host=apd_config.local_redis_host,
                          port=apd_config.local_redis_port,
                          decode_responses=True,
                          password=apd_config.local_redis_passwd,
                          db=0)

local_cache_1 = redis.Redis(host=apd_config.local_redis_host,
                            port=apd_config.local_redis_port,
                            decode_responses=True,
                            password=apd_config.local_redis_passwd,
                            db=1)

local_cache_2 = redis.Redis(host=apd_config.local_redis_host,
                            port=apd_config.local_redis_port,
                            decode_responses=True,
                            password=apd_config.local_redis_passwd,
                            db=2)

local_cache_3 = redis.Redis(host=apd_config.local_redis_host,
                            port=apd_config.local_redis_port,
                            decode_responses=True,
                            password=apd_config.local_redis_passwd,
                            db=3)

apd_filter_cache = redis.Redis(host=apd_config.local_redis_host,
                               port=apd_config.local_redis_port,
                               decode_responses=True,
                               password=apd_config.local_redis_passwd,
                               db=3)

apd_strategy_cache = redis.Redis(host=apd_config.apd_strategy_redis_host,
                                 port=apd_config.apd_strategy_redis_port,
                                 decode_responses=True,
                                 password=apd_config.apd_strategy_redis_passwd,
                                 db=0)

ah_price_cache = redis.Redis(host=apd_config.apd_strategy_redis_host,
                             port=apd_config.apd_strategy_redis_port,
                             decode_responses=True,
                             password=apd_config.apd_strategy_redis_passwd,
                             db=1)

test_ah_price_cache = redis.Redis(host='121.42.159.37',
                                  port=6139,
                                  decode_responses=True,
                                  password='af42bc0ada00320c679db3d3aweelfly',
                                  db=1)

proxy_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                          port=int(config.cookie_redis_url.split(":")[1]),
                          decode_responses=True,
                          password=config.cookie_redis_pwd,
                          db=35)

cn_vps_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                           port=int(config.cookie_redis_url.split(":")[1]),
                           decode_responses=True,
                           password=config.cookie_redis_pwd,
                           db=4)

proxy_cache_37 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                             port=int(config.cookie_redis_url.split(":")[1]),
                             decode_responses=True,
                             password=config.cookie_redis_pwd,
                             db=46)

proxy_cache_62 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                             port=int(config.cookie_redis_url.split(":")[1]),
                             decode_responses=True,
                             password=config.cookie_redis_pwd,
                             db=62)

proxy_long_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                               port=int(config.cookie_redis_url.split(":")[1]),
                               decode_responses=True,
                               password=config.cookie_redis_pwd,
                               db=36)

fr_account_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                               port=int(config.cookie_redis_url.split(":")[1]),
                               decode_responses=True,
                               password=config.cookie_redis_pwd,
                               db=79)

w9_account_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                               port=int(config.cookie_redis_url.split(":")[1]),
                               decode_responses=True,
                               password=config.cookie_redis_pwd,
                               db=94)

proxy_aws_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                              port=int(config.cookie_redis_url.split(":")[1]),
                              decode_responses=True,
                              password=config.cookie_redis_pwd,
                              db=67)

redis_81 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=81)

redis_82 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=82)

proxy_aws_us_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                                 port=int(config.cookie_redis_url.split(":")[1]),
                                 decode_responses=True,
                                 password=config.cookie_redis_pwd,
                                 db=73)

public_proxy_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                                 port=int(config.cookie_redis_url.split(":")[1]),
                                 decode_responses=True,
                                 password=config.cookie_redis_pwd,
                                 db=25)

redis_53 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=53)

redis_90 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=90)

redis_66 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=False,
                       password=config.cookie_redis_pwd,
                       db=66)

redis_52 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=52)

redis_11 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=11)

redis_200 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                        port=int(config.cookie_redis_url.split(":")[1]),
                        decode_responses=True,
                        password=config.cookie_redis_pwd,
                        max_connections=50,
                        db=200)

redis_201 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                        port=int(config.cookie_redis_url.split(":")[1]),
                        decode_responses=True,
                        password=config.cookie_redis_pwd,
                        db=201)

redis_202 = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                        port=int(config.cookie_redis_url.split(":")[1]),
                        decode_responses=True,
                        password=config.cookie_redis_pwd,
                        db=202)

A5J_admin_free_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                                   port=int(config.cookie_redis_url.split(":")[1]),
                                   decode_responses=True,
                                   password=config.cookie_redis_pwd,
                                   db=6)

currency_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                             port=int(config.cookie_redis_url.split(":")[1]),
                             decode_responses=True,
                             password=config.cookie_redis_pwd,
                             db=61)
abck_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                         port=int(config.cookie_redis_url.split(":")[1]),
                         decode_responses=True,
                         password=config.cookie_redis_pwd,
                         db=52)
fr_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                       port=int(config.cookie_redis_url.split(":")[1]),
                       decode_responses=True,
                       password=config.cookie_redis_pwd,
                       db=86)
anti_spider_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                                port=int(config.cookie_redis_url.split(":")[1]),
                                decode_responses=True,
                                password=config.cookie_redis_pwd,
                                db=83)
anti_spider_db = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                             port=int(config.cookie_redis_url.split(":")[1]),
                             decode_responses=True,
                             password=config.cookie_redis_pwd,
                             db=85)
fr_ip_idea = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                         port=int(config.cookie_redis_url.split(":")[1]),
                         decode_responses=True,
                         password=config.cookie_redis_pwd,
                         db=46)
w9_new_account_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                                   port=int(config.cookie_redis_url.split(":")[1]),
                                   decode_responses=True,
                                   password=config.cookie_redis_pwd,
                                   db=94)

u2_order_check_cache = redis.Redis(host=config.cookie_redis_url.split(":")[0],
                                   port=int(config.cookie_redis_url.split(":")[1]),
                                   decode_responses=True,
                                   password=config.cookie_redis_pwd,
                                   db=95)

cookie_cache = redis_53

apd_black_list_cache = local_cache_1

apd_cache = local_cache

apd_show_cache = local_cache_2

apd_tpr_cache = local_cache_3


def get_proxy_aws():
    _key = proxy_aws_cache.randomkey()
    ttl = proxy_aws_cache.ttl(_key)
    if int(ttl) < 20:
        return get_proxy_aws()
    return "http://" + _key.split('_')[1]


def get_vps_proxy():
    _key = proxy_aws_cache.randomkey()
    ttl = proxy_aws_cache.ttl(_key)
    if int(ttl) < 20:
        return get_proxy_aws()
    return "http://" + _key.split('_')[1]


def get_proxy_cache_37():
    _key = proxy_cache_37.randomkey()
    ttl = proxy_cache_37.ttl(_key)
    if int(ttl) < 20:
        return get_proxy_cache_37()
    return "http://" + _key.split('_')[1]


def get_proxy_cache_fr():
    _key = fr_account_cache.randomkey()
    ttl = fr_account_cache.ttl(_key)
    if int(ttl) < 20:
        return get_proxy_cache_fr()
    return "http://" + _key.split('_')[1]


def get_proxy_us_aws():
    _key = proxy_aws_us_cache.randomkey()
    ttl = proxy_aws_cache.ttl(_key)
    if int(ttl) < 20:
        return get_proxy_us_aws()
    return "http://" + _key.split('_')[1]


def spider_counter(name, status):
    name = f"{name} {config.proxy_type} {datetime.now().strftime('%Y-%m-%d %H:00')}"
    redis_53.hincrby(name, f"{status}")
    redis_53.expire(name, config.spider_count_expiration_time)


def add_cookie(name, cookie):
    cookie_cache.lpush(name, cookie)


def pop_cookie(name):
    return cookie_cache.lpop(name)


def get_baipiao_proxy():
    ipList = ["125.208.17.", "125.208.23."]
    ip = random.choice(ipList) + str(random.randint(2, 252))
    port = '9048'
    user = 'test'
    password = 'qwer1011'
    return f"http://{user}:{password}@{ip}:{port}"


# def get_fr_adsl_proxy(flag=1):
#     proxy = fr_account_cache.get('adslProxy')
# if proxy is None:
#     if flag >= 10:
#         return False
#     flag += 1
#     time.sleep(1)
#     return get_fr_adsl_proxy(flag)
# else:
#     return proxy


def get_random_proxy(type_proxy=None):
    select_type = type_proxy

    if select_type == 46:
        return get_proxy_cache_fr()

    if select_type == 111:
        # FR adsl proxy
        # proxy = get_fr_adsl_proxy()
        # if proxy is False:
        #     return False
        proxy = fr_account_cache.get('adslProxy')
        return "http://" + proxy.split('|')[0]

    if select_type == 39:
        key = proxy_cache.randomkey()
        ip = key.split("_")[-1]
        host = ip.split(':')[0]
        port = str(int(ip.split(':')[-1]))
        return "http://" + host + ":" + port

    if select_type == 35:
        key = proxy_cache.randomkey()
        ip = key.split("_")[-1]
        host = ip.split(':')[0]
        port = str(int(ip.split(':')[-1]) + 1)
        return "socks5://" + host + ":" + port
    if select_type == 350:
        key = proxy_cache.randomkey()
        ip = key.split("_")[-1]
        host = ip.split(':')[0]
        port = str(int(ip.split(':')[-1]))
        return "http://" + host + ":" + port
    elif select_type == 34:
        key = proxy_cache.randomkey()
        ip = key.split("_")[-1]
        host = ip.split(':')[0]
        port = str(int(ip.split(':')[-1]))
        return "http://" + host + ":" + port
    elif select_type == 0 or select_type is None:
        return None

    elif select_type == 1:
        proxyUser = "HJ38461X2P9R7X3D"
        proxyPass = "F7EF83A2184CCCDF"
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        return proxyMeta
    elif select_type == 67:
        return get_proxy_aws()
    elif select_type == 73:
        return get_proxy_us_aws()
    elif select_type == 80:
        return get_vps_proxy()
    elif select_type == 2:
        return get_ip_idea()
    elif select_type == 4:
        key = cn_vps_cache.randomkey()
        ip = key.split("_")[-1]
        return "http://" + ip
    elif select_type == 5:
        return get_baipiao_proxy()
    elif select_type == 6:
        return get_astoip_proxy()
    elif select_type == 7:
        return get_astoip_http_proxy()
    elif select_type == 370:
        return get_proxy_cache_37()
    elif select_type == 8:
        return get_astoip_proxy_2()
    elif select_type == 1087:
        return "http://127.0.0.1:1087"
    elif select_type == 8889:
        return "http://127.0.0.1:8889"
    elif select_type == 8888:
        return "http://127.0.0.1:8888"
    elif select_type == 10809:
        return "http://127.0.0.1:10809"
    elif select_type == 36:
        key = proxy_long_cache.randomkey()
        ip = key.split("_")[-1]
        host = ip.split(':')[0]
        port = str(int(ip.split(':')[-1]) + 1)
        return "socks5://" + host + ":" + port
    elif select_type == 37:
        return get_ipidea_proxy()
    elif select_type == 38:
        return get_ipidea_proxy_fr()
    elif select_type == 62:
        return get_ipidea_proxy(regions='jp')
    elif select_type == 25:
        key = public_proxy_cache.randomkey()
        ip = key.split("_")[-1]
        host = ip.split(':')[0]
        port = str(int(ip.split(':')[-1]) + 1)
        return "socks5://" + host + ":" + port
    elif select_type == 26:
        return "http://127.0.0.1:3213"
    else:
        return f"http://127.0.0.1:{select_type}"
