import os
os.chdir("../../")

import unittest
from auto_check.ALM.ALMCheckApi import ALMCheckWeb
from auto_check.ALM.ALMCheckService import ALMCheckService
from utils.searchparser import parser_from_task




def test_check_api():
    # app = ALMCheckWeb(proxies_type=7, retry_count=3, timeout=60)
    # app.check(last_name='DALGARNO',pnr='ADHJ6S')

    ALMCheckService.show_check_part_info(last_name="HANNON", pnr="ADHHV8")


if __name__ == '__main__':
    test_check_api()