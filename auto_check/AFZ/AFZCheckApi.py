# -*- coding: UTF-8 -*-
from utils.astoip_proxy_3 import get_astoip_http_proxy

from utils.log import check_FZ_logger

from airline.base import AirAgentV3Development


class AFZCheckWeb(AirAgentV3Development):
    """
    对sign值的判断
    sign有值则请求成功
    sign = ""预定已过期或者没找到该订单
    sign = None 发起请求失败
    """

    def __init__(self, proxies_type=0, retry_count=3, timeout=60):
        super().__init__(proxies_type, retry_count, timeout)
        self.sign = None

    def return_sign_api(self, last_name: str, pnr: str):

        try:
            url = "https://www.flydubai.com/en/Form/ManageBookingCredentials"

            file = {'LastName': (None, last_name, 'application/json, text/javascript, */*; q=0.01', None),
                    'ReferenceNumber': (None, pnr, 'application/json, text/javascript, */*; q=0.01', None),
                    'AppId': (None, 'Desktop', 'application/json, text/javascript, */*; q=0.01', None)}

            headers = {
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'closed',
                'Origin': 'https://www.flydubai.com',
                'Pragma': 'no-cache',
                'Referer': 'https://www.flydubai.com/en/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }

            response = self.post(url=url, headers=headers, files=file, verify=False)

            check_FZ_logger.info(f"status_code: {response.status_code}")
            check_FZ_logger.info(f"response_text: {response.text}")
            if response.status_code == 200:

                result = self.json.loads(response.text)

                if result["desktopUrl"] != "":
                    desktop_url = result["desktopUrl"]

                    self.sign = desktop_url.split("=")[-1]
                    check_FZ_logger.info(f"从desktopUrl中提取到的加密值为: {self.sign}")
                else:

                    self.sign = ""
        except:
            import traceback
            check_FZ_logger.error(f"{traceback.print_exc()}")

    def fz_check_api(self):

        """
        得到质检的所有数据的response对象
        :return:
        """

        try:

            if self.sign is None:
                return None

            elif self.sign == "":

                return ""
            else:
                url = "https://bookings1.flydubai.com/api/modify/booking/" + self.sign
                headers = {
                    'authority': 'bookings1.flydubai.com',
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    'cache-control': 'no-cache',
                    'Connection': 'closed',
                    'pragma': 'no-cache',
                    'referer': 'https://bookings1.flydubai.com/en/booking/view?websessionid=spHgxtqIEkBDrk',
                    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                }

                response = self.get(url=url, headers=headers, verify=False)
                self.check_info_response = response

                check_FZ_logger.info(f"FZ质检接口的resposne_status: {response.status_code}")

                return self.check_info_response

        except Exception:
            import traceback

            check_FZ_logger.error(f"{traceback.print_exc()}")


if __name__ == '__main__':
    app = AFZCheckWeb()

    app.return_sign_api("WU", "QOTMLK")
    print(app.sign)
    response = app.fz_check_api()



