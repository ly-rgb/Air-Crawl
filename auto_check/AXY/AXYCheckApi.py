# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AXYCheckApi.py
@effect: "XY官网质检API层"
@Date: 2022/11/9 14:10
"""
import traceback
from requests_curl import CURLAdapter
from utils.file_helper import MsgFileRecorder
from utils.log import check_XY_logger
from airline.base import AirAgentV3Development, HttpRetryMaxException
from pyhttpx import HttpSession

from utils.redis import get_random_proxy


class SpiderPyHttps(HttpSession):
    """
    优点: 可以随意修改ja3/TLS指纹
    缺点: 只可以进行https请求
    默认JA3: '771,35466-4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,51914-0-23-65281-10
            -11-35-16-5-13-18-51-45-43-27-43690-21,43690-29-23-24,0'
    默认exts_payload: {43690: '\x00'}
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=None, request_log=False, cookie_debug=False,
                 ja3=None, exts_payload=None):

        super().__init__(ja3=ja3, exts_payload=exts_payload)
        import json
        from lxml.html import etree
        import execjs
        self.json = json
        self.etree = etree
        self.execjs = execjs
        self.proxies_type = proxies_type
        self.retry_count = retry_count
        self.timeout = timeout
        self.logger = logger
        self.msg_file_recorder = MsgFileRecorder(self.__class__.__name__)
        self.__request_log__ = request_log
        self.__cookie_debug__ = cookie_debug

    def request(self, method, url, update_cookies=True, timeout=None, proxies=None, proxy_auth=None,
                params=None, data=None, headers=None, cookies=None, json=None, allow_redirects=True, verify=None
                ):

        if not timeout:
            timeout = self.timeout
        msg = ""
        for _ in range(self.retry_count):
            try:

                response = super().request(method, url, update_cookies, timeout, proxies, proxy_auth,
                                           params, data, headers, cookies, json, allow_redirects,
                                           verify)
                if self.__request_log__:
                    self.logger.info(f'[request {method} {url}] ===> [response {response.status_code} {response.url}]')
                if self.__cookie_debug__:
                    self.logger.info(
                        f'[request {method} {url}] ===> [response {response.status_code} {response.url}][Set-Cookie {response.headers.get("Set-Cookie")}]')
                return response

            except Exception as e:
                if not self.retry_count:
                    raise e
                import traceback
                traceback.print_exc()
                msg = str(e)
                if self.proxies_type:
                    self.proxies = {'https': get_random_proxy(self.proxies_type)["url"]}
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

    def default_tls_info(self):
        """
        返回的tls信息
        :return:
        """
        result = self.get('https://tls.peet.ws/api/all').json

        self.logger.info(f"tls_info: <======================>\n"
                         f"IP: {result['ip']}\n"
                         f"http_version: {result['http_version']}\n"
                         f"Method: {result['method']}\n"
                         f"tls --> ciphers: {result['tls']['ciphers']}\n"
                         f"tls --> extensions: {result['tls']['extensions']}\n"
                         f"ja3: {result['tls']['ja3']}\n"
                         f"ja3-hash: {result['tls']['ja3_hash']}\n"
                         f"总览: {result}")


class AXYCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_XY_logger):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout, logger=logger)
        self.error_code = "-1"
        self.session_create_url = "https://booking.flynas.com/api/SessionCreate"
        self.retrieve_booking_url = "https://booking.flynas.com/api/RetrieveBooking"
        self.check_url = "https://booking.flynas.com/api/Booking"
        self.mount('https://', CURLAdapter(verbose=0, cookie=False))
        self.retrieve_booking_response = None
        self.check_response = None

    @property
    def base_headers(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://booking.flynas.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-Culture': 'en-US',
            'X-Session-Token': 'ew0KICAiYWxnIjogIkhTMjU2IiwNCiAgInR5cCI6ICJKV1QiDQp9.ew0KICAic2Vzc2lvbklkIjogIml3aG9ocGVjMWQ1aW5oeXQ0NG5pcG4zaCIsDQogICJhZGRpdGlvbmFsRGF0YSI6IHt9DQp9._LpU24DuLK0lMgifqVdtGJFF0wYCQidz8hSqewx2TD4',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            # 'Cookie': 'ak_bmsc=470D0697837BC68AE5AAECB8D26D3FE0~000000000000000000000000000000~YAAQFElDF3NWH4WEAQAA7xyl9BJz7zN/Y9Y7LT6+l7zch5SXD5hVS2vx1WRNPTdfvjQU67LF0Dxag50W3Y2Po3Ooe1IU4wcFCitEzBjkEFZnkGhopZpoBm7zZ0BBxBCJdk3yNyZ3XeNLLgJV0/e/4VxMgUdRcUdHqlrgNJYKgH3G8voi+iWibNXps5xpPNpe41qHpnAwAEwz1PjjMm3QzYJsT4nygf9ACGNJ1vbw779qRXEJu+kZLZsu/UacCyc1Zs0fyiLC8ub+GYqPbNgMeJXOEqaWuNZNLXGHoGBIa9eRpvFrvq2CEswlclDN/rZG851ofZYmOK9nmmGxxM0rFZfcdoMheKQWVAlRs6KBhSDhbvr4gEWrA11Ymic=; dtCookie=v_4_srv_3_sn_C3F9D8706A25CA41BC14ACA1A75B9BC3_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_1; ASP.NET_SessionId=2prvqvewvol3u3rvxmyh0ja1; dotrez=2335739402.20480.0000'
        }

        return headers

    def session_create(self):

        payload = "{\"session\":{\"channel\":\"web\"}}"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://booking.flynas.com',
            'Pragma': 'no-cache',
            'Referer': 'https://booking.flynas.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-Culture': 'en-US',
            'X-Session-Token': 'ew0KICAiYWxnIjogIkhTMjU2IiwNCiAgInR5cCI6ICJKV1QiDQp9.ew0KICAic2Vzc2lvbklkIjogIml3aG9ocGVjMWQ1aW5oeXQ0NG5pcG4zaCIsDQogICJhZGRpdGlvbmFsRGF0YSI6IHt9DQp9._LpU24DuLK0lMgifqVdtGJFF0wYCQidz8hSqewx2TD4',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        try:
            response = self.post(url=self.session_create_url, headers=headers, data=payload)

            if response.status_code == 200:
                self.error_code = "1"
                self.retrieve_booking_response = response
                self.logger.info(f"请求成功, 接口地址: {self.session_create_url}")
                self.logger.info(f"请求载荷: {payload}")
            else:
                self.error_code = "-1"
                self.logger.error(f"请求接口地址: {self.session_create_url}")
                self.logger.error(f"响应状态码: {response.status_code}")
                self.logger.error(f"请求载荷: {payload}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"请求失败！！！请求接口地址: {self.session_create_url}, 请求参数: {payload}")
            self.logger.error(f"{traceback.print_exc()}")

    def retrieve_booking(self, last_name, pnr):
        params = {
            "pnr": pnr,
            "email": "",
            "lastName": last_name
        }
        try:
            response = self.get(url=self.retrieve_booking_url, headers=self.base_headers, params=params)
            if response.status_code == 200:
                self.error_code = "1"
                self.retrieve_booking_response = response
                self.logger.info(f"请求成功, 接口地址: {self.retrieve_booking_url}")
                self.logger.info(f"请求载荷: {params}")
                self.logger.info(f"response-headers: {self.retrieve_booking_response.headers}")
            elif response.status_code == 400:
                self.error_code = "0"
                self.logger.error(f"请求失败, 没找到PNR或者LastName错误")
                self.logger.error(f"请求接口地址: {self.retrieve_booking_url}")
                self.logger.error(f"请求载荷: {params}")

            elif response.status_code == 403:
                self.error_code = "-1"
                self.refresh_proxy(proxies_type=self.proxies_type)
                self.logger.error(f"请求失败，状态码403")

            else:
                self.error_code = "-1"
                self.logger.error("发生其他错误，请检查接口")
                self.logger.error(f"请求接口地址: {self.retrieve_booking_url}")
                self.logger.error(f"响应状态码: {response.status_code}")
                self.logger.error(f"请求载荷: {params}")
        except Exception:
            self.error_code = "-1"
            self.logger.error(f"请求失败！！！请求接口地址: {self.retrieve_booking_url}, 请求参数: {params}")
            self.logger.error(f"{traceback.print_exc()}")

    def check(self):

        try:
            response = self.get(url=self.check_url, headers=self.base_headers)

            if response.status_code == 200:
                self.error_code = "1"
                self.check_response = response

                self.logger.info(f"请求成功，接口地址: {self.check_url}")
                self.logger.info(f"请求结果: {self.check_response.text}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")
