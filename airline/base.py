import abc
import re
import threading
import time
from datetime import datetime
from http.cookiejar import Cookie
from logging import Logger
from typing import *

import phone_gen
import requests
from lxml.etree import _Element
from requests import Session
from requests.models import Response
from websocket import WebSocketApp, ABNF

from airline.baggage import Baggage
from config import config
from native.api import get_exchange_rate_carrier, pay_order_log, register_email
from robot import HoldTask
from spider.model import Journey
from utils.date_tools import data_reformat
from utils.file_helper import MsgFileRecorder
from utils.log import robot_logger
from utils.redis import get_random_proxy, redis_53


class HttpRetryMaxException(Exception):
    pass


class HCaptchaException(Exception):
    pass


class AirAgent(object):
    import requests
    session: requests.Session

    class Exception(Exception):
        pass

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        import json
        from lxml.html import etree
        self.json = json
        self.etree = etree
        self.proxies_type = proxies_type
        self.retry_count = retry_count
        self.timeout = timeout
        self.session_init()

    def session_init(self):
        self.session = self.requests.session()
        if self.proxies_type:
            self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
        self.session.verify = False
        print('proxies', self.session.proxies)

    def post(self, *args, **kwargs):
        for _ in range(self.retry_count):
            try:
                response = self.session.post(*args, timeout=self.timeout, **kwargs)
                return response
                # return self.session.post(*args, timeout=self.timeout, **kwargs)
            except Exception:
                import traceback
                traceback.print_exc()

                print("post error")
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)
        raise HttpRetryMaxException()

    def get(self, *args, **kwargs):
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = self.session.get(*args, timeout=self.timeout, **kwargs)
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)

        raise HttpRetryMaxException(msg)

    def put(self, *args, **kwargs):
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = self.session.put(*args, timeout=self.timeout, **kwargs)
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)

        raise HttpRetryMaxException(msg)

    def delete(self, *args, **kwargs):
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = self.session.delete(*args, timeout=self.timeout, **kwargs)
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)

        raise HttpRetryMaxException(msg)

    def refresh_proxy(self):
        print('proxies', self.session.proxies)
        if self.proxies_type:
            self.session.proxies = {'https': get_random_proxy(self.proxies_type)}

    @staticmethod
    def api_search(task):
        pass

    def hCaptcha(self, response, ua):
        url = response.url
        data_site_key = re.findall('data-sitekey="(.*?)"', response.text)[0]
        print('开始打码')
        print('url', url)
        print('data_site_key', data_site_key)

        key = 'a7e9a587617ae10ce72a2258a870ca80'
        params = {
            'key': key,
            'method': 'hcaptcha',
            'sitekey': data_site_key,
            'pageurl': url
        }

        response = self.requests.get('http://2captcha.com/in.php', params=params, timeout=30)
        if 'OK' not in response.text:
            raise Exception(f"打码失败: {response.text}")
        _id = response.text.split('|')[1]
        params = {
            'key': key,
            'action': 'get',
            'id': _id
        }
        for _ in range(10):
            time.sleep(10)
            response = self.requests.get('http://2captcha.com/res.php', params=params, timeout=60)
            print('打码结果', response.text)
            if 'OK' in response.text:
                captcha = response.text.split('|')[1]
                data = {
                    'recaptcha_response': '',
                    'h-captcha-response': captcha,
                    'g-recaptcha-response': captcha
                }
                headers = {
                    'Host': 'validate.perfdrive.com',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Microsoft Edge";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://validate.perfdrive.com',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': url,
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }
                response = self.session.post(url, data=data, timeout=30, headers=headers, allow_redirects=False)
                return response
        else:
            raise Exception("打码失败")


