# -*- coding: UTF-8 -*-
import json
from lxml import etree
import requests

from utils.log import check_LM_logger
from airline.base import AirAgentV3Development
import traceback


class ALMCheckWeb(AirAgentV3Development):
    """

    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)
        self.session = requests.session()

        self.error_code = "-1"

    def check(self, last_name, pnr):
        """
        """
        try:
            get_VarsSessionID_url = 'https://booking.loganair.co.uk/VARS/Public/CustomerPanels/MMBLoginbs.aspx'
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            }
            sessid_response = self.session.get(url=get_VarsSessionID_url, headers=headers)
            if sessid_response.status_code == 200:
                sessid_html = self.etree.HTML(sessid_response.text)
                input = sessid_html.xpath('//*[@id="VarsSessionID"]')
                sessid = input[0].attrib.get('value')
                check_LM_logger.info(f"sessid_response接口返回数据长度为(正常11367左右): {len(sessid_response.text)}")
                check_LM_logger.info(f"sessid为: {sessid}")
            else:
                check_LM_logger.error('sessid获取失败')
                return
            get_info_url = 'https://booking.loganair.co.uk/VARS/Public/WebServices/LoginWs.asmx/DoMMBLogin?VarsSessionID={}'.format(
                sessid)
            data = {'loginRq': {
                'Language': "en",
                'Surname': last_name.replace(" ",""),
                'VarsSessionID': sessid,
                'pnr': pnr.replace(" ",""),
            }}
            get_info_url_response = self.session.post(url=get_info_url, headers=headers, data=json.dumps(data))
            if get_info_url_response.status_code == 200:
                info_url = get_info_url_response.json()['d']['NextURL']
                if len(info_url) < 2:
                    self.error_code = "0"
                    return
                check_LM_logger.info(f"info_url为: {info_url}")
            else:
                check_LM_logger.error('info_url获取失败')
                return
            headers = {
                'Host': 'booking.loganair.co.uk',
                'Connection': 'keep-alive',
                'Origin': 'https://booking.loganair.co.uk',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Dest': 'document',
                'Referer': 'https://booking.loganair.co.uk/VARS/Public/CustomerPanels/MMBLoginbs.aspx',
                'Accept-Encoding': 'gzip, deflate, br',
            }
            info_response = self.session.get(url=info_url, headers=headers)
            if info_response.status_code == 200:
                self.error_code = "1"
                self.check_response = info_response.text
                check_LM_logger.info(f"info_response接口返回数据长度为(正常345449左右): {len(info_response.text)}")
            else:
                check_LM_logger.error('info_response获取失败')
                return
            get_sex_url = info_url.replace("confirm","PassengerDetails")
            try:
                sex_response = self.session.get(url=get_sex_url, headers=headers)
                req_html = etree.HTML(sex_response.text)
                divs = req_html.xpath('//*[@class="table-responsive"]//text()')
                if "MR" in divs:
                    self.sex = "M"
                elif "MISS" in divs:
                    self.sex = "F"
                elif "MS" in divs:
                    self.sex = "F"
                elif "MRS" in divs:
                    self.sex = "F"
                else:
                    self.sex = ""
            except:
                pass
        except Exception:
            check_LM_logger.error(f"质检登录失败: {traceback.format_exc()}")
