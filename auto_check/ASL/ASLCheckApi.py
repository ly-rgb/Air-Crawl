# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: ASLCheckApi.py
@effect: "请填写用途"
@Date: 2022/12/15 15:20
"""
from datetime import datetime

from airline.base import AirAgentV3Development
from requests_curl import CURLAdapter
from utils.log import check_SL_logger
import traceback


class ASLCheckWeb(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, logger=check_SL_logger, request_log=True, otaid=None):
        super().__init__(proxies_type=proxies_type, retry_count=retry_count, timeout=timeout, logger=logger,
                         request_log=request_log)
        self.error_code = "-1"
        self.mount('https://', CURLAdapter(verbose=0, cookie=False))
        self.otaid = otaid
        self.__index_url = "https://search.lionairthai.com"
        self.__location = None
        self.__next_url = None
        self.__form = None
        self.__birthday_form = None
        self.birthday_response = None
        self.flight_response = None
        self.baggage_response = None
        self.name_birthday_dict = {}

    def front_check(self, last_name, first_name, pnr):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://www.lionairthai.com/',
            'Origin': 'https://www.lionairthai.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
        }

        data = {
            'opr': pnr,
            'ofn': first_name,
            'oln': last_name,
        }

        try:
            response = self.post(url="https://search.lionairthai.com/sl/onlineaddonbooking.aspx", headers=headers,
                                 data=data, allow_redirects=False)
            if response.status_code == 302:
                self.__next_url = self.__index_url + response.headers['location']
                self.logger.info(f"重定向成功！！！ Location: {response.headers['location']}")
                self.logger.info(f"请求载荷: {data}")
            else:
                raise Exception(f"重定向失败!! 状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.info(f"请求载荷: {data}")
            self.logger.error(f"{traceback.print_exc()}")

    def redirect_1(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://www.lionairthai.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
        }

        try:
            response = self.get(
                self.__next_url,
                headers=headers,
                allow_redirects=False,
            )
            if response.status_code == 302:
                self.__next_url = self.__index_url + response.headers['location']
                self.logger.info(f"重定向成功！！！ Location: {response.headers['location']}")
            elif response.status_code == 200:
                self.birthday_response = response
                self.logger.info(f"生日界面访问成功！！！")
                self.birthday_html()
            else:
                raise Exception(f"重定向失败!! 状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")

    def birthday_html(self):

        try:
            headers = {
                'authority': 'search.lionairthai.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'no-cache',
                'origin': 'https://search.lionairthai.com',
                'pragma': 'no-cache',
                'referer': 'https://search.lionairthai.com/',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }

            self.pay_order_name_birthday()
            self.__extract_birthday_form(text=self.birthday_response.text)
            response = self.post(
                url=self.__next_url,
                headers=headers,
                data=self.__birthday_form,
                allow_redirects=False
            )
            if response.status_code == 302:
                self.__next_url = self.__index_url + response.headers['location']
                self.logger.info(f"重定向成功！！！ Location: {response.headers['location']}")
            else:
                raise Exception(f"重定向失败!! 状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")

    def redirect_2(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://www.lionairthai.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
        }

        try:
            response = self.get(
                self.__next_url,
                headers=headers,
                allow_redirects=False,
            )

            if response.status_code == 302:
                self.__next_url = self.__index_url + response.headers['location']
                self.logger.info(f"重定向成功！！！ Location: {response.headers['location']}")
            else:
                raise Exception(f"重定向失败!! 状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")

    def check(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://www.lionairthai.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
        }

        try:
            response = self.get(
                self.__next_url,
                headers=headers,
                allow_redirects=False,
            )

            if response.status_code == 200:
                self.logger.info(f"flight页面请求成功!!!, 下面解析表单数据")
                self.logger.info(f"{response.text}")
                self.error_code = "1"
                self.flight_response = response
                self.__extract_form(response.text)

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")

    def get_baggage_redirect1(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://www.lionairthai.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
        }

        try:
            response = self.post(url=self.__next_url, headers=headers, data=self.__form, allow_redirects=False)
            if response.status_code == 302:
                self.__next_url = self.__index_url + response.headers['location']
                self.logger.info(f"重定向成功！！！ Location: {response.headers['location']}")
            else:
                raise Exception(f"重定向失败!! 状态码: {response.status_code}")

        except Exception:
            self.error_code = "-1"
            self.logger.error(f"{traceback.print_exc()}")

    def get_baggage_html(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://search.lionairthai.com/',
            'Origin': 'https://search.lionairthai.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',

        }
        try:
            response = self.get(url=self.__next_url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                self.logger.info(f"获取行李信息成功")
                self.logger.info(f"{response.text}")
                self.baggage_response = response
            else:
                raise Exception(f"获取行李界面失败!! 状态码: {response.status_code}")

        except Exception:
            self.error_code = -1
            self.logger.error(f"{traceback.print_exc()}")

    def __extract_form(self, text):

        html = self.etree.HTML(text=text)

        __EVENTTARGET = html.xpath("//input[@id='__EVENTTARGET']/@value")[0]
        __EVENTARGUMENT = html.xpath("//input[@id='__EVENTARGUMENT']/@value")[0]
        __VIEWSTATE = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
        __VIEWSTATEGENERATOR = html.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value")[0]
        __VIEWSTATEENCRYPTED = html.xpath("//input[@id='__VIEWSTATEENCRYPTED']/@value")[0]
        __EVENTVALIDATION = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
        hdnRelativePath = html.xpath("//input[@id='hdnRelativePath']/@value")[0]
        bodycontent_hfNewRetrive = html.xpath("//input[@id='bodycontent_hfNewRetrive']/@value")[0]
        bodycontent_hfConfrimMsg = html.xpath("//input[@id='bodycontent_hfConfrimMsg']/@value")[0]
        bodycontent_hfPlsAgree = html.xpath("//input[@id='bodycontent_hfPlsAgree']/@value")[0]
        bodycontent_hfPaymentFailed = html.xpath("//input[@id='bodycontent_hfPaymentFailed']/@value")[0]
        bodycontent_btnAddon = html.xpath("//input[@name='ctl00$bodycontent$btnAddon']/@value")[0]
        bodycontent_hdRemovedItem = ''
        bodycontent_hdnCustomerUserID = ''

        self.logger.info(f"__EVENTTARGET: {__EVENTTARGET}\n"
                         f"__EVENTARGUMENT: {__EVENTARGUMENT}\n"
                         f"__VIEWSTATE: {__VIEWSTATE}\n"
                         f"__VIEWSTATEGENERATOR: {__VIEWSTATEGENERATOR}\n"
                         f"__VIEWSTATEENCRYPTED: {__VIEWSTATEENCRYPTED}\n"
                         f"__EVENTVALIDATION: {__EVENTVALIDATION}\n"
                         f"hdnRelativePath: {hdnRelativePath}\n"
                         f"bodycontent_hfNewRetrive: {bodycontent_hfNewRetrive}\n"
                         f"bodycontent_hfConfrimMsg: {bodycontent_hfConfrimMsg}\n"
                         f"bodycontent_hfPlsAgree: {bodycontent_hfPlsAgree}\n"
                         f"bodycontent_hfPaymentFailed: {bodycontent_hfPaymentFailed}\n"
                         f"bodycontent_btnAddon: {bodycontent_btnAddon}\n"
                         f"bodycontent_hdRemovedItem: {bodycontent_hdRemovedItem}\n"
                         f"bodycontent_hdnCustomerUserID: {bodycontent_hdnCustomerUserID}")

        self.__form = {
            "__EVENTTARGET": __EVENTTARGET,
            "__EVENTARGUMENT": __EVENTARGUMENT,
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__VIEWSTATEENCRYPTED": __VIEWSTATEENCRYPTED,
            "__EVENTVALIDATION": __EVENTVALIDATION,
            "ctl00$hdnRelativePath": hdnRelativePath,
            "ctl00$bodycontent$hfNewRetrive": bodycontent_hfNewRetrive,
            "ctl00$bodycontent$hfConfrimMsg": bodycontent_hfConfrimMsg,
            "ctl00$bodycontent$hfPlsAgree": bodycontent_hfPlsAgree,
            "ctl00$bodycontent$hfPaymentFailed": bodycontent_hfPaymentFailed,
            'ctl00$bodycontent$btnAddon': bodycontent_btnAddon,
            'ctl00$bodycontent$hdRemovedItem': bodycontent_hdRemovedItem,
            'ctl00$bodycontent$hdnCustomerUserID': bodycontent_hdnCustomerUserID
        }

    def __extract_birthday_form(self, text):
        """
        解析生日表单
        :param text:
        :return:
        """
        html = self.etree.HTML(text=text)

        __VIEWSTATE = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
        __VIEWSTATEGENERATOR = html.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value")[0]

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': __VIEWSTATE,
            '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
            '__VIEWSTATEENCRYPTED': '',
            'btnUpdateEmailMobile': 'Continue'
        }

        row = html.xpath(
            "//div[@id='divDOB']/div[@class='row']/div[@class='col-md-9']/div[@class='form-group']/div[@class='triple']")
        for idx, element in enumerate(row):
            first_name = element.xpath(f"//input[@id='lvPassengerDOB_hdnFirstName_{idx}']/@value")[0]
            last_name = element.xpath(f"//input[@id='lvPassengerDOB_hdnSurName_{idx}']/@value")[0]
            pax_type = element.xpath(f"//input[@id='lvPassengerDOB_hdnPaxType_{idx}']/@value")[0]
            hdn_number = element.xpath(f"//input[@id='lvPassengerDOB_hdnNameNumber_{idx}']/@value")[0]

            for k, v in self.name_birthday_dict.items():
                birthday = v.split("-")
                if first_name.replace(" ", "") in k.replace(" ", ""):
                    data.update({
                        f'lvPassengerDOB$ctrl{idx}$hdnFirstName': first_name,
                        f'lvPassengerDOB$ctrl{idx}$hdnSurName': last_name,
                        f'lvPassengerDOB$ctrl{idx}$hdnPaxType': pax_type,
                        f'lvPassengerDOB$ctrl{idx}$hdnNameNumber': hdn_number,
                        f'lvPassengerDOB$ctrl{idx}$ddlDay': birthday[2],
                        f'lvPassengerDOB$ctrl{idx}$ddlMonth': birthday[1],
                        f'lvPassengerDOB$ctrl{idx}$ddlYear': birthday[0]
                    })
                    break
        check_SL_logger.info(f"提取到的birthday-data: {data}")
        self.__birthday_form = data

    def pay_order_name_birthday(self):
        """
        解析任务并返回first_name--birthday 的字典
        :return:
        """
        from config import config

        url = "http://47.104.182.61:5454/order/getAutoCheckPayOrder"
        params = {
            "otaId": self.otaid,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            # 'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        check_SL_logger.info(f"开始访问质检任务接口: {url}")
        try:
            for _ in range(10):
                response = self.get(url=url, params=params, headers=headers)
                if response.status_code == 200:
                    pay_order_task = response.json()
                    for passenger in pay_order_task["payOrderProto"]["payPassengers"]:
                        first_name = passenger["passengerName"].split("/")[1]
                        birthday = datetime.strptime(passenger["birthday"], "%b %d, %Y %H:%M:%S %p").strftime(
                            "%Y-%m-%d")
                        birthday = "-".join(list(map(self.birthday_int, birthday.split("-"))))
                        self.name_birthday_dict.update({
                            first_name: birthday
                        })
                    check_SL_logger.info(f"提取到的name_birthday_dict: {self.name_birthday_dict}")
                    break
                else:
                    check_SL_logger.error(f"访问任务接口失败: {url}")
        except Exception:
            self.logger.error(traceback.print_exc())

    def birthday_int(self, x):
        return str(int(x))


