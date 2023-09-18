# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: AEWCheckApi.py
@effect: "EW质检API层"
@Date: 2022/10/26 10:08
"""

from utils.log import check_EW_logger
from airline.base import AirAgentV3Development
import traceback
import requests
from urllib import parse


class AEWCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout)
        self.session = requests.session()

        self.front_check_url = "https://mobile.eurowings.com/booking/scripts/BookingList/BookingValidation.aspx"
        self.check_redirect_url = "https://mobile.eurowings.com/booking/BookingList.aspx"
        self.check_url = "https://mobile.eurowings.com/booking/MyFlight.aspx"
        self.front_check_response = None
        self.check_redirect_response = None
        self.check_response = None

        self.error_code = "-1"

    @property
    def base_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive'
        }

        return headers

    def front_check(self, last_name, pnr):
        payload = f'recordlocator={pnr}&lastname={last_name}&appversion=4.8.0'

        try:

            response = self.session.post(url=self.front_check_url, headers=self.base_headers, data=payload)
            result = response.json()["validated"]
            if response.status_code == 200 and result:
                self.front_check_response = response
                check_EW_logger.info(f"请求成功！！！请求接口地址: {self.front_check_url}")
                check_EW_logger.info(f"请求载荷: {payload}")
                check_EW_logger.info(f"请求结果: {self.front_check_response.json()}")

            else:
                self.error_code = "0"
                check_EW_logger.error(f"请求失败，未找到PNR！！！请求接口地址: {self.front_check_url}")
                check_EW_logger.error(f"请求载荷: {payload}")
                check_EW_logger.error(f"请求结果: {response.json()}")

        except Exception:
            self.error_code = "-1"
            check_EW_logger.error(f"请求失败！！！请求接口地址: {self.front_check_url}, 请求参数: {payload}")
            check_EW_logger.error(f"{traceback.print_exc()}")

    def check_redirect(self, last_name, pnr, gender):

        payload_dict = {
            "__EVENTTARGET": "retrievebooking",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": "qBgdo+Mod47bduVN5bKcB70VNWvmDgE7FDJWWMwCVy+6xJ7ymxRomO4MKTHxitRjswJ9TXzAxwCNxFVycv9mTTt9++4=",
            "__VIEWSTATEGENERATOR": "CD00428D",
            "__VIEWSTATEENCRYPTED": "",
            "CsrfToken": "HhcggRHgLmNaWH4IIE9cp+/DZoP6QMhefuKNl4RlSaexfHTKp2IwmFD6VzLjLouvtNO+NEOX9cBtm63ppQS7VA==",
            "BookingListViewControlGroup$BookingListBookingsControl$contextField": "retrievebooking",
            "context": "retrievebooking",
            "BookingListViewControlGroup$BookingListBookingsControl$selectedRecordLocator": pnr,
            "BookingListViewControlGroup$BookingListBookingsControl$selectedLastName": last_name,
            "BookingListViewControlGroup$BookingListBookingsControl$selectedFirstName": "",
            "BookingListViewControlGroup$BookingListBookingsControl$selectedGender": "",
            "BookingListViewControlGroup$BookingListBookingsControl$selectedCheckInMode": "1",
            "gender": gender,
            "recordLocator": pnr,
            "lastname": last_name,
            "BookingListViewControlGroup$BookingListBookingsControl$ButtonSubmit": "Next"
        }

        payload = "&".join([parse.quote(k) + "=" + parse.quote(v) for k, v in payload_dict.items()])

        try:
            response = self.session.post(url=self.check_redirect_url, headers=self.base_headers, data=payload,
                                         allow_redirects=False)

            if response.status_code == 302:
                self.error_code = "1"
                self.check_response = response
                check_EW_logger.info(f"状态码: {response.status_code}")
                check_EW_logger.info(f"请求载荷: {payload}")
            elif response.status_code == 200:
                self.error_code = "0"
                check_EW_logger.error(f"请求载荷: {payload}")
                check_EW_logger.error(f"PNR: {pnr}, LastName: {last_name}, gender: {gender} 不匹配，请重新检查")

        except Exception:
            self.error_code = "-1"
            check_EW_logger.error(f"请求载荷: {payload}")
            check_EW_logger.error(f"{traceback.print_exc()}")

    def check(self):

        try:
            response = self.session.get(url=self.check_url, headers=self.base_headers)
            if response.status_code == 200:
                self.error_code = "1"
                self.check_response = response
                check_EW_logger.info(f"请求成功！！！请求接口地址: {self.check_url}")
        except Exception:
            self.error_code = "-1"
            check_EW_logger.error(f"请求失败！！！请求接口地址: {self.check_url}")
            check_EW_logger.error(f"{traceback.print_exc()}")