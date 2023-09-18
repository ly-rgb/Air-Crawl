# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/10/29 16:14
"""

import os
os.chdir("../../")

import unittest
from auto_check.AEW.AEWCheckApi import AEWCheckWeb
from auto_check.AEW.AEWCheckService import AEWCheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"

        app = AEWCheckWeb(proxies_type=0)
        app.front_check(last_name="MARTINEZBORREL", pnr="ZJHUWQ")
        app.check_redirect(last_name="MARTINEZBORREL", pnr="ZJHUWQ", gender="MR")
        app.check()

    def test_check_service(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"

        AEWCheckService.show_check_part_info(last_name="KRIEGLER", pnr="RCHGKF", gender="")