class AirAgentHCaptcha(AirAgent):
    ua: str

    def post(self, *args, **kwargs):
        for _ in range(self.retry_count):
            try:
                response = self.session.post(*args, timeout=self.timeout, **kwargs)
                if "https://validate.perfdrive.com" in response.url:
                    self.hCaptcha(response, self.ua)
                    continue
                return response
                # return self.session.post(*args, timeout=self.timeout, **kwargs)
            except Exception:
                import traceback
                traceback.print_exc()

                print("post error")
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)
        raise HttpRetryMaxException()

    def get(self, *args, **kwargs):
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = self.session.get(*args, timeout=self.timeout, **kwargs)
                if "https://validate.perfdrive.com" in response.url:
                    self.hCaptcha(response, self.ua)
                    continue
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)

        raise HttpRetryMaxException(msg)

    def put(self, *args, **kwargs):
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = self.session.put(*args, timeout=self.timeout, **kwargs)
                if "https://validate.perfdrive.com" in response.url:
                    self.hCaptcha(response, self.ua)
                    continue
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)
        raise HttpRetryMaxException(msg)

    def delete(self, *args, **kwargs):
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = self.session.delete(*args, timeout=self.timeout, **kwargs)
                if "https://validate.perfdrive.com" in response.url:
                    self.hCaptcha(response, self.ua)
                    continue
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.session.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.session.proxies)
        raise HttpRetryMaxException(msg)


