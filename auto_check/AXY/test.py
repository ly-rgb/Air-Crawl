# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "测试文件"
@Date: 2022/11/9 15:10
"""

import os
import time

os.chdir("../../")

import unittest
from auto_check.AXY.AXYCheckApi import AXYCheckWeb
from auto_check.AXY.AXYCheckService import AXYCheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"

        app = AXYCheckWeb(proxies_type=0)
        # app.session_create()
        app.retrieve_booking(last_name="ALSHAMLY IBRAHIM", pnr="GHKZQB")
        app.check()

    def test_check_service(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"

        result = AXYCheckService.show_check_part_info(last_name="ALMAKALAWI", pnr="V74QUV")
        print(result)







