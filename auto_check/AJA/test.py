# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/11/18 14:57
"""

import os
os.chdir("../../")

import unittest
from auto_check.AJA.AJACheckApi import AJACheckWeb
from auto_check.AJA.AJACheckService import AJACheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"

        app = AJACheckWeb(proxies_type=7)
        app.retrieve_check(last_name="GUASTAMACCHIA", pnr="P28KFL")
        app.check()

    def test_check_service(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"

        result = AJACheckService.show_check_part_info(last_name="GUASTAMACCHIA", pnr="P28KFL")
        print(result)