# -*- coding: UTF-8 -*-
import json

import requests

from utils.log import check_6E_logger
from airline.base import AirAgentV3Development
import traceback


class A6ECheckWeb(AirAgentV3Development):

    """
    这个质检的难点是请求规律 indexAEM -> checkIn -> View
    每次请求使用session保持会话
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)
        self.session = requests.session()

        self.index_aem_url = "https://book.goindigo.in/Flight/IndexAEM"
        self.retrieve_aem_url = "https://book.goindigo.in/Booking/RetrieveAEM"
        self.view_aem_url = "https://book.goindigo.in/Booking/ViewAEM"

        self.error_code = "-1"

    def index_AEM(self):
        """
        访问IndexAEM接口，
        :return:
        """

        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Origin': 'https://www.goindigo.in',
                'Pragma': 'no-cache',
                'Referer': 'https://www.goindigo.in/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            response = self.session.get(self.index_aem_url, headers=headers)

            if response.status_code == 200:
                check_6E_logger.info(f"IndexAEM接口返回数据为: {response.text}")
                check_6E_logger.info(f"set-cookie: {requests.utils.dict_from_cookiejar(response.cookies)}")

        except Exception:
                check_6E_logger.error(f"IndexAEM接口请求失败: {traceback.format_exc()}")

    def retrieve_AEM(self, last_name, pnr):
        """
        通过CheckInInfoAEM这个接口，返回一个ASP.NET_SessionId
        :return:
        """

        try:
            payload = f"indiGoRetrieveBooking.RecordLocator={pnr}&polymorphicField={last_name}&typeSelected=SearchByNAMEFLIGHT&indiGoRetrieveBooking.IndiGoRegisteredStrategy=Nps.IndiGo.Strategies.IndigoValidatePnrContactNameStrategy%2C+Nps.IndiGo&indiGoRetrieveBooking.IsToEmailItinerary=false&indiGoRetrieveBooking.EmailAddress=&indiGoRetrieveBooking.LastName={last_name}"
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.goindigo.in',
                'Pragma': 'no-cache',
                'Referer': 'https://www.goindigo.in/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            response = self.session.post(url=self.retrieve_aem_url, headers=headers, data=payload)

            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            if "ASP.NET_SessionId" in list(cookies.keys()) and response.status_code == 200:
                self.error_code = "1"
                check_6E_logger.info(f"CheckInInfoAEM接口返回数据为: {response.text}")
                check_6E_logger.info(f"set-cookie: {cookies}")

            else:
                self.error_code = "0"
                check_6E_logger.error(f"CheckInInfoAEM接口返回错误代码为: {response.json()['indiGoError']}")
                check_6E_logger.error(f"set-cookie: {cookies}")

        except Exception:

            check_6E_logger.error(f"{traceback.format_exc()}")

    def view_AEM(self):

        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Origin': 'https://www.goindigo.in',
                'Pragma': 'no-cache',
                'Referer': 'https://www.goindigo.in/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            response = self.session.get(url=self.view_aem_url, headers=headers)

            check_6E_logger.info(f"{response.text}")

            return response

        except Exception:

            check_6E_logger.error(f"{traceback.format_exc()}")
