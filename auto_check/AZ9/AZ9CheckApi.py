# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AZ9CheckApi.py
@effect: "请填写用途"
@Date: 2022/12/30 12:00
"""
import traceback

from airline.base import AirAgentV3Development
from utils.log import check_Z9_logger
from utils.AgentDb import select_agent_db


class AZ9CheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_Z9_logger):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout)
        self.logger = logger

        self.login_url = "https://myairline-api.ezycommerce.sabre.com/api/v1/TravelAgent/Login"
        self.check_url = 'https://myairline-api.ezycommerce.sabre.com/api/v1/Booking/Get'
        self.error_code = "-1"

    def login(self, pnr):
        self._user_pwd = select_agent_db(pnr=pnr, logger=self.logger)
        user_name = self._user_pwd["user_name"]
        password = self._user_pwd["password"]

        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'languageCode': 'en-us'
        }

        data = {
            'username': user_name,
            'password': password,
            'languageCode': 'en-us',
        }

        self.logger.info(f"开始请求: {self.login_url}")

        response = self.post(url=self.login_url, headers=headers, json=data)
        if response.status_code == 200:
            self.logger.info(f"登录成功")
            self.hash_password = response.json()["hashedPassword"]
        elif user_name is None:
            self.error_code = "0"
            self.logger.error(f"没有找到pnr: {pnr}对应的账号密码")
            raise Exception(f"查询pnr对应账号密码失败......")
        else:
            self.logger.error(
                f"登录失败... code: {response.status_code} data: {data} login1_error_res: {response.text}")
            raise Exception(f"登录失败......")


    def login2(self):
        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'languageCode': 'en-us'
        }

        data = {
            'username': self._user_pwd["user_name"],
            'password': self.hash_password,
            'hashed': True,
            'languageCode': 'en-us',
        }

        self.logger.info(f"开始请求: {self.login_url}")

        response = self.post(url=self.login_url, headers=headers, json=data)

        if response.status_code == 200:
            self.logger.info(f"第二次登录成功...")
            self.SessionToken = response.json().get("sessiontoken")
            self.AuthorizationToken = "bearer " + response.headers.get('x-authorizationtoken')
        else:
            self.logger.error(
                f"第二次请求失败... code: {response.status_code} data: {data} login2_error_res: {response.text}")
            raise Exception(f"第二次登录失败...")


    def check(self, last_name, pnr):
        headers = {
            'Accept': 'text/plain',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Tenant-Identifier': 'bNYGgLTJVY8uzyV3aHscrXubhTRKyAJo3UQGkRvxXMerjCUiveKAUptpz6mWq9JW',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-UserIdentifier': 'hEcoIpknKSadMf6wxyAoVp32cxXjLx',
            'languageCode': 'en-us',
            'SessionToken': self.SessionToken,
            'Authorization': self.AuthorizationToken
        }

        data = {
            'confirmationNumber': pnr,
            'bookingLastName': last_name,
            'languageCode': 'en-us',
        }

        self.logger.info(f"开始请求接口: {self.check_url}")
        response = self.post(url=self.check_url, headers=headers, json=data)
        if response.status_code == 200:
            self.check_response = response
            self.error_code = "1"
            self.logger.info(f"check请求结果: {self.check_response.text}")
        elif response.status_code == 401:
            self.error_code = "0"
            self.logger.error(
                f"没有找到PNR或者LastName错误... code: {response.status_code} data: {data} errod_res: {response.text}")
            raise Exception(f"没有找到PNR或者LastName错误...")
        else:
            self.logger.error(f"请求质检接口失败！！！ code: {response.status_code} data: {data} errod_res: {response.text}")
            raise Exception(f"请求质检接口失败...")



