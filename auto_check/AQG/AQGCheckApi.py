# -*- coding: UTF-8 -*-

import pyhttpx

from utils.log import check_QG_logger
from airline.base import AirAgentV3Development
import traceback


class AQGCheckWeb(AirAgentV3Development):
    """

    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)
        self.error_code = "-1"

    def check(self, last_name, pnr):
        """
        """
        try:
            sess = pyhttpx.HttpSession()
            get_cookie_url = 'https://www.citilink.co.id'
            headers = {
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            }
            # 获取ASP.NET_SessionId
            response = sess.get(url=get_cookie_url, headers=headers)
            if response.status_code == 200:
                ASP_NET_SessionId = sess.cookies.get('ASP.NET_SessionId')
                check_QG_logger.info(f"ASP.NET_SessionId为: {ASP_NET_SessionId}")
            else:
                check_QG_logger.error('ASP.NET_SessionId获取失败')
                return

            get_info_url = 'https://book.citilink.co.id/RetrieveBooking.aspx?culture=en-US'
            data = {
                '__EVENTTARGET': 'ControlGroupRetrieveBookingNewView$BookingRetrieveInputRetrieveBookingNewView$LinkButtonRetrieve',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': '/wEPDwUBMGRkanpi0dMg5Dyys4LtW8qDkNMISyU=',
                'pageToken': '',
                'ControlGroupRetrieveBookingNewView$BookingRetrieveInputRetrieveBookingNewView$CONFIRMATIONNUMBER1': pnr.replace(
                    " ", ""),
                'ControlGroupRetrieveBookingNewView$BookingRetrieveInputRetrieveBookingNewView$PAXLASTNAME1': last_name.replace(
                    " ", "")
            }
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'book.citilink.co.id',
                'Origin': 'https://book.citilink.co.id',
                'Referer': 'https://book.citilink.co.id/RetrieveBooking.aspx?culture=en-US',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
            }
            # 确认 ASP.NET_SessionId
            response = sess.get(url=get_info_url, headers=headers)
            if response.status_code == 200:
                check_QG_logger.info('ASP.NET_SessionId确认成功')
            else:
                check_QG_logger.error('ASP.NET_SessionId确认失败')
                return

            get_info_url_response = sess.post(url=get_info_url, headers=headers, data=data,
                                              allow_redirects=False)
            if get_info_url_response.headers.get('location') == '/ChangeItinerary.aspx':
                self.error_code = '0'
                check_QG_logger.info('重定向成功')
            else:
                check_QG_logger.error('重定向失败')
                return
            info_url = 'https://book.citilink.co.id/ChangeItinerary.aspx'
            info_response = sess.get(url=info_url, headers=headers)
            if info_response.status_code == 200:
                self.error_code = "1"
                self.check_response = info_response.text
                # print(self.check_response)
                check_QG_logger.info(f"info_response接口返回数据长度为(正常37873左右): {len(info_response.text)}")
            else:
                check_QG_logger.error('info_response获取失败')
                return

        except Exception:
            check_QG_logger.error(f"质检登录失败: {traceback.format_exc()}")
