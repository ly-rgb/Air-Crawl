from utils.log import check_UO_logger
from airline.base import AirAgentV3Development
import traceback
import requests


class AUOCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout)
        self.session = requests.session()

        self.login_url = "https://booking-api.hkexpress.com/api/v1.0/agent"
        self.manage_booking_url = "https://booking-api.hkexpress.com/api/v1.0/booking/ManageBookingLogin"
        self.check_url = "https://booking-api.hkexpress.com/api/v1.0/booking/refresh"
        self.agent_check_url = "http://47.74.250.125:8985/supplier/searchPnr"

        self.get_session_response = None
        self.manage_booking_response = None
        self.check_response = None
        self.agent_check_response = None

        self.error_code = "-1"

    @property
    def base_headers(self):

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'apiKey': '1a739d42f96658378a0ac7804fefdb2ebd649182e4971c99a3edd1e949277270',
            'apiNvcSessionToken': '',
            'fareclub_token': '',
            'isCharterPortal': '0'
        }

        return headers

    def manage_booking(self, last_name, first_name, pnr):
        params = {
            'recordLocator': pnr,
            'lastName': last_name,
            'surname': first_name,
        }

        try:
            response = self.session.get(url=self.manage_booking_url, headers=self.base_headers, params=params)
            self.manage_booking_response = response
            if response.status_code == 200 and response.json()["success"]:
                self.error_code = "1"
                check_UO_logger.info(f"manage_booking接口请求成功，接口地址为: {self.manage_booking_url}")
            else:
                self.error_code = "0"
                check_UO_logger.error(
                    f"没有找到PNR，请求参数为: {params}, "
                    f"请求状态码为: {self.manage_booking_response.status_code}")
        except Exception:
            self.error_code = "-1"
            check_UO_logger.info(
                f"manage_booking接口请求失败，接口地址为: {self.manage_booking_url}, "
                f"请求状态码为: {self.manage_booking_response.status_code}")
            check_UO_logger.error(f"请求参数为: {params}")
            check_UO_logger.error(f"{traceback.print_exc()}")

    def check(self):
        """
        真正返回质检信息的接口
        :return:
        """
        params = {
            "pageRequest": "home"
        }

        try:
            response = self.session.get(url=self.check_url, headers=self.base_headers, params=params)
            self.check_response = response
            if response.status_code == 200 and response.json()["success"]:
                self.error_code = "1"
                check_UO_logger.info(f"(质检接口)请求成功，接口为: {self.check_url}")
                check_UO_logger.info(f"返回的航班信息为: {self.check_response.json()['journeys']}")
            else:
                self.error_code = "0"
                check_UO_logger.error(
                    f"请求状态码为: {self.manage_booking_response.status_code}")
        except Exception:
            self.error_code = "-1"
            check_UO_logger.error(f"请求失败, 接口地址为: {self.check_url}")
            check_UO_logger.error(f"{traceback.print_exc()}")

    def agent_check(self, pnr):

        """
        UO代理人账户质检
        :param pnr: PNR
        """

        params = {
            "channel": "AFARE",
            "carrier": "UO",
            "pnr": pnr,
            "ori": "true"
        }

        try:
            response = self.get(url=self.agent_check_url, params=params)
            if "异常pnr" in response.text or "无效pnr" in response.text or "非法pnr" in response.text:
                self.error_code = "0"
                check_UO_logger.error(f"{response.text}")
            else:
                self.error_code = "1"
                self.agent_check_response = response
                check_UO_logger.info(f"UO代理人接口请求成功，接口地址： {self.agent_check_url}, 请求参数为: {params}")

        except Exception:
            self.error_code = "-1"
            check_UO_logger.error(f"UO代理人接口请求异常，接口地址： {self.agent_check_url}, 请求参数为: {params}")
            check_UO_logger.error(f"{traceback.print_exc()}")







