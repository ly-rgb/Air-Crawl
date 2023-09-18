import re
import uuid

from airline.base import AirAgentV3Development
from utils.log import refund_VY_logger


class AVYMobile(AirAgentV3Development):
    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)

    @property
    def base_headers(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/94.0.4606.81 Safari/537.36',
        }
        return headers

    def full_refund(self, task):
        url = 'https://apimobile.vueling.com/Vueling.Mobile.BookingServices' \
              '.WebAPI/api/GetBooking/DoGetBooking'
        pnr = task["data"]["payOrderBasicInfo"]["payPnrBasicInfos"][0][
            "pnr"]
        data = {
            'DeviceType': "WEB",
            'Email': 'nevergiveup17apr05@qq.com',
            'RecordLocator': pnr,
        }
        resp = self.post(url=url, headers=self.base_headers, json=data)
        refund_VY_logger.info(f'{pnr}全退的响应状态码为{resp.status_code}')
        try:
            JourneysKey = re.findall('.*?Key":"(.*?)".*?', resp.text, re.S)[0]
        except(IndexError):
            return 'failure'
        refund_VY_logger.info(f'{pnr}获取到的key为{JourneysKey}')
        url = 'https://apimobile.vueling.com/Vueling.Mobile.RefundServices' \
              '.WebAPI/api/refund/send'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,af;q=0.8,en;q=0.7,es;q=0.6,zh-TW;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'apimobile.vueling.com',
            'Origin': 'https://m.vueling.com',
            'Pragma': 'no-cache',
            'Referer': 'https://m.vueling.com/',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        }
        data = {
            "DeviceType": "WEB",
            "UserAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
                         "Mobile Safari/537.36",
            "Udid": str(uuid.uuid4()),
            # "IP": "235.231.34.152",
            "AppVersion": "16.15.0",
            "Domain": "https://m.vueling.com",
            "PaxName": "David",
            "PaxSurname": "Zheng",
            "Email": "nevergiveup17apr05@qq.com",
            "Phone": "+86/8618611715578",
            "RecordLocator": pnr,
            "Comment": "",
            "JourneysKey": [JourneysKey],
            "Type": "Cash",
            "Language": "en-GB"
        }
        resp = self.post(url=url, headers=headers, json=data)
        refund_VY_logger.info(f'{resp.text}')
        if 'IsSendMailOk' in resp.text:
            refund_VY_logger.info(f'全退成功')
            return 'success'
        return 'failure'