class AirAgentV2(AirAgent, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def getFlightByBooking(self) -> (str, str):
        pass

    def pay_check(self, holdPnrProto, orderId: str):
        fn, std = self.getFlightByBooking()
        departTime = datetime.strptime(holdPnrProto['depTime'], "%b %d, %Y %I:%M:%S %p").strftime("%Y-%m-%d %H:%M")
        if std != departTime:
            pay_order_log(orderId.split('_')[0], '支付发现：航变', 'Trident', f"Old:{departTime}, Now: {std}")
            raise Exception(f"departTime error: {departTime} {std}")


class AirAgentV3Development(Session):
    """
    :var proxies_type: 代理类型
    :var retry_count: http请求失败重试次数
    :var logger: 日志记录器
    :var msg_file_recorder: 文件消息记录器
    :exception Exception: AirAgent异常记录
    """

    class Exception(Exception):
        pass

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=None, request_log=False, cookie_debug=False):
        super().__init__()
        import json
        from lxml.html import etree
        self.json = json
        self.etree = etree
        self.proxies_type = proxies_type
        self.retry_count = retry_count
        self.timeout = timeout
        self.session_init()
        self.logger = logger or robot_logger
        self.msg_file_recorder = MsgFileRecorder(self.__class__.__name__)
        self.__request_log__ = request_log
        self.__cookie_debug__ = cookie_debug
        self.verify = False

    def session_init(self):
        if self.proxies_type:
            self.proxies = {'https': get_random_proxy(self.proxies_type)}
        self.verify = False
        print('proxies', self.proxies)

    def request(self, method, url,
                params=None, data=None, headers=None, cookies=None, files=None,
                auth=None, timeout=None, allow_redirects=True, proxies=None,
                hooks=None, stream=None, verify=None, cert=None, json=None, is_retry=True, hCaptcha=False,
                hCaptcha_lock=False, hCaptcha_clear_cookie=False) -> Response:
        if not timeout:
            timeout = self.timeout
        msg = ""
        for _ in range(self.retry_count):
            try:
                response = super().request(method, url, params, data, headers, cookies, files, auth, timeout,
                                           allow_redirects,
                                           proxies, hooks, stream, verify, cert, json)
                if self.__request_log__:
                    self.logger.info(f'[request {method} {url}] ===> [response {response.status_code} {response.url}]')
                if self.__cookie_debug__:
                    self.logger.info(
                        f'[request {method} {url}] ===> [response {response.status_code} {response.url}][Set-Cookie {response.headers.get("Set-Cookie")}]')
                if "https://validate.perfdrive.com" in response.url and hCaptcha:
                    self.hCaptcha(response, hCaptcha_lock=hCaptcha_lock, hCaptcha_clear_cookie=hCaptcha_clear_cookie)
                    continue
                # if response.text == 'nil':
                #     self.refresh_proxy()
                #     continue
                return response
            except Exception as e:
                if not is_retry:
                    raise e
                else:
                    self.retry_hook()
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.proxies = {'https': get_random_proxy(self.proxies_type)}
                print('proxies', self.proxies)
        raise HttpRetryMaxException(msg)

    def refresh_proxy(self, proxies_type=None):
        if proxies_type:
            self.proxies = {'https': get_random_proxy(self.proxies_type)}
            print('proxies', self.proxies)

            return
        if self.proxies_type:
            self.proxies = {'https': get_random_proxy(self.proxies_type)}
            print('proxies', self.proxies)

    @staticmethod
    def getFlightNumberFromJourneyKey(journeySellKey, ignore_departTime_check=False):
        journeySellKeys = journeySellKey.split('^')
        flightNo = []
        times = []
        for key in journeySellKeys:
            ks = key.split('~')
            flightNo.append(f"{ks[0].strip()}{ks[1].strip()}")
            times.append(data_reformat(ks[5], '%m/%d/%Y %H:%M', '%Y-%m-%d %H:%M'))
        if ignore_departTime_check:
            return '/'.join(flightNo)
        else:
            return '/'.join(flightNo) + '_' + '/'.join(times)

    @staticmethod
    def getFlightFromJourneyKey(journeySellKey):
        resutl = []
        journeySellKeys = journeySellKey.split('^')

        for key in journeySellKeys:
            ks = key.split('~')
            resutl.append({'carrier': ks[0],
                           'flightNumber': f"{ks[0].strip()}{ks[1].strip()}",
                           'depAirport': ks[4],
                           'depTime': data_reformat(ks[5], '%m/%d/%Y %H:%M', '%Y%m%d%H%M'),
                           'arrAirport': ks[6],
                           'arrTime': data_reformat(ks[7], '%m/%d/%Y %H:%M', '%Y%m%d%H%M')})
        return resutl

    def recaptcha(self, googlekey, pageurl) -> Tuple[Optional[Exception], Optional[str]]:
        key = 'a7e9a587617ae10ce72a2258a870ca80'
        params = {
            'key': key,
            'method': 'userrecaptcha',
            'googlekey': googlekey,
            'pageurl': pageurl
        }
        url = f'http://2captcha.com/in.php?key={key}&method=userrecaptcha&googlekey={googlekey}&pageurl={pageurl}'
        respones = requests.get(url)
        if respones.text[:2] != 'OK':
            return self.Exception(f'打码失败: {respones.text}'), None
        _id = respones.text.split("|")[-1]
        for _ in range(40):
            url = f'http://2captcha.com/res.php?key={key}&action=get&id={_id}'
            respones = requests.get(url, params=params)
            if 'CAPCHA_NOT_READY' in respones.text:
                time.sleep(2)
            else:
                print('打码结果', respones.text)
                if respones.text[:2] == 'OK':
                    return None, respones.text.split('|')[-1]
                else:
                    return self.Exception(f'打码失败: {respones.text}'), None
        else:
            return self.Exception(f'打码超时'), None

    def hCaptcha(self, response, hCaptcha_lock=None, hCaptcha_clear_cookie=False):
        if hCaptcha_lock:
            if redis_53.get(f'hCaptcha_lock_{hCaptcha_lock}_{config.agent}'):
                self.logger.info(f'[打码锁定中]')
                time.sleep(30)
                raise Exception("hCaptcha 锁定中")
            redis_53.set(f'hCaptcha_lock_{hCaptcha_lock}_{config.agent}', '1', ex=30)
        url = response.url
        data_site_key = re.findall('data-sitekey="(.*?)"', response.text)[0]
        self.logger.info(f'[开始打码][{data_site_key}][{url}]')
        print('开始打码')
        print('url', url)
        print('data_site_key', data_site_key)

        key = 'a7e9a587617ae10ce72a2258a870ca80'
        params = {
            'key': key,
            'method': 'hcaptcha',
            'sitekey': data_site_key,
            'pageurl': url
        }

        response = requests.get('http://2captcha.com/in.php', params=params, timeout=30)
        if 'OK' not in response.text:
            raise HCaptchaException(f"打码失败: {response.text}")
        _id = response.text.split('|')[1]
        params = {
            'key': key,
            'action': 'get',
            'id': _id
        }
        for _ in range(10):
            time.sleep(10)
            response = requests.get('http://2captcha.com/res.php', params=params, timeout=60)
            print('打码结果', response.text)
            self.logger.info(f'[打码结果][{response.text}]')
            if 'OK' in response.text:
                captcha = response.text.split('|')[1]
                data = {
                    'recaptcha_response': '',
                    'h-captcha-response': captcha,
                    'g-recaptcha-response': captcha
                }
                headers = {
                    'Host': 'validate.perfdrive.com',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Microsoft Edge";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://validate.perfdrive.com',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': url,
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }
                response = self.post(url, data=data, timeout=30, headers=headers, allow_redirects=False)
                if hCaptcha_clear_cookie:
                    self.cookies.clear()
                time.sleep(1)
                self.logger.info(f'[打码成功]')
                redis_53.set(f'hCaptcha_lock_{hCaptcha_lock}_{config.agent}', '1', ex=60 * 5)
                return response
        else:
            redis_53.delete(f'hCaptcha_lock_{hCaptcha_lock}_{config.agent}')
            self.logger.info(f'[打码失败]')
            raise HCaptchaException("打码失败")

    def get_cookies_str(self):
        ret = []
        cookies = self.cookies.get_dict()
        for x in cookies:
            ret.append(f'{x}={cookies[x]}')
        return '; '.join(ret)

    def retry_hook(self):
        pass


