# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: ADDCheckApi.py
@effect: "DD质检api层"
@Date: 2022/10/17 10:01
"""

from airline.base import AirAgentV3Development
from utils.log import check_DD_logger
import traceback


class ADDCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout)

        self.authorization = None
        self.session_token = None
        self.login_url = "https://api-production-nokair-booksecure.ezyflight.se/api/v1/TravelAgent/Login"
        self.check_url = "https://api-production-nokair-booksecure.ezyflight.se/api/v1/Booking/Get"

        self.login_response = None
        self.check_response = None
        self.error_code = "-1"

    @property
    def base_headers(self):
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'tenant-identifier': 'FkDcDjsr3Po6GAHFnBh48dHff8MvWpCMfkKyXJ3WVQ7frJ68bD2ubXZDx6sPFRTW',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'x-useridentifier': 'njHPFyoeuQdwPCI2Rv2ubwygOqdtuF'
        }
        return headers

    def agent_login(self, **kwargs):
        """
        代理人登录
        :param username:
        :param password:
        :return:
        """
        # {'user_name': 'Daran2', 'password': '1qaz@WSX'}
        user_name = kwargs.get("account")
        password = kwargs.get("password")
        try:
            if user_name is None:
                check_DD_logger.error("暂不支持官网质检")
                raise Exception(f"暂不支持官网质检")
            else:

                data = self.json.dumps({"username": "Daran2",
                                        "password": "1qaz@WSX",
                                        "languageCode": "en-us"})
                check_DD_logger.info(f"所有API账户都要使用Daran2账户")
                response = self.post(self.login_url,
                                     headers=self.base_headers, data=data)
                if response.status_code == 200:
                    self.login_response = response
                    self.authorization = "bearer " + response.headers["X-AuthorizationToken"]
                    self.session_token = response.headers["SessionToken"]
                    check_DD_logger.info(f"LOGIN Success: ==> "
                                         f"请求url: {self.login_url}"
                                         f"请求参数: {data}"
                                         f"请求结果: {self.login_response.text}")

                elif response.status_code == 401:
                    check_DD_logger.error("用户名或者密码错误")
                    check_DD_logger.error(f"{response.text}")
                else:
                    check_DD_logger.error(f"其他错误: {response.text}")

        except Exception:
            check_DD_logger.error(f"LOGIN FAIL: ==> "
                                  f"请求url: {self.login_url}"
                                  f"请求参数: {data}"
                                  f"请求状态码: {self.login_response.status_code}"
                                  f"请求结果: {self.login_response.text}")
            check_DD_logger.error(f"{traceback.print_exc()}")

    def check(self, last_name: str, pnr: str):
        """
        拿到质检信息
        :return:
        """
        headers = self.base_headers
        headers.update({
            "sessiontoken": self.session_token,
            "authorization": self.authorization
        })

        data = self.json.dumps({"confirmationNumber": pnr,
                                "bookingLastName": last_name,
                                "languageCode": "en-us"})

        try:
            response = self.post(url=self.check_url, headers=headers, data=data)
            if response.status_code == 200:
                self.error_code = "1"
                self.check_response = response
                check_DD_logger.info(f"LOGIN Success: ==> "
                                     f"请求url: {self.check_url}\n"
                                     f"请求参数: {data}\n"
                                     f"请求头Header: {headers}\n"
                                     f"请求结果: {self.check_response.text}")

            elif response.status_code == 401:
                self.error_code = "-1"
                check_DD_logger.error(f"LOGIN FAIL: ==> PNR或者LAST_NAME错误，请重试!!!\n"
                                      f"请求url: {self.check_url}\n"
                                      f"请求参数: {data}\n")
                check_DD_logger.error(f"失败结果: {response.text}")
            elif response.status_code == 500:
                self.error_code = "0"
                check_DD_logger.error(f"该账户没找到此PNR: {pnr}\n"
                                      f"请求结果为: {response.text}")
        except Exception:
            self.error_code = "-1"
            check_DD_logger.error(f"LOGIN FAIL: ==> "
                                  f"请求url: {self.check_url}\n"
                                  f"请求参数: {data}\n"
                                  f"请求头Header: {headers}\n")
            check_DD_logger.error(f"{traceback.print_exc()}")





