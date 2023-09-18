# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/11/11 15:38
"""

import os
os.chdir("../../")

import unittest
from auto_check.AVB.AVBCheckApi import AVBCheckWeb
from auto_check.AVB.AVBCheckService import AVBCheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"

        app = AVBCheckWeb(proxies_type=0)

        app.check(last_name="NG", pnr="GD8VRQ")
    def test_check_service(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"
        result = AVBCheckService.show_check_part_info(last_name="SANCHEZ", pnr="IDMJYQ")
