import os
os.chdir("../../")

import unittest
from auto_check.AQG.AQGCheckApi import AQGCheckWeb
from auto_check.AQG.AQGCheckService import AQGCheckService
from utils.searchparser import parser_from_task




def test_check_api():
    # app = AQGCheckWeb(proxies_type=7, retry_count=3, timeout=60)
    # app.check(last_name='ROHANI',pnr='RF9PNG')

    AQGCheckService.show_check_part_info(last_name="LIANG", pnr="M9K6SI")


if __name__ == '__main__':
    test_check_api()