class AirAgentV4(AirAgentV3Development):

    def __init__(self, task: Optional[HoldTask] = None, proxies_type=0, retry_count=3, timeout=60, logger=None,
                 request_log=False, cookie_debug=False):
        super().__init__(proxies_type, retry_count, timeout, logger, request_log, cookie_debug)
        self.flights: Dict[str, Journey] = dict()
        self.task: Optional[HoldTask] = task
        self.currency: Optional[str] = None
        self.tag: Set[str] = set()
        self.phone: Optional[str] = None
        self.phone_code: Optional[str] = None
        self.email: Optional[str] = None
        self.baggage_list: List[Baggage] = list()
        self._html: Optional[_Element] = None
        self.baggage_price = 0
        self.logger.info(f'[{self.task.orderCode}][proxies][{self.proxies}]')

    def check_flight(self, airline):
        flight = self.flights.get(self.task.flightNumber, None)
        if not flight:
            raise Exception(
                f'[{self.task.orderCode}][航班未找到: {self.task.flightNumber}][航班列表: {self.flights.keys()}]')

        if 'IgnoreFlightChange' not in self.task.tags:
            dep_time = datetime.strptime(flight.fromSegments[0].depTime, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M')
            if dep_time != self.task.departTime:
                raise self.Exception(
                    f'[{self.task.orderCode}][{self.task.flightNumber} 航变][old: {self.task.departTime}][new: {dep_time}]')

        self.logger.info(
            f'[{self.task.orderCode}][选中航班][{self.task.flightNumber}_{flight.fromSegments[0].depTime}][{flight.adultPrice + flight.adultTax} {flight.cur}]')
        er = get_exchange_rate_carrier(airline, flight.cur)
        cny_price = flight.adultPrice * er
        if self.task.taskType != 'PAO_DAN' and cny_price - float(self.task.targetPrice) > 10:
            raise self.Exception(
                f"[{self.task.orderCode}][涨价 curr: {cny_price},old: {self.task.targetPrice}]")
        return flight

    def post_form(self, html, form_id: Optional[str] = None, form_name: Optional[str] = None, def_data=None,
                  allow_redirects=False, host: Optional[str] = None, headers=None, url=None):
        if headers is None:
            headers = dict()
        if def_data is None:
            def_data = {}
        if form_id:
            form = html.xpath(f'//form[@id="{form_id}"]')
        elif form_name:
            form = html.xpath(f'//form[@name="{form_name}"]')
        else:
            raise Exception(f'[{self.task.orderCode}][post_form 需要 form_id 或则 form_name]')
        if not form:
            raise Exception(f'[{self.task.orderCode}][post_form 未找到表单 {form_id} {form_name}]')

        form = form[0]
        if not url:
            url = form.xpath('./@action')
            if not url:
                raise Exception(f'[{self.task.orderCode}][post_form {form_id or form_name} 获取url 失败]')
            url = url[0]
            if host and url[:5] != 'https':
                if url[0] != '/':
                    url = f'/{url}'
                url = f'https://{host}{url}'

        data = dict()
        for _input in form.xpath('//input'):
            name = _input.xpath('./@name')
            if not name:
                continue
            name = name[0]
            if not name:
                continue
            data[name] = list(map(lambda x: str(x), form.xpath(f'//input[@name="{name}"]/@value')))
        data.update(def_data)
        self.logger.info(f'[{self.task.orderCode}][post_form {form_id or form_name}][url][{url}][data][{data}]')
        response = self.post(url, data=data, allow_redirects=allow_redirects, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f'[{self.task.orderCode}][post_form {form_id or form_name} post 失败][{url}][{data}][{response.status_code}][{response.text}]')
        self.logger.info(f'[{self.task.orderCode}][post_form {form_id or form_name} post 成功][{url}]')
        return response

    @staticmethod
    def register_email(*args, **kwargs):
        return register_email(*args, **kwargs)

    @staticmethod
    def get_exchange_rate_carrier(*args, **kwargs):
        return get_exchange_rate_carrier(*args, **kwargs)

    @staticmethod
    def pay_order_log(payOrderUuid, operation, userId, request):
        return pay_order_log(payOrderUuid, operation, userId, request)

    def apply_email_and_phone(self, domain=None):
        if domain is None:
            domain = ['iugogo.cn']
        self.email = self.register_email(domain)
        phone_number = phone_gen.PhoneNumber(self.task.current_passengers[0].nationality)
        self.phone = phone_number.get_number(full=False)
        self.phone_code = phone_number.get_code()
        self.pay_order_log(self.task.orderCode, "申请邮箱电话", "Trident",
                           f"{self.email} {self.phone_code} {self.phone}")
        self.logger.info(f'[{self.task.orderCode}][申请邮箱电话][{self.email} {self.phone_code} {self.phone}]')

    def apply_union_pay(self, order, url, data, card: str, month: str, year: str, password: str, timeout=300,
                        cookie=None,
                        open_url=None, amount: Optional[float] = None, success_mark=None):
        json = {
            'open_url': open_url,
            'order': order,
            'url': url,
            'data': data,
            'card': card,
            'month': month,
            'year': year,
            'password': password,
            'cookie': cookie,
            'amount': amount,
            'success_mark': success_mark
        }
        self.logger.info(f'[{order}][apply_union_pay][{json}]')
        response = requests.post('http://82.157.25.196:10000/unionPay', json=json, timeout=timeout)
        return response.json()

    def get_cookies_details(self):
        cookies = []
        for domain in self.cookies._cookies:
            for path in self.cookies._cookies[domain]:
                for name in self.cookies._cookies[domain][path]:
                    cookie: Cookie = self.cookies._cookies[domain][path][name]

                    cookies.append({
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                    })
        return cookies

    def refresh_proxy(self, proxies_type=None):
        super().refresh_proxy(proxies_type)
        self.logger.info(f'[{self.task.orderCode}][refresh_proxy][{self.proxies}]')


class AirAgentWebsocket(WebSocketApp):
    import json

    def __init__(self, url, logger: Logger, header=None, keep_running=True, get_mask_key=None, cookie=None,
                 subprotocols=None, socket=None):
        super().__init__(url, header=header, keep_running=keep_running, get_mask_key=get_mask_key, cookie=cookie,
                         subprotocols=subprotocols, socket=socket, on_open=self._on_open, on_message=self._on_message,
                         on_error=self._on_error)
        self._msg_cache = []
        self._error = None
        self.logger = logger
        self._run_thread = None
        self._is_open = False

    def start(self, timeout, *args, **kwargs):
        st = time.time()
        if not self._run_thread:
            self._run_thread = threading.Thread(target=self.run_forever, args=args, kwargs=kwargs)
        self._run_thread.start()
        while not self._is_open:
            if time.time() - st > timeout:
                raise Exception(f'[连接超时][{self.url}]')
            else:
                time.sleep(1)

    def clear_msg_cache(self):
        self._msg_cache.clear()

    def get_msg(self, wait: int, timeout: int):
        time.sleep(wait)
        st = time.time()
        while True:
            if time.time() - st > timeout:
                raise Exception('获取信息超时')
            if not self._msg_cache:
                time.sleep(1)
                continue
            try:
                return self._msg_cache
            except Exception:
                time.sleep(1)
            if self._error:
                raise self._error

    def _on_message(self, ws, msg):
        self.logger.info(f'[on_message][{msg}]')
        self._msg_cache.append(msg)

    def send(self, data, opcode=ABNF.OPCODE_TEXT):
        self.clear_msg_cache()
        self.logger.info(f'[send][{data}]')
        return super().send(data, opcode)

    def _on_open(self, ws):
        self.logger.info(f'[on_open][连接成功]')
        self._is_open = True

    def _on_error(self, ws, error):
        self.logger.error(f'[on_error][{error}]')
        self._error = error


def error_result(payOrder, holdPnrProto, msg, code, pnrTags=None):
    return {
        "pnr": {
            "otaId": payOrder['otaId'],
            "payOrderUuid": payOrder['uuid'],
            "userName": "Trident",
            "cabin": holdPnrProto['cabin'],
            "payBillCode": 1,
            "payBagCode": 1,
            "pnrTags": pnrTags
        },
        "code": code,
        "cause": msg,
        "type": 1,
        "address": config.agent,
        "taskstep": "login"
    }


def pay_error_result(payOrder, msg, code, pnrTags=None):
    if len(msg) > 200:
        msg = msg[:200]
    return {
        "pnr": {
            "otaId": payOrder['otaId'],
            "payOrderUuid": payOrder['uuid'],
            "userName": "Trident",
            "cabin": "",
            "payBillCode": 1,
            "payBagCode": 1,
            "pnrTags": pnrTags
        },
        "code": code,
        "cause": msg,
        "type": 1,
        "address": config.agent,
        "taskstep": "login"
    }


def convert_voucher_pay(task, card_id, pnr, total_amount, ticket_total_amount, currency, phone, email,
                        voucherBaseAmount, voucherPayCurrency, voucherPaAmount, confirm_nb_number=None, pnrTags=None,
                        payRoute=None, ticketAccount: Optional[str] = None,
                        accountUsername: Optional[str] = None, accountPassword: Optional[str] = None,
                        address1: Optional[str] = None, address2: Optional[str] = None, address3: Optional[str] = None,
                        postcode: Optional[str] = None):
    payOrder: dict = task['payOrderDetail']['payOrder']
    noPayedUnitList: list = task['payOrderDetail'].get('noPayedUnitList', [])
    noPayedUnitBagList: list = task['payOrderDetail'].get('noPayedUnitBagList', [])
    payOrderInfoIds = list(map(lambda x: x['payOrderInfoIds'], noPayedUnitList))
    payBaggageIds = list(map(lambda x: x['payOrderInfoIds'], noPayedUnitBagList))
    voucherInfo = task['voucherInfo']
    if total_amount - ticket_total_amount == 0:
        payBaggageIds = []
    return {
        "pnr": {
            "otaId": payOrder['otaId'],
            "payOrderUuid": payOrder['uuid'],
            "pnr": pnr,
            "payPrice": total_amount,
            "payTicketPrice": ticket_total_amount,
            "payBaggagePrice": total_amount - ticket_total_amount,
            "payCurrency": currency,
            "payPhone": phone,
            "payEmail": email,
            "payRoute": payRoute or task['paymentAccount']['account'],
            "payType": card_id,
            "client": "system_wh",
            "payOrderInfoIds": payOrderInfoIds,
            "payBaggageIds": payBaggageIds,
            "userName": "Trident",
            "cabin": "",
            "payBillCode": 3,
            "payBagCode": 1,
            "bookingId": confirm_nb_number,
            "voucherItems": [{
                "payedIndex": 1,
                "pnr": pnr,
                "pnrType": 1,
                "payedIsAll": 0,
                "voucherNumber": voucherInfo['voucherNumber'],
                "payOrderUuid": payOrder['uuid'],
                "voucherAmount": voucherBaseAmount,
                "payedCurrency": voucherPayCurrency,
                "payedAmount": voucherPaAmount,
            }],
            "secondPayPrice": voucherPaAmount,
            "secondPayCurrency": voucherPayCurrency,
            "secondPayType": str(voucherInfo['id']),
            "secondPayRoute": task['paymentAccount']['account'],
            "pnrTags": pnrTags,
            "ticketAccount": ticketAccount,
            "accountUsername": accountUsername,
            "accountPassword": accountPassword,
            "address1": address1,
            "address2": address2,
            "address3": address3,
            "postcode": postcode
        },
        "code": 0,
        "type": 1,
        "address": config.agent,
        "taskstep": "login"
    }


def convert_hold_pay(task, card_id, pnr, total_amount: float, ticket_total_amount: float, currency, phone, email,
                     confirm_nb_number=None, pnrTags=None, payRoute=None, ticketAccount: Optional[str] = None,
                     accountUsername: Optional[str] = None, accountPassword: Optional[str] = None,
                     address1: Optional[str] = None, address2: Optional[str] = None, address3: Optional[str] = None,
                     postcode: Optional[str] = None, ticket_no: Optional[Dict[str, str]] = None):
    payOrder: dict = task['payOrderDetail']['payOrder']
    noPayedUnitList: list = task['payOrderDetail'].get('noPayedUnitList', [])
    noPayedUnitBagList: list = task['payOrderDetail'].get('noPayedUnitBagList', [])
    payOrderInfoIds = list(map(lambda x: x['payOrderInfoIds'], noPayedUnitList))
    payBaggageIds = list(map(lambda x: x['payOrderInfoIds'], noPayedUnitBagList))
    segments = noPayedUnitList[0]['payFlightSplicedSegment']
    payFlightSegments: list = task['payOrderDetail'].get('payFlightSegments', [])
    payFlightSegments = sorted(list(filter(lambda x: x['flightType'] == segments['flightType'], payFlightSegments)),
                               key=lambda x: x['sequence'])
    ticketNos = []
    if ticket_no:
        for payFlightSegment in payFlightSegments:
            for noPayedUnit in noPayedUnitList:
                if not ticket_no.get(str(noPayedUnit['payPassenger']['passengerName']).upper().replace(' ', ''), None):
                    continue
                ticket = {
                    "segment": {
                        "carrier": payFlightSegment['carrier'],
                        "depPort": payFlightSegment['depPort'],
                        "arrPort": payFlightSegment['arrPort'],
                        "flightNum": payFlightSegment['flightNum'],
                        "depTime": payFlightSegment['depDate'],
                        "cabin": payFlightSegment['cabin'],
                        "sequence": payFlightSegment['sequence'],
                        "flightType": payFlightSegment['flightType']
                    },
                    "passenger": {
                        "passengerName": noPayedUnit['payPassenger']['passengerName'],
                        "birthday": noPayedUnit['payPassenger']['birthday'],
                        "baggages": []
                    },
                    "ticketNo": ticket_no[str(noPayedUnit['payPassenger']['passengerName']).upper().replace(' ', '')]
                }
                ticketNos.append(ticket)

    return {
        "pnr": {
            "otaId": payOrder['otaId'],
            "payOrderUuid": payOrder['uuid'],
            "pnr": pnr,
            "payPrice": total_amount,
            "payTicketPrice": ticket_total_amount,
            "payBaggagePrice": total_amount - ticket_total_amount,
            "payCurrency": currency,
            "payPhone": phone,
            "payEmail": email,
            "payRoute": payRoute or task['paymentAccount']['account'],
            "payType": card_id,
            "client": "system_wh",
            "payOrderInfoIds": payOrderInfoIds,
            "payBaggageIds": payBaggageIds,
            "userName": "Trident",
            "cabin": "",
            "payBillCode": 1,
            "payBagCode": 1,
            "bookingId": confirm_nb_number,
            "pnrTags": pnrTags,
            "ticketAccount": ticketAccount,
            "accountUsername": accountUsername,
            "accountPassword": accountPassword,
            "address1": address1,
            "address2": address2,
            "address3": address3,
            "postcode": postcode,
            'ticketNos': ticketNos
        },
        "code": 0,
        "type": 1,
        "address": config.agent,
        "taskstep": "login"
    }


def convert_hold_pay_v2(task, card_id, pnr, total_amount: float, ticket_total_amount: float, currency, phone, email,
                        confirm_nb_number=None, pnrTags=None, payRoute=None, ticketAccount: Optional[str] = None,
                        accountUsername: Optional[str] = None, accountPassword: Optional[str] = None,
                        address1: Optional[str] = None, address2: Optional[str] = None, address3: Optional[str] = None,
                        postcode: Optional[str] = None, payBaggageIds=None, payOrderInfoIds=None):
    if payOrderInfoIds is None:
        payOrderInfoIds = []
    if payBaggageIds is None:
        payBaggageIds = []
    payOrder: dict = task['payOrderDetail']['payOrder']
    return {
        "pnr": {
            "otaId": payOrder['otaId'],
            "payOrderUuid": payOrder['uuid'],
            "pnr": pnr,
            "payPrice": total_amount,
            "payTicketPrice": ticket_total_amount,
            "payBaggagePrice": total_amount - ticket_total_amount,
            "payCurrency": currency,
            "payPhone": phone,
            "payEmail": email,
            "payRoute": payRoute or task['paymentAccount']['account'],
            "payType": card_id,
            "client": "system_wh",
            "payOrderInfoIds": payOrderInfoIds,
            "payBaggageIds": payBaggageIds,
            "userName": "Trident",
            "cabin": "",
            "payBillCode": 1,
            "payBagCode": 1,
            "bookingId": confirm_nb_number,
            "pnrTags": pnrTags,
            "ticketAccount": ticketAccount,
            "accountUsername": accountUsername,
            "accountPassword": accountPassword,
            "address1": address1,
            "address2": address2,
            "address3": address3,
            "postcode": postcode
        },
        "code": 0,
        "type": 1,
        "address": config.agent,
        "taskstep": "login"
    }


def add_on_select_flight(task: HoldTask, flights: List):
    if not task.transit:
        result = list(filter(lambda x: len(x['fromSegments']) == 1, flights))
    else:
        result = list(
            filter(lambda x: len(x['fromSegments']) > 1 and x['fromSegments'][1]['depAirport'] == task.transit,
                   flights))
    if not result:
        raise Exception(f'[{task.orderCode}][add_on_select_flight][无目标航班]')
    result = result[0]
    task.flightNumber = result['data']
    task.departDate = datetime.strptime(result['fromSegments'][0]['depTime'], "%Y%m%d%H%M").strftime('%Y-%m-%d')
    task.departTime = datetime.strptime(result['fromSegments'][0]['depTime'], "%Y%m%d%H%M").strftime('%Y-%m-%d %H:%M')
    if len(result['fromSegments']) > 1:
        task.transitTime = datetime.strptime(result['fromSegments'][1]['depTime'], "%Y%m%d%H%M").strftime(
            '%Y-%m-%d %H:%M')
