# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AFDCheckApi.py
@effect: "亚航代理人质检接口"
@Date: 2022/10/15 14:51
"""
from airline.base import AirAgentV3Development
from utils.log import check_FD_logger
import traceback


class AFDCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, timeout=60, retry_count=3):
        super().__init__(proxies_type=proxies_type, timeout=timeout, retry_count=retry_count)
        self.login_url = "https://lemon.apiairasia.com/api/v1/auth/login"
        self.get_user_url = "https://lemon.apiairasia.com/api/v1/user"
        self.booking1_url = "https://lemon.apiairasia.com/api/v1/booking/list"
        self.booking2_url = "https://lemon.apiairasia.com/api/v1/booking"

        self.login_response = None
        self.agent_user_response = None
        self.booking1_response = None
        self.booking2_response = None

        self.token = None
        self.authorization = None
        self.error_code = "-1"

    @property
    def base_headers(self):

        headers = {"Accept": "application/json, text/plain, */*",
                   "Content-Type": "application/json",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
        return headers

    def login(self, account: str, password: str) -> None:
        """
        login，拿到token
        :param user_name:
        :param password:
        :return:
        """

        data = self.json.dumps({
            "username": account,
            "password": password
        })

        try:
            response = self.post(url=self.login_url, headers=self.base_headers, data=data)
            if response.status_code == 200 and "accessToken" in response.text:
                self.login_response = response
                self.error_code = "1"
                self.token = self.json.loads(self.login_response.text)["accessToken"]
                check_FD_logger.info(f"请求成功！！！\n"
                                     f"请求URL: {self.login_url}\n"
                                     f"请求载体: {data}\n"
                                     f"状态码: {self.login_response.status_code}\n"
                                     f"返回值: {self.login_response.text}\n")

            else:
                self.error_code = "-1"
                check_FD_logger.error(f"请求失败")
        except Exception:
            self.error_code = "-1"
            check_FD_logger.error(f"请求失败！！！"
                                  f"请求URL: {self.login_url}\n"
                                  f"请求载体: {data}\n"
                                  f"状态码: {self.login_response.status_code}\n"
                                  f"返回值: {self.login_response.text}\n")
            check_FD_logger.error(f"{traceback.print_exc()}")

    def agent_user(self):
        """
        get user
        :return:
        """
        self.authorization = "Bearer " + self.token

        headers = self.base_headers
        headers.update({"authorization": self.authorization})
        try:
            response = self.get(url=self.get_user_url, headers=headers)
            if response.status_code == 200 and "OrganizationCode" in response.text:
                self.agent_user_response = response
                self.error_code = "1"
                self.organization_code = self.json.loads(self.agent_user_response.text)["OrganizationCode"]
                check_FD_logger.info(f"organization_code: {self.organization_code}")
                check_FD_logger.info(f"请求成功！！！\n"
                                     f"请求URL: {self.get_user_url}\n"
                                     f"状态码: {self.agent_user_response.status_code}\n"
                                     f"返回值: {self.agent_user_response.text}\n")

        except Exception:
            self.error_code = "-1"
            check_FD_logger.error(f"请求失败！！！\n"
                                  f"请求URL: {self.get_user_url}\n"
                                  f"状态码: {self.agent_user_response.status_code}\n"
                                  f"返回值: {self.agent_user_response.text}\n")
            check_FD_logger.error(f"{traceback.print_exc()}")

    def booking1(self, account: str):

        headers = self.base_headers
        headers.update({"authorization": self.authorization})

        params = {
            "status": "1",
            "agency": "",
            "agent": account
        }

        try:
            response = self.get(url=self.booking1_url, headers=headers, params=params)
            if response.status_code == 200:
                self.booking1_response = response
                self.error_code = "1"
                check_FD_logger.info(f"请求成功！！！\n"
                                     f"请求URL: {self.booking1_url}\n"
                                     f"请求载体: {params}\n"
                                     f"状态码: {self.booking1_response.status_code}\n"
                                     f"返回值: {self.booking1_response.text}\n")

        except Exception:
            self.error_code = "-1"
            check_FD_logger.error(f"请求失败！！！\n"
                                  f"请求URL: {self.booking1_url}\n"
                                  f"状态码: {self.booking1_response.status_code}\n"
                                  f"请求载体: {self.params}"
                                  f"返回值: {self.booking1_response.text}\n")
            check_FD_logger.error(f"{traceback.print_exc()}")

    def booking2(self, pnr: str):
        headers = self.base_headers
        headers.update({"authorization": self.authorization})

        params = {
            "agency": self.organization_code,
            "pnr": pnr
        }
        try:
            response = self.get(url=self.booking2_url, headers=headers, params=params)

            if response.status_code == 200:
                self.booking2_response = response
                result = self.json.loads(self.booking2_response.text)
                recordLocator = result["recordLocator"]
                bookingStatus = result["info"]["status"]
                paidStatus = result["info"]["paidStatus"]
                check_FD_logger.info(f"输入参数pnr: {pnr}, recordLocator: {recordLocator}, bookingStatus: {bookingStatus}, "
                                     f"paidStatus: {paidStatus}")

                if pnr == recordLocator:
                    if bookingStatus == 2 and paidStatus == 1:
                        self.error_code = "1"
                        check_FD_logger.info(f"请求成功！！！\n"
                                             f"请求URL: {self.booking2_url}\n"
                                             f"请求载体: {params}\n"
                                             f"状态码: {self.booking2_response.status_code}\n"
                                             f"返回值: {self.booking2_response.text}\n")
                    else:
                        self.error_code = "-3"
                        check_FD_logger.error("漏支付")
                else:
                    self.error_code = "0"
                    check_FD_logger.error("没找到PNR")

        except Exception:
            self.error_code = "-1"
            check_FD_logger.error(f"请求失败！！！\n"
                                  f"请求URL: {self.booking2_url}\n"
                                  f"状态码: {self.booking2_response.status_code}\n"
                                  f"请求载体: {self.params}"
                                  f"返回值: {self.booking2_response.text}\n")
            check_FD_logger.error(f"{traceback.print_exc()}")


