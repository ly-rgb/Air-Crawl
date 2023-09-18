import os
import json
import re
import requests
from loguru import logger
from py_mini_racer import MiniRacer

# os.environ['http_proxy'] = 'http://127.0.0.1:8888'
# os.environ['https_proxy'] = 'http://127.0.0.1:8888'


class AIN:

    def __init__(self):
        self.session = requests.session()

    def get_Authorization(self,ssrdata):
        ctx = MiniRacer()
        with open('./aio_test_js.js','r',encoding='utf8') as f:
            js = f.read()
        ctx.eval(js)
        return ctx.call('autho',ssrdata)

    def search(self):
        try:
            ssrdata_url = "https://k.airasia.com/ssr/v2/getssrdata"
            headers = {
                'Accept': 'application/json',
                'channel_hash': '98ba1fad5baab2959fd06259acc292c6ebf46e210735882afc32a084',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            }
            res_ssrdata = self.session.post(url=ssrdata_url, headers=headers)
            if res_ssrdata.status_code == 200:
                ssrdata =res_ssrdata.json()
                logger.info(ssrdata)
            else:
                raise Exception('ssrdata获取失败..')
            ticket_info_url = 'https://k.airasia.com/shopprice-n/api/v4/pricesearch/0/0/BKK/CNX/2022-10-03/1/0/0'
            logger.info(self.get_Authorization(ssrdata))
            headers = {
                'Authorization': self.get_Authorization(ssrdata)['search'],
                'Accept': 'application/json',
                'channel_hash': '98ba1fad5baab2959fd06259acc292c6ebf46e210735882afc32a084',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            }
            ticket_info_res = self.session.get(url=ticket_info_url, headers=headers)
            logger.debug(ticket_info_res.text)




        except Exception as e:
            logger.debug(e)

    def convert_search(self):

        result = []
        try:

            return result

        except Exception:
            pass


if __name__ == '__main__':
    ain = AIN()
    ain.search()
