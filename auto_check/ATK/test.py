# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/11/30 15:58
"""

import os
os.chdir("../../")
import unittest

from auto_check.ATK.ATKCheckApi import ATKCheckWeb
from auto_check.ATK.ATKCheckService import ATKCheckService


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"

        app = ATKCheckWeb(proxies_type=0)

        app.check(last_name="MITSUI", pnr="SNPLQ7")

    def test_check_service(self):

        app = ATKCheckService()
        result = app.show_check_part_info(last_name="MCKIRDY", pnr="WFJNBX")
        print(result)