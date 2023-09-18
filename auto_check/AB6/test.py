# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/12/7 15:54
"""

import os
import time

os.chdir("../../")

import unittest
from auto_check.AB6.AB6CheckApi import AB6CheckWeb
from auto_check.AB6.AB6CheckService import AB6CheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"


        app = AB6CheckWeb(proxies_type=7)
        app.check(last_name="CHISHOLM", pnr="CKNYYP")

    def test_check_service(self):

        app = AB6CheckService()
        result = app.show_check_part_info(last_name="DELEVANTE", pnr="EVSAXH")
        print(result